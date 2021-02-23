##
import json
import os
import subprocess
from collections import defaultdict
from math import ceil
from sys import argv

import pandas as pd

##


DIRECTORY = argv[1] if 1 < len(argv) < 4 else "."
RATE = int(argv[2]) if len(argv) == 3 else 7

files = list(filter(lambda x: ".jsonl" in x, os.listdir(DIRECTORY)))

documents = defaultdict(list)
for file in files:
    with open(os.path.join(DIRECTORY, file)) as f:
        documents[file].extend(
            map(lambda x: x["raw_text"], [json.loads(i) for i in list(f)])
        )

doc_lens = defaultdict(list)
for file, doc_list in documents.items():
    filename = f"/tmp/raw_doc.tmp"
    for doc in doc_list:
        with open(filename, "w") as f:
            f.write(doc)
        doc_lens[file].append(
            int(subprocess.check_output(["wc", "-w", filename]).split()[0])
        )

del documents

count, total = 0, 0
print(f"doc lengths: {doc_lens}")
print(f"#files: {len(files)}")
with open("invoice.csv", "w") as f:
    for file, lens in doc_lens.items():
        f.writelines(file)
        num_docs, num_words, file_total = 0, 0, 0

        for doclen in lens:
            doc_price = RATE * ceil(doclen / 150)
            f.writelines(f"\n{doclen}, {doc_price}")
            count += 1
            total += doc_price
            num_docs += 1
            num_words = doclen
            file_total += doc_price
        f.writelines(f"\nDocuments: {num_docs}, Words: {num_words}, total: {file_total}\n\n")
    f.writelines(f"\nGrand Total, {total}")

    print("invoice.csv generated")
    print(f"#Documents: {count}")
    print(f"Total: {total}")
##
