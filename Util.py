#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import threading
import StringIO
import urllib
from _winreg import QueryValue, OpenKey, HKEY_CURRENT_USER, SetValue, REG_SZ

class HandleUrl(object):
    baseUrl = r"http://weimonitor.sundding.cn/index.php?"
    def __init__(self, name):
        self.projectName = name
        self.thread = threading.Timer(1*60, self.heartbeat)
    
    def register(self):
        key = OpenKey(HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")       
        url = "{}module=register&p_name={}".format(self.baseUrl, self.projectName)
        response = urllib2.urlopen(url).read()
        try:
            res = json.loads(response)
            try:
                print "QueryValue: %s" % QueryValue(key, "ID")
                self.id = QueryValue(key, "ID")
                self.p_name = QueryValue(key, "P_NAME")
            except Exception, _e:
                self.id = res['ID']
                self.p_name = res['P_NAME']
                SetValue(key, "ID", REG_SZ, self.id)                   
                SetValue(key, "P_NAME", REG_SZ, self.p_name)
        except Exception, _e:
            self.id = ''
            self.p_name = ''    
        
    def heartbeat(self):
        url = "{}module=heartbeat&ID={}".format(self.baseUrl, self.id)
        response = urllib2.urlopen(url).read()
        print 'call heartbeat, res={}'.format(response)
        #try:
        #    res = json.loads(response)
        #    if res['STATUS'] == "OK":
        #        pass
        #    else:
        #        pass
        #except Exception, _e:
        #    pass

    def message(self, message, description):
        param = {'module':'message', 'ID': self.id, 'message': message, 'description': description}
        print self.baseUrl + urllib.urlencode(param)
        response = urllib2.urlopen(self.baseUrl + urllib.urlencode(param)).read()
        res = dict(json.loads(response))
        return res['MESSAGE'] + ", " +  res['STATUS'] + ', ' +  res.get('REASON', '')
    
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
    def setpname(self, pname):
        url = "{}module=setpname&ID={}&p_name={}".format(self.baseUrl, self.id, pname)
        response = urllib2.urlopen(url).read()
        res = json.loads(response)
        if res['Result'] == 'OK':
            key = OpenKey(HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
            self.p_name = pname
            SetValue(key, "P_NAME", REG_SZ, self.p_name)
        print "setpname result: %s" % response
               
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
    print handle.message("fuck", 'b')
    handle.clientinfo()
    print handle.result
    print handle.ticket
    handle.startHeartBeat()
    alarmStr = '发送报警信息: 高高:{} 当前值:{} {}成功'.format(20, 20, 20)
    print handle.message(alarmStr, 'a')