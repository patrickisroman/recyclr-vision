from pathlib import Path, PosixPath
from enum import Enum, unique
import json as jsonlib

class DynamicEnum(Enum):
    def __init__(self, enum, *args, **kwargs):
        super(DynamicEnum, self).__init__(*args, **kwargs)
    
    @classmethod
    def as_json(cls, indent=4) -> str:
        return jsonlib.dumps({e.name:e.value for e in set(cls)}, sort_keys=True, indent=indent)

    @classmethod
    def get_enum_names(cls) -> list:
        return [e.name for e in set(cls)]
    
    @classmethod
    def as_enums(cls) -> set:
        return set(cls)

    @classmethod
    def enum(cls, name) -> Enum:
        return next(filter(lambda e: e.name == name, set(cls)))
    
    @classmethod
    def id(cls, id) -> Enum:
        return cls(id)

    @classmethod
    def as_map(cls) -> dict:
        return {e.name : e.value for e in set(cls)}
    
    @classmethod
    def from_json(self, json, name='enum') -> 'DynamicEnum':
        if isinstance(json, (Path, PosixPath)):
            with open(json, 'r') as f:
                json = f.read()

        if type(json) is str:
            json = jsonlib.loads(json)
        
        mapping = {item:i for i,item in enumerate(json.keys())}
        return DynamicEnum(name, mapping)