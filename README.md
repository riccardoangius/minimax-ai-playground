The Dots and Boxes game with a sprinkle of AI with Minimax , developed by Riccardo Angius. riccardo.angius@me.com

This app was developed and tested on OS X 10.9, Python 3.7, depending on python modules NetworkX 2 and WxPython 4.

Riccardo Angius
riccardo.angius@me.com

Features:
1. Multiplayer game
2. Naive Minimax Agent
3. Pruning, cutoff and ply evaluatio
5. Transposition table
6. Successor soting
7. Backtracking search
8. Iterative deepening search
9. Real-time
10. Quiescence search


Running:

`python controller.py`

Usage: 
`python controller.py [-h] [-l SIDELENGTH] [-p CPUPLAYERS] [-s SECONDSTODECIDE] [-ca PLAYERCONFIGA] [-cb PLAYERCONFIGB] [-t] [-d] [-q]`

  
optional arguments:

```
-h, --help  show help message and exit

-l SIDELENGTH, --side_length SIDELENGTH

Number of dots on each side of the gameboard.

-p CPUPLAYERS, --cpu_players CPUPLAYERS

Number of CPU players (min 0, max 2)

-s SECONDSTODECIDE, --seconds_to_decide SECONDSTODECIDE

Seconds allowed to each CPU player to make their

decision.

-ca PLAYERCONFIGA, --player_config_a PLAYERCONFIGA

Configuration for Player A (first to move).

-cb PLAYERCONFIGB, --player_config_b PLAYERCONFIGB

Configuration for Player B (second to move).

-t, --talking_players

Make CPU players print information about their

computations.

-d, --details_on_gameover

Print out experiment details on gameover.

-q, --quit_on_gameover

Exit application on gameover.
```