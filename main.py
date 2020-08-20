#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse é o arquivo principal que dá inicio a todo processo
"""

# importações do python
import pickle
import argparse
import subprocess
import os


# importações do Ryu
from topologies.fattree import FatTreeTopo
from topologies.bcube import BCubeTopo
from topologies.generic import GenericTopo

# importações do mininet
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections

# processa os argumentos
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--topology", help="Topologia de emtrada, pode ser: fattree, bcube ou generic",
                    choices=['fattree', 'bcube', 'generic'], default='fattree')
parser.add_argument(
    "-k", "--ports", help="número de portas do switch", dest="k", type=int, default=4)
parser.add_argument(
    "-f", "--file", help="Arquivo de entrada quando topologia é generic")
parser.add_argument("-n", help="número de portas do switch",
                    type=int, default=4)
args = parser.parse_args()
print(args)
k = args.k
n = args.n

# arquivo pickle
file_path_pickle = 'topo.pkl'

# função principal


def main():
    # cria as topologias de acordo com os argumentos
    if args.topology == 'fattree':
        topo = FatTreeTopo(k=k)
    if args.topology == 'bcube':
        topo = BCubeTopo(k, n)
    if args.topology == 'generic':
        if not args.file:
            print('você deve informar o arquivo')
            exit(1)
        topo = GenericTopo(args.file)

    # atribuição de macs para os hosts
    count_host = 1
    for host in topo.nodes():
        if not topo.isSwitch(host):
            mac = str(hex(count_host).split('x')[-1]).upper()
            mac = "00:00:00:00:00:{}".format(
                mac if len(mac) > 1 else '0'+str(mac))
            ip = "10.0.0.{}".format(count_host)
            topo.setNodeInfo(host, {"ip": ip, "mac": mac})

        count_host += 1

    # # atribuição dos id dos switches
    switch_count = 1
    for switch in topo.switches():
        info = topo.nodeInfo(switch)
        info["dpid"] = hex(switch_count).split('x')[-1]
        topo.setNodeInfo(switch, info)
        switch_count += 1

    # guarda a topologia para que o controlador possa ler
    with open(file_path_pickle, 'wb') as f:
        graph = dict()
        graph['hosts'] = topo.hosts()
        graph['switches'] = topo.switches()
        graph['links'] = topo.links(sort=True)
        graph['ip_host'] = {topo
                            .nodeInfo(host)['ip']: host for host in topo.hosts()}
        graph['host_mac'] = {host: topo
                             .nodeInfo(host)['mac'] for host in topo.hosts()}
        pickle.dump(graph, f)

    # inicia o controlador
    process_controller = subprocess.Popen(
        'bash init_controller.sh'.split(), stdout=subprocess.PIPE)

    # limpa mininet anterior
    clean_mininet = subprocess.Popen('mn -c'.split())
    clean_mininet.wait()

    # iniciando mininet
    net = Mininet(topo, controller=RemoteController)

    net.start()

    s1 = net.switches[0]
    print s1.MAC()
    
    # net.pingPair()
    # net.pingPairFull()
    net.pingAll(timeout=1)
    # CLI(net)
    net.stop()

    # finaliza o controlador
    process_controller.kill()
    process_controller.wait()
    # apaga o arquivo da topologia
    if os.path.exists("topo.picle"):
        os.remove("topo.picle")


if __name__ == "__main__":
    main()

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'
