"""This is code to create and maintain a checker board."""

import random
import time
import threading

import tkinter as tk
import tkinter.messagebox
from pygame import mixer

import cfg
import checkerLogic


__author__ = "Matthew Dolinka"


def select(row, col):
    tile = cfg.boardTiles[row][col]

    if (
        cfg.activePlayer != cfg.NO_GAME_IN_PROGRESS
        and cfg.activePlayer != cfg.GAME_OVER
        and (cfg.playerType[cfg.activePlayer] == cfg.PLAYER_CPU_DUMB
        or cfg.playerType[cfg.activePlayer] == cfg.PLAYER_CPU_SMART)
        ):
        #the player should not be able to make a move while
        #the computer player is deciding a move
        return
    
    if cfg.lastSelectedItem == None and not cfg.boardIsBeingCustomized:
        cfg.lastSelectedItem = (row, col)
        updateDisplay2(
            "selected %c%d" %(chr(97+col), row+1)
            )
        tile.config(relief=cfg.SELECTED_RELIEF)

        #play sound file
        cfg.pressButtonSound.play()

    elif cfg.lastSelectedItem == None and cfg.boardIsBeingCustomized:
        #a click on any spot on the board while the board is being customized
        #will cause the tile to become whatever type the user has selected
        #in the custom game window
        
        playerSelection = cfg.customCheckersGameWindow.buttonFrame1.var.get()
        pieceSelection = cfg.customCheckersGameWindow.buttonFrame2.var.get()

        if(
            pieceSelection == cfg.CHECKER_MAN
            and ((row == 7 and playerSelection == cfg.PLAYER_1)
            or (row == 0 and playerSelection == cfg.PLAYER_2))
           ):
            #the player should not be able to place a man in a spot
            #where it cannot move
            
            #important
            deselectTile()

            errorMessage = "INVALID: you can't put a man on the wrong side"
            errorMessage += " of the board"
            updateDisplay2(errorMessage)
            cfg.errorSound.play()
            
            return

        if tile.player != cfg.UNOCCUPIED:
                #changing a tile that a player owns
                #should diminish a player's piece count
                cfg.playerPieces[tile.player] -= 1
                

        if pieceSelection != cfg.NO_PIECE:
            #filling a tile should increase a player's piece count
            cfg.playerPieces[playerSelection] += 1
            
            editTile(
                row, col,
                playerSelection, pieceSelection
                )
        else:
            #makes an empty tile
            editTile(
                row, col,
                cfg.UNOCCUPIED, pieceSelection
                )

        #sound effect for placing down a custom piece
        cfg.killSound.play()
        #important to deselect the tile so we will come here again
        deselectTile()
        
        
    elif cfg.lastSelectedItem != (row, col):
        #this code calls the logic file's makeMove
        #function with the starting row and col
        #and the destination row and col in that order
        
        #if no logic file has been imported (the game has not started)
        #then we will return and nothing will be done
        if cfg.logicFile == None:
            return

        #this will ensure that the thread does not run during the move
        #making process
        cfg.threadMode = cfg.THREAD_NO_ACTION

        cfg.logicFile.makeMove(
            cfg.lastSelectedItem[0], cfg.lastSelectedItem[1],
            row, col
            )

        #the move is over and the thread can now run
        cfg.threadMode = cfg.THREAD_MAKE_MOVE
    
    elif cfg.lastSelectedItem == (row, col):
        deselectTile()
        #play sound file
        cfg.depressButtonSound.play()

def deselectTile():
    """simply unselects a tile. Used in making a move"""
    if cfg.lastSelectedItem != None:
        target = cfg.boardTiles[cfg.lastSelectedItem[0]][cfg.lastSelectedItem[1]]
    
        cfg.lastSelectedItem = None
        target.config(relief=cfg.UNSELECTED_RELIEF)
        
    updateDisplay2(cfg.DEFAULT_DISPLAY_2_TEXT)
        

