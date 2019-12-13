#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Università degli Studi di Padova
# Corso di Laurea Magistrale in Informatica
# 
# wx.CallAfter(pub.sendMessage
# Riccardo Angius
#
# players.py

import copy
import time 
from random import seed, shuffle
from common import *

class SuccessorIterator:
    """Iterator over the successor states of the state (gameboard) passed
    to the constructor.
      
    Its usage allows for backtracking search, i.e. using O(m) memory, 
    where m is the maximum tree depth.
    """
    
    def __init__(self, gameboard):
        self.actions = [(dot1,dot2) for (dot1, dot2, l) in gameboard.edges(data=True) if unstruck(l)]
        
        seed()
        shuffle(self.actions)        
        
        n = gameboard.dotsPerSide
 
        self.gameboard = gameboard

    def __iter__(self):
        return self

    def next(self):
        if len(self.actions) < 1:
            raise StopIteration
        else:
            action = self.actions.pop()
            
            successor = copy.deepcopy(self.gameboard)
            successor.strikeLine(action)

            return (action, successor)
    
def successors(gameboard):
    """ Returns the unsorted list of the state's successors. """

    actions = [(dot1, dot2) for (dot1, dot2, l) in gameboard.edges(data=True) if unstruck(l)]
    
    shuffle(actions)
    
    reached = list()
    
    for action in actions:
        successor = copy.deepcopy(gameboard)
        successor.strikeLine(action)
        
        reached.append((action, successor))
            
    return reached

def evalFun1(gameboard):
    """ Evaluation function #1: number of squares taken by A minus those taken by B
    """
    return payoff(gameboard)
    
def evalFun2(gameboard):
    """ Evaluation function #2: number of lines taken by A minus those taken by B
    """
    
    return gameboard.linesStruck[PLAYER_A] - gameboard.linesStruck[PLAYER_B]
    
def evalFun3(gameboard):
    """ Evaluation function #3: sum of Eval1 and Eval2
    """
    return evalFun1(gameboard) + evalFun2(gameboard)

def evalFun4(gameboard):
    """ Evaluation function #4: Flaherty-Wu loss function 
    http://www.rowlandoflaherty.com/wp-content/uploads/2012/04/Project1_Paper_DotsAndBoxes_OFlaherty_Wu.pdf
    
    """
    
    struckLines = set(gameboard.pastPlies)
    
    S2 = 0
    S3 = 0     
    
    for key in gameboard.squares:
        taker = gameboard.squares[key]
  
        if (taker == NoPlayer):
                        
            a = key
            b = pairSum(a, (0,1))
            c = pairSum(b, (1,0))
            d = pairSum(c, (0,-1))
            
            linesInSquare = int((a, b) in struckLines) + int((b, c) in struckLines) + int((c, d) in struckLines) + int((d, a) in struckLines)

            if linesInSquare == 2:
                S2 = S2+1
            elif linesInSquare == 3:
                S3 = S3+1
    
    sign = 1 if (gameboard.currentPlayer == PLAYER_A) else -1

    t1 = 2*payoff(gameboard)
    t2 = (0.75*S3 -0.5*S2)

    stateValue = t1 + sign*t2
    
    return stateValue

def evalFun5(gameboard):
    """ Evaluation function #5: 2*payoff(state) ±S2 """
    
    struckLines = set(gameboard.pastPlies)

    S2 = 0

    for key in gameboard.squares:
        taker = gameboard.squares[key]
  
        if (taker == NoPlayer):            
            a = key
            b = pairSum(a, (0,1))
            c = pairSum(b, (1,0))
            d = pairSum(c, (0,-1))
            
            linesInSquare = int((a, b) in struckLines) + int((b, c) in struckLines) + int((c, d) in struckLines) + int((d, a) in struckLines)

            if linesInSquare == 2:
                S2 = S2+1
    
    sign = 1 if (gameboard.currentPlayer == PLAYER_A) else -1
    
    t1 = 2*payoff(gameboard)
    t2 = S2

    stateValue = t1 + sign*t2
    
    return stateValue

def evalFun6(gameboard):
    """ Evaluation function #6: 2*payoff(state) ±S3 """
    
    struckLines = set(gameboard.pastPlies)
    
    S3 = 0
    
    for key in gameboard.squares:
        taker = gameboard.squares[key]
  
        if (taker == NoPlayer):
            
            a = key
            b = pairSum(a, (0,1))
            c = pairSum(b, (1,0))
            d = pairSum(c, (0,-1))
            
            linesInSquare = int((a, b) in struckLines) + int((b, c) in struckLines) + int((c, d) in struckLines) + int((d, a) in struckLines)

            if linesInSquare == 3:
                S3 = S3+1
    
    sign = 1 if (gameboard.currentPlayer == PLAYER_A) else -1
        
    t1 = 2*payoff(gameboard)
    t2 = S3

    stateValue = t1 + sign*t2
    
    return stateValue

