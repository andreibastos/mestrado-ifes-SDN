#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse arquivo contém a geração da topologia generic
"""
from mininet.topo import Topo
from json import load

class GenericTopo(Topo):
    edges = []
    def __init__(self, filename):
        # Initialize topology
        Topo.__init__(self)

        with open(filename, 'r') as f:
            self.edges = load(f)
            print(self.edges)
        
        for edge in self.edges:
            switches = list()
            for node in edge:
                switch = 's%s'%(node+1)
                if not switch in self.switches():
                    self.addSwitch(switch)
                    host = self.addHost('h%s'%(node+1))
                    self.addLink(host, switch)
                switches.append(switch)
            self.addLink(switches[0], switches[1])

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'