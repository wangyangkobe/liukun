#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2015��8��18��

@author: elqstux
'''
import wx, wx.grid as grd

class RuleGrid(grd.Grid):
    def __init__(self, parent, callback):
        grd.Grid.__init__(self, parent, -1)
        
        self.callback = callback
        
        self.CreateGrid(1,3)
        self.RowLabelSize = 0
        #self.ColLabelSize = 20

        self.SetColLabelValue(0, u"序号")
        self.SetColLabelValue(1, u"生效")
        self.SetColLabelValue(2, u"地址")
        
        self.SetCellValue(0, 0, "0")
        self.SetCellValue(0, 1, "1")
        self.SetCellValue(0, 2, u"OPCServer1.Group1.Item1")
        
        attr = grd.GridCellAttr()
        attr.SetEditor(grd.GridCellBoolEditor())
        attr.SetRenderer(grd.GridCellBoolRenderer())
        self.SetColAttr(1,attr)
        
        self.SetColSize(1,50)
        self.SetColSize(2,300)
        
        #self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        self.SetSelectionMode(self.wxGridSelectRows)
        #self.AutoSizeColumns(True)
        
        self.SetReadOnly(0,0,True)
        #self.SetReadOnly(0,1,True)
        self.SetReadOnly(0,2,True)
        
        self.SetDefaultCellBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_FRAMEBK))
        
        self.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK,self.onMouse)
        self.Bind(grd.EVT_GRID_SELECT_CELL,self.onCellSelected)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)
        
        self.rules = {}

    def onMouse(self,evt):
        if evt.GetRow() == 0 and evt.GetCol() ==1:
            return
        if evt.Col == 1:
            wx.CallLater(100,self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        try:
            self.cb.Value = not self.cb.Value
        
            selectedRow = self.GridCursorRow
            if callable(self.callback):
                self.callback(selectedRow, self.cb.Value)
                address = self.GetCellValue(selectedRow, 2)
                self.rules[address] = self.cb.Value
            self.afterCheckBox(self.cb.Value)
        except Exception, _e:
            pass

    def onCellSelected(self,evt):
        if evt.Col == 1:
            wx.CallAfter(self.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self,evt):
        if evt.Col == 1:
            self.cb = evt.Control
            self.cb.WindowStyle |= wx.WANTS_CHARS
            self.cb.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
            self.cb.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
        evt.Skip()

    def onKeyDown(self,evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.DisableCellEditControl()
                self.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.GridCursorRow < (self.NumberRows-1):
                self.DisableCellEditControl()
                self.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.GridCursorCol > 0:
                self.DisableCellEditControl()
                self.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.GridCursorCol < (self.NumberCols-1):
                self.DisableCellEditControl()
                self.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self,evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self,isChecked):
        print 'afterCheckBox',self.GridCursorRow,isChecked
        
    def addItem(self, value):
        self.AppendRows()
        (number, validate, address) = value
        self.SetCellValue(number, 0, str(number))
        self.SetCellValue(number, 1, str(validate))
        self.SetCellValue(number, 2, address)
        print value
        self.SetReadOnly(number,0,True)
        #self.SetReadOnly(number,1,True)
        self.SetReadOnly(number,2,True)
        
        self.rules[address] = bool(validate)
        self.ForceRefresh()

class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Custom cell editor test", size=(250,200))
        panel = wx.Panel(self,style=0)
        grid = RuleGrid(panel)
        grid.SetFocus()
        self.CentreOnScreen()

class MyApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    MyApp(0).MainLoop()