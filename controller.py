# -*- coding: utf-8 -*-
# Hub
# Autor: Andrei Bastos
# Data: 21/07/2018
"""
    Esse programa é para demonstrar o funcionamento de um switch simples usando RYU.
"""

from ryu.base import app_manager
from ryu.controller.ofp_event import EventOFPPacketIn, EventOFPSwitchFeatures
from ryu.controller.dpset import EventDP
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event as evt
from ryu.lib.packet import packet, ethernet, arp

import networkx as nx
import matplotlib.pyplot as plt

import pickle
import re
import os

# arquivo pickle
file_path_pickle = 'topo.pkl'


class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    switches_datapath = dict()

    # construtor
    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        # obtém o método via variavel de ambiente ou 'OSPF' por padrão
        self.method = os.environ.get('METHOD', 'OSPF')
        self.logger.info(
            'Iniciando controlador.. usando método %s', self.method)

        try:
            # leitura da topologia a partir do arquivo gerado pelo programa principal
            with open(file_path_pickle, 'rb') as f:
                self.topology = pickle.load(f)  # obtém dados da topologia

            self.g = nx.Graph()  # cria o gráfo
            # adiciona os switches
            self.g.add_nodes_from(self.topology['switches'])
            self.g.add_nodes_from(self.topology['hosts'])  # adiciona os hosts
            self.g.add_edges_from(self.topology['links'])  # adiciona os links

            # salva a topologia em topo.png
            colors = []  # cores dos hosts
            for node in self.g:  # para cada nó do gráfo
                if node in self.topology['hosts']:  # se o nó é o um host
                    colors.append('blue')  # adiciona a cor azul
                else:  # se for um switch
                    colors.append('red')  # adiciona cor vermelha
            nx.draw(self.g, node_color=colors,
                    with_labels=True, font_weight='bold')  # desenha o grafo
            plt.savefig("topo.png")  # salva a figura
            self.logger.info('imagem da topologia salva em topo.png')

        except Exception as error:
            # caso dê algum erro na leitura da topologia
            self.logger.error('%s', error)
            self.logger.info(
                'você deve gerar a topologia antes de executar o controlador')

    # eventos de conexões do switch
    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def _event_switch_enter_handler(self, event):
        ports = event.ports  # obtem as portas do switch
        switch_name = ports[-1].name.split('-eth')[0]  # nome do switch

        # adiciona na dicionário de switch_name e datapah
        self.switches_datapath.setdefault(switch_name, event.dp)

        if event.enter:  # verifica se é uma nova conexão de switch
            self.logger.info('switch %s connected', switch_name)
        else:  # se o switch desconectar
            del self.switches_datapath[switch_name]  # remove do dict
            self.logger.info('switch %s disconnected', switch_name)

    # eventos de pacotes recebidos
    @set_ev_cls(EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, event):
        msg = event.msg  # obtem a mensagem
        datapath = msg.datapath  # obtem informação do switch

        # caso não tenha adicionado na lista, (evita condições de corrida)
        # obtem o nome do switch
        switch_name = datapath._ports.values()[0].name.split('-eth')[0]
        # adiciona no dict
        self.switches_datapath.setdefault(switch_name, datapath)

        pkt = packet.Packet(msg.data)  # obtém o pacote da mensagem recebida
        eth_protocol = pkt.get_protocols(ethernet.ethernet)[
            0]  # protoloco ethernet

        # mac de origem e destino
        dst = eth_protocol.dst
        src = eth_protocol.src

        # protoloco arp
        arp_protocol = pkt.get_protocols(arp.arp)
        if len(arp_protocol) > 0:
            dst_ip = arp_protocol[0].dst_ip  # pega o ip destino
            src_ip = arp_protocol[0].src_ip  # pega o ip origem

            # obtem o nome do host de origem, exemplo: h1
            src_host = self.topology['ip_host'][src_ip]
            switch_in = list(self.g.adj[src_host])[0]

            # obtem o nome do host de destino, exemplo: h2
            dst_host = self.topology['ip_host'][dst_ip]
            switch_out = list(self.g.adj[dst_host])[0]

            # procura a rota de acordo com o método de roteamento
            path = self.find_route(switch_in, switch_out, self.method)

            # instala as regras em cada switch da rota encontrado
            self.install_path(path, msg, src_host, dst_host)

    # funcionalidade para evitar bugs do switch virtual, adicionando tabela de encaminhamento vazias
    @set_ev_cls(EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        datapath = ev.msg.datapath  # switch
        ofproto = datapath.ofproto  # protocolo openflow
        parser = datapath.ofproto_parser  # parser do protocolo daquele switch
        match = parser.OFPMatch()  # filtro vazio
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]  # ações
        self.add_flow(datapath, 0, match, actions)  # adiciona no switch

    # adicionado um fluxo em um switch
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto  # protocolo openflow
        parser = datapath.ofproto_parser  # parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]  # ações
        if buffer_id:  # se tiver buffer_id
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match, instructions=inst)
        else:  # se não tiver buffer_id
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)  # envia

    # função que instala a regra em cada switch da rota

    def install_path(self, path, msg, src_host, dst_host):
        size_path = len(path)  # número de switches do caminho

        # macs de origem e destino
        src_mac = self.topology['host_mac'][src_host]
        dst_mac = self.topology['host_mac'][dst_host]

        # para cada switch do caminho
        for index, switch in enumerate(path):
            # obtem o datapah de acordo com o nome do switch
            datapath = self.switches_datapath[switch]

            if size_path == 1:  # caso só tenha uma switch, o host está conectado no mesmo switch
                # porta de entrada é da propria mensagem
                in_port = msg.match['in_port']
                # procura a porta de saida entre switch e o host
                out_port = self.get_port_between_nodes(switch, dst_host)
            elif index == 0:  # caso seja 2 switches ou mais, se for primeiro deles:
                # porta de entrada é da propria mensagem
                in_port = msg.match['in_port']
                # verifica quem é o switch da frente
                next_switch = path[index+1]
                # procura a porta de saida entre o switch atual e o proximo switch
                out_port = self.get_port_between_nodes(switch, next_switch)
            elif index < size_path - 1:  # caso não seja o primeiro e não é o último do caminho
                previous_switch = path[index-1]  # pega o switch anterior
                next_switch = path[index+1]  # switch da frente
                in_port = self.get_port_between_nodes(switch, previous_switch)
                out_port = self.get_port_between_nodes(switch, next_switch)
            else:  # caso seja o ultimo
                previous_switch = path[index-1]  # pega o switch anterior
                in_port = self.get_port_between_nodes(switch, previous_switch)
                out_port = self.get_port_between_nodes(switch, dst_host)

            # depois de saber qual porta de entrada e de saida de cada switch
            ofproto = datapath.ofproto  # obtem o protocolo daquele switch
            parser = datapath.ofproto_parser  # obtem o parser
            # ação na porta de saída
            actions = [parser.OFPActionOutput(out_port)]
            # filtro porta de entrada e destino final
            match = parser.OFPMatch(in_port=in_port,  eth_dst=dst_mac)

            # adiciona o fluxo de acordo se tem buffer na mensagem
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
            else:
                self.add_flow(datapath, 1, match, actions)

            # responde o pacote atual
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
            # monta o pacote
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)  # envia

    # busca a melhora rota de acordo com o método de roteamento
    def find_route(self, switch_in, switch_out, method):
        path = []  # path vazio
        if method == 'OSPF':
            path = nx.shortest_path(
                self.g, switch_in, switch_out)  # caminho mais curto
        elif method == 'ECMP':
            # melhores caminhos
            paths = [path
                     for path in nx.all_shortest_paths(self.g, switch_in, switch_out)]
            path = self.get_route_ecmp(switch_in, switch_out, paths)
        return path

    # caso tenha mais que uma rota
    def get_route_ecmp(self, switch_in, switch_out, paths):
        if paths:
            hash = generate_hash(switch_in, switch_out)
            choice = hash % len(paths)
            path = sorted(paths)[choice]
            return path
        else:
            return []

    # verifica qual porta de conexão entre dois nodes
    def get_port_between_nodes(self, switch_1, switch_2):
        return self.topology['node_ports'][switch_1][switch_2]


def generate_hash(switch_in, switch_out):
    # função hash para obter um caminho
    return int(re.findall(
        r'\d+', switch_in)[0] + re.findall(r'\d+', switch_out)[0])
