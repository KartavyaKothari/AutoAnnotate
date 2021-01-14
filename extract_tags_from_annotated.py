import json
import os
import re
import argparse
from os import listdir
from os.path import isfile, join


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input dir path")
    ap.add_argument("--tag", required=True, help="Tag to be extracted")
    av = ap.parse_args()

    documents = []
    for pth in [join(av.input, f) for f in listdir(av.input) if isfile(join(av.input, f))]:
        with open(pth, 'r') as json_file:
            documents.extend([json.loads(i) for i in list(json_file)])

    with open(av.tag+'s.new', 'w') as json_file:
        for document in documents:
            if document is None:
                print("Error in")
                continue
            for ne in document['annotations']['named_entity']:
                if ne['tag'].lower() == av.tag.lower():
                    json_file.write(ne['extent'] + "\n")