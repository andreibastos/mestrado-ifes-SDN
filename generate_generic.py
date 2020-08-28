#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse programa gera topologias aleatórias
"""

from networkx import nx
import matplotlib.pyplot as plt
import argparse
from json import dump

# tratando argumentos
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--switches",
                    help="número de switches", dest="s", type=int, default=4)
parser.add_argument(
    "-l", "--links", help="número links na rede (default: dobro de switches)", dest="l", type=int)
parser.add_argument(
    "-o", "--output", help="Arquivo de saída", default='topo.txt')
parser.add_argument("-v", "--view", help="visualizar a rede",
                    dest="view", action="store_true", default=False)
args = parser.parse_args()  # realiza o parse

print ("### Gerando Topologia Genérica com %s switches e  %s links ###" %
       (args.s, args.l))
switches = args.s  # é a quantidade de switches
# é quantidade de enlaces ou o dobro de switches
links = args.l if args.l else 2*switches
output = args.output  # arquivo de saida
view = args.view  # indica se quer visualizar a rede

# manipulando o grafo
G = nx.gnm_random_graph(switches, links)  # grapho aleatório

edges = []  # lista de arestas

for line in nx.generate_adjlist(G):  # para cada linha das adjascentes
    nodes = line.split()  # quebra por espaços
    first = int(nodes[0])  # pega o primeiro
    for node in nodes[1:]:  # para cada node restante
        edges.append([first, int(node)])  # adiciona na lista o parte de node

# manipulando arquivo
with open(output, "w") as f:  # abre o arquivo para escrita
    dump(edges, f)  # escreve o arquivo

if view:
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'
