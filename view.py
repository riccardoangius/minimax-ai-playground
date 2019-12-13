#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Università degli Studi di Padova
# Corso di Laurea Magistrale in Informatica
# 
# wx.CallAfter(pub.sendMessage
# Riccardo Angius
#
# view.py

import wx

from common import *

appName = 'Dots and Boxes'
windowSize = (400, 450)

import os

class MainWindow(wx.Frame):
    def __init__(self, dotsPerSide):
        wx.Frame.__init__(self, None, title=appName)
        
        menuBar = wx.MenuBar()

        fileMenu = wx.Menu()
        
        exitItem = fileMenu.Append(wx.ID_EXIT, "&Exit")
        
        self.Bind(wx.EVT_MENU, self.onClose, exitItem)
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # This is not necessary unless we add more actions to the menu
        # menuBar.Append(fileMenu, "&File")
        
        self.SetMenuBar(menuBar)
        
        self.panel = wx.Panel(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.scoreText = wx.StaticText(self.panel, label='')
        self.sizer.Add(self.scoreText, flag=wx.ALL, border=3)
                    
        self.turnText = wx.StaticText(self.panel, label='')
        self.sizer.Add(self.turnText, flag=wx.ALL, border=3)
        
        # Gameboard is a square, with each side composed of (dots) dots and (dots-1) lines
        sideLength = dotsPerSide*2-1            
        
        self.gameboardSizer = wx.GridBagSizer(sideLength, sideLength)

        for i in range(0, sideLength, 2):
            for j in range(0, sideLength, 2):
                dot = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap('includes/dot.png'))
                self.gameboardSizer.Add(dot, pos=(i,j), flag=wx.ALL|wx.ALIGN_CENTER)

        # Add clickable lines
        # Horizontal first
        for i in range(0, sideLength, 2):
            for j in range(1, sideLength-1, 2):
                dot1 = ((i/2)+1,(j/2)+1)
                dot2 = pairSum(dot1, (0,1))
                                    
                lineBtn = wx.BitmapButton(self.panel, bitmap=wx.Bitmap('includes/noHorizontalLine.png'))
                lineBtn.SetBitmapDisabled(bitmap=wx.Bitmap('includes/noHorizontalLine.png'))
                lineBtn.SetBitmapCurrent(bitmap=wx.Bitmap('includes/horizontalLine.png'))
                lineBtn.SetBackgroundColour('#62625B')

                lineBtn.lineDots = (dot1, dot2)
                
                self.gameboardSizer.Add(lineBtn, pos=(i,j), flag=wx.ALL|wx.ALIGN_CENTER)

        # Then vertical
        for i in range(1, sideLength-1, 2):
            for j in range(0, sideLength, 2):
                dot1 = ((i/2)+1,(j/2)+1)
                dot2 = pairSum(dot1, (1,0))
                
                lineBtn = wx.BitmapButton(self.panel, bitmap=wx.Bitmap('includes/noVerticalLine.png'))
                lineBtn.SetBitmapDisabled(bitmap=wx.Bitmap('includes/verticalLine.png'))
                lineBtn.SetBitmapCurrent(bitmap=wx.Bitmap('includes/verticalLine.png'))
                lineBtn.SetBackgroundColour('#62625B')
                
                lineBtn.lineDots = (dot1, dot2)
                
                self.gameboardSizer.Add(lineBtn, pos=(i,j), flag=wx.ALL|wx.ALIGN_CENTER)

        # Placeholders for squares
        for i in range(1, sideLength-1, 2):
            for j in range(1, sideLength-1, 2):
                placeholder = wx.Image(100,100, False)
                square = wx.StaticBitmap(self.panel, bitmap = wx.Bitmap.FromRGBA(100,100,alpha=1))
                
                self.gameboardSizer.Add(square, pos=(i,j), flag=wx.ALL|wx.ALIGN_CENTER)

        # Add gameboard
        self.sizer.Add(self.gameboardSizer, 0, flag=wx.ALL|wx.ALIGN_CENTER, border=5)
        
        self.panel.SetSizer(self.sizer)
        
        self.SetBackgroundColour('#62625B')
        
        self.sizer.Fit(self)

        # Remember what lines have been drafted by CPU players
        self.draftLines = []

        self.Show(True)
        self.Center()

    def close(self):
        self.onClose(wx.EVT_CLOSE)

    def onClose(self, event):
        self.Destroy()

    def addClickHandler(self, clickHandler):
        self.Bind(wx.EVT_BUTTON, clickHandler)

    def disableGameboard(self):
        self.SetEvtHandlerEnabled(False)
        
    def enableGameboard(self):
        self.SetEvtHandlerEnabled(True)
             
    def updateScore(self, score):
        self.scoreText.SetLabel("SCORES PlayerA: %d, Player B: %d" % (score[PLAYER_A], score[PLAYER_B]))
    
    def updateCurrentPlayer(self, currentPlayer):
        self.turnText.SetLabel("It's %s's turn!" % (currentPlayer,))
    
    def gameOver(self, winner):
        self.turnText.SetLabel("GAME OVER! %s wins!" % (winner,))
    
    def draftLine(self, dots):
        self.draftLines.append(dots)
        self.drawLine(dots)
    
    def clearDraftLines(self):        
        while len(self.draftLines) > 0:
            self.clearDraftLine(self.draftLines[-1])
    
    def drawLine(self, dots):
        (dot1, dot2) = sorted(dots)
        
        direction = 'h' if row(dot1) == row(dot2) else 'v'

        if direction == 'h':
            i = (row(dot1)*2)-2
            j = (col(dot1)*2)-1
        else:
            i = (row(dot1)*2)-1
            j = (col(dot1)*2)-2
        
        target = self.gameboardSizer.FindItemAtPosition((i,j)).GetWindow()
        target.Enable(False)
        
        if (not hasattr(target,"plainColour")):
            target.plainColour = target.GetBackgroundColour() 
            target.SetBackgroundColour("red")

    def clearDraftLine(self, dots):
        
        try:
            self.draftLines.remove(dots)
        except ValueError:
            return
            
        (dot1, dot2) = sorted(dots)
                    
        direction = 'h' if row(dot1) == row(dot2) else 'v'

        if direction == 'h':
            i = (row(dot1)*2)-2
            j = (col(dot1)*2)-1
        else:
            i = (row(dot1)*2)-1
            j = (col(dot1)*2)-2
        
        
        target = self.gameboardSizer.FindItemAtPosition((i,j)).GetWindow()
        target.SetBackgroundColour(target.plainColour)
        target.Enable(True)
        
        del target.plainColour
        
    def squareTaken(self, taker, position):
        imgPath = SQUARE_A if taker == PLAYER_A else SQUARE_B
        # Let's adjust the position with respect to the sizer
        i, j = position

        i = i*2-1
        j = j*2-1
        
        target = self.gameboardSizer.FindItemAtPosition((i,j)).GetWindow()
        target.SetBitmap(wx.Bitmap(imgPath))