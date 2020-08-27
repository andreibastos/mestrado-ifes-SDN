#!./venv/bin python
# -*- coding: utf-8 -*-

"""
Esse é o arquivo principal que dá inicio a todo processo
"""

# importações do python
import pickle
import argparse
import subprocess
from multiprocessing import Process
import os
from time import sleep


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
parser.add_argument("-m", "--method", help="método de roteamento",
                    dest="method", type=str, choices=['ECMP', 'OSPF'], default='ECMP')

args = parser.parse_args()
k = args.k
n = args.n
method = args.method

# arquivo pickle
file_path_pickle = 'topo.pkl'


def main():
    # função principal
    print ("\n### INICIANDO NOVO TESTE com Topologia: %s e Método: %s ###" %
           (args.topology, method))

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

    # atribuição dos id dos switches
    switch_count = 1
    for switch in topo.switches():
        info = topo.nodeInfo(switch)
        info["dpid"] = hex(switch_count).split('x')[-1]
        topo.setNodeInfo(switch, info)
        switch_count += 1

    # limpa mininet anterior
    print('\nlimpando a mininet anterior...')
    clean_mininet = subprocess.Popen('mn -c -v error'.split())
    clean_mininet.wait()

    # iniciando mininet
    print('\niniciando mininet atual...')
    net = Mininet(topo, controller=RemoteController, autoSetMacs=True)

    # mapeamento de nodes e portas
    print('\nmapeamento de portas dos nodes...')
    node_ports = dict()
    for link in net.links:  # para cada link
        # obtem o nós conectados e a porta
        node_1, port_1 = link.intf1.name.split('-eth')
        node_2, port_2 = link.intf2.name.split('-eth')

        # adiciona o node e a porta
        node_ports.setdefault(node_1, dict())
        node_ports[node_1][node_2] = int(port_1)
        node_ports.setdefault(node_2, dict())
        node_ports[node_2][node_1] = int(port_2)

    # salva a topologia para que o controlador possa ler
    print('\nsalvando topologia em arquivo...')
    with open(file_path_pickle, 'wb') as f:
        graph = dict()
        graph['hosts'] = [h.name for h in net.hosts]
        graph['switches'] = [s.name for s in net.switches]
        graph['node_ports'] = node_ports
        graph['links'] = topo.links(sort=True)
        graph['ip_host'] = {host.IP(): host.name for host in net.hosts}
        graph['host_mac'] = {host.name: host.MAC() for host in net.hosts}
        pickle.dump(graph, f)

    # inicia o controlador
    process_controller = subprocess.Popen(
        ('bash init_controller.sh method %s' % method).split(), stdout=subprocess.PIPE)

    # inicia o minenet
    print('\ninicio do mininet...')
    net.start()

    # aguarda 800 ms para cada switch conectar no controlador, evita condição de corrida
    wait_time = 0.8*len(topo.switches())
    print('\naguardando %s segundos para que todos os switches se conectem...' % wait_time)
    sleep(wait_time)

    # pinga toda rede
    print('\nping de todos os hosts...')
    net.pingAll(timeout=1)

    # Chamada da função de monitoramento de pacotes de rede
    print('\niniciando monitor de tráfego...')
    monitor_cpu = Process(target=monitor_bwm_ng, args=('dados.bwm', 1))
    monitor_cpu.start()
    monitor_cpu.join()

    # Inicia o teste de comunicação de todos para todos
    port = 5001
    MB = 8*(1 << 20)
    data_size = 10 * MB
    print('\nteste de comunicação todos para todos com %s MBytes' % (data_size/MB))
    for h in net.hosts:
        # inicia o serviço de iperf em cada host
        h.cmd('iperf -s -p %s > /dev/null &' % port)
    for client in net.hosts:
        for server in net.hosts:
            if client != server:  # se n for de host para ele mesmo
                client.cmd('iperf -c %s -p %s -n %d -i 1 -yc > /dev/null &' %
                           (server.IP(), port, data_size))

    # 500 ms para cada node + 900 ms para cada MB
    wait_time = 0.5*len(topo.nodes()) + 0.9*data_size/(MB)
    print('\naguardando experimento por mais %s segundos' % wait_time)
    sleep(wait_time)

    print('\nfinalizando processo de monitor de tráfego...')
    os.system("killall -9 iperf")
    os.system("killall -9 bwm-ng")
    monitor_cpu.terminate()

    print('\nfinalizando mininet...')
    net.stop()

    # finaliza o controlador
    print('\nfinalizando controlador...')
    process_controller.kill()
    process_controller.wait()

    # apaga o arquivo da topologia
    print('\napagando dados da topologia...')
    if os.path.exists(file_path_pickle):
        os.remove(file_path_pickle)

# Definição da função de monitoramento de pacotes de rede


def monitor_bwm_ng(fname, interval_sec):
    cmd = ("sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' | grep total > %s" %
           (interval_sec * 1000, fname))
    subprocess.Popen(cmd, shell=True).wait()


if __name__ == "__main__":
    main()

__author__ = 'Andrei Bastos'
__email__ = 'andreibastos@outlook.com'
