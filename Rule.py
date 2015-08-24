
class Rule(object):
    def __init__(self, Id, key, validated=None, lower=None, low=None, high=None, higher=None, dang=None, interal=5):
        self.Id = Id
        self.key = key
        self.validated = validated
        self.strKey = '.'.join(self.key)
        self.lower = lower
        self.low = low
        self.high = high
        self.higher = higher
        self.dang = dang
        self.interal = interal
    def __str__(self):
        print "key: {}, validate: {}, strKey: {}, lower: {}, low: {}, high: {}, higher: {}, dang: {}, interal: {}".format(self.key,
                                                                                                                          self.validated,
                                                                                                                          self.strKey,
                                                                                                                          self.lower,
                                                                                                                          self.low,
                                                                                                                          self.high,
                                                                                                                          self.higher,
                                                                                                                          self.dang,
                                                                                                                          self.interal
                                                                                                                          )