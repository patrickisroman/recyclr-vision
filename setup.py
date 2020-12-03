# BRIEF: 
#   - sets up recyclr environment
#
# > download coco
# > download weights
# > download dataset
# > download backbone
# > organize assets
# > update yolact configuration

import subprocess
import os
import wget
import tarfile
import shutil
import json
import boto3
import sys

from git import Repo
from botocore import UNSIGNED
from botocore.client import Config
from google_drive_downloader import GoogleDriveDownloader as gdd
from pathlib import Path
from stream import stream_manager
from stream import prune

# Yolact Configurations

VIDEO_MULTIFRAME = .1
TOP_K = 15
SCORE_THRESHOLD = .5

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
YOLACT_GIT_URL  = 'https://github.com/dbolya/yolact.git'
BACKBONE_URL_ID = '1tvqFPd4bJtakOlmn-uIA492g2qurRChj'

DATASET_FILE     = 'frames.tar.gz'
ANNOTATIONS_FILE = 'coco_new.json'
WEIGHTS_FILE     = 'weights.pth'
BACKBONE_FILE    = 'resnet101_reducedfc.pth'

DATASET_PATH     = TMP_DIRECTORY.joinpath(DATASET_FILE)
ANNOTATIONS_PATH = TMP_DIRECTORY.joinpath(ANNOTATIONS_FILE)
WEIGHTS_PATH     = TMP_DIRECTORY.joinpath(WEIGHTS_FILE)

YOLACT_CONF = 'yolact_recyclr_config'

# Boto setup
BOTO_S3_CLIENT = boto3.client('s3', config=Config(signature_version=UNSIGNED))

def train():
    config = YOLACT_CONF
    weight = None
    if os.path.exists('./weights'):
        weight = [w for w in os.listdir('./weights') if 'interrupt' in w][-1]
    train_file = YOLACT_DIRECTORY.joinpath('train.py')

    if weight is not None:
        cmd = [
            'python',
            train_file,
            '--config=%s' % config,
            '--cuda=1', '--resume=./weights/%s' % weight,
            '--save_interval=1000'
            ]
    else:
        cmd = ['python', train_file, '--config=%s' % config, '--cuda=1', '--save_interval=1000']

    p = subprocess.Popen(cmd, cwd=str(os.path.abspath(YOLACT_DIRECTORY)))
    p.wait()

def prune_coco(min_items_per_class=10):
    sm = stream_manager.StreamManager()
    return prune.prune(ANNOTATIONS_FILE, min_items_per_class)

def evaluate(config=YOLACT_CONF,
             top_k=TOP_K,
             score_threshold=SCORE_THRESHOLD,
             video_multiframe=VIDEO_MULTIFRAME,
             input_video='input.mov',
             output_video='output.mp4'):

    # loaded
    if os.path.exists(BACKBONE_DIRECTORY):
       weight = [w for w in os.listdir(BACKBONE_DIRECTORY) if 'interrupt' in w][-1]
       weight = BACKBONE_DIRECTORY.joinpath(weight)
   
    print(weight)
    if not weight:
        return

    cmd = [
        'python',
        'eval.py',
        '--trained_model=%s' % weight, 
        '--config=%s' % config,
        '--top_k=%s' % top_k, 
        '--score_threshold=%s' % score_threshold,
        '--video_multiframe=%s' % video_multiframe,
        '--video=%s:%s' % (input_video, output_video)
        ]
    p = subprocess.Popen(cmd, cwd=str(os.path.abspath(YOLACT_DIRECTORY)))
    p.wait()

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
        category_list = []
        with open(DATA_DIRECTORY.joinpath(ANNOTATIONS_FILE), 'r') as ann:
            json_obj = json.loads(ann.read())
            for cat in json_obj['categories']:
                category_list.append(cat['name'])
            
        cat_list = str(category_list).replace('[', '(').replace(']', ')')
        abs_annotation_path = os.path.abspath(DATA_DIRECTORY.joinpath(ANNOTATIONS_FILE))
        abs_data_path = os.path.abspath(DATA_DIRECTORY)

        shutil.copyfile(WEIGHTS_PATH, BACKBONE_DIRECTORY.joinpath(WEIGHTS_FILE))

        conf_str_template = (
            "recyclr_dataset = dataset_base.copy({\n"
            "\t'name'         : 'Recyclr Dataset',\n"
            "\t'train_info'   : '%s',\n"
            "\t'train_images' : '%s',\n"
            "\t'valid_info'   : '%s',\n"
            "\t'valid_images' : '%s',\n"
            "\t'class_names'  : %s,\n"
            "\t'label_map'    : {k:k for k in range(200)}\n"
            "})\n")
        
        conf_str = conf_str_template % (
            abs_annotation_path,
            abs_data_path,
            abs_annotation_path,
            abs_data_path,
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
            YOLACT_CONF,
            YOLACT_CONF,
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
    
    contents.insert(conf_line,  data_conf[0])
    contents.insert(model_line, data_conf[1])

    out_conf_file = YOLACT_DIRECTORY.joinpath('data').joinpath('config.py')

    with open(out_conf_file, 'w+') as f:
        f.write(''.join(contents))

    print('YOLACT configuration generated at %s' % out_conf_file)


def setup():
    print('\nRecyclr Setup')
    setup_tmp()
    setup_coco()
    setup_yolact()
    print('Setup Completed\n')

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
    clean() # clean workspace by default
    setup()

if __name__ == '__main__':
    main()
