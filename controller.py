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

# arquivo pickle
file_path_pickle = 'topo.pkl'


class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    switches_datapath = dict()

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.logger.info('iniciando controlador..')

        try:
            with open(file_path_pickle, 'rb') as f:
                self.graph = pickle.load(f)
            self.g = nx.Graph()
            self.g.add_nodes_from(self.graph['switches'])
            self.g.add_nodes_from(self.graph['hosts'])
            self.g.add_edges_from(self.graph['links'])
            self.logger.info('%s', self.graph)

            colors = []
            for node in self.g:
                self
                if node.startswith('h'):
                    colors.append('blue')
                else:
                    colors.append('red')
            nx.draw(self.g, node_color=colors,
                    with_labels=True, font_weight='bold')
            plt.savefig("topo.png")
            # self.logger.info("%s", self.g.adj)

        except Exception as error:
            self.logger.error('%s', error)
            self.logger.info(
                'você deve iniciar o controlador depois de iniciar o main.py, para gerar a topologia')

    # eventos de conexões do switch
    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def _event_switch_enter_handler(self, event):
        ports = event.ports  # obtem as portas do switch
        switch_name = ports[-1].name.split('-eth')[0]

        self.switches_datapath.setdefault(switch_name, event.dp)

        if event.enter:  # verifica se o estado é conectado
            self.logger.info('switch %s connected', switch_name)
            # self.logger.info('switch %s connected with %s ports', switch_name, ports)
            pass
        else:
            del self.switches_datapath[switch_name]
            # caso seja um evento de disconectado
            self.logger.info('switch %s disconnected', switch_name)

    # eventos de pacotes recebidos
    @set_ev_cls(EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, event):
        msg = event.msg  # obtem a mensagem
        datapath = msg.datapath  # obtem informação do switch
        switch_name = datapath._ports.values()[0].name.split('-eth')[0]
        self.switches_datapath.setdefault(switch_name, datapath)

        # converte o dado da mensagem para um packet
        pkt = packet.Packet(msg.data)
        # obtem o os dados do protocolo ethernet
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        pkt_arp = pkt.get_protocols(arp.arp)

        if len(pkt_arp) > 0:
            dst_ip = pkt_arp[0].dst_ip  # pega o ip destino
            src_ip = pkt_arp[0].src_ip  # pega o ip origem

            src_host = self.graph['ip_host'][src_ip]
            switch_in = list(self.g.adj[src_host])[0]

            dst_host = self.graph['ip_host'][dst_ip]
            switch_out = list(self.g.adj[dst_host])[0]

            # self.logger.info('%s => %s', src_host, dst_host)

            path = self.find_route(switch_in, switch_out, 'ECMP')
            # self.logger.info('path=%s', path)

            self.install_path(path, msg, src_host, dst_host)
            # self.logger.info("instalou o path via arp")
        else:
            # self.logger.info(pkt)

            # self.logger.info("%s, %s", src, dst)
            pass

    # funcionalidade para evitar bugs do switch virtual, adicionando tabela de encaminhamento vazias

    @set_ev_cls(EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    # adicionado um fluxo em um switch
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    def install_path(self, path, msg, src_host, dst_host):
        size_path = len(path)  # número de switches do caminho
        # self.logger.info('instalando path %s',path)

        src_mac = self.graph['host_mac'][src_host]
        dst_mac = self.graph['host_mac'][dst_host]

        for index, switch in enumerate(path):
            datapath = self.switches_datapath[switch]

            if size_path == 1:
                in_port = msg.match['in_port']
                out_port = self.get_port_between_nodes(switch, dst_host)
                # self.logger.info('index: (%s), switch: %s:\t from: %s (in_port: %s) to: %s (out_port:%s)',
                #                  index, switch, switch, in_port, dst_host, out_port)
            elif index == 0:
                in_port = msg.match['in_port']
                next_switch = path[index+1]
                out_port = self.get_port_between_nodes(switch, next_switch)
                # self.logger.info('index: (%s), switch: %s:\t from: %s (in_port: %s) to: %s (out_port:%s)',
                #                  index, switch, src_host, in_port, next_switch, out_port)
            elif index < size_path - 1:
                previous_switch = path[index-1]
                next_switch = path[index+1]
                in_port = self.get_port_between_nodes(switch, previous_switch)
                out_port = self.get_port_between_nodes(switch, next_switch)
                # self.logger.info('index: (%s), switch: %s:\t from: %s (in_port: %s) to: %s (out_port:%s)',
                #                  index, switch, previous_switch, in_port, next_switch, out_port)

            else:
                previous_switch = path[index-1]
                in_port = self.get_port_between_nodes(switch, previous_switch)
                out_port = self.get_port_between_nodes(switch, dst_host)
                # self.logger.info('index: (%s), switch: %s:\t from: %s (in_port: %s) to: %s (out_port:%s)',
                #                  index, switch, previous_switch, in_port, dst_host, out_port)

            ofproto = datapath.ofproto  # obtem o protocolo daquele switch
            parser = datapath.ofproto_parser  # obtem o parser
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port,  eth_dst=dst_mac)

            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
            else:
                self.add_flow(datapath, 1, match, actions)

            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

    def find_route(self, switch_in, switch_out, method):
        path = []
        if method is 'OSPF':
            path = nx.shortest_path(self.g, switch_in, switch_out)
        elif method is 'ECMP':
            paths = [path
                     for path in nx.all_shortest_paths(self.g, switch_in, switch_out)]
            path = self.get_route_ecmp(switch_in, switch_out, paths)
        return path

    def get_route_ecmp(self, switch_in, switch_out, paths):
        if paths:
            # Escolha a função de hash que desejar, desde que gere um número inteiro.
            hash = generate_hash(switch_in, switch_out)
            choice = hash % len(paths)
            path = sorted(paths)[choice]
            return path
        else:
            return []

    def get_port_between_nodes(self, switch_1, switch_2):
        return self.graph['node_ports'][switch_1][switch_2]


def generate_hash(switch_in, switch_out):
    return int(re.findall(
        r'\d+', switch_in)[0]) + int(re.findall(r'\d+', switch_out)[0])
