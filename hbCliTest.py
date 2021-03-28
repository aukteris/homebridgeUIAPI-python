import argparse
import json

clFile = "commandList.json"
with open(clFile, "r") as f:
    commandList = json.loads(f.read())

parser = argparse.ArgumentParser()

for i in commandList:
    parser.add_argument(*i[0],**i[1])

args = parser.parse_args()

print(args)