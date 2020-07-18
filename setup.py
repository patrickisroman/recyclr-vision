# BRIEF: 
#   - sets up recyclr environment
#
# > download coco
# > download weights
# > download dataset
# > download backbone
# > organize assets
# > update yolact configuration

import os
import wget
import tarfile
import shutil
import json
import boto3
import sys
import ship

from git import Repo
from botocore import UNSIGNED
from botocore.client import Config
from google_drive_downloader import GoogleDriveDownloader as gdd
from pathlib import Path

# Setup Directory
CURRENT_DIRECTORY  = Path(__file__).absolute().parent
TMP_DIRECTORY      = CURRENT_DIRECTORY.joinpath('tmp')
OUT_DIRECTORY      = CURRENT_DIRECTORY.joinpath('recyclr')
DATASET_DIRECTORY  = OUT_DIRECTORY.joinpath('datasets')
RECYCLR_DIRECTORY  = DATASET_DIRECTORY.joinpath('recyclr')
YOLACT_DIRECTORY   = RECYCLR_DIRECTORY.joinpath('yolact')
DATA_DIRECTORY     = RECYCLR_DIRECTORY.joinpath('data')
BACKBONE_DIRECTORY = YOLACT_DIRECTORY.joinpath('weights')

# External Data URLs
DATASET_URL     = 'https://recyclr.s3-us-west-2.amazonaws.com/frames.tar.gz'
ANNOTATIONS_URL = 'https://recyclr.s3-us-west-2.amazonaws.com/coco_new.json'
WEIGHTS_URL     = 'https://recyclr.s3-us-west-2.amazonaws.com/weights.pth'
YOLACT_GIT_URL  = 'https://github.com/dbolya/yolact.git'
BACKBONE_URL_ID = '1tvqFPd4bJtakOlmn-uIA492g2qurRChj'

DATASET_FILE     = 'frames.tar.gz'
ANNOTATIONS_FILE = 'coco_new.json'
WEIGHTS_FILE     = 'weights.pth'
BACKBONE_FILE    = 'resnet101_reducedfc.pth'

DATASET_PATH     = TMP_DIRECTORY.joinpath(DATASET_FILE)
ANNOTATIONS_PATH = TMP_DIRECTORY.joinpath(ANNOTATIONS_FILE)
WEIGHTS_PATH     = TMP_DIRECTORY.joinpath(WEIGHTS_FILE)

YOLACT_RECYCLR_CONF = 'yolact_recyclr_config'

# Boto setup
BOTO_S3_CLIENT = boto3.client('s3', config=Config(signature_version=UNSIGNED))

def train():
    # command args
    input_video = 'validation720.mov'
    output_video = 'output.mp4'
    video_multiframe = 1
    top_k = 15
    score_threshold = .3
    config = 'yolact_plus_base_recyclr_config'
    # loaded
    weight = [w for w in os.listdir('./weights') if 'interrupt' in w][-1] if os.path.exists('./weights') else None
    train_file = YOLACT_DIRECTORY.joinpath('train.py')

    if weight is not None:
        os.system('python %s --config=%s --cuda=1 --resume=./weights/%s --save_interval=1000' %(train_file, config, weight))
    else:
        os.system('python %s --config=%s --cuda=1 --save_interval=1000' % (train_file, config))

def eval():
    # command args
    input_video = 'a.mov'
    output_video = 'output.mp4'
    video_multiframe = 1
    top_k = 15
    score_threshold = .35
    config = 'yolact_plus_base_recyclr_config'
    # loaded
    weight = [w for w in os.listdir('./weights') if 'interrupt' in w][-1]
    if weight:
        os.system('python recyclr/yolact/eval.py --trained_model=./weights/%s --config=%s --top_k=%s --score_threshold=%s --video_multiframe=%s --video=%s:%s' %  (weight, config, top_k, score_threshold, video_multiframe, input_video, output_video))

def download():
    clean()

    if not TMP_DIRECTORY.exists():
        TMP_DIRECTORY.mkdir()

    if not WEIGHTS_PATH.exists():
        print('\nDownloading weights')
        BOTO_S3_CLIENT.download_file('recyclr', WEIGHTS_FILE, str(WEIGHTS_PATH))

    if not DATASET_PATH.exists():
        print('\nDownloading dataset')
        BOTO_S3_CLIENT.download_file('recyclr', DATASET_FILE, str(DATASET_PATH))
    
    if not ANNOTATIONS_PATH.exists():
        print('\nDownloading annotations')
        BOTO_S3_CLIENT.download_file('recyclr', ANNOTATIONS_FILE, str(ANNOTATIONS_PATH))