def editTile(row, col, player, pieceType):
        currTile = cfg.boardTiles[row][col]
        
        color = -1
        
        if player == cfg.PLAYER_1:
            currTile.player = cfg.PLAYER_1
            color = cfg.PLAYER_1_COLOR
        elif player == cfg.PLAYER_2:
            currTile.player = cfg.PLAYER_2
            color = cfg.PLAYER_2_COLOR
        elif player == cfg.UNOCCUPIED:
            currTile.player = cfg.UNOCCUPIED
            color = cfg.boardTiles[row][col].defaultColor
        elif color == -1:
            updateDisplay1("error editing tile")
            return

        if pieceType == cfg.CHECKER_KING:
            currTile.config(text="king")
        else:
            currTile.config(text="")

        currTile.pieceType = pieceType
            
        currTile.config(bg=color)
        


class Tile(tk.Button):
    """a tile is basically a button with an extra variable
that tells you who the piece belongs to. Also the default color
of the peice is saved if it needs to be reset"""
    
    def __init__(self, parent, color, width, height, relief, command):
        tk.Button.__init__(
            self, parent, bg=color, width=width, height=height,
            relief=relief, command=command
            )
        self.player = cfg.UNOCCUPIED
        self.pieceType = cfg.NO_PIECE
        self.defaultColor = color
        

class TileFrame(tk.Frame):

    def __init__(self, parent=None, isColor1=True, numTiles=0, fillMe=[],
                 row=0):
        tk.Frame.__init__(self, parent)

        if isColor1:
                tileColor = cfg.COLOR_2
        else:
                tileColor = cfg.COLOR_1

        for i in range(numTiles):
            #the color of the tiles alternates
            if tileColor == cfg.COLOR_2:
                tileColor = cfg.COLOR_1
            else:
                tileColor = cfg.COLOR_2

            command = lambda r=row, c=i: select(r, c)

            
            tile = Tile(self, tileColor,
                        cfg.TILE_WIDTH, cfg.TILE_HEIGHT,
                        cfg.UNSELECTED_RELIEF, command,
                        )
            
            tile.pack(side="left")
            fillMe.append(tile)


def endGame():

    cfg.playerType[cfg.PLAYER_1] = cfg.PLAYER_UNDEFINED
    cfg.playerType[cfg.PLAYER_2] = cfg.PLAYER_UNDEFINED
    cfg.gameType = cfg.GAME_UNDEFINED

    cfg.activePlayer = cfg.nonActivePlayer = cfg.NO_GAME_IN_PROGRESS

    #if any tile is already selected then deselect
    if cfg.lastSelectedItem != None:
        deselectTile()
    
    cfg.delayTime = cfg.DEFAULT_DELAY

    cfg.playerPieces[cfg.PLAYER_1] = 0
    cfg.playerPieces[cfg.PLAYER_2] = 0

    cfg.obligatedPieces[cfg.PLAYER_1] = []
    cfg.obligatedPieces[cfg.PLAYER_2] = []

    cfg.logicFile = None

    updateDisplay1(cfg.DEFAULT_DISPLAY_1_TEXT)
    
    cfg.root.title(cfg.DEFAULT_ROOT_TITLE_TEXT)
    
    cfg.root.gameButton.config(
        text=cfg.START_GAME_BUTTON_TEXT,
        command=cfg.root.askGameInfo
        )
    
    #clear the tiles on the board to default settings
    for row in range(len(cfg.boardTiles)):
        for tile in cfg.boardTiles[row]:
            tile.player = cfg.UNOCCUPIED
            tile.pieceType = cfg.NO_PIECE

            tile.config(text="", bg=tile.defaultColor,
                        relief=cfg.UNSELECTED_RELIEF)

def makeThreadEndGame():
    """tells the computer player thread to end the game"""
    
    if not tk.messagebox.askokcancel(
        "end game?", "do you wish to end the game"
        ):
        #if the user changes their mind don't exit
        return
    
    cfg.threadMode = cfg.THREAD_EXIT_GAME
    

