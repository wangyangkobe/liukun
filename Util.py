#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import threading
import StringIO

class HandleUrl(object):
    baseUrl = r"http://weimonitor.sundding.cn/index.php?"
    def __init__(self, name):
        self.projectName = name
        self.thread = threading.Timer(1*60, self.heartbeat)
    
    def register(self):
        url = "{}module=register&p_name={}".format(self.baseUrl, self.projectName)
        response = urllib2.urlopen(url).read()
        try:
            res = json.loads(response)
            self.id = res['ID']
            self.p_name = res['P_NAME']
        except Exception, _e:
            self.id = ''
            self.p_name = ''    
        
    def heartbeat(self):
        url = "{}module=heartbeat&ID={}".format(self.baseUrl, self.id)
        response = urllib2.urlopen(url).read()
        print 'call heartbeat, res={}'.format(response)
        try:
            res = json.loads(response)
            if res['STATUS'] == "OK":
                pass
            else:
                pass
        except Exception, _e:
            pass

    def message(self, message):
        url = "{}module=message&ID={}&message={}".format(self.baseUrl, self.id, message)
        response = urllib2.urlopen(url).read()
        return  response
    
    def clientinfo(self):
        url = "{}module=clientinfo&ID={}".format(self.baseUrl, self.id)
        response = urllib2.urlopen(url).read()
        try:
            res = json.loads(response)
            self.ticket = res['TICKET']
            self.result = res['RESULT']
            self.expire = res['EXPIRE_SECONDS']
        except Exception, _e:
            self.ticket = ''
            self.result = ''
            self.expire = ''
            
    def startHeartBeat(self):
        self.thread.start()
    def stopHeadtBeat(self):
        self.thread.cancel()
    def getImage(self):
        url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}".format(self.ticket)
        buf= urllib2.urlopen(url).read()
        sbuf = StringIO.StringIO(buf)
        return sbuf
    
if __name__ == '__main__':
    handle = HandleUrl("snsmmsmsmsm")
    handle.register()
    print handle.id
    print handle.heartbeat()
    print handle.message("fuck")
    handle.clientinfo()
    print handle.result
    print handle.ticket
    handle.startHeartBeat()