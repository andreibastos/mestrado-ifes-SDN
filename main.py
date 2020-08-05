#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse é o arquivo principal que dá inicio a todo processo
"""
import argparse

# importações do Ryu
from topologies.fattree import FatTreeTopo
from topologies.bcube import BCubeTopo
from topologies.generic import GenericTopo

# importações do mininet
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--topology", help="Topologia de emtrada, pode ser: fattree, bcube ou generic", choices=['fattree', 'bcube', 'generic'], default='fattree')
parser.add_argument("-k", "--ports", help="número de portas do switch", dest="k", type=int, default=4)
parser.add_argument("-f","--file", help="Arquivo de entrada quando topologia é generic")
parser.add_argument("-n", help="número de portas do switch", type=int, default=4)
args = parser.parse_args()
print(args)
k = args.k
n = args.n
if args.topology == 'fattree':    
    topo = FatTreeTopo(k=k)
if args.topology == 'bcube':
    topo = BCubeTopo(k, n)
if args.topology == 'generic':
    if not args.file:
        print('você deve informar o arquivo')
        exit(1)
    topo = GenericTopo(args.file)

net = Mininet(topo, controller=RemoteController)
net.start()
print "Dumping host connections"
dumpNodeConnections(net.hosts)
net.pingAll()
net.stop()

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'