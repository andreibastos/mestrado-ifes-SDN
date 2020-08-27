#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse arquivo contém a geração da topologia bcube,
"""
from mininet.topo import Topo


class BCubeTopo(Topo):

    def __init__(self, k=1, n=4):

        # Initialize topology
        Topo.__init__(self)

        # level 1
        switches_level_1 = []
        for i in range(n):
            switch = self.addSwitch('s_1_%s' % (i+1))
            switches_level_1.append(switch)

        switches_level_0 = []
        for i in range(n):
            switch = self.addSwitch('s_0_%s' % (i+1))
            switches_level_0.append(switch)

        for i in range(n**2):
            switch_host = self.addSwitch('s%s' % (i+1))
            host = self.addHost('h%s' % (i+1))
            self.addLink(switch_host, host)
            for switch in switches_level_0:
                self.addLink(switch, switch_host)
            self.addLink(switch_host, switches_level_1[((i) % n)])


__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'
