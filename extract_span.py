import json
import os
import re
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input file path")
    ap.add_argument("--tag", required=True, help="Tag to be extracted")
    av = ap.parse_args()

    with open(av.input, 'r') as json_file:
        documents = [json.loads(i) for i in list(json_file)]

    with open(av.tag+'s.koala', 'w') as json_file:
        for document in documents:
            for ne in document['annotations']['named_entity']:
                if ne['tag'].lower() == av.tag.lower():
                    json_file.write(ne['extent'] + "\n")