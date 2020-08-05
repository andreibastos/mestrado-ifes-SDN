#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse arquivo contém a geração da topologia bcube,
código veio de https://github.com/kuailedubage/DataCenterTopo/blob/master/DCTopo.py
"""
from mininet.topo import Topo

class BCubeTopo(Topo):
    """
    This topology is defined as a recursive structure. A :math:`Bcube_0` is 
    composed of n hosts connected to an n-port switch. A :math:`Bcube_1` is 
    composed of n :math:`Bcube_0` connected to n n-port switches. A :math:`Bcube_k` is
    composed of n :math:`Bcube_{k-1}` connected to :math:`n^k` n-port switches.
    This topology comprises:
     * :math:`n^(k+1)` hosts, each of them connected to :math:`k+1` switches
     * :math:`n*(k+1)` switches, each of them having n ports
    Parameters
    ----------
    k : int
        The level of Bcube
    n : int
        The number of host per :math:`Bcube_0`
    """

    def __init__(self, k=1, n=4):
        "Create bcube topo."

        # Initialize topology
        Topo.__init__(self)

        # Validate input arguments
        if not isinstance(n, int) or not isinstance(k, int):
            raise TypeError('k and n arguments must be of int type')
        if n < 1:
            raise ValueError("Invalid n parameter. It should be >= 1")
        if k < 0:
            raise ValueError("Invalid k parameter. It should be >= 0")

        # add hosts
        n_hosts = n ** (k + 1)
        for i in xrange(n_hosts):
            self.addHost('h{}_{}'.format(i / n, i % n))

        # add switches according level and connect with hosts
        for level in xrange(k + 1):
            sid = 0
            arg1 = n ** level
            arg2 = n ** (level + 1)
            # i is the horizontal position of a switch a specific level
            for i in xrange(n ** k):
                # add switch at given level
                sw = self.addSwitch('s{}_{}'.format(level, sid))
                # add links between hosts and switch
                m = i % arg1 + i / arg1 * arg2
                hosts = xrange(m, m + arg2, arg1)
                nodeslist = self.nodes()
                sid = sid + 1
                for v in hosts:
                    self.addLink(sw, nodeslist[v])


__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'