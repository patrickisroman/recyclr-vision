from pathlib import Path, PosixPath
from detection import Detection
from utils import DynamicEnum
from enum import Enum

import random
import config
import json as jsonlib

'''
Loads config/streams.json into a dynamic mapping
'''

class Sorter:
    def __init__(self, streams=config.streams_file, elements=config.elements_file, materials=config.material_file):
        self.materials = config.ConfigTree(materials, 'materials')
        self.elements = config.ConfigTree(elements, 'elements')
        self.streams = self.__load_streams(streams)
    
        self.enums = dict()
        self.enums['streams'] = DynamicEnum.from_json({k:i for i,k in enumerate(self.streams['streams'])}, 'stream')
        self.enums['elements'] = self.elements.to_enum()
        self.enums['materials'] = self.materials.to_enum()

        self.sort_map = self.__generate_sort_map()
    
    def __generate_sort_map(self):
        sort_map = dict()
        sort_map['default'] = {'default' : 'default'}

        for m,s in self.streams['materials'].items():
            if not m in sort_map:
                sort_map[m] = {'default' : 'default'}

            if type(s) is str:
                sort_map[m]['default'] = s
            elif type(s) is dict:
                for e,s in s.items():
                    sort_map[m][e] = s
        
        return sort_map

    def __load_streams(self, streams):
        if isinstance(streams, (Path, PosixPath)):
            with open(streams, 'r') as f:
                streams = f.read()
        
        if type(streams) is str:
            streams = jsonlib.loads(streams)
        
        return streams

    def sort(self, detection:Detection=None, material=None, element=None):
        if detection is not None:
            (element, material) = (detection.element, detection.material)
        
        if element is None or material is None:
            return None

        if type(element) is Enum:
            element = element.name
        
        if type(material) is Enum:
            material = material.name

        current_material = material
        current_element = element

        if current_material is None or current_element is None:
            return None

        while not current_material in self.sort_map:
            current_material = self.materials.get_parents(current_material)[0]

        while not current_element in self.sort_map[current_material]:
            current_element = self.elements.get_parents(current_element)[0]

        return self.enums['streams'].enum(self.sort_map[current_material][current_element])
    
    def get_stream_list(self, stream):
        out = list()

        for m in self.enums['materials']:
            for e in self.enums['elements']:
                if self.sort(material=m.name, element=e.name) == stream:
                    out.append((m.name, e.name))
    
        return out
    
    def get_map(self):
        return self.sort_map.copy()