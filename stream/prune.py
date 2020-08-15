import json
import os
from .stream_manager import StreamManager

def prune(coco_file, min_items_per_class=10):
    if not os.path.exists(coco_file):
        return None
    
    with open(coco_file, 'r') as f:
        src = f.read()
    
    src = src.replace('/datasets/b/', '/data/')
    a = json.loads(src)

    # create our stream manager and get all possible classes in reverse tree order
    sm = StreamManager()
    reversed_classes = sm.in_order_list(reverse_list=True)

    # track pruning mappings (start id -> end id)
    prune_mappings = {cat['id']:None for cat in a['categories']}
    # track number of instances of each category
    categories = {cat['id']:0 for cat in a['categories']}
    # mapping from name to id / id to name
    name_to_id = {cat['name']:cat['id'] for cat in a['categories']}
    id_to_name = {v:k for k,v in name_to_id.items()}

    def get_name(id):
        return id_to_name[id] if id in id_to_name else None
    
    def get_id(name):
        return name_to_id[name] if name in name_to_id else None
    
    # count up how many of each category is in the dataset
    for ann in a['annotations']:
        categories[ann['category_id']] += 1
    

    for category in reversed_classes:
        if get_id(category) is None:
            continue

        if categories[get_id(category)] < min_items_per_class:
            node = sm.search_tree(category)
            if not node or node.predecessor(sm.stream_tree.identifier) is None:
                continue
            
            parent = node.predecessor(sm.stream_tree.identifier)
            p_id, n_id = get_id(parent), get_id(node.identifier)
            if p_id is None or n_id is None:
                continue

            categories[p_id] += categories[n_id]
            categories[n_id] = 0

            # add the prune mapping (old -> new)
            prune_mappings[n_id] = p_id
    
    # for each annotation, find the highest unpruned parent
    for i in range(len(a['annotations'])):
        ann = a['annotations'][i]
        cat = ann['category_id']

        if cat not in prune_mappings or prune_mappings[cat] is None:
            continue

        while prune_mappings[cat] is not None:
            cat = prune_mappings[cat]
        a['annotations'][i]['category_id'] = cat
    
    return a