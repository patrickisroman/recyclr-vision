import taco_connector
import trashcan_connector

class Connector:
    def __init__(self):
        self.taco = taco_connector.mapping
        self.trashcan = trashcan_connector.mapping
    
    def __convert_coco(self, file, mapping, target_mapping):
        with open(file, 'r') as f:
            annotations = json.loads(f.read())
        
        categories = {a['id']:a['name'].lower() for a in annotations['categories']}
        annotations = annotations['annotations']
        results = []
        for i in range(len(annotations)):
            cat = annotations[i]['category_id']

            if cat not in mapping:
                continue

            if mapping[cat] not in target_mapping:
                continue

            if mapping[cat][0] is None or target_mapping[mapping[cat]] is None:
                continue

            (element, material) = target_mapping[mapping[cat]]
            annotations[i]['category_id'] = element
            annotations[i]['material'] = material
            results.append(annotations[i])
        
        return results
    
    def convert_taco_coco(self, taco_file, target_mapping):
        return self.__convert_coco(taco_file, self.taco, target_mapping)
    
    def convert_trashcan_coco(self, trashcan_file, target_mapping):
        return self.__convert_coco(trashcan_file, self.trashcan, target_mapping)