def evalFun7(gameboard):
    """ Evaluation function #7: 2*payoff(state) ±S1 """
    
    struckLines = set(gameboard.pastPlies)
    
    S1 = 0
    
    for key in gameboard.squares:
        taker = gameboard.squares[key]
  
        if (taker == NoPlayer):
            
            a = key
            b = pairSum(a, (0,1))
            c = pairSum(b, (1,0))
            d = pairSum(c, (0,-1))
            
            linesInSquare = int((a, b) in struckLines) + int((b, c) in struckLines) + int((c, d) in struckLines) + int((d, a) in struckLines)

            if linesInSquare == 1:
                S1 = S1+1
    
    o = 1 if (gameboard.currentPlayer == PLAYER_A) else -1
        
    t1 = 2*payoff(gameboard)
    t2 = S1

    stateValue = t1 + o*t2
    
    return stateValue

def evalFun(gameboard, evalFunID):
    if evalFunID == 0:
        return payoff(gameboard)
    elif evalFunID == 1:
        return evalFun1(gameboard)
    elif evalFunID == 2:
        return evalFun2(gameboard)
    elif evalFunID == 3:
        return evalFun3(gameboard)
    elif evalFunID == 4:
        return evalFun4(gameboard)    
    elif evalFunID == 5:
        return evalFun5(gameboard) 
    elif evalFunID == 6:
        return evalFun6(gameboard)
    elif evalFunID == 7:
        return evalFun7(gameboard)
    else:
        raise ValueError("Value '%s' was given as Evaluation function ID." % (str(evalFunID),))

def terminalTest(gameboard):
    return gameboard.gameOver()

def cutoffTest(gameboard, ttl):
    return terminalTest(gameboard) or (ttl == 0)

def quiescent1(gameboard):
    """ Quiescence check #1: if a single move allows the opponent 
        to score a square, then the state is not quiescent
    """
    struckLines = set(gameboard.pastPlies)
    
    for key in gameboard.squares:
        # TODO: Should optimize the computation of line IDs
        taker = gameboard.squares[key]
  
        if (taker == NoPlayer):
            movesToSquare = 4
            
            a = key
            b = pairSum(a, (0,1))
            
            if (a, b) in struckLines:
                movesToSquare = movesToSquare -1

            c = pairSum(b, (1,0))
            
            if (b, c) in struckLines:
                movesToSquare = movesToSquare -1

            d = pairSum(c, (0,-1))

            if (c, d) in struckLines:
                movesToSquare = movesToSquare -1

            if movesToSquare == 1:
                return False
            
            if (d, a) in struckLines:
                movesToSquare = movesToSquare -1            
            
            if movesToSquare == 1:
                return False            
        
            # This could be more elegant but unfortunately less efficient, too 
            # squareLines = set([(a,b), (b,c), (c,d), (d,a)])
        
            # if (len(struckLines.intersection(squareLines)) > 2):
            #    return False
            
    return True

def quiescent4(gameboard):
    return True

def quiescent5(gameboard):
    return True

def quiescent6(gameboard):
    return True

def quiescent7(gameboard):
    return True

def quiescent(gameboard, evalFunID):
    # Quiescence is defined with respect to the evaluation function
    terminal = terminalTest(gameboard)
    
    if evalFunID == 0 or terminal:
        """Quiescence search is reserved to evaluation 
        functions applied before terminal states, thus it makes no sense
        to evaluate whether it is ok to cut off the search
        """
        return True
        
    elif evalFunID == 1:
        return quiescent1(gameboard)

    elif evalFunID == 2:
        return quiescent1(gameboard)

    elif evalFunID == 3:
        return quiescent1(gameboard)
        
    elif evalFunID == 4:
        return quiescent4(gameboard)

    elif evalFunID == 5:
        return quiescent5(gameboard)

    elif evalFunID == 6:
        return quiescent6(gameboard)

    elif evalFunID == 7:
        return quiescent7(gameboard)

    else:
        raise ValueError("Value '%s' was given as Evaluation function ID." % (str(evalFunID),))

def previousPassEval(hashTable, gameboard):
    try:
        evaluation = hashTable[hash(gameboard)]['v']
    except KeyError:
        evaluation = 0

    return evaluation

def bestActionSearch(gameboard, alpha, beta, ttl, playerConfig, frame):
    return bestValueSearch(gameboard, alpha, beta, ttl, playerConfig, frame, searchingAction=True)

