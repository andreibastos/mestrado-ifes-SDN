#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse é o que gera topologias aleatórias
"""

from networkx import nx
import argparse
from json import dump

## tratando argumentos 
parser = argparse.ArgumentParser()
parser.add_argument("-o","--output", help="Arquivo de saída quando topologia é generic", default='topo.txt')
parser.add_argument("-k", "--ports", help="número de portas do switch", dest="k", type=int, default=4)
parser.add_argument("-s", "--switches", help="número de portas do switch", dest="s", type=int)
parser.add_argument("-l", "--links", help="número de portas do switch", dest="l", type=int)
args = parser.parse_args() # realiza o parse
print args
output = args.output # arquivo de saida 
k = args.k # numero de portas dos switches
switches = args.s if args.s else k*k  # é a quantidade de switches ou o quadrado de portas
links = args.l if args.l else 2*switches  # é quantidade de enlaces ou o dobro de switches

## manipulando o grafo
G = nx.gnm_random_graph(switches, links) # grapho aleatório

edges = [] # lista de arestas

for line in nx.generate_adjlist(G): # para cada linha das adjascentes
    nodes = line.split()  # quebra por espaços
    first = int(nodes[0]) # pega o primeiro
    for node in nodes[1:]: # para cada node restante
        edges.append([first, int(node)]) # adiciona na lista o parte de node

## manipulando arquivo
with open(output, "w") as f: # abre o arquivo para escrita
    dump(edges, f) # escreve o arquivo

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'