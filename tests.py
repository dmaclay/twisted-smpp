
from twisted_smpp.client import *
from smpp.clickatell import *

import credentials_test
try:import credentials_priv
except:pass



esmeTransFact = EsmeTransmitterFactory()
esmeTransFact.loadDefaults(clickatell_defaults)
esmeTransFact.loadDefaults(credentials_test.logica)
print esmeTransFact.defaults
reactor.connectTCP(
        esmeTransFact.defaults['host'],
        esmeTransFact.defaults['port'],
        esmeTransFact)
reactor.run()
