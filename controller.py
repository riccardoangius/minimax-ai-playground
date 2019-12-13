#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Università degli Studi di Padova
# Corso di Laurea Magistrale in Informatica
# 
# Riccardo Angius
#
# controller.py

import datetime
import threading
import sys, argparse

import wx

from time import sleep

from model import *
from view import * 
from common import *
from players import *

from copy import deepcopy

def clickHandler(gameboard, rightToStrike, frame, event):
    """Plays the move chosen by the user through the GUI.
    Won't be called while a CPU Player is making its decision.
    """
    
    rightToStrike.acquire()
        
    lineBtn = event.GetEventObject()
    
    ply = lineBtn.lineDots
    print(ply)
    plyManager(gameboard, rightToStrike, ply, True, frame)
    
    rightToStrike.release()        
    
def timeUp(timeout):
    """Set flag signaling timeout to CPU player."""
    timeout.set()
    
def player(gameboard, rightToStrike, playerConfig, frame):
    """Target function started on a thread for each CPU player """
        
    rightToStrike.acquire()
    
    # Wait for other player to make first move
    if (not playerConfig.movesFirst and gameboard.depth == 0):
        rightToStrike.wait()
    
    # Main CPU player loop
    while (not gameboard.gameOver()):
        
        frame.disableGameboard() # Disable GUI
                
        then = datetime.datetime.now() # For experimentation purposes

        if frame.talkingPlayers:
            printAtOnce("[%s] Player %s: now computing...\n" % (str(datetime.datetime.now()), gameboard.currentPlayer))
        
        if playerConfig.evalFunID == 0: 
            # Player generates a complete game tree
            bestMoveSoFar = decision(gameboard, IntInfinity, playerConfig, frame)
            
        else:
            # Player adopts a real-time strategy, cutting off search before terminal states and sorting non-terminal states through an evaluation function
            
            # Thread-safe flag used to signal timeout (i.e. player has no more time to make a decision)
            timeoutEvent = threading.Event()

            playerConfig.timeoutEvent = timeoutEvent

            # Start the timer before the timeout flag is set
            timer = threading.Timer(gameboard.secondsToDecide, timeUp, (timeoutEvent,))
            timer.start()
        
            # Each complete iteration will overwrite the move computed
            # by the previous, shallower, iteration
            bestMoveSoFar = None
                        
            lookAhead = 0 # Iterative deepening depth counter
        
            while (not timeoutEvent.isSet()):
            
                try:
                    # Look ahead one more level
                    lookAhead = lookAhead + 1
                
                    # No point in reiterating when the previous
                    # iteration already reached the maximum depth
                    # in the game tree
                    
                    pliesInAGame = gameboard.pliesInAGame
                    willReach = gameboard.depth + lookAhead
                
                    exceededMaxDepth = willReach > pliesInAGame
                
                    if (exceededMaxDepth):
                        timer.cancel()
                        raise ExceededMaxDepth()

                    # Compute best decision up to current depth plus lookAhead
                    line = decision(gameboard, lookAhead, playerConfig, frame)
                    bestMoveSoFar = line
                        
                except (Timeout, ExceededMaxDepth):
                    # Cleanup leftover draft lines
                    frame.clearDraftLines()
                    break

        now = datetime.datetime.now()
        took = now-then

        if frame.talkingPlayers:
            printAtOnce("[%s] Player %s: Done, took %s.\n\n" % (str(now), gameboard.currentPlayer, str(took)))
        
        # Play on board the computed ply
        plyManager(gameboard, rightToStrike, bestMoveSoFar, False, frame)

def plyManager(gameboard, rightToStrike, ply, humanPlayer, frame):
    """ Mirrors on the GUI the effects of a ply.
    When called by a CPU player, does not return until the opponent has played their turn.
    """
    
    legalPly = gameboard.strikeLine(ply)            

    if (legalPly):
        player, squaresTaken = legalPly

        for squarePosition in squaresTaken:
            frame.squareTaken(player, squarePosition)
        
        frame.updateCurrentPlayer(gameboard.currentPlayer)
        frame.updateScore(gameboard.score)

        frame.drawLine(ply)
        
        if gameboard.gameOver():
            # Game over because of caller's ply 
            frame.gameOver(winner(gameboard))
            
            if (frame.detailsOnGameover):   
                details = winner(gameboard) + ' wins.\n' + gameboard.experimentDetails()
                print(details)

            # Wake up CPU opponent so it can break out of its loop
            rightToStrike.notify()
            
            if (not humanPlayer):
                # Make GUI responsive again (basically re-enables close button)
                frame.enableGameboard()
                # Done playing
                rightToStrike.release()
                            
            if frame.quitOnGameover:
                frame.onClose(wx.EVT_CLOSE)
        else:
            # Game goes on
            
            if (gameboard.skip):
                gameboard.acknowledgeSkip()
            else:
                # Let the opponent play
                frame.enableGameboard() 

                # Wake it up if it necessary
                rightToStrike.notify()
                
                if (not humanPlayer):
                    # Wait for 
                    rightToStrike.wait()

