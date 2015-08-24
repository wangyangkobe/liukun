#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2015��8��17��

@author: elqstux
'''
import wx
import wx.grid
from scrapy.item import Item
from Tix import Grid

class CreateRuleDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        self.rulePath = kw.pop('rulepath')
        self.itemValue = kw.pop('itemvalue')
        self.rules = kw.pop('rules')
        super(CreateRuleDialog, self).__init__(*args, **kw)      
        self.InitUI()
        self.SetSize((450, 270))
        self.SetTitle(u"规则配置")
    def InitUI(self): 
        vbox = wx.BoxSizer(wx.VERTICAL)
        (server, group, item) = self.rulePath
        labelText = u"地址：{}.{}.{}".format(server, group, item)
        addressLabel = wx.StaticText(self, -1, label = labelText)
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        addressLabel.SetFont(font)
        vbox.Add(addressLabel, flag=(wx.ALL|wx.ALIGN_CENTER|wx.BOTTOM),border=5) 
        
        grid = wx.grid.Grid(self)
        grid.CreateGrid(6, 2)
        grid.SetDefaultRowSize(25)
        grid.SetColLabelValue(0, u"值")
        grid.SetColLabelValue(1, u"报警信息")
        
        grid.SetRowLabelValue(0, u'低低')
        grid.SetRowLabelValue(1, u'低')
        grid.SetRowLabelValue(2, u'高')
        grid.SetRowLabelValue(3, u'高高')
        grid.SetRowLabelValue(4, u'当')
        grid.SetRowLabelValue(5, u'间隔时间(分)')
        grid.SetRowLabelSize(70)
        
        #attr = wx.grid.GridCellAttr()
        #attr.SetEditor(wx.grid.GridCellChoiceEditor())
        #attr.SetRenderer(wx.grid.GridCellChoiceEditor(['5', '15', '30', '60'], True))
        grid.SetCellEditor(4, 0, wx.grid.GridCellChoiceEditor([u'真', u'假'], True))
        grid.SetCellValue(4, 0, u'假')
        
        grid.SetCellEditor(5, 0, wx.grid.GridCellChoiceEditor(['5', '15', '30', '60'], True))
        grid.SetCellValue(5, 0, '5')
        
        grid.SetColSize(0, 50)
        grid.SetColSize(1, 300)
        
        grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        grid.SetCellValue(5, 1, u"当前温度：{}".format(self.itemValue[0]))
        grid.SetReadOnly(5, 1, True)
        
        vbox.Add(grid,proportion=1,flag=(wx.ALL|wx.ALIGN_CENTER))
        
        btn = wx.Button(self, -1, label=u"确定")
        btn.Bind(wx.EVT_BUTTON, lambda event, grid=grid: self.btnClick(event, grid))
        vbox.Add(btn,proportion=1,flag=(wx.TOP|wx.CENTRE), border=5)
        self.SetSizer(vbox)  
        
        for item in self.rules:
            if item.keys()[0] == self.rulePath:
                (lower1, lower2)    = item.values()[0]['lower']
                (low1, low2)        = item.values()[0]['low']
                (high1, high2)      = item.values()[0]['high']
                (higher1, higher2)  = item.values()[0]['higher']
                (dang1, dang2)      = item.values()[0]['dang']
                interal             = item.values()[0]['interal']
                
                grid.SetCellValue(0, 0, lower1)
                grid.SetCellValue(0, 1, lower2)
                grid.SetCellValue(1, 0, low1)
                grid.SetCellValue(1, 1, low2)
                grid.SetCellValue(2, 0, high1)
                grid.SetCellValue(2, 1, high2)
                grid.SetCellValue(3, 0, higher1)
                grid.SetCellValue(3, 1, higher2)
                
                grid.SetCellValue(4, 0, u'真' if dang1 else u'假')
                grid.SetCellValue(4, 1, dang2)
                grid.SetCellValue(5, 0, interal)
                
    def btnClick(self, e, grid):
        for row in range(5):
            for col in range(2):
                if grid.GetCellValue(row, col) == '':
                    wx.MessageBox(u'亲爱的用户，您的规则没有配置完整！', u'提示', wx.OK | wx.ICON_EXCLAMATION)
                    return
                else:
                    try:
                        int(grid.GetCellValue(5, 0))
                    except Exception, _e:
                        wx.MessageBox(u'亲爱的用户，时间间隔需要整数！', u'提示', wx.OK | wx.ICON_EXCLAMATION)
                        return
                            
        rule = {}
        rule['lower']  = (grid.GetCellValue(0, 0), grid.GetCellValue(0, 1))
        rule['low']    = (grid.GetCellValue(1, 0), grid.GetCellValue(1, 1))
        rule['high']   = (grid.GetCellValue(2, 0), grid.GetCellValue(2, 1))
        rule['higher'] = (grid.GetCellValue(3, 0), grid.GetCellValue(3, 1))
        rule['dang']   = (grid.GetCellValue(4, 0) == u'真', grid.GetCellValue(4, 1))
        rule['interal']= grid.GetCellValue(5, 0)
        
        for item in self.rules:
            if item.keys()[0] == self.rulePath:
                index = self.rules.index(item)
                self.rules[index] = {self.rulePath : rule}
                print "modify rule: {}, rules: {}".format(self.rulePath, self.rules)
                self.Destroy()
                return
        self.rules.append({self.rulePath : rule})
        print "create rule: {}".format(rule)
        self.Destroy()
        pass    
    def OnClose(self, e):
        self.Destroy()

class MyFrame(wx.Frame):
    def __init__(self, parent, ID):
        wx.Frame.__init__(self, parent, ID)
        btn = wx.Button(self, -1)
        btn.Bind(wx.EVT_BUTTON, self.click)
    def click(self, e):
        dialog = CreateRuleDialog(None, -1, rulepath=('Server1','Group1','Item1=120'), itemvalue=(120,), rules=[])
        dialog.ShowModal()
        dialog.Destroy()  
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, -1)
    frame.Show(True)
    app.MainLoop()
    pass