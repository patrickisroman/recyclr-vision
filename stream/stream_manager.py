from treelib import Node, Tree
from pathlib import Path
import os
import json
import pathlib

DEFAULT_STREAM_DIR = Path.joinpath(Path(__file__).resolve().parent, 'stream_data/')

class BlankObject:
    def __init__(self, val):
        self.value = val

class StreamManager:
    def __init__(self, stream_dir=DEFAULT_STREAM_DIR):
        self.stream_dir = stream_dir
        self.stream_tree = self.build_stream_tree()
    
    def print_stream(self):
        self.stream_tree.show()
    
    def search_tree(self, class_name):
        node = self.stream_tree.get_node(class_name)
        return node
    
    # left-to-right in-order list that can be transformed into graph
    def build_stream_tree(self):
        tree = Tree()

        # lol there's probably a 1-liner for this whole function
        def sort_streams(stream_arr):
            visited_streams = []
            iters = 0
            while len(stream_arr) > 0:
                start_len = len(visited_streams)
                for stream in stream_arr:
                    if 'parent' not in stream:
                        visited_streams.insert(0, stream)
                        stream_arr.remove(stream)
                        break
                    for v_stream in visited_streams:
                        if v_stream['stream'] == stream['parent']:
                            visited_streams.append(stream)
                            stream_arr.remove(stream)
                            break
                if len(visited_streams) == start_len:
                    break
            return visited_streams

        for stream in sort_streams(self.read_streams()):
            if 'parent' in stream:
                tree.create_node(stream['stream'], stream['stream'], data=stream, parent=stream['parent'])
            else:
                tree.create_node(stream['stream'], stream['stream'], data=stream)

        return tree
    
    def read_streams(self):
        streams = []
        for stream_file in self.stream_dir.glob('*.json'):
            with open(stream_file, 'r') as f:
                streams.append(json.loads(f.read()))

        return streams
    
    def get_parent(self, class_name):
        n = self.search_tree(class_name)
        return None if n is None else self.stream_tree.parent(n.identifier)
