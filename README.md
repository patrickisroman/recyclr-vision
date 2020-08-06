# Recyclr Vision

Recyclr vision is the computer vision portion of Recyclr, which is responsible for trash/recyclable object detection and stream sorting.

![Test](https://i.imgur.com/L4kuEJD.jpg)

# Setup Environment

## Install Requirements:
```sh
virtualenv recyclrenv
source recyclrenv/bin/activate
pip install -r requirements.txt
pip install torch==1.2.0 torchvision==0.4.0 pycocotools
```

## Train:

```sh
$ python recyclr.py train
```

## Eval:

```sh
$ python recyclr.py eval
````

## Download mode:
If you want to manually run commands, you can use the download module to download datasets, weights, and backbones so you can run commands without needing to setup everything.

```sh
$ python recyclr.py download
```