def startGame(gameMode, player1Mode, player2Mode, delayTime, firstPlayer):
    """Sets up the game. The logicFile variable points to the file that
is being used to compute the moves"""

    #the game button is repurposed to end the game when pressed
    #TELLS THE THREAD TO END THE GAME (makes the thread call the
    #end game function)
    cfg.root.gameButton.config(
        text=cfg.END_GAME_BUTTON_TEXT,
        command=makeThreadEndGame
        )
    

    #the logic file for the appropriate game is imported
    if gameMode == cfg.GAME_CHECKERS:
        cfg.logicFile = checkerLogic
        cfg.root.title(cfg.CHECKERS_NAME)
        
    elif gameMode == cfg.GAME_CHESS:
        #not yet implemented
        try:
            cfg.logicFile = chessLogic
            cfg.root.title(cfg.CHESS_NAME)
        except:
            updateDisplay1("CHESS is not yet implemented")
            return
        

    if(gameMode == cfg.GAME_UNDEFINED or player1Mode == cfg.PLAYER_UNDEFINED
       or player2Mode == cfg.PLAYER_UNDEFINED
       or firstPlayer == cfg.PLAYER_UNDEFINED):
        #this should never happen
        print("selection error")
        return
    else:
        cfg.gameType = gameMode
        cfg.playerType[cfg.PLAYER_1] = player1Mode
        cfg.playerType[cfg.PLAYER_2] = player2Mode
        cfg.delayTime = delayTime
        

    #the board is set up for the selected game and difficulty
    cfg.logicFile.populateBoard()

    #set the initial player randomly if necessary
    if firstPlayer != cfg.RANDOM_PLAYER:
        if firstPlayer == cfg.PLAYER_1:
            cfg.activePlayer = cfg.PLAYER_1
            cfg.nonActivePlayer = cfg.PLAYER_2
        elif firstPlayer == cfg.PLAYER_2:
            cfg.activePlayer = cfg.PLAYER_2
            cfg.nonActivePlayer = cfg.PLAYER_1
        
    else:
        random.seed(a=None, version=2)
        #returns either 0 or 1
        randomVal = random.randrange(2)

        if randomVal == 0:
            cfg.activePlayer = cfg.PLAYER_1
            cfg.nonActivePlayer = cfg.PLAYER_2
        elif randomVal == 1:
            cfg.activePlayer = cfg.PLAYER_2
            cfg.nonActivePlayer = cfg.PLAYER_1

    #if any tile is already selected then deselect
    if cfg.lastSelectedItem != None:
        deselectTile()

    displayActivePlayer()

    #allow the thread to excecute moves
    cfg.threadMode = cfg.THREAD_MAKE_MOVE


    
    

def updateDisplay1(displayMe):
    cfg.root.display1.config(text=displayMe)

def updateDisplay2(displayMe):
    cfg.root.display2.config(text=displayMe)
    

def displayActivePlayer():
    """updates the display with who is the active player, usually
done between rounds"""
    
    if cfg.activePlayer == cfg.NO_GAME_IN_PROGRESS:
        updateDisplay1(cfg.DEFAULT_DISPLAY_1_TEXT)
    elif cfg.activePlayer == cfg.PLAYER_1:
        updateDisplay1("player one's turn")
    elif cfg.activePlayer == cfg.PLAYER_2:
        updateDisplay1("player two's turn")



##tk instances
class RadiobuttonFrame(tk.Frame):
    def __init__(self, parent=None, labelText="", options=[]):
        """The labelText parameter is for the leftmost text label of the frame.
The parameter options is a list of tuples of the form:
(button text, value of button)"""
        
        tk.Frame.__init__(self, parent)
        
        self.label = tk.Label(
            self, text=labelText, font=("Calibri", 10, "bold")
            )
        self.label.pack(side="left")

        #all the buttons share this variable
        self.var = tk.IntVar(self)
        #a list of all the radiobuttons in the frame
        self.buttons = []

        for option in options:
            curr = tk.Radiobutton(
                self, text=option[0], variable=self.var,
                value=option[1]
                )
            curr.pack(side="left")
            self.buttons.append(curr)
            


