import sys
from pathlib import Path

# Add base directory
PWD = Path(__file__).parent
ANNOTATION_DIR = PWD.parent
sys.path.append(str(ANNOTATION_DIR))
ROOT_DIR = ANNOTATION_DIR.parent
sys.path.append(str(ROOT_DIR))

import shutil
import subprocess
import os
import annotation
import json as jsonlib

from PIL import Image
from git import Repo

TACO_GIT_REPO_URL = 'https://github.com/pedropro/TACO.git'

VIRTUALENV_PYTHON = PWD.parent.parent.joinpath('venv').joinpath('bin').joinpath('python')
TACO_GIT_DIR = PWD.joinpath('taco')
DATA_DIR = PWD.joinpath('data')
TACO_ANNOTATION_FILE = TACO_GIT_DIR.joinpath('taco_annotations.json')

PYTHON_BIN = str(VIRTUALENV_PYTHON) if VIRTUALENV_PYTHON.exists() else 'python'

TACO_DOWNLOAD_FILE = TACO_GIT_DIR.joinpath('download.py')
TACO_DOWNLOAD_COMMAND = [str(VIRTUALENV_PYTHON), str(TACO_DOWNLOAD_FILE)]
TACO_DATA_DIR = TACO_GIT_DIR.joinpath('data')
TACO_GIT_ANNOTATION_FILE = TACO_DATA_DIR.joinpath('annotations.json')

def clean():
    shutil.rmtree(DATA_DIR)
    shutil.rmtree(TACO_GIT_DIR)

def setup():
    if not DATA_DIR.exists():
        DATA_DIR.mkdir()
    
    if not TACO_GIT_DIR.exists():
        TACO_GIT_DIR.mkdir()
        Repo.clone_from(TACO_GIT_REPO_URL, TACO_GIT_DIR)

    if not VIRTUALENV_PYTHON.exists():
        print('Ruh roh, couldn\'t find a virtualenv directory, so this script may fail!')

    # Download taco files using the taco download script
    # Fuck this is slow, it downloads on a single thread, 1 at a time...
    # could cherry pick a commit to download using a threadpool but im too lazy for now 
    p = subprocess.Popen(TACO_DOWNLOAD_COMMAND, cwd=TACO_GIT_DIR)
    p.wait()

    mapping = dict()
    json = dict()
    with open(TACO_GIT_ANNOTATION_FILE, 'r') as f:
        json = jsonlib.loads(f.read())

    image_files = [(img['file_name'], TACO_DATA_DIR.joinpath(img['file_name'])) for img in json['images']]
    for img in image_files:
        if img[1].exists():
            mapping[img[0]] = annotation.md5(img[1])
    
    for file,md5hash in mapping.items():
        shutil.move(TACO_DATA_DIR.joinpath(file), DATA_DIR.joinpath(md5hash + '.jpg'))
    
    for i in range(len(json['images'])):
        f_name = json['images'][i]['file_name']
        if f_name in mapping:
            json['images'][i]['file_name'] = str(DATA_DIR.joinpath(mapping[f_name] + '.jpg'))

    with open(str(TACO_ANNOTATION_FILE), 'w+') as f:
        outstr = jsonlib.dumps(json, indent=4)
        f.write(outstr)
    
    shutil.rmtree(TACO_GIT_DIR)