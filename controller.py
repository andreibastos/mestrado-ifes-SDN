# -*- coding: utf-8 -*-
## Hub 
## Autor: Andrei Bastos
## Data: 21/07/2018
"""
    Esse programa é para demonstrar o funcionamento de um switch simples usando RYU. 
"""

from ryu.base import app_manager 
from ryu.controller.ofp_event import  EventOFPPacketIn, EventOFPSwitchFeatures
from ryu.controller.dpset import EventDP
from ryu.controller.handler import MAIN_DISPATCHER,set_ev_cls,CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.topology import event as evt
from ryu.lib.packet import packet, ethernet

import networkx as nx
import matplotlib.pyplot as plt

import pickle

# arquivo pickle
file_path_pickle = 'topo.pkl'
class Controller(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    mac_to_port = dict()

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)

        try:
            with open(file_path_pickle, 'rb') as f:
                self.graph = pickle.load(f)
            self.g = nx.Graph()
            self.g.add_nodes_from(self.graph['switches'])
            self.g.add_nodes_from(self.graph['hosts'])
            self.g.add_edges_from(self.graph['links'])
            
            nx.draw(self.g, with_labels=True, font_weight='bold')
            plt.show()
            self.logger.info("%s", self.g)
            
        except Exception as error:
            self.logger.error('%s', error)
            self.logger.info('você deve iniciar o controlador depois de iniciar o main.py, para gerar a topologia')

    
    ## eventos de conexões do switch
    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def _event_switch_enter_handler(self, event):
        dpid = event.dp.id
        self.mac_to_port.setdefault(dpid, dict())
        ports = event.ports # obtem as portas do switch

        if (event.enter): # verifica se o estado é conectado
            self.logger.info('\nswitch %s connected with %s ports', dpid, str(len(ports)-1)+" ports: " + ", ".join([p.name for p in ports]))
        else:
            self.mac_to_port[dpid].clear()
            self.logger.info('switch %s disconnected', dpid) # caso seja um evento de disconectado
            
    ## eventos de pacotes recebidos
    @set_ev_cls(EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, event):
        msg = event.msg # obtem a mensagem
        in_port = msg.match['in_port'] # verifica a porta de quem está enviando a mensagem
        datapath = msg.datapath # obtem informação do switch
        ofproto = datapath.ofproto # obtem o protocolo daquele switch
        ofproto_parser = datapath.ofproto_parser # obtem o parser
    
        dpid = datapath.id    
        pkt = packet.Packet(msg.data) # converte o dado da mensagem para um packet
        eth = pkt.get_protocols(ethernet.ethernet)[0] # obtem o os dados do protocolo ethernet
        src = eth.src # pega o mac de origem
        dst = eth.dst # pega o mas de destino

        self.mac_to_port.setdefault(dpid, dict())

        self.mac_to_port[dpid][src] = in_port # coloca no dicionário, a porta física de origem
        
        out_port = self.mac_to_port[dpid].get(dst) # verifica se existe a porta física do mac de destino

        if not out_port or dst is 'ff:ff:ff:ff:ff':
            out_port = ofproto.OFPP_FLOOD # a porta de saida será um FLOOD
        
        self.logger.info('switch %s: from in_port=%s:%s to out_port=%s:%s', dpid, in_port, src, out_port, dst) # exibe informações do switch e da porta
        
        actions = [ofproto_parser.OFPActionOutput(out_port)] # cria uma ação com porta de saida
        
        ## essa parte adiciona uma modificação na tabela de encaminhamento para evitar que pacotes vão até o controlador, reduz o tempo 
        if out_port != ofproto.OFPP_FLOOD: # se for uma porta conhecida,
            match = ofproto_parser.OFPMatch(in_port=in_port, eth_dst=dst) # cria a busca
            self.add_flow(datapath, 1, match, actions, msg.buffer_id)
        else:
            # para aquele pacote que acabou de chegar, encaminha ele para o destino correto (flood ou porta física)
            out = ofproto_parser.OFPPacketOut(
                datapath=datapath, # switch
                buffer_id=msg.buffer_id, # identificador do buffer 
                in_port=in_port, # porta de entrada (para não enviar para ela mesma)
                actions=actions) # ação de flood
            datapath.send_msg(out) # envia para o switch
    

    ## funcionalidade para evitar bugs do switch virtual, adicionando tabela de encaminhamento vazias
    @set_ev_cls(EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def _switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath,0,match, actions)
    
    # adicionado um fluxo em um switch
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    def install_path():
        pass

    def find_route(switch_in, switch_out, method):
        if method is'OSPF':
            pass
        elif method is 'ECMP':
                pass
        pass

    def get_route_ecmp(switch_in, switch_out, paths):
        if paths:
        # Escolha a função de hash que desejar, desde que gere um número inteiro.
            hash = generate_hash (switch_in, switch_out)
            choice = hash % len(paths)
            path = sorted(paths)[choice]
            return path
        else:
            return None
    