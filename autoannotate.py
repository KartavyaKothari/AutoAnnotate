import json
import os
import re
import argparse

def getSpans(pattern,raw_txt,tag):
    spans = []
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = tag
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getGenderAnnotations(raw_txt):
    annotations = []
    gender_words = ['he','her','she','his','him','man','woman','men','women','mr','mrs','brother','sister','wife','husband','uncle','male','female']
    for gender in gender_words:
        annotations.extend(getSpans(r'\b'+gender+r'\b',raw_txt,"GENDER"))
  
    return annotations

def getBasicAnnotations(raw_txt):
    allAnnotations = []
    allAnnotations.extend(getGenderAnnotations(raw_txt))
    allAnnotations.extend(getSpans(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+',raw_txt,"EMAIL"))
    
    return {"named_entity":sorted(allAnnotations,key=lambda x: x["start"])}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input file path")
    av = ap.parse_args()

    with open(av.input, 'r') as json_file:
        documents = [json.loads(i) for i in list(json_file)]

    with open(av.input, 'w') as json_file:
        for document in documents:
            document["annotations"] = getBasicAnnotations(document["raw_text"])
            json_file.write(json.dumps(document) + "\n")      
