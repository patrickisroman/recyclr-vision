# Recyclr Vision

Recyclr vision is the computer vision portion of Recyclr, which is responsible for trash/recyclable object detection and stream sorting.

![Test](https://i.imgur.com/L4kuEJD.jpg)

# Setup Environment

## Install Requirements:
```sh
virtualenv recyclrenv
source recyclrenv/bin/activate
pip install -r requirements.txt
```

```
$ ./recyclr.py --help
Accepted Modules: ['clean', 'download', 'eval', 'train', 'prune', 'setup']
```

## Modules

## download
Downloads the dataset, then prunes classes with fewer than 50 training instances.
```sh
$ ./recyclr.py download
$ ./recyclr.py prune 50
```

## setup
Sets up the environment to train or evaluate
```sh
$ ./recyclr.py setup
```

## train
Trains the network by downloading the dataset, setting up the environment,
and beginning the training
```sh
$ ./recyclr.py train
```

## clean:
Cleans the workspace by removing downloaded files and tmp directories
```sh
$ ./recyclr.py clean
```

## eval:
Evaluates the input on the most recent weights
```sh
$ ./recyclr.py eval inputvideo.mp4
```