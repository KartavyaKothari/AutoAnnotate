import json
import os
import re
import argparse

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Input file path")
    ap.add_argument("--new", required=True, help="Input file path")
    av = ap.parse_args()

    content = []

    with open(av.base, 'r') as f:
        content.extend(list(map(lambda x: x.lower(),f.read().split('\n'))))
    with open(av.new, 'r') as f:
        content.extend(list(map(lambda x: x.lower(),f.read().split('\n'))))

    name_list = sorted(list(set(content)),key=len,reverse=True)

    with open(av.base,'w') as f:
        outstr = []
        for word in name_list:
            if len(word)==0:
                continue
            outstr.append(word.strip())
        f.write('\n'.join(outstr))