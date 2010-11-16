
from twisted.python import log
#log.startLogging(open('tests.log', 'w'))

from twisted_smpp.client import *
from smpp.clickatell import *

import credentials_test
try:import credentials_priv
except:pass



esmeTransFact = EsmeTransceiverFactory()
esmeTransFact.loadDefaults(clickatell_defaults)
esmeTransFact.loadDefaults(credentials_test.logica)

print 'Factory Defaults:', esmeTransFact.defaults, '\n'

reactor.connectTCP(
        esmeTransFact.defaults['host'],
        esmeTransFact.defaults['port'],
        esmeTransFact)
reactor.run()
