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

**clean:** Cleans the workspace

**download:** downloads datasett and YOLACT

**setup:** Clean & Download

**train:** Begin training network

**prune:** Relabel low-quantity training examples

**eval:** Run the network on a video or RTMP stream

## Modules

## Download and prune dataset
Downloads the dataset, then prunes classes with fewer than 50 training instances.
```
$ ./recyclr.py download
$ ./recyclr.py prune 50
```
## Train:

```sh
$ ./recyclr.py train
```

## Eval:

```sh
$ ./recyclr.py eval
````

## Download mode:
If you want to manually run commands, you can use the download module to download datasets, weights, and backbones so you can run commands without needing to setup everything.

```sh
$ python recyclr.py download
```