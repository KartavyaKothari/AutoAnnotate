import argparse
import json
from os import listdir
from os.path import isfile, join


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input dir path")
    parser.add_argument("--tag", required=True, help="Tag to be extracted")
    args = parser.parse_args()

    documents = []
    for pth in filter(isfile,
                      map(lambda f: join(args.input, f), listdir(args.input))):

        with open(pth, "r") as json_file:
            documents.extend([json.loads(i) for i in list(json_file)])

    with open(args.tag + "s.new", "w") as json_file:
        for document in documents:
            if document is None:
                print("Error in")
                continue
            for entity in document["annotations"]["named_entity"]:
                if entity["tag"].lower() == args.tag.lower():
                    json_file.write(entity["extent"] + "\n")


if __name__ == "__main__":
    main()
