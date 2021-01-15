# AutoAnnotate
Run the following command BEFORE annotating yourself or there can be duplicate annotations which could be problematic

`python3 autoannotate.py --input <filename>`
OR
`python3 autoannotate.py -i <filename>`


## Extract tags

Run following command on already annotated files to extract particular tag extents

`python3 extract_spans.py -i <filename> --tag <tag-to-extract>`

Example : `python3 extract_spans.py -i file.jsonl --tag name`