def setup_tmp():
    if not OUT_DIRECTORY.exists():
        OUT_DIRECTORY.mkdir()
    
    if not DATASET_DIRECTORY.exists():
        DATASET_DIRECTORY.mkdir()

    if not RECYCLR_DIRECTORY.exists():
        RECYCLR_DIRECTORY.mkdir()

    if not TMP_DIRECTORY.exists():
        TMP_DIRECTORY.mkdir()

    if not DATA_DIRECTORY.exists():
        DATA_DIRECTORY.mkdir()

    download()

    assert(DATASET_PATH.exists())

    # extract dataset to dataset directory
    tar = tarfile.open(str(DATASET_PATH))
    print('Extracting dataset "%s" to %s' % (DATASET_FILE, DATA_DIRECTORY))
    tar.extractall(path=str(DATA_DIRECTORY))
    tar.close()
    
    # setup git
    print('Cloning YOLACT base')
    Repo.clone_from(YOLACT_GIT_URL, YOLACT_DIRECTORY)

def setup_coco():
    print('Loading COCO annotation file')
    with open(ANNOTATIONS_PATH, 'r') as f:
        coco_obj = json.loads(f.read())
        for i in range(len(coco_obj['images'])):
            coco_obj['images'][i]['path'] = coco_obj['images'][i]['file_name']
    
    print('Writing updated COCO annotation file')
    out_annotation_dir = DATA_DIRECTORY.joinpath(ANNOTATIONS_FILE)
    with open(out_annotation_dir, 'w+') as f:
        f.write(json.dumps(coco_obj, indent=4))

def setup_yolact():
    print('Setting up YOLACT configuration')
    if not BACKBONE_DIRECTORY.exists():
        BACKBONE_DIRECTORY.mkdir()

    print('Downloading resnet101 backbone')
    gdd.download_file_from_google_drive(
        file_id=BACKBONE_URL_ID,
        dest_path=BACKBONE_DIRECTORY.joinpath(BACKBONE_FILE)
        )
    
    print('File Downloaded')
    config_file = YOLACT_DIRECTORY.joinpath('data').joinpath('config.py')

    def generate_yolact_config():
        # build category list
        conf_str_template = (
            "recyclr_dataset = dataset_base.copy({\n"
            "\t'name'         : 'Recyclr Dataset',\n"
            "\t'train_info'   : '%s',\n"
            "\t'train_images' : '%s',\n"
            "\t'valid_info'   : '%s',\n"
            "\t'valid_images' : '%s',\n"
            "\t'class_names'  : %s,\n"
            "\t'label_map'    : {k:k for k in range(200)}\n"
            "})\n"
        )

        category_list = []
        with open(DATA_DIRECTORY.joinpath(ANNOTATIONS_FILE), 'r') as ann:
            json_obj = json.loads(ann.read())
            for cat in json_obj['categories']:
                category_list.append(cat['name'])
            
        cat_list = str(category_list).replace('[', '(').replace(']', ')')
        rel_annotation_path = os.path.relpath(DATA_DIRECTORY.joinpath(ANNOTATIONS_FILE), YOLACT_DIRECTORY)
        rel_data_path = os.path.relpath(DATA_DIRECTORY, YOLACT_DIRECTORY)

        conf_str = conf_str_template % (
            rel_annotation_path,
            rel_data_path,
            rel_annotation_path,
            rel_data_path,
            cat_list
        )

        # build model setup
        model_str_template = (
            "\n%s = yolact_base_config.copy({\n"
            "\t'name' : '%s',\n"
            "\t'dataset' : recyclr_dataset,\n"
            "\t'num_classes' : %d,\n"
            "\t'max_size' : 700\n"
            "})\n"
        )

        model_str = model_str_template % (
            YOLACT_RECYCLR_CONF,
            YOLACT_RECYCLR_CONF,
            len(category_list) + 1
        )
        
        return (conf_str, model_str)
    
    print('Updating yolact configuration')
    data_conf = generate_yolact_config()

    current_conf = open(config_file, 'r')
    contents = current_conf.readlines()
    conf_line = 0
    model_line = 0

    for i, line in enumerate(contents):
        if 'TRANSFORMS' in line:
            conf_line = i - 1
        if 'yolact_im400_config' in line:
            model_line = i
    
    contents.insert(conf_line, data_conf[0])
    contents.insert(model_line, data_conf[1])

    OUT_CONF_FILE = YOLACT_DIRECTORY.joinpath('data').joinpath('config.py')

    with open(OUT_CONF_FILE, 'w+') as f:
        f.write(''.join(contents))

    print('Finished setting up YOLACT configuration')


def setup():
    print('\n=== Recyclr Setup ====')
    setup_tmp()
    setup_coco()
    setup_yolact()
    print('=== Setup Completed ===\n')

def clean():
    # clean tmp directory
    if TMP_DIRECTORY.exists():
        shutil.rmtree(str(TMP_DIRECTORY))

    # clean dataset directory
    if DATASET_DIRECTORY.exists():
        shutil.rmtree(str(DATASET_DIRECTORY))
    
    # clean yolact repo
    if YOLACT_DIRECTORY.exists():
        shutil.rmtree(str(YOLACT_DIRECTORY))
    
    # clean recyclr environment
    if RECYCLR_DIRECTORY.exists():
        shutil.rmtree(str(RECYCLR_DIRECTORY))
    
def main():
    clean()
    setup()

if __name__ == '__main__':
    main()
