#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Università degli Studi di Padova
# Corso di Laurea Magistrale in Informatica
# 
# wx.CallAfter(pub.sendMessage
# Riccardo Angius
#
# model.py

import networkx as nx
import operator
from common import *

def Line(i, j, direction='h'):
        horizontal = (direction == 'h')
        vertical = not horizontal
        
        if horizontal:
            head = pairSum((i,j),(0,1))
            
        if vertical:
            head = pairSum((i,j),(1,0))
                        
        return ((i, j), head, {'taker': NoPlayer})

class GameBoard(nx.Graph):
        
    def __init__(self, dotsPerSide, secondsToDecide):
        
        self.dotsPerSide = dotsPerSide
        self.secondsToDecide = secondsToDecide
        self.experimentPlayers = dict()
        
        self.squaresTotal = (dotsPerSide-1) * (dotsPerSide-1)
        
        upperBound = dotsPerSide + 1
        
        # For the sake of sanity, indices start at 1
        
        # Horizontal lines are inserted in the graph from left to right beginning on dot i,j
        lines = [Line(i, j, 'h') for i in range(1, upperBound) for j in range(1, upperBound-1)]

        # Vertical lines are inserted in the graph from top to bottom beginning on dot i,j
        lines = lines + [Line(i, j, 'v') for i in range(1, upperBound-1) for j in range(1, upperBound)]
        
        super(GameBoard, self).__init__(lines)

        self.depth = 0
        
        self.pliesInAGame = self.number_of_edges()
        
        self.pastPlies = list()
        
        self.squares = dict()
        
        for i in range(1, dotsPerSide):
            for j in range(1, dotsPerSide):
                self.squares[(i,j)] = NoPlayer
        
        self.linesStruck = dict()
        self.linesStruck[PLAYER_A] = 0
        self.linesStruck[PLAYER_B] = 0
        
        self.score = { PLAYER_A: 0, PLAYER_B: 0 }
        
        self.currentPlayer = PLAYER_A
        
        self.skip = False
        
    def gameOver(self):
        availableActions = self.pliesInAGame - len(self.pastPlies)
        return (availableActions == 0)
            
    def acknowledgeSkip(self):
        self.skip = False
        self.currentPlayer = PLAYER_B if self.currentPlayer == PLAYER_A else PLAYER_A
    
    def strikeLine(self, line):
        # TO-DO: add exceptions to manage ill values
        
        if (self.skip):
            self.acknowledgeSkip()
            return False
        
        self.depth = self.depth + 1
        print(line)

        (dot1, dot2) = sorted(line)
        

        # G[tail][head] is handy sugar offered by nx
        # to access the edge between *tail* and *head*
        targetLine = self[dot1][dot2]
        
        if struck(targetLine):
            return False
        
        direction = 'h' if row(dot1) == row(dot2) else 'v'
        
        plyPlayer = self.currentPlayer
        
        self.linesStruck[plyPlayer] = self.linesStruck[plyPlayer] + 1
        
        squaresTaken = list()
        
        targetLine['taker'] = self.currentPlayer

        # Check if one or more squares were taken
    
        # Transpose if necessary
        startDot = revPair(dot1) if direction == 'h' else dot1
        
        i, j = startDot                
    
        # left
        if j > 1:
            a = pairSum(startDot, (0,-1))
            b = pairSum(a, (1,0))
            c = pairSum(b, (0,1))
        
            if direction == 'h':
                # Transpose back
                a, b, c = revPair(a), revPair(b), revPair(c)
                                        
            if struck(self[dot1][a]) and struck(self[a][b]) and struck(self[b][c]):
                # A square has been taken
                self.score[self.currentPlayer] = self.score[self.currentPlayer] +1
            
                squareID = min(dot1,a,b,c)

                squaresTaken.append(squareID)
            
                self.squares[squareID] = self.currentPlayer
        
        # right
        if j < self.dotsPerSide:
            a = pairSum(startDot, (1,0))
            b = pairSum(a, (0,1))
            c = pairSum(b, (-1,0))

            if direction == 'h':
                # Transpose back
                a, b, c = revPair(a), revPair(b), revPair(c)

            if struck(self[a][b]) and struck(self[b][c]) and struck(self[c][dot1]):
                # A square has been taken
                self.score[self.currentPlayer] = self.score[self.currentPlayer] +1
                squareID = min(dot1,a,b,c)
                squaresTaken.append(squareID)
            
                self.squares[squareID] = self.currentPlayer

        self.pastPlies.append(line)

        if SQUARE_TAKER_PLAYS_AGAIN:       
            self.skip = len(squaresTaken) > 0

        # Interleave each other's plies
        self.currentPlayer = PLAYER_B if plyPlayer == PLAYER_A else PLAYER_A
        
        return (plyPlayer, squaresTaken)
    
    def experimentDetails(self):
        
        details = []
        
        details.append("Game was played on %dx%d gameboard." % (self.dotsPerSide,self.dotsPerSide))
        details.append("CPU players were given %f second(s) to decide their move." % (self.secondsToDecide,))
        
        for playerID in self.experimentPlayers:
            playerConfig = self.experimentPlayers[playerID]
            del playerConfig.hashTable
            del playerConfig.descendants
            del playerConfig.nodesVisited
            del playerConfig.timeoutEvent            
            del playerConfig.movesFirst
            
            details.append("Player %s: " % (playerID,))
            details.append(str(vars(playerConfig)))
            details.append("\n")
    
        details = '\n'.join(details)
    
        return details
    
    def __hash__(self):
        """Represent graph as current player followed by current player, followed by state of squares followed by state of lines """
        
        squaresStr = ""
        
        for key in sorted(self.squares):
            squaresStr = squaresStr + self.squares[key]
        
        linesStr = ""
        
        struckLines = self.pastPlies
        
        for line in sorted(struckLines):
            linesStr = linesStr + str(line)
        
        skipFlag = "1" if self.skip else "0"
        
        gbhash = hash(skipFlag + self.currentPlayer + squaresStr + linesStr)
        
        return gbhash