class CustomCheckersGameWindow(tk.Toplevel):
    """this is the window that is used to customize a checkers game board to
the player's liking if they so desire."""
    
    def __init__(self, parent=None):
        
        tk.Toplevel.__init__(self, parent)

        self.geometry("250x140+600+200")
        
        self.title("custom game designer")

        self.openingText = tk.Label(
            self, anchor="center",
            text="""Please select the settings for the piece,
then select anywhere on the board to place it"""
            )
        self.openingText.pack(pady=(2,5))

        self.buttonFrame1 = RadiobuttonFrame(
            self, labelText="pick a player",
            options=[
                ("player 1", cfg.PLAYER_1),
                ("player 2", cfg.PLAYER_2)
                ]
            )
        self.buttonFrame1.var.set(cfg.PLAYER_1)
        self.buttonFrame1.pack()

        self.buttonFrame2 = RadiobuttonFrame(
            self, labelText="pick a piece",
            options=[
                ("man", cfg.CHECKER_MAN),
                ("king", cfg.CHECKER_KING),
                ("empty", cfg.NO_PIECE)
                ]
            )
        self.buttonFrame2.var.set(cfg.CHECKER_MAN)
        self.buttonFrame2.pack()

        self.button = tk.Button(
            #this button will be used to start the game
            self, text=cfg.START_GAME_BUTTON_TEXT,
            command=cfg.startGameWindow.callStartGame
            )
        self.button.pack(pady=(4, 3))
        

        
