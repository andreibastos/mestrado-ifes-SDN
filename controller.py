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
from ryu.lib.packet import packet, ethernet

class Switch(app_manager.RyuApp):
    # OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    mac_to_port = dict()
    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)
    
    ## eventos de conexões do switch
    @set_ev_cls(EventDP, CONFIG_DISPATCHER)
    def switch_connection(self, event):
        id_switch = event.dp.id
        self.mac_to_port[id_switch] = dict()
        ports = event.ports # obtem as portas do switch
        if (event.enter): # verifica se o estado é conectado
            self.logger.info('\nswitch %s connected with %s ports', event.dp.id, str(len(ports))+" ports: " + ", ".join([p.name for p in ports]))
            print(self.mac_to_port)
                # print("\t{} com mac: {}".format(port.name, port.hw_addr)) # exibe uma informação
        else:
            self.mac_to_port[id_switch].clear()
            self.logger.info('switch %s disconnected', event.dp.id) # caso seja um evento de disconectado
    
    ## eventos de pacotes recebidos
    @set_ev_cls(EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        msg = event.msg # obtem a mensagem
        in_port = msg.match['in_port'] # verifica a porta de quem está enviando a mensagem
        dp = msg.datapath # obtem informação do switch
        ofp = dp.ofproto # obtem o protocolo daquele switch
        ofp_parser = dp.ofproto_parser # obtem o parser

        sid = dp.id    
        pkt = packet.Packet(msg.data) # converte o dado da mensagem para um packet
        eth = pkt.get_protocols(ethernet.ethernet)[0] # obtem o os dados do protocolo ethernet
        src = eth.src # pega o mac de origem
        dst = eth.dst # pega o mas de destino

        if not self.mac_to_port.has_key(sid):
            self.mac_to_port[sid] = dict()
            print(self.mac_to_port)
        
        self.mac_to_port[sid][src] = in_port # coloca no dicionário, a porta física de origem
        
        if dst is 'ff:ff:ff:ff:ff':
            out_port = ofp.OFPP_FLOOD # a porta de saida será um FLOOD
        else:
            out_port = self.mac_to_port[sid].get(dst) # verifica se existe a porta física do mac de destino
        
        self.logger.info('switch %s: from in_port=%s to out_port=%s', sid, in_port, 'FLOOD' if not out_port else out_port) # exibe informações do switch e da porta
        

        if not out_port: # caso não tenha,
            out_port = ofp.OFPP_FLOOD # a porta de saida será um FLOOD

        actions = [ofp_parser.OFPActionOutput(out_port)] # cria uma ação com portA de saida
        
        ## essa parte adiciona uma modificação na tabela de encaminhamento para evitar que pacotes vão até o controlador, reduz o tempo 
        if out_port != ofp.OFPP_FLOOD: # se for uma porta conhecida, 
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst) # cria a busca
            inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)] # adiciona uma instrução de aplicar ação, que noaso será a saida para aquela porta fisica
            mod = ofp_parser.OFPFlowMod(datapath=dp, buffer_id=msg.buffer_id, priority=1, match=match, instructions=inst) # cria uma modificação na tabela de encaminhamento
            dp.send_msg(mod) # envia ao swich
        
        # para aquele pacote que acabou de chegar, encaminha ele para o destino correto (flood ou porta física)
        out = ofp_parser.OFPPacketOut(
            datapath=dp, # switch
            buffer_id=msg.buffer_id, # identificador do buffer 
            in_port=in_port, # porta de entrada (para não enviar para ela mesma)
            actions=actions) # ação de flood
        dp.send_msg(out) # envia para o switch
    

    ## funcionalidade para evitar bugs do switch virtual, adicionando tabela de encaminhamento vazias
    @set_ev_cls(EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)