def main(args):
    
    sideLength = args.sideLength
    secondsToDecide = args.secondsToDecide
    cpuPlayers = args.cpuPlayers
    
    wx.Log.EnableLogging(False)     

    gameboard = GameBoard(sideLength, secondsToDecide)
    rightToStrike = threading.Condition()
    
    app = wx.App()

    frame = MainWindow(sideLength)
    
    frame.quitOnGameover = args.quitOnGameover
    frame.detailsOnGameover = args.detailsOnGameover
    frame.talkingPlayers = args.talkingPlayers
    
    app.SetTopWindow(frame)

    frame.addClickHandler(lambda event: clickHandler(gameboard, rightToStrike, frame, event))

    # Initialize view
    frame.updateCurrentPlayer(gameboard.currentPlayer)
    frame.updateScore(gameboard.score)

    # Configure CPU opponents
    if (args.playerConfigA):
        # TODO: make this safe
        configA = eval(args.playerConfigA)
    else:
        configA = PlayerConfig( alphaBetaPruning=True, 
                                useHashTable=True, 
                                evalFunID=5, 
                                successorSortCriteria=None, 
                                quiescenceSearch=False
                                )

    if (args.playerConfigB):
        # TODO: make this safe
        configB = eval(args.playerConfigB)
    else:
        configB = PlayerConfig( alphaBetaPruning=True, 
                                useHashTable=True, 
                                evalFunID=4, 
                                successorSortCriteria=None, 
                                quiescenceSearch=False)

    gameboard.experimentPlayers['A'] = deepcopy(configA)
    gameboard.experimentPlayers['B'] = deepcopy(configB)

    if (cpuPlayers > 1):
        configA.movesFirst = True
        s = threading.Thread(name = "CPU Player A", target=player, args=(gameboard, rightToStrike, configA, frame))
        s.daemon = True
        s.start()
    

    if (cpuPlayers > 0):        
        t = threading.Thread(name = "CPU Player B", target=player, args=(gameboard, rightToStrike, configB, frame))
        t.daemon = True
        t.start()

        
    app.MainLoop()
        
    if payoff(gameboard) > 0:
        code = 1
    elif payoff(gameboard) < 0:
        code = 2
    else:
        code = 3
        
    exit(code)
    
if __name__ == '__main__':
    
    # TO-DO: use Python-provided argparse
    
    parser = argparse.ArgumentParser(description='The Dots and Boxes game, developed by Riccardo Angius.\nriccardo.angius@me.com')
    
    parser.add_argument('-l', '--side_length', type=int, dest='sideLength',
                        default=DEFAULT_SIDE_LENGTH,
                       help='Number of dots on each side of the gameboard.')
    
    parser.add_argument('-p', '--cpu_players', dest='cpuPlayers', type=int,
                        default=DEFAULT_CPU_PLAYERS,
                        help='Number of CPU players (min 0, max 2)')

    parser.add_argument('-s', '--seconds_to_decide', dest='secondsToDecide', type=float,
                        default=DEFAULT_SECONDS_TO_DECIDE,
                        help='Seconds allowed to each CPU player to make their decision.')

    parser.add_argument('-ca', '--player_config_a', dest='playerConfigA',
                        default="",
                        help='Configuration for Player A (first to move).')

    parser.add_argument('-cb', '--player_config_b', dest='playerConfigB',
                        default="",
                        help='Configuration for Player B (second to move).')

    parser.add_argument('-t', '--talking_players', dest='talkingPlayers', action='store_true',
                        help='Make CPU players print information about their computations.')

    parser.add_argument('-d', '--details_on_gameover', dest='detailsOnGameover', action='store_true',
                        help='Print out experiment details on gameover.')

    parser.add_argument('-q', '--quit_on_gameover', dest='quitOnGameover', action='store_true',
                       help='Exit application on gameover.')

    args = parser.parse_args()   

    main(args)