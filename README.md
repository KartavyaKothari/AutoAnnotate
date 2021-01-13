# AutoAnnotate
Run the following command BEFORE annotating yourself or there can be duplicate annotations which could be problematic

`python3 autoannotate.py --input <Filename>`


## Extarct tags

Run following command on already annotated files to extract particular tag extents

`python3 extarct_spans.py --input <Filename> --tag <Tagname to extract>`

Example : `python3 extarct_spans.py --input file.jsonl --tag name`