#this is the window that starts up when the player wants to start a game
class StartGameWindow(tk.Toplevel):
    def __init__(self, parent=None):
        tk.Toplevel.__init__(self, parent)

        self.title("game settings")
        #window will not be resized or maximized
        self.resizable(width=False, height=False)

        self.dialogue = tk.Label(
            self,
            text="Game Setup",
            font=("Calibri", 14)
            )
        self.dialogue.pack(pady=(0,5))

        #the padding and anchor for the question frames
        padding = (2, 0)
        anchor = "center"
        
        #set up the radio buttons for choosing the game type
        #(ex: chess or checkers)
        self.gameChoiceFrame = RadiobuttonFrame(
            parent=self, labelText="choose a game type:",
            options=[("checkers", cfg.GAME_CHECKERS), ("chess", cfg.GAME_CHESS)]
            )
        self.gameChoiceFrame.var.set(cfg.GAME_CHECKERS)
        self.gameChoiceFrame.pack(padx=padding, anchor=anchor)
        

        #set up the radio buttons for choosing player 1
        self.player1ChoiceFrame = RadiobuttonFrame(
            parent=self, labelText="player 1:",
            options=[
                ("human", cfg.PLAYER_HUMAN),
                ("dumb cpu", cfg.PLAYER_CPU_DUMB),
                ("smart cpu", cfg.PLAYER_CPU_SMART)
                     ]
            )
        self.player1ChoiceFrame.var.set(cfg.PLAYER_HUMAN)
        self.player1ChoiceFrame.pack(padx=padding, anchor=anchor)

        
        #set up the radio buttons for choosing player 2
        self.player2ChoiceFrame = RadiobuttonFrame(
            parent=self, labelText="player 2:",
            options=[
                ("human", cfg.PLAYER_HUMAN),
                ("dumb cpu", cfg.PLAYER_CPU_DUMB),
                ("smart cpu", cfg.PLAYER_CPU_SMART)
                     ]
            )
        self.player2ChoiceFrame.var.set(cfg.PLAYER_HUMAN)
        self.player2ChoiceFrame.pack(padx=(5,0), anchor="w")
        
        
        #ask who plays first
        self.firstPlayerChoiceFrame = RadiobuttonFrame(
            parent=self, labelText="who plays first?",
            options=[
                ("player 1", cfg.PLAYER_1),
                ("player 2", cfg.PLAYER_2),
                ("random", cfg.RANDOM_PLAYER)
                     ]
            )
        self.firstPlayerChoiceFrame.var.set(cfg.PLAYER_1)
        self.firstPlayerChoiceFrame.pack(padx=padding, anchor=anchor)
        

        #ask if the user wants a custom board
        #ask who plays first
        self.customGameChoiceFrame = RadiobuttonFrame(
            parent=self, labelText="do you want a custom board?",
            options=[
                ("yes", cfg.CUSTOM_BOARD),
                ("no", cfg.DEFAULT_BOARD)
                ]
            )
        self.customGameChoiceFrame.var.set(cfg.DEFAULT_BOARD)
        self.customGameChoiceFrame.pack(padx=padding, anchor=anchor)



        #slider for selecting the delay on a cpu's move
        self.delayText = tk.Label(self,
                             text="select computer player delay (seconds):")
        
        self.delayText.pack(pady=(6,0))


        self.delaySliderFrame = tk.Frame(self)
        self.delaySliderFrame.pack(pady=(0,10))

        self.delaySlider = tk.Scale(
            self.delaySliderFrame,
            from_=0, to=2,
            resolution = 0.1,
            orient=tk.HORIZONTAL
            )
        self.delaySlider.pack(side="left")
        self.delaySlider.set(cfg.DEFAULT_DELAY)



        self.finalButton = tk.Button(
            self, text=cfg.START_GAME_BUTTON_TEXT,
            command=self.customizeBoard
            )
        
        self.finalButton.pack(pady=(0,5))

    def customizeBoard(self):
        """either sets up the game for a custom game or starts the game as
        a standard board"""
        
        self.withdraw()

        decision = self.customGameChoiceFrame.var.get()
        
        if decision == cfg.CUSTOM_BOARD:
            #setup the board to be customized

            #the root's start game button will now start the game
            #just like the customCheckersGameWindow' start game button.
            #Clicking either button on each window will start the game
            cfg.root.gameButton.config(
                command=self.callStartGame
            )

            cfg.boardIsBeingCustomized = True

            updateDisplay2(cfg.CUSTOMIZING_BOARD_TEXT)
            
            cfg.customCheckersGameWindow.deiconify()
            
        elif decision == cfg.DEFAULT_BOARD:
            #go ahead and start the game
            
            self.callStartGame()
        else:
            updateDisplay1("customize board error")
            


    def callStartGame(self):
        """grabs the values of all the windows settings and calls
            startGame() with them"""

        #it is invalid if the player tries to start a custom game
        #where any one player does not have any pieces
        if (
            cfg.boardIsBeingCustomized
            and (cfg.playerPieces[cfg.PLAYER_1] == 0
            or cfg.playerPieces[cfg.PLAYER_2] == 0)
            ):

            errorMessage = "INVALID: please give every player"
            errorMessage += " at least one piece"
            updateDisplay2(errorMessage)
            cfg.errorSound.play()
            return

        #in case this window is open
        cfg.customCheckersGameWindow.withdraw()
        #cfg.boardIsBeingCustomized is set to false in populateBoard
            
        
        startGame(
                self.gameChoiceFrame.var.get(),
                self.player1ChoiceFrame.var.get(),
                self.player2ChoiceFrame.var.get(),
                self.delaySlider.get(),
                self.firstPlayerChoiceFrame.var.get()
                )

        


