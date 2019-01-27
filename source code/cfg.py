"""This file has the variables that are meant to be shared between the files
in the module

Variables in all caps are constants and should not be changed.
Other variables are free to change."""

import tkinter as tk
from pygame import mixer

#colors
COLOR_1 = "wheat1"
COLOR_2 = "tan4"
PLAYER_1_COLOR = "red"
PLAYER_2_COLOR = "blue"

#tile height and width
TILE_WIDTH = 8
TILE_HEIGHT = 4

#Board size
NUM_COLS = 8
NUM_ROWS = 8

#reliefs
SELECTED_RELIEF = tk.SUNKEN
UNSELECTED_RELIEF = tk.FLAT

#the color of the top dashboard where the displays are
WINDOW_COLOR = "snow"
DISPLAY_COLOR = "gray80"

#display strings
DEFAULT_DISPLAY_1_TEXT = "no game in progress"
DEFAULT_DISPLAY_2_TEXT = "nothing selected"

DEFAULT_ROOT_TITLE_TEXT = "select a game"

START_GAME_BUTTON_TEXT = "Start Game"
END_GAME_BUTTON_TEXT ="End Game"

INVALID_MOVE = "INVALID MOVE"

CUSTOMIZING_BOARD_TEXT = "customizing the game board"

#tk windows/gui
root = None

startGameWindow = None

customCheckersGameWindow = None


#this is the imported file that will be used to populate the board and
#make moves using the populateBoard() and makeMove() functions
#this file is imported in main.py based on the user's choice of game
logicFile = None


#the thread used to run the computer player
compThread = None

#signals what the thread should do, ie. make a move or
#exit the game it should perform another task like exit the game
THREAD_NO_ACTION = 0
THREAD_MAKE_MOVE = 1
THREAD_EXIT_GAME = 2

threadMode = THREAD_NO_ACTION



#the delay between each action by any cpu player
DEFAULT_DELAY = .5
delayTime = DEFAULT_DELAY

#game names, use these when you need to name the game
CHECKERS_NAME = "checkers"
CHESS_NAME = "chess"


#custom board generator stuff
DEFAULT_BOARD = 0
CUSTOM_BOARD = 1

boardIsBeingCustomized = False



#Game types
GAME_UNDEFINED = 0
GAME_CHECKERS = 1
GAME_CHESS = 2

#this variable can be used to assertain the game type
gameType = GAME_UNDEFINED



#every tile on the board belongs to a player (or not)
UNOCCUPIED = NO_GAME_IN_PROGRESS = 0
GAME_OVER = -1
PLAYER_1 = 1
PLAYER_2 = 2
RANDOM_PLAYER = 3

#shows which player should be alowed to move currently
activePlayer = NO_GAME_IN_PROGRESS
nonActivePlayer = NO_GAME_IN_PROGRESS

#the number of pieces that each player has on the board
playerPieces = {PLAYER_1: 0, PLAYER_2: 0}


#the maximum amount of pieces that any one player can have active in a game
CHECKERS_MAX_PIECES = 12
CHESS_MAX_PIECES = 16


#these are the types of pieces in the game, in many game modes the
#piece name is displayed on the tile
NO_PIECE = 0
CHECKER_MAN = 1
CHECKER_KING = 2

CHESS_PAWN = 3
CHESS_ROOK = 4


#Player types, dumb and smart are for the computer player
PLAYER_UNDEFINED = 0
PLAYER_HUMAN = 1
PLAYER_CPU_DUMB = 2
PLAYER_CPU_SMART = 3

#this is used to tell what type of player is (usually the active player)
playerType = {PLAYER_1: PLAYER_UNDEFINED, PLAYER_2: PLAYER_UNDEFINED}



#this is used as a tuple with the form (row, column) to record the last
#selected tile
lastSelectedItem = None

#these are used by the checker game logic
inKillChain = False
#this is a tuple that represents the piece that has to complete the kill chain
chainKiller = None

#these are pieces that could attack for each player.
#The rules require that a player attack if any round if they are able
#the lists contain tuples with the form (row, col)
obligatedPieces = {PLAYER_1: [], PLAYER_2: []}


#a 2d list that has every tile on the board
boardTiles = []

#the tkinter frames that hold all the tiles in the game
frames = []

#sounds
mixer.init(44100)
pressButtonSound = mixer.Sound("sounds/pressButtonSound.wav")
depressButtonSound = mixer.Sound("sounds/depressButtonSound.wav")
errorSound = mixer.Sound("sounds/errorSound.wav")
killSound = mixer.Sound("sounds/killSound.wav")
moveSound = mixer.Sound("sounds/moveSound.wav")

#sounds not currently used
menuButtonSound = mixer.Sound("sounds/menuButtonSound.wav")
