
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.task import LoopingCall

from smpp.pdu_builder import *


class EsmeTransceiver(Protocol):

    def __init__(self, seq=[1]):
        self.name = 'EsmeTransciever' + str(seq)
        print '__init__', self.name
        self.defaults = {}
        self.state = 'CLOSED'
        print 'STATE :', self.name, ':', self.state
        self.seq = seq
        self.datastream = ''


    def getSeq(self):
        return self.seq[0]


    def incSeq(self):
        self.seq[0] +=1


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
        if pdu['header']['command_id'] == 'deliver_sm':
            self.handle_deliver_sm(pdu)
        if pdu['header']['command_id'] == 'enquire_link_resp':
            self.handle_enquire_link_resp(pdu)
        print 'STATE :', self.name, ':', self.state


    def loadDefaults(self, defaults):
        self.defaults = dict(self.defaults, **defaults)


    def connectionMade(self):
        self.state = 'OPEN'
        print 'STATE :', self.name, ':', self.state
        pdu = BindTransceiver(self.getSeq(), **self.defaults)
        self.incSeq()
        self.transport.write(pdu.get_bin())


    def connectionLost(self, *args, **kwargs):
        self.state = 'CLOSED'
        print 'STATE :', self.name, ':', self.state
        try:
            self.lc_enquire.stop()
            del self.lc_enquire
            print self.name, 'stop & del looping call'
        except:
            pass


    def dataReceived(self, data):
        self.datastream += data
        data = self.popData()
        while data != None:
            self.handleData(data)
            data = self.popData()


    def handle_bind_transceiver_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            self.state = 'BOUND_TRX'
            self.lc_enquire = LoopingCall(self.enquire_link)
            self.lc_enquire.start(55.0)
            #self.submit_sm(
                    #short_message = 'gobbledygook',
                    #destination_addr = '555',
                    #)
            #self.submit_multi(
                    #short_message = 'gobbledygook',
                    #dest_address = ['444','333'],
                    #)
            #self.submit_multi(
                    #short_message = 'gobbledygook',
                    #dest_address = [
                        #{'dest_flag':1, 'destination_addr':'111'},
                        #{'dest_flag':2, 'dl_name':'list22222'},
                        #],
                    #)
        print 'STATE :', self.name, ':', self.state


    def handle_submit_sm_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            pass


    def handle_submit_multi_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            pass


    def handle_deliver_sm(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            sequence_number = pdu['header']['sequence_number']
            pdu = DeliverSMResp(sequence_number, **self.defaults)
            print pdu.get_obj()
            self.transport.write(pdu.get_bin())


    def handle_enquire_link_resp(self, pdu):
        if pdu['header']['command_status'] == 'ESME_ROK':
            pass


    def submit_sm(self, **kwargs):
        if self.state in ['BOUND_TX', 'BOUND_TRX']:
            pdu = SubmitSM(self.getSeq(), **dict(self.defaults, **kwargs))
            self.incSeq()
            self.transport.write(pdu.get_bin())


    def submit_multi(self, dest_address=[], **kwargs):
        if self.state in ['BOUND_TX', 'BOUND_TRX']:
            pdu = SubmitMulti(self.getSeq(), **dict(self.defaults, **kwargs))
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
            self.incSeq()
            self.transport.write(pdu.get_bin())


    def enquire_link(self, **kwargs):
        print self.name, 'wants to Enquire Link.'
        if self.state in ['BOUND_TX', 'BOUND_TRX']:
            print self.name, 'enquiring about link.'
            pdu = EnquireLink(self.getSeq(), **dict(self.defaults, **kwargs))
            self.incSeq()
            self.transport.write(pdu.get_bin())


class EsmeTransceiverFactory(ReconnectingClientFactory):

    def __init__(self):
        self.seq = [1]
        self.initialDelay = 30.0
        self.maxDelay = 45
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
        esme = EsmeTransceiver(self.seq)
        esme.loadDefaults(self.defaults)
        self.resetDelay()
        return esme


    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