class Root(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.title(cfg.DEFAULT_ROOT_TITLE_TEXT)
        self.config(bg=cfg.WINDOW_COLOR)

        #window will not be resized or maximized
        self.resizable(width=False, height=False)

        #set up top dashboards
        self.dashboard1 = tk.Frame(bg=cfg.DISPLAY_COLOR)
        self.dashboard1.pack(expand=1, fill=tk.BOTH)
        self.dashboard2 = tk.Frame(bg=cfg.DISPLAY_COLOR)
        self.dashboard2.pack(expand=1, fill=tk.BOTH)

        #set up the two displays. The top display is for displaying
        #the current player
        self.display1 = tk.Label(
            self.dashboard1, text=cfg.DEFAULT_DISPLAY_1_TEXT,
            bg=cfg.DISPLAY_COLOR
            )
        self.display1.pack()
        
        self.display2 = tk.Label(
            self.dashboard2, text=cfg.DEFAULT_DISPLAY_2_TEXT,
            bg=cfg.DISPLAY_COLOR
            )
        self.display2.pack()

        #frames is where the frames for the tiles are kept
        cfg.frames = []
        
        isColor1 = True
        for i in range(cfg.NUM_ROWS):
            if i % 2 == 0:
                isColor1 = True
            else:
                isColor1 = False
                
            tilesInFrame = []
                
            cfg.frames.append(
                TileFrame(
                    self, isColor1, cfg.NUM_COLS, tilesInFrame,
                    cfg.NUM_ROWS - i - 1
                    )
                )
            cfg.frames[i].pack()
            cfg.boardTiles.append(tilesInFrame)

        #the reverse is so that the grid works like a cartesian plane
        #with y=0 at bottom
        cfg.frames.reverse()
        cfg.boardTiles.reverse()
        

        #set up bottom dashboard
        self.bottomDashboard = tk.Frame(bg=cfg.WINDOW_COLOR)
        self.bottomDashboard.pack()

        #start game button
        self.gameButton = tk.Button(
            self.bottomDashboard, text=cfg.START_GAME_BUTTON_TEXT,
            command=self.askGameInfo, bg=cfg.WINDOW_COLOR
            )
        self.gameButton.pack(pady=(10,5))

    def askGameInfo(self):
        """Opens the settings window and requests info from the
        user to set up the game."""
        
        cfg.startGameWindow.deiconify()
        
        

def computerLoop():
    """continually checks whether it is the computer's turn to play.
Will sleep according to how long the user desires before calling in
the computer move"""

    while True:
        
        if (
            cfg.threadMode == cfg.THREAD_MAKE_MOVE
            and
            (cfg.activePlayer == cfg.PLAYER_1
            or cfg.activePlayer == cfg.PLAYER_2)
            and
            (cfg.playerType[cfg.activePlayer] == cfg.PLAYER_CPU_DUMB
            or cfg.playerType[cfg.activePlayer] == cfg.PLAYER_CPU_SMART)
            ):
            time.sleep(cfg.delayTime)
            cfg.logicFile.computeComputerMove()

        if cfg.threadMode == cfg.THREAD_EXIT_GAME:
            #the thread resets itself then calls to exit the game
            cfg.threadMode = cfg.THREAD_NO_ACTION
            endGame()
            


def main():
    cfg.root = Root()

    #the window that is used to ask the user for game info
    cfg.startGameWindow = StartGameWindow(cfg.root)
    cfg.startGameWindow.protocol(
        'WM_DELETE_WINDOW',
        lambda: cfg.startGameWindow.withdraw()
        )
    cfg.startGameWindow.withdraw()
    

    #create the custom game board menu
    cfg.customCheckersGameWindow = CustomCheckersGameWindow(cfg.root)
    
    #closing this window will start the game
    cfg.customCheckersGameWindow.protocol(
        'WM_DELETE_WINDOW',
        lambda: cfg.startGameWindow.callStartGame()
        )
    cfg.customCheckersGameWindow.withdraw()
    

    #this is the thread that will make computer moves
    cfg.threadCanRun = False
    cfg.compThread = threading.Thread(target=computerLoop)
    cfg.threadMode = cfg.THREAD_NO_ACTION
    cfg.compThread.start()

    
    
    cfg.root.mainloop()

    
    

if __name__ == "__main__":
    main()



