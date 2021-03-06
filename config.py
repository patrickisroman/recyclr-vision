import json as jsonlib

from utils import DynamicEnum
from treelib import Node, Tree
from pathlib import Path

config_path   = Path.joinpath(Path(__file__).resolve().parent, 'config')
config_file   = Path.joinpath(config_path, 'config.json')
material_file = Path.joinpath(config_path, 'materials.json')
elements_file = Path.joinpath(config_path, 'elements.json')
streams_file  = Path.joinpath(config_path, 'streams.json')

class ConfigTree():
    def __init__(self, file, name=''):
        if type(file) is str:
            file = Path(file)
        self.tree = self.__load(file)
        self.name = name
    
    def print(self, item=None):
        self.tree.show(nid=self.get(item))
    
    def get_parents(self, child) -> list:
        if type(child) is Enum:
            child = child.name
        return list(self.tree.rsearch(child))[1:]

    def type_of(self, parent, child) -> bool:
        return (self.tree.contains(parent)
            and self.tree.contains(child) 
            and self.tree.is_ancestor(parent, child))

    def get(self, item) -> Node:
        return self.tree.get_node(item)

    def get_parent(self, item) -> Node:
        node = self.get(item)

        if node is None:
            return None

        return self.tree.get_node(node.predecessor(self.tree.identifier))

    def __validate(self, file:Path) -> bool:
        if not file.exists():
            return False
        
        with open(file, 'r') as f:
            src = jsonlib.loads(f.read())
        valid_entries = set(src.keys())
        
        for _,v in src.items():
            if 'parent' in v and v['parent'].strip() not in valid_entries:
                print(v, 'not a valid entry')
                return False
        return True
    
    def __load(self, file:Path):
        if not self.__validate(file):
            raise ValueError('invalid configuration file %s' % file.name)
        
        with open(file, 'r') as f:
            src = jsonlib.loads(f.read())

        tree = Tree()

        # sort all items such that index(parent) < index(child)
        sorted_items = []
        for key,config in src.items():
            if not 'parent' in config:
                sorted_items.insert(0, key)
            elif config['parent'] in sorted_items:
                sorted_items.insert(sorted_items.index(config['parent'])+1, key)
            else:
                sorted_items.insert(1, key)
        
        # build the tree by iterating forward
        for i,item in enumerate(sorted_items):
            tree.create_node(item, item, data=src[item], parent=None if i == 0 else src[item]['parent'])

        return tree
    
    def to_enum(self) -> 'DynamicEnum':
        return DynamicEnum.from_json({k.tag:i for i,k in enumerate(self.tree.all_nodes())}, self.name)
    
if __name__ == '__main__':
    elements = ConfigTree(elements_file)
    materials = ConfigTree(material_file)

    with open('config.tree', 'w+') as f:
        config = {
            'elements' : jsonlib.loads(elements.tree.to_json()),
            'materials' : jsonlib.loads(materials.tree.to_json())
        }
        f.write(jsonlib.dumps(config, indent=4))