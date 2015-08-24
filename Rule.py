#!/usr/bin/env python
# -*- coding: utf-8 -*-
class Rule(object):
    def __init__(self, Id=None, key=None, validated=True, lower=None, low=None, high=None, higher=None, dang=None, interal=5, isBool=False):
        self.Id = Id
        self.key = key
        self.validated = validated
        if key:
            self.strKey = '.'.join(self.key)
        self.lower = lower
        self.low = low
        self.high = high
        self.higher = higher
        self.dang = dang
        self.interal = interal
        self.isBool = isBool 
        
    def __str__(self):
        strFormater = r"key: {}, validated: {}, strKey: {}, lower: {}, low: {}, high: {}, higher: {}, dang: {}, interal: {}, isBool: {}"
        return strFormater.format(self.key,
                                  self.validated,
                                  self.strKey,
                                  self.lower,
                                  self.low,
                                  self.high,
                                  self.higher,
                                  self.dang,
                                  self.interal,
                                  self.isBool
                                  )
