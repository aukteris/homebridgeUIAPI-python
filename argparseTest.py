import argparse

parser = argparse.ArgumentParser(prog='PROG')
subparsers = parser.add_subparsers(help='sub-command help',dest='action',title="Actions")

parser_a = subparsers.add_parser('a', help='a help')
parser_a.add_argument('bar', type=int, help='bar help')

subparsers.add_parser('b', help='b help').add_argument('--baz', choices='XYZ', help='baz help')

args = parser.parse_args()
print(args)