# coding: utf-8+-
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--topology", help="Topologia de emtrada, pode ser: fattree, bcube ou generic", choices=['fattree', 'bcube', 'generic'], default='fattree')
parser.add_argument("-k", "--ports", help="número de portas do switch", type=int, default=4)
parser.add_argument("--file", help="Arquivo de entrada quando topologia é generic")
parser.add_argument("-n", help="número de portas do switch", type=int, default=4)
args = parser.parse_args()

if args.topology == 'fattree':
    pass
if args.topology == 'bcube':
    pass
if args.topology == 'generic':
    if not args.file:
        print('você deve informar o arquivo')
        exit(1)

