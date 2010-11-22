from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from twisted_smpp.client import *
from smpp.clickatell import *


class Options(usage.Options):
    optParameters = [
            ["host", "h", "localhost", "The url to connect to."],
            ["port", "p", 2775, "The port number to connect on."],
            ["system_id", "i", None, "The id/username."],
            ["password", "w", None, "The password."],
            ["system_type", "s", None, "Used to categorise/identify SMPP system."],
            ]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "smpp"
    description = "A SMPP ESME running as a Transceiver."
    options = Options

    def makeService(self, options):
        """
        Construct a TCPClient from a EsmeTransceiverFactory.
        """
        #print "host", options["host"]
        #print "port", options["port"]
        #print "system_id", options["system_id"]
        #print "password", options["password"]
        #print "system_type", options["system_type"]

        esmeTransFact = EsmeTransceiverFactory()
        esmeTransFact.loadDefaults(clickatell_defaults)
        esmeTransFact.loadDefaults({"host":options["host"], "port":int(options["port"])})
        if options["system_id"]:
            esmeTransFact.loadDefaults({"system_id":options["system_id"]})
        if options["password"]:
            esmeTransFact.loadDefaults({"password":options["password"]})
        if options["system_type"]:
            esmeTransFact.loadDefaults({"system_type":options["system_type"]})

        print 'Factory Defaults:', esmeTransFact.defaults, '\n'

        return internet.TCPClient(
                esmeTransFact.defaults['host'],
                esmeTransFact.defaults['port'],
                esmeTransFact)

serviceMaker = MyServiceMaker()

