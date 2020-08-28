#!./venv/bin python
# -*- coding: utf-8 -*-
# Andrei Bastos
# Mestrado IFES 2020 - Computação Aplicada - Redes de Computadores - SDN

"""
Esse arquivo contém as definiçoes das topologia bcube, fattree e genérica,
"""
from mininet.topo import Topo
from json import load

###################################
############## BCUBE ##############
###################################
class BCubeTopo(Topo):
    def __init__(self, k=1, n=4):
        Topo.__init__(self)

        # level 1
        switches_level_1 = []
        for i in range(n):
            switch = self.addSwitch('s_1_%s' % (i+1))
            switches_level_1.append(switch)

        # level 0
        switches_level_0 = []
        for i in range(n):
            switch = self.addSwitch('s_0_%s' % (i+1))
            switches_level_0.append(switch)

        # hosts
        for i in range(n**2):
            switch_host = self.addSwitch('s%s' % (i+1))
            host = self.addHost('h%s' % (i+1))
            self.addLink(switch_host, host)
            for switch in switches_level_0:
                self.addLink(switch, switch_host)
            self.addLink(switch_host, switches_level_1[((i) % n)])


###################################
############# FATTREE #############
###################################
class FatTreeTopo(Topo):
    """
    Parameters
    ----------
    k : int
        Ports per switch
    """

    def __init__(self, k=4):
        Topo.__init__(self)

        self.k = k

        # cria os switchtes core
        core = self.create_core()

        # cria os pods
        for n in range(k):
            # cria um pode
            pod = self.create_pod(n+1)
            # cria um link entre um pode e o core
            self.link_pod_core(pod, core)

    # cria link entre os switchs do pod e os switches core
    def link_pod_core(self, pod, core):
        aggregations = pod['aggregations']  # obtém os switches de aggregation
        size = len(aggregations)  # verifica quantos exitem
        # para cada switch
        for index, switch_aggregation in enumerate(aggregations):
            # separa em metade da lista
            if index < size / 2:
                core_half = core[0:len(core)/2]
            else:
                core_half = core[len(core)/2:]
            # para cada switch core
            for switch_core in core_half:
                self.addLink(switch_aggregation, switch_core)

    # cria um pod, com algum id (pod_n)
    def create_pod(self, pod_n):
        aggregations = self.create_aggregation(pod_n)
        edges = self.create_edge(pod_n)
        pod = {'aggregations': aggregations, 'edges': edges}

        # conecta o switches de aggregation e egde
        for switch in aggregations:
            for edge in edges:
                self.addLink(switch, edge)

        # cria os hosts e adiciona nos switches de edge
        for index, switch in enumerate(edges):
            # nome do host id que varia de 0 a k²
            hosts = ['h%s' %
                     ((pod_n-1)*self.k + index*2+h+1) for h in range(2)]

            # para cada host, conecta no switch de edge
            for host in hosts:
                self.addHost(host)
                self.addLink(switch, host)
        return pod

    # cria os switch core
    def create_core(self):
        return self.create_switches(self.k, 's_c_')

    # cria os switch aggregation
    def create_aggregation(self, pod):
        return self.create_switches(self.k/2, 's_%s_a_' % pod)

    # cria os switch edge
    def create_edge(self, pod):
        return self.create_switches(self.k/2, 's_%s_e_' % pod)

    # cria os switches
    def create_switches(self, n, prefix):
        switches = []
        for s in range(n):
            switch = '%s%s' % (prefix, s+1)
            self.addSwitch(switch)
            switches.append(switch)
        return switches


###################################
############# GENÉRICA#############
###################################
class GenericTopo(Topo):
    def __init__(self, filename):
        Topo.__init__(self)

        # ler o arquivo de lista de pares de arestas
        with open(filename, 'r') as f:
            self.edges = load(f)

        # para cada aresta
        for edge in self.edges:
            switches = [] # zera os switches
            for node in edge: # para cada nó no par de arestas
                id = node+1 # identificação do nó
                switch = 's%s' % (id) # cria o switch com aquele nome 
                switches.append(switch) # adiciona na lista 
                if not switch in self.switches(): # se o switch não tiver adicionado,
                    self.addSwitch(switch) # adiciona na topologia
                    host = self.addHost('h%s' % (id)) # adiciona um host com o mesmo id
                    self.addLink(host, switch) # linka os dois
            self.addLink(switches[0], switches[1]) # adiciona o linke entre os dois pares


__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'
