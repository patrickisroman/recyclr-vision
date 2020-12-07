from . import taco_connector
from . import trashcan_connector

import json

class Connector:
    def __init__(self):
        self.taco = taco_connector.mapping
        self.trashcan = trashcan_connector.mapping
    
    def __convert_coco(self, file, mapping, target_mapping):
        with open(file, 'r') as f:
            annotations = json.loads(f.read())
        
        categories = {int(a['id']):a['name'].lower() for a in annotations['categories']}
        annotations = annotations['annotations']
        results = []
        for i in range(len(annotations)):
            category_id = annotations[i]['category_id']
            if category_id not in categories or categories[category_id] not in mapping:
                continue

            category_name = categories[category_id]
            if mapping[category_name][0] is None:
                continue

            (element, material) = mapping[category_name]
            if element not in target_mapping:
                continue

            target_id = target_mapping[element]
            
            annotations[i]['category_id'] = target_id
            if material is not None:
                annotations[i]['material'] = material
    
            results.append(annotations[i])

        return results
    
    def convert_taco_coco(self, taco_file, target_mapping):
        return self.__convert_coco(taco_file, self.taco, target_mapping)
    
    def convert_trashcan_coco(self, trashcan_file, target_mapping):
        return self.__convert_coco(trashcan_file, self.trashcan, target_mapping)