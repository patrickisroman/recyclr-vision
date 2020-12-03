#!/usr/bin/env python

import os
import sys
import setup

from pathlib import Path

MODULES = [
    'clean',
    'download',
    'eval',
    'train',
    'prune',
    'setup'
]

def parse_module():
    assert len(sys.argv) > 1, "No module provided.\n\nAccepted Modules: %s" % MODULES

    module = sys.argv[1]
    assert module in MODULES, "Invalid module provided.\n\nAccepted Modules: %s" % MODULES

    return module

def main():
    module = parse_module()

    if module == 'setup':
        setup.setup()
    elif module == 'clean':
        setup.clean()
    elif module == 'download':
        setup.download()
    elif module == 'eval':
        setup.evaluate()
    elif module == 'train':
        setup.train()
    elif module == 'prune':
        prune_num = 10
        if len(sys.argv) > 2:
            prune_num = int(sys.argv[2])
        setup.prune_coco(prune_num)

if __name__ == '__main__':
    main()
