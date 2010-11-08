
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory

from smpp.pdu_builder import *


class EsmeTransceiver(Protocol):

    def __init__(self):
        self.defaults = {}
        self.state = 'CLOSED'
        print 'STATE :', self.state
        self.sequence_number = 1
        self.datastream = ''


    def popData(self):
        data = None
        if(len(self.datastream) >= 16):
            command_length = int(binascii.b2a_hex(self.datastream[0:4]), 16)
            if(len(self.datastream) >= command_length):
                data = self.datastream[0:command_length]
                self.datastream = self.datastream[command_length:]
        return data


    def handleData(self, data):
            pdu = unpack_pdu(data)
            print pdu
            if pdu['header']['command_id'] == 'bind_transceiver_resp':
                self.handle_bind_transceiver_resp(pdu)
            if pdu['header']['command_id'] == 'submit_sm_resp':
                self.handle_submit_sm_resp(pdu)
            if pdu['header']['command_id'] == 'submit_multi_resp':
                self.handle_submit_multi_resp(pdu)
            print 'STATE :', self.state


    def loadDefaults(self, defaults):
        self.defaults = dict(self.defaults, **defaults)


    def connectionMade(self):
        self.state = 'OPEN'
        print 'STATE :', self.state
        pdu = BindTransceiver(self.sequence_number, **self.defaults)
        self.sequence_number +=1
        self.transport.write(pdu.get_bin())


    def dataReceived(self, data):
        self.datastream += data
        #self.datastream += binascii.a2b_hex('00000010000000000000000000000000')
        data = self.popData()
        while data != None:
            self.handleData(data)
            data = self.popData()


    def handle_bind_transceiver_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            self.state = 'BOUND_TRX'
            self.submit_sm(
                    short_message = 'gobbledygook',
                    destination_addr = '555',
                    )
            self.submit_multi(
                    short_message = 'gobbledygook',
                    dest_address = ['444','333'],
                    )
            self.submit_multi(
                    short_message = 'gobbledygook',
                    dest_address = [
                        {'dest_flag':1, 'destination_addr':'111'},
                        {'dest_flag':2, 'dl_name':'list22222'},
                        ],
                    )


    def handle_submit_sm_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            pass


    def handle_submit_multi_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            pass


    def submit_sm(self, **kwargs):
        if self.state in ['BOUND_TX', 'BOUND_TRX']:
            print dict(self.defaults, **kwargs)
            pdu = SubmitSM(self.sequence_number, **dict(self.defaults, **kwargs))
            self.sequence_number +=1
            self.transport.write(pdu.get_bin())


    def submit_multi(self, dest_address=[], **kwargs):
        if self.state in ['BOUND_TX', 'BOUND_TRX']:
            pdu = SubmitMulti(self.sequence_number, **dict(self.defaults, **kwargs))
            for item in dest_address:
                if isinstance(item, str): # assume strings are addresses not lists
                    pdu.addDestinationAddress(
                            item,
                            dest_addr_ton = self.defaults['dest_addr_ton'],
                            dest_addr_npi = self.defaults['dest_addr_npi'],
                            )
                elif isinstance(item, dict):
                    if item.get('dest_flag') == 1:
                        pdu.addDestinationAddress(
                                item.get('destination_addr', ''),
                                dest_addr_ton = item.get('dest_addr_ton',
                                    self.defaults['dest_addr_ton']),
                                dest_addr_npi = item.get('dest_addr_npi',
                                    self.defaults['dest_addr_npi']),
                                )
                    elif item.get('dest_flag') == 2:
                        pdu.addDistributionList(item.get('dl_name'))
            self.sequence_number +=1
            self.transport.write(pdu.get_bin())



class EsmeTransceiverFactory(ClientFactory):

    def __init__(self):
        self.defaults = {
                'host':'127.0.0.1',
                'port':2775,
                'dest_addr_ton':0,
                'dest_addr_npi':0,
                }

    def loadDefaults(self, defaults):
        self.defaults = dict(self.defaults, **defaults)

    def startedConnecting(self, connector):
        print 'Started to connect.'


    def buildProtocol(self, addr):
        print 'Connected'
        esme = EsmeTransceiver()
        esme.loadDefaults(self.defaults)
        return esme



