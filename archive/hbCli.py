import argparse
import json

from classes import cliHelper

thisExec = cliHelper.cliExecutor()

# parse command line arguments
clFile = "commandList.json"
with open(clFile, "r") as f:
    commandList = json.loads(f.read())

parser = argparse.ArgumentParser()

for i in commandList:
    parser.add_argument(*i[0],**i[1])

# process command line arguments
args = parser.parse_args()
thisExec.processArgs(args)