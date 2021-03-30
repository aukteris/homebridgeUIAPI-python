import argparse
import json

"""
parser = argparse.ArgumentParser(prog='PROG')
subparsers = parser.add_subparsers(help='sub-command help',dest='action')

parser_a = subparsers.add_parser('a', help='a help')
parser_a.add_argument('bar', type=int, help='bar help')

subparsers.add_parser('b', help='b help').add_argument('--baz', choices='XYZ', help='baz help')

args = parser.parse_args()
print(args)
"""

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

args = parser.parse_args()
print(json.dumps({"test":True}))