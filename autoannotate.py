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
    gender_words = ['he','her','she','his','him','man','woman','men','women','mr','mrs','brother','sister','wife','husband','uncle','male','female','son','daughter','father','mother', 'king', 'queen', 'himself', 'herself', 'motherhood']
    for gender in gender_words:
        annotations.extend(getSpans(r'\b'+gender+r'\b',raw_txt,"GENDER"))
  
    return annotations

def getTimeSpans(raw_txt):
    spans = []
    pattern = r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]|([0-1]?[0-9]|2[0-3]):[0-5][0-9]\s[aApP][mM]|([0-1]?[0-9]|2[0-3]):[0-5][0-9]|[0-1]?[0-9][aApP][mM]'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {"properties":{"DATE-TIME-SUBTYPE":"TIME"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans

def getDateSpans(raw_txt):
    spans = []
    pattern = r'(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01]))[,\s]*[12][0-9]{3})|(((mon|tues?|wed(nes?)|thu(rs)?|fri|sat(ur)?|sun)(day)?)[,\s]*((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]?((0[1-9]|[12]\d|3[01])|([1-9]|[12]\d|3[01])))|((jan|febr?)(uary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)[,\s]*[12][0-9]{3}'
    indexes = [(i.start(),i.end()) for i in re.finditer(pattern,raw_txt,flags=re.IGNORECASE)]
    for t in indexes:
        ne = {"properties":{"DATE-TIME-SUBTYPE":"DATE"}}
        ne["start"] = t[0]
        ne["end"] = t[1]
        ne["tag"] = "DATE-TIME"
        ne["extent"] = raw_txt[t[0]:t[1]]
        spans.append(ne)
    return spans
    
    
    
def getBasicAnnotations(raw_txt):
    allAnnotations = []
    allAnnotations.extend(getGenderAnnotations(raw_txt))
    allAnnotations.extend(getSpans(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+',raw_txt,"EMAIL"))
    allAnnotations.extend(getTimeSpans(raw_txt))
    allAnnotations.extend(getDateSpans(raw_txt))
    
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
