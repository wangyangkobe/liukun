#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import socket
import images
import OpenOPC
import string
import CreateRuleDialog
import RuleGrid
import traceback
import itertools
import Rule       
 
rules = []  # 配置的rules

opc = OpenOPC.client()
# opc.set_trace(sys.stdout.write)
opcServers = opc.servers()
print "opc servers: {}".format(opcServers)
print opc.connect(opcServers[0], 'localhost')
print "opc groups: {}".format(opc.list())
serverInfo = dict(opc.info())
opcItems = {}
for server in opc.servers():
    opc.connect(server, 'localhost')
    groups = {}
    for group in opc.list():
        items = []
        for item in opc.list(group):
            items.append(item)
        groups[group] = items
    opcItems[server] = groups

print opcItems    

computerName = socket.gethostname()
print "computer name: {}".format(computerName)

infoText = u"2、配置报警点。\n" + u"3、微信扫描右侧二维码并关注, 即可获取报警推送\n" + u"4、如果需要推送给其它同事，请将下面链接发送给他:" + u" http://wx.indyun.com/uidABCDEFGH\n" + u"5、任何问题或合作意向，请联系wxpush@indyu.com或18016061306"

class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Main Frame")
        
        topSplitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        topSplitter.SetMinimumPaneSize(150)
        
        downSplitter = wx.SplitterWindow(topSplitter, style=wx.SP_LIVE_UPDATE)
        downSplitter.SetMinimumPaneSize(150)
        
        leftPanel = wx.Panel(downSplitter, -1, style=wx.BORDER_SUNKEN)
        rightPanel = wx.Panel(downSplitter, -1, style=wx.BORDER_SUNKEN)
        downSplitter.SplitVertically(leftPanel, rightPanel)
        # vSplitter.SetSashGravity(0.2)
        downSplitter.SetSashPosition(200)
        
        topPanel = wx.Panel(topSplitter, -1, style=wx.BORDER_SUNKEN)
        topSplitter.SplitHorizontally(topPanel, downSplitter)
        # topSplitter.SetSashGravity(0.2)
        topSplitter.SetSashPosition(150, True)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.configureTopPanel(topPanel)
        self.configureLeftPanel(leftPanel)
        self.configureRightPanel(rightPanel)
        
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(3)
        self.statusBar.SetStatusWidths([-1, -2, -3])
        self.statusBar.SetStatusText(u'server状态: {}'.format(serverInfo['State']), 0)
        
        self.totalRuleNum = 0
        
        self.__close_callback = None
        self.Bind(wx.EVT_CLOSE, self._when_closed)
        self.timers = {}
        
    def register_close_callback(self, callback):
        self.__close_callback = callback

    def _when_closed(self, event):
        doClose = True if not self.__close_callback else self.__close_callback()
        if doClose:
            print '_when_closed'
            for _, timer in self.timers.items():
                timer.Stop()
            event.Skip()
    
    def configDialogClose(self, event):
        print 'In configDialogClose'
        event.Skip()

    def configDialogDestroy(self, event): 
        '''点击左边item添加rule时调用'''
        if len(rules) > self.totalRuleNum:
            self.ruleGrid.addItem(rules[-1])
            self.ruleGrid.ForceRefresh()
            self.scheldRule()
        print 'In OnDestroy'
        event.Skip()
    def onCheckBoxSelected(self, row, isSelected):
        ruleItem = rules[row - 1]
        ruleItem.validated = isSelected
        rules[row - 1] = ruleItem
        self.scheldRule()
        print 'onCheckBoxSelected: %s' % ruleItem
        
    def configureRightPanel(self, panel):
        noteBook = wx.Notebook(panel, -1, style=wx.NB_TOP)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        
        rulePanel = wx.Panel(noteBook, -1)
        rulePanel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        logPanel = wx.Panel(noteBook, -1)
        
        staticBox = wx.StaticBox(rulePanel, -1, u"")
        stacticBoxSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        
        btnBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        addBtn = wx.Button(rulePanel, -1, label=u"增加")
        delBtn = wx.Button(rulePanel, -1, label=u"删除")        
        modBtn = wx.Button(rulePanel, -1, label=u"修改")  
                  
        btnBoxSizer.Add(addBtn, 0, wx.ALL, 2)
        btnBoxSizer.Add(delBtn, 0, wx.ALL, 2)
        btnBoxSizer.Add(modBtn, 0, wx.ALL, 2)
        
        self.ruleGrid = RuleGrid.RuleGrid(rulePanel, self.onCheckBoxSelected)
        
        stacticBoxSizer.Add(btnBoxSizer, 0, wx.ALL | wx.CENTER, 0)
        stacticBoxSizer.Add(self.ruleGrid, 1, wx.ALL | wx.CENTER, 5)
        
        rulePanel.SetSizer(stacticBoxSizer)
        
        addBtn.Bind(wx.EVT_BUTTON, self.clickAddBtn)
        delBtn.Bind(wx.EVT_BUTTON, self.clickDelBtn)
        modBtn.Bind(wx.EVT_BUTTON, self.clickModifyBtn)
        
        
        logTextCtrl = wx.TextCtrl(logPanel, -1, style=(wx.BORDER_NONE | wx.MULTIPLE | wx.TE_READONLY | wx.TE_AUTO_URL))
        logBoxSizer = wx.BoxSizer(wx.VERTICAL)
        logBoxSizer.AddSizer(logTextCtrl, 1, wx.EXPAND)
        logPanel.SetSizer(logBoxSizer)
        
        logTarget = wx.LogTextCtrl(logTextCtrl)
        logTarget.SetTimestamp("%Y-%m-%d %H:%M:%S")
        wx.Log.SetActiveTarget(logTarget)
       
        noteBook.AddPage(rulePanel, u"现有规则", select=True)
        noteBook.AddPage(logPanel, u"日志")
        panelSizer.Add(noteBook, 1, wx.ALL | wx.EXPAND)
        panel.SetSizer(panelSizer)
        pass
    
    def configureTopPanel(self, panel):
        staticBox = wx.StaticBox(panel, -1, u"使用说明")
        font = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        staticBox.SetFont(font)
        boxSizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        
        font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        
        nameBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        nameLabel = wx.StaticText(panel, -1, u"1、输入项目名称：")
        nameLabel.SetFont(font)
        nameInput = wx.TextCtrl(panel, -1, computerName)
        nameBtn = wx.Button(panel, -1, label=u"确定")
        
        nameBoxSizer.Add(nameLabel, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        nameBoxSizer.Add(nameInput, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        nameBoxSizer.Add(nameBtn, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        text = wx.TextCtrl(panel, -1, infoText, style=(wx.BORDER_NONE | wx.MULTIPLE | wx.TE_READONLY | wx.TE_AUTO_URL))
        text.SetFont(font)
        text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        
        nameBtn.Bind(wx.EVT_BUTTON, lambda evt, textCtrl=text: self.projNameBtnClick(evt, textCtrl))
        # text = wx.StaticText(self, -1, infoText)
       
        # text.SetFont(font)
        
        boxSizer.Add(nameBoxSizer, 0, wx.Left)
        boxSizer.Add(text, 0, wx.ALL | wx.EXPAND)
        border = wx.BoxSizer()
        border.Add(boxSizer, 1, wx.EXPAND | wx.ALL, 5)
        
        bitmap = wx.Image(r'C:\Users\elqstux\Desktop\Python\WxPython\picture.jpg', wx.BITMAP_TYPE_JPEG).Scale(120, 120, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
        
        staticBitMap = wx.StaticBitmap(panel, -1, bitmap)
       
        border.Add(staticBitMap, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(border)
        # panel.SetSizerAndFit(border)
    
    def configureLeftPanel(self, panel):
        panel.Bind(wx.EVT_SIZE, self.onSize)
        tID = wx.NewId()
        self.tree = wx.TreeCtrl(panel, tID, style=wx.TR_HAS_BUTTONS)

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, isz))
        fileidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        smileidx = il.Add(images.Smiles.GetBitmap())

        self.tree.SetImageList(il)
        self.il = il

        # NOTE:  For some reason tree items have to have a data object in
        #        order to be sorted.  Since our compare just uses the labels
        #        we don't need any real data, so we'll just use None below for
        #        the item data.

        self.root = self.tree.AddRoot(u"可用OPC列表")
        self.tree.SetPyData(self.root, None)
        self.tree.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)


        for server in opcItems.keys():
            child = self.tree.AppendItem(self.root, server)
            self.tree.SetPyData(child, None)
            self.tree.SetItemImage(child, fldridx, wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(child, fldropenidx, wx.TreeItemIcon_Expanded)

            for group in opcItems[server].keys():
                last = self.tree.AppendItem(child, group)
                self.tree.SetPyData(last, None)
                self.tree.SetItemImage(last, fldridx, wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(last, fldropenidx, wx.TreeItemIcon_Expanded)

                for leaf in opcItems[server][group]:
                    item = self.tree.AppendItem(last, leaf)
                    self.tree.SetPyData(item, None)
                    self.tree.SetItemImage(item, fileidx, wx.TreeItemIcon_Normal)
                    self.tree.SetItemImage(item, smileidx, wx.TreeItemIcon_Selected)

        self.tree.Expand(self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.treeLeafDoubleClick, self.tree)
    
    def onSelChanged(self, event):
        item = event.GetItem()
        if self.isLeafItem(item) and self.getItemPath(item):
            (server, group, item) = self.getItemPath(item)
            itemValue = self.getItemValue(server, group, item)
            self.statusBar.SetStatusText(str(itemValue), 1)
            event.Skip()
            
    def treeLeafDoubleClick(self, event):
        item = event.GetItem()
        if self.isLeafItem(item):
            (serverText, groupText, itemText) = self.getItemPath(item)
            itemValue = self.getItemValue(serverText, groupText, itemText)
            ruleItem = Rule.Rule()
            configRuleDialog = CreateRuleDialog.CreateRuleDialog(ruleItem,
                                                                 rulePath=self.getItemPath(item),
                                                                 itemValue=itemValue,
                                                                 rules=rules,
                                                                 isBool=(type(itemValue[0]) == type(True)) 
                                                                 )
            self.totalRuleNum = len(rules)
            configRuleDialog.Bind(wx.EVT_CLOSE, self.configDialogClose)
            configRuleDialog.Bind(wx.EVT_WINDOW_DESTROY, self.configDialogDestroy)
            
            configRuleDialog.ShowModal()
            configRuleDialog.Destroy()
        event.Skip()
        
    def isLeafItem(self, item):
        return item and (self.tree.GetChildrenCount(item) == 0)
    
    def getItemPath(self, item):
        itemText = str(self.tree.GetItemText(item))
        if string.index(itemText, '.') != -1:
            group = self.tree.GetItemParent(item)
            server = self.tree.GetItemParent(group)
            return (self.tree.GetItemText(server), self.tree.GetItemText(group), itemText)
        else:
            return None
        
    def getItemValue(self, server, group, item):
            opc.close()
            opc.connect(server, 'localhost')
            return opc.read(item, group=group, sync=True, timeout=5000*2)
                     
    def onSize(self, event):
        w, h = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, w, h)    
        
    def clickAddBtn(self, e):
        print 'clickAddBtn'   
    def clickDelBtn(self, e):
        try:
            for rowNum in self.ruleGrid.GetSelectedRows():
                if rowNum == 0:
                    break
                delRuleKey = self.ruleGrid.GetCellValue(rowNum, 2)
                for item in rules:
                    if item.strKey == delRuleKey:
                        rules.remove(item)
                        self.ruleGrid.DeleteRows(rowNum)
                print 'delete rule: {}'.format(delRuleKey)
        
            self.ruleGrid.ForceRefresh()
        except Exception, _e:
            pass
        print 'clickDelBtn'
           
    def clickModifyBtn(self, e):
        try:
            selectRowNum = self.ruleGrid.GetSelectedRows()[0]
            rulePath = self.ruleGrid.GetCellValue(selectRowNum, 2)

            for item in rules:
                ruleKey = item.key
                itemValue = self.getItemValue(ruleKey[0], ruleKey[1], ruleKey[2])

                if '.'.join(ruleKey) == rulePath:
                    configRuleDialog = CreateRuleDialog.CreateRuleDialog(item,
                                                                         rulePath=ruleKey,
                                                                         itemValue=itemValue,
                                                                         rules=rules,
                                                                         isBool=(type(itemValue[0]) == type(True))
                                                                         )
                    configRuleDialog.ShowModal()
                    configRuleDialog.Destroy()
                self.scheldRule()    
        except Exception, _e:
            print traceback.format_exc()
        print 'clickModifyBtn' 
        
    def projNameBtnClick(self, e, textCtrl):
        print "projNameBtnClick"
        textCtrl.SetValue("Hello")
        pass
    
    def scheldRule(self):
        for _, timer in self.timers.items():
            timer.Stop()
        self.timers = {}
        
        for timerKey, group in itertools.groupby(rules, lambda rule : rule.interal):          
            timer = wx.Timer(self, int(timerKey))
            timer.Start(1000)             
            timer.rules = list(group)
            self.timers[timerKey] = timer  
            
            self.Bind(wx.EVT_TIMER, self.onTimerEvent, timer)
        
    def onTimerEvent(self, evt):
        timerKey = str(evt.GetId())
        groupRules = self.timers[timerKey].rules
        for ruleItem in groupRules:   
            (server, group, item) = ruleItem.key
            if ruleItem.validated:
                currentValue = self.getItemValue(server, group, item)
                if ruleItem.isBool:
                    (dang1, dang2) = ruleItem.dang
                    if currentValue[0] != dang1:
                        wx.LogMessage(dang2)
                pass
        pass
        
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(parent=None)
    # frame.CreateStatusBar()
    frame.Maximize(True)
    frame.Show(True)
    frame.register_close_callback(lambda: True)
    
    wx.LogMessage(u"PM 登录成功")
    # frame.ShowFullScreen(True, style=(wx.FULLSCREEN_NOTOOLBAR | wx.FULLSCREEN_NOSTATUSBAR |wx.FULLSCREEN_NOBORDER |wx.FULLSCREEN_NOCAPTION))
    app.MainLoop()   
