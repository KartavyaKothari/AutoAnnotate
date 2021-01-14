import json
import os
import re
import argparse


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input file path")
    av = ap.parse_args()

    with open(av.input, 'r') as f:
        content = f.read()

    name_list = sorted(list(set(list(map(lambda x: x.lower(),content.split('\n'))))),key=len,reverse=True)

    with open('outregex','w') as f:
        outstr = []
        for word in name_list:
            if len(word)==0:
                continue
            re.sub('.','\.',word)
            re.sub(' ','\s',word)
            outstr.append('\\b'+word.strip()+'\\b')
        f.write('|'.join(outstr))