import os
import sys
import setup

from pathlib import Path

MODULES = [
    'clean',
    'download',
    'eval',
    'train',
    'prune'
]

def parse_module():
    assert len(sys.argv) > 1, "No module provided"
    module = sys.argv[1]
    assert module in MODULES, "Invalid module provided.\n\tAccepted Modules:\n\t\t- %s" % MODULES
    return module

def main():
    module = parse_module()

    if module == 'clean':
        setup.clean()
    elif module == 'download':
        setup.download()
    elif module == 'eval':
        setup.eval()
    elif module == 'train':
        setup.train()
    elif module == 'prune':
        prune_num = 10
        if len(sys.argv) > 2:
            prune_num = int(sys.argv[2])
        setup.prune_coco(prune_num)

if __name__ == '__main__':
    main()