def bestValueSearch(gameboard, alpha, beta, ttl, playerConfig, frame, searchingAction=False):

    timeoutEvent = playerConfig.timeoutEvent

    if timeoutEvent and timeoutEvent.isSet():
        raise Timeout()
    
    hashTable = playerConfig.hashTable
    alphaBeta = playerConfig.alphaBetaPruning
    evalFunID = playerConfig.evalFunID
    quiescenceSearch = playerConfig.quiescenceSearch

    if (gameboard.skip):
        gameboard.acknowledgeSkip()
        return bestValueSearch(gameboard, alpha, beta, ttl, playerConfig, frame, searchingAction)
    
    playerConfig.nodesVisited = playerConfig.nodesVisited + 1

    playerConfig.descendants = playerConfig.descendants +1

    if cutoffTest(gameboard, ttl):
        if (not quiescenceSearch) or (gameboard.depth == playerConfig.maxQuiescenceSearchDeepening) or  quiescent(gameboard, evalFunID):
            stateValue = evalFun(gameboard, evalFunID)
            
            if (stateValue is None):
                raise ValueError("State value was not assigned.")
            
            return stateValue
        else:
            ttl = ttl + 1
    
    maximizing = (gameboard.currentPlayer == PLAYER_A)
    minimizing = not maximizing
        
    if (playerConfig.useHashTable) and (not searchingAction):
        if (hash(gameboard) in hashTable):
            if (evalFunID == 0) or (hashTable[hash(gameboard)]['cutoffLevel'] >= gameboard.depth + ttl):
                playerConfig.descendants = playerConfig.descendants + hashTable[hash(gameboard)]['belowThisNode']
                return hashTable[hash(gameboard)]['v']
    
    if maximizing:
        v = -Infinity
    elif minimizing:
        v = Infinity
    
    if alphaBeta and playerConfig.successorSortCriteria:
        # Sort successors
        criteria = playerConfig.successorSortCriteria
        
        if criteria == 1:
            sortingCriteria = lambda action, successor: evalFun(successor, evalFunID)
        elif criteria == 2:
            sortingCriteria = lambda action, successor: previousPassEval(hashTable, successor)
        
        candidates = sorted(successors(gameboard), key=sortingCriteria, reverse = maximizing)
        
    else:
        # No point in wasting resources sorting successors if
        # we're going to expand them all anyway
        candidates = successors(gameboard)
    
    a = None
    
    if alphaBeta:
        pruned = False
    
    if evalFunID > 0:
        childTtl = ttl-1
    else:
        childTtl = ttl
    
    totalDescendantsBefore = playerConfig.descendants
    
    for action, successor in candidates:
                
        frame.draftLine(action)
        
        tmp = v

        if maximizing:
            
            v = max(v, bestValueSearch(successor, alpha, beta, childTtl, playerConfig, frame))
            
            if (v != tmp): 
                a = action
            
            if alphaBeta:
                if (v >= beta):
                    pruned = True
                    break

                alpha = max(alpha, v)

        elif minimizing:
                        
            v = min(v, bestValueSearch(successor, alpha, beta, childTtl, playerConfig, frame))
            
            if (v != tmp):
                a = action
            
            if alphaBeta:
                if (v <= alpha):
                    pruned = True
                    break
                            
                # Looking for the most negative value so to tell other child nodes
                # how good are previously considered moves
                beta = min(beta, v)
        
        frame.clearDraftLine(action)
        
    belowThisNode = playerConfig.descendants - totalDescendantsBefore
    
    if alphaBeta and pruned:
        frame.clearDraftLine(action)

    if playerConfig.useHashTable:
        hashTable[hash(gameboard)] = {'v': v, 'cutoffLevel': gameboard.depth + ttl, 'belowThisNode': belowThisNode }
        
    if searchingAction:
        return a
    
    return v
    
class PlayerConfig(object):
    def __init__(self, evalFunID, quiescenceSearch=False, movesFirst=False, timeoutEvent=None, alphaBetaPruning=True, successorSortCriteria=None, useHashTable=True):
        self.nodesVisited = 0
        self.descendants = 0
        self.quiescenceSearch = quiescenceSearch
        self.evalFunID = evalFunID
        self.movesFirst = movesFirst
        self.timeoutEvent = timeoutEvent
        self.hashTable = dict()
        self.alphaBetaPruning = alphaBetaPruning
        self.successorSortCriteria = successorSortCriteria
        self.useHashTable = useHashTable
        
def decision(gameboard, ttl, playerConfig, frame):
    
    if frame.talkingPlayers and (playerConfig.evalFunID > 0):
        print("Trying to reach depth %d." % (gameboard.depth + ttl))
    
    playerConfig.nodesVisited = 0
    
    playerConfig.descendants = 0
    
    playerConfig.maxQuiescenceSearchDeepening = gameboard.depth + ttl + QUIESCENCE_BONUS
    
    if playerConfig.alphaBetaPruning:
        a = bestActionSearch(gameboard, -Infinity, Infinity, ttl, playerConfig, frame)
    else:
        a = bestActionSearch(gameboard, None, None, ttl, playerConfig, frame)
        
    if frame.talkingPlayers:
        print("%d (virtually %d) nodes were visited. " % (playerConfig.nodesVisited, playerConfig.descendants))

    return a 