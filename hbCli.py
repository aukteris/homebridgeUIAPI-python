import argparse
import json

from classes.cliExecutorRefactored import create_default_executor
thisExec = create_default_executor()

# parse command line arguments
clFile = "commands.json"
with open(clFile, "r") as f:
    commandList = json.loads(f.read())

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='action',title='actions')

subparserParser = {}

for i in commandList:
    subparserParser[i[0][0]] = subparsers.add_parser(*i[0], **i[1])
    for c in i[2]:
        subparserParser[i[0][0]].add_argument(*c[0],**c[1])

# process command line arguments
args = parser.parse_args()
thisExec.processArgs(args)