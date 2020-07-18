import os
import sys
import setup
import ship

from pathlib import Path

MODULES = [
    'clean',
    'download',
    'eval',
    'train',
    'ship'
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
    elif module == 'ship'
    pass

if __name__ == '__main__':
    main()