#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Università degli Studi di Padova
# Corso di Laurea Magistrale in Informatica
# 
# common.py

import sys

# Default gameboard side length (in dots)
DEFAULT_SIDE_LENGTH = 3

DEFAULT_SECONDS_TO_DECIDE = 1.0

SQUARE_TAKER_PLAYS_AGAIN = True

DEFAULT_CPU_PLAYERS = 2
MAX_CPU_PLAYERS = 2

QUIESCENCE_BONUS = 2

PLAYER_A = 'A'
PLAYER_B = 'B'
NoPlayer = 'O'

Infinity = float("infinity")
IntInfinity = sys.maxsize

SQUARE_A = 'includes/squareA.png'
SQUARE_B = 'includes/squareB.png'

def printAtOnce(text):
    print (text)
    sys.stdout.flush()

def row(i_j):
    i, j = i_j

    return i

def col(i_j):
    i, j = i_j

    return j

def count(x):
    return len(x)

def revPair(i_j):
    i, j = i_j
    return (j,i)

def pairSum(a_b,c_d):
    a, b = a_b
    c, d = c_d
    return (a+c,b+d)
    
def struck(line):
    return (not unstruck(line))

def unstruck(line):
    return line['taker'] == NoPlayer 

def payoff(gameboard):
    return gameboard.score[PLAYER_A] - gameboard.score[PLAYER_B]    
    
def winner(gameboard):
    if payoff(gameboard) == 0:
        return "Nobody"
    elif payoff(gameboard) > 0:
        return "Player A"
    else:
        return "Player B"

class Timeout(Exception):
    pass
    
class ExceededMaxDepth(Exception):
    pass