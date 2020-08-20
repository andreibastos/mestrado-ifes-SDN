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
        
        for edge in self.edges:
            switches = []
            for node in edge:
                id = node+1
                switch = 's%s'%(id)
                switches.append(switch)
                if not switch in self.switches():
                    self.addSwitch(switch)
                    host = self.addHost('h%s'%(id))
                    self.addLink(host, switch)
            self.addLink(switches[0],switches[1])

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'