import json
import os
import re
import argparse

def getSpans(pattern,offset,raw_txt,tag):
    spans = []
    indexes = [i.start() for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for i in indexes:
        ne = {}
        ne["start"] = i
        ne["end"] = i+offset
        ne["tag"] = tag
        ne["extent"] = raw_txt[i:i+offset]
        spans.append(ne)
    return spans

def getGenderAnnotations(raw_txt):
    annotations = []
    gender_words = ['he','she','his','him','man','woman','men','women','mr','mrs','brother','sister']
    for gender in gender_words:
        annotations.extend(getSpans(r'\b'+gender+r'\b',len(gender),raw_txt,"GENDER"))
  
    return annotations

def getBasicAnnotations(raw_txt):
    allAnnotations = []
    allAnnotations.extend(getGenderAnnotations(raw_txt))
    return {"named_entity":sorted(allAnnotations,key=lambda x: x["start"])}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="OpenEA base dir (in)")
    av = ap.parse_args()

    with open(av.input, 'r') as json_file:
        documents = [json.loads(i) for i in list(json_file)]

    with open(av.input, 'w') as json_file:
        for document in documents:
            document["annotations"] = getBasicAnnotations(document["raw_text"])
            json_file.write(json.dumps(document) + "\n")      