"""This file contains two functions used to run a game of checkers."""

import random
import time
from pygame import mixer
import checkerboard as chb
import cfg

def invalidMoveResponse():
    """lets the player know they have made an invalid move"""
    chb.deselectTile()
    chb.updateDisplay2(cfg.INVALID_MOVE)
    cfg.errorSound.play()
    return False

def pleaseFinishChainResponse():
    """the piece's color will be changed so that the player
knows what the correct piece to move is"""
    colorMe = cfg.boardTiles[cfg.chainKiller[0]][cfg.chainKiller[1]]
    colorMe.config(bg="yellow")

    chb.deselectTile()
    
    chb.updateDisplay2("INVALID: you must kill with this piece")
    cfg.errorSound.play()
    return False

def pleaseHandleObligatedPieces():
    """lets the player know that they have to attack this round.
Highlights all pieces that could attack with"""

    chb.deselectTile()
    chb.updateDisplay2("INVALID: you must attack")
    cfg.errorSound.play()

    for coords in cfg.obligatedPieces[cfg.activePlayer]:
        curr = cfg.boardTiles[coords[0]][coords[1]]
        curr.config(bg="yellow")
        
        
    return False

def unhighlightPieces():
    """returns all pieces that were highlighted (obligated pieces)
to their own team color"""
    
    for coords in cfg.obligatedPieces[cfg.PLAYER_1]:
        curr = cfg.boardTiles[coords[0]][coords[1]]
        curr.config(bg=cfg.PLAYER_1_COLOR)

    for coords in cfg.obligatedPieces[cfg.PLAYER_2]:
        curr = cfg.boardTiles[coords[0]][coords[1]]
        curr.config(bg=cfg.PLAYER_2_COLOR)
            

def declareWinner(winner, looserResigned=False):
    winText = " wins"
    if winner == cfg.PLAYER_1:
        winText = "player one" + winText
    elif winner == cfg.PLAYER_2:
        winText = "player two" + winText
    else:
        winText = "win calculation error"

    if looserResigned:
        winText = "oppenent resigns... " + winText
        
    chb.updateDisplay1(winText)
    cfg.activePlayer = cfg.GAME_OVER

def shouldIBeKing(row, col):
    """determines if the passed in piece should be a king and
if so makes the piece a king"""
    
    kingCandidate = cfg.boardTiles[row][col]
    
    if kingCandidate.pieceType == cfg.CHECKER_KING:
        return False

    if row == 7 and kingCandidate.player == cfg.PLAYER_1:
        chb.editTile(row, col, cfg.PLAYER_1, cfg.CHECKER_KING)
        return True

    if row == 0 and kingCandidate.player == cfg.PLAYER_2:
        chb.editTile(row, col, cfg.PLAYER_2, cfg.CHECKER_KING)
        return True

    return False

def whereCanIKill(row, col, player, pieceType):
    """Checks if the piece in the current space can kill. Returns a list
of tuples each with a row and a column indicating what moves the player
could take to kill with the current location. The player parameter is for
who the attacking piece belongs to. The piece type is the player var
lets the function know ifthe piece is a king or not.
The space on the board does not actually have to have a piece on it
for the calculation to be done."""

    killMoves = []

    board=cfg.boardTiles
    
    isKing = True if pieceType == cfg.CHECKER_KING else False
    
    enemy = 0
    if player == cfg.PLAYER_1:
        enemy = cfg.PLAYER_2
    else:
        enemy = cfg.PLAYER_1
    
    if (
        (isKing or player == cfg.PLAYER_1) and row != 6 and row != 7
        ):
       #checks if can attack upwards
        #check left
        if (
            col != 0 and col != 1
            and board[row+1][col-1].player == enemy
            and board[row+2][col-2].player == cfg.UNOCCUPIED
            ):
            #we dont wanna check col = 0 and 1 because it will go out of bounds
            killMoves.append((row+2, col-2))

        #check right
        if (
            col != 6 and col != 7
            and board[row+1][col+1].player == enemy
            and board[row+2][col+2].player == cfg.UNOCCUPIED
            ):
            #we dont wanna check col = 6 and 7 because it will go out of bounds
            killMoves.append((row+2, col+2))

    if (
        (isKing or player == cfg.PLAYER_2) and (row != 0 and row != 1)
        ):
        #checks if can attack downwards
        if (
            col != 0 and col != 1
            and board[row-1][col-1].player == enemy
            and board[row-2][col-2].player == cfg.UNOCCUPIED
            ):
            killMoves.append((row-2, col-2))

        if (
            col != 6 and col != 7
            and board[row-1][col+1].player == enemy
            and board[row-2][col+2].player == cfg.UNOCCUPIED
            ):
            killMoves.append((row-2, col+2))

    return killMoves


def whereCanIMove(row, col, player, pieceType):
    """Checks if the piece in the current space can move. Returns a list
of tuples each with a row and a column indicating what places the player
could move to with the current location. The player parameter is for
who the moving piece belongs to. The piece type is the player var
lets the function know ifthe piece is a king or not.
The space on the board does not actually have to have a piece on it
for the calculation to be done."""
    
    moves = []

    board=cfg.boardTiles
    
    isKing = True if pieceType == cfg.CHECKER_KING else False
    
    if (isKing or player == cfg.PLAYER_1) and row != 7:
       #checks if can attack upwards
        #check left
        if (
            col != 0
            and board[row+1][col-1].player ==  cfg.UNOCCUPIED
            ):
            moves.append((row+1, col-1))

        #check right
        if (
            col != 7
            and board[row+1][col+1].player == cfg.UNOCCUPIED
            ):
            moves.append((row+1, col+1))

    if (isKing or player == cfg.PLAYER_2) and row != 0:
        #checks if can attack downwards
        if (
            col != 0
            and board[row-1][col-1].player == cfg.UNOCCUPIED
            ):
            moves.append((row-1, col-1))

        if (
            col != 7
            and board[row-1][col+1].player == cfg.UNOCCUPIED
            ):
            moves.append((row-1, col+1))

    return moves


def checkForObligatedPieces(player):
    """checks for any pieces for this player that can attack now"""
    for row in range(len(cfg.boardTiles)):
        for col, tile in enumerate(cfg.boardTiles[row]):
            if (
                tile.player == player
                and len(whereCanIKill(
                    row, col, tile.player, tile.pieceType)) != 0
                ):
                    cfg.obligatedPieces[player].append((row, col))


def mustIResign(player):
    """Checks if all of the active player's pieces cannot move.
If so then this function ends the game and calls declareWinner with
the non-resigned player."""
    
    for row in range(len(cfg.boardTiles)):
        for col, tile in enumerate(cfg.boardTiles[row]):
            
            if (
                tile.player == player
                and (
                    len(whereCanIMove(
                    row, col, cfg.activePlayer, tile.pieceType)) != 0
                or 
                    len(whereCanIKill(
                    row, col, cfg.activePlayer, tile.pieceType)) != 0
                    )
                ):
                #if a piece has been found that can move or kill,
                #return, do not declare a winner
                return
            
    declareWinner(cfg.nonActivePlayer, looserResigned=True)
        

                
def populateBoard():
    """sets up a checker game for play. Places checker pieces
on the board"""

    if cfg.boardIsBeingCustomized:
        #if the board is custom then there is no need to set it up
        #for a standard game
        cfg.boardIsBeingCustomized = False
        return

    magicNumber = int(cfg.NUM_ROWS/2 - 1)
    
    #populate bottom of board (player 1)
    for row in range(magicNumber):
        for col in range(cfg.NUM_COLS):
            if col % 2 == row % 2:
                chb.editTile(row, col, cfg.PLAYER_1, cfg.CHECKER_MAN)
    cfg.playerPieces[cfg.PLAYER_1] = cfg.CHECKERS_MAX_PIECES

    #populate bottom of board (player 2)
    for row in range(cfg.NUM_ROWS - magicNumber, cfg.NUM_ROWS):
        for col in range(cfg.NUM_COLS):
            if col % 2 == row % 2:
                chb.editTile(row, col, cfg.PLAYER_2, cfg.CHECKER_MAN)
    cfg.playerPieces[cfg.PLAYER_2] = cfg.CHECKERS_MAX_PIECES

def makeMove(row1, col1, row2, col2):
    """Computes whether a move is valid and if so makes the move.
This function returns False if the move is not valid (and nothing was done)
and True if the move was valid and an action was completed.
row1 and col1 are for the initial tile and row2, col2 are for the
destination tile

If a piece can jump another piece after a jump it has to immediately.
The game will not allow the player to select any piece but this"""
    
    curr = cfg.boardTiles[row1][col1]
    dest = cfg.boardTiles[row2][col2]

    if cfg.activePlayer == cfg.GAME_OVER:
        #no moves can be made during game over
        return False

    
    #unhighlights any pieces that might have been earlier highlighted
    if len(cfg.obligatedPieces[cfg.activePlayer]) != 0:
        unhighlightPieces()

                    

    if curr.player != cfg.activePlayer:
        return invalidMoveResponse()
    

    if curr.pieceType != cfg.CHECKER_KING:
        #the king can move in any direction
        if cfg.activePlayer == cfg.PLAYER_1 and row1 >= row2:
            #player 1 may not move backwards or on the same row
            return invalidMoveResponse()

        if cfg.activePlayer == cfg.PLAYER_2 and row2 >= row1:
            #player 2 may not move backwards or on the same row
            return invalidMoveResponse()

    if abs(row2 - row1) != abs(col2 - col1):
        #non diagonal movement is invalid
        return invalidMoveResponse()

    if abs(row2 - row1) > 2:
        #the player should never be able to move more than 2 tiles
        #at a time
        return invalidMoveResponse()

    if dest.player != cfg.UNOCCUPIED:
        #if the destination is already occupied
        return invalidMoveResponse()


    if cfg.inKillChain:
        #if a player can immediately make another killing jump they
        #have to and they can only move the same piece
        if row1 != cfg.chainKiller[0] or col1 != cfg.chainKiller[1]:
            #if the player has attempted to move another piece
            #during a jump chain
            return pleaseFinishChainResponse()
        if abs(row2 - row1) == 1:
            #the move has to be a killing move, a move of one
            #space is never a killing move
            return pleaseFinishChainResponse()
        


    #must make sure that the user atacks if they can.
    #the obligated pieces are pieces that can attack
        
    if len(cfg.obligatedPieces[cfg.activePlayer]) != 0 and not cfg.inKillChain:
        if(row1, col1) not in cfg.obligatedPieces[cfg.activePlayer]:
            #the player must use a piece that can kill
            return pleaseHandleObligatedPieces()
        if abs(row2 - row1) == 1:
            #a nonkilling move in invalid
            return pleaseHandleObligatedPieces()
            

    

    #now that we have only two cases: where the move is one space
    #or the move is a two space killing move
        
    if abs(row2 - row1) == 1:
        #perform the move
        #
        #depress the current tile
        chb.deselectTile()
        chb.editTile(row2, col2, cfg.activePlayer, curr.pieceType)
        chb.editTile(row1, col1, cfg.UNOCCUPIED, cfg.NO_PIECE)

        cfg.moveSound.play()

        #checks if the piece is now qualified to become a king
        shouldIBeKing(row2, col2)


    if abs(row2 - row1) == 2:
        #the game has to check that the player is actually killing another
        #piece if they make a two space jump
        #the midTile is the tile between curr and dest
        midTile = None
        midRow = 0
        midCol = 0
        if row2 - row1 > 0:
            midRow = row1 + 1
        else:
            midRow = row1 - 1

        if col2 - col1 > 0:
            midCol = col1 + 1
        else:
            midCol = col1 - 1

        midTile = cfg.boardTiles[midRow][midCol]

        if midTile.player != cfg.nonActivePlayer:
            #the mid piece has to of the enemy team
                return invalidMoveResponse()


        #the move is valid so make the kill.
        #depress the current tile
        chb.deselectTile()
        chb.editTile(row2, col2, cfg.activePlayer, curr.pieceType)
        chb.editTile(midRow, midCol, cfg.UNOCCUPIED, cfg.NO_PIECE)
        chb.editTile(row1, col1, cfg.UNOCCUPIED, cfg.NO_PIECE)
        #decrement
        cfg.playerPieces[cfg.nonActivePlayer] -= 1

        cfg.killSound.play()

        #checks if a piece has become a king, this is important for
        #determining if a chain kill should continue
        shouldIBeKing(row2, col2)

        if (
            #checks if the piece can kill from the new location
            len(
                whereCanIKill(
                    row2, col2, cfg.activePlayer,
                    cfg.boardTiles[row2][col2].pieceType
                    )
                    
                ) != 0
            ):
            #if a piece can kill after killing then a chain kill has begun
            cfg.inKillChain = True
            cfg.chainKiller = (row2, col2)
        else:
            #end the jump chain
            cfg.inKillChain = False
            cfg.chainKiller = None
            



    #check if the game is now over, if so then just
    #display the winner and return
    if cfg.playerPieces[cfg.PLAYER_1] == 0:
        declareWinner(cfg.PLAYER_2)
        return True

    if cfg.playerPieces[cfg.PLAYER_2] == 0:
        declareWinner(cfg.PLAYER_1)
        return True
    

    #change active player. in a chain jump the player
    #should not be changed
    if not cfg.inKillChain:
        if cfg.activePlayer == cfg.PLAYER_1:
            cfg.activePlayer = cfg.PLAYER_2
            cfg.nonActivePlayer = cfg.PLAYER_1
        else:
            cfg.activePlayer = cfg.PLAYER_1
            cfg.nonActivePlayer = cfg.PLAYER_2

        chb.displayActivePlayer()
        

        
    #looks for pieces on the board that can now attack for the active
    #player. Remember that we have just changed active players
    cfg.obligatedPieces[cfg.PLAYER_1] = []
    cfg.obligatedPieces[cfg.PLAYER_2] = []
    checkForObligatedPieces(cfg.activePlayer)


    if len(cfg.obligatedPieces[cfg.activePlayer]) == 0:
        #checks if the active player cannot move
        #if there are obligated pieces then obviosly the player can move
        
        mustIResign(cfg.activePlayer)
    
        
    
    return True




##computer player functions

class ModelTile():
    """a model tile is like a tile in that it has a player and a pieceType
but it is not in fact a button.

The point of a modelTile is to be used in
calculations by the computer of checker moves without having to worry about
the Tile also being a button."""
    
    def __init__(self, player, pieceType):
        self.player = player
        self.pieceType = pieceType
        

def produceModelBoard(board):
    """takes in a 2d list of either Tile or ModelTiles and makes a deep copy
of this board and returns a reference to it.

In order to use this Model Board one has to set the cfg.boardTiles variable
to point to the new board before making a calculation. The only functions that
can be called with the model board produced are whereCanIKill(),
whereCanIMove() and the provided function makeModelMove(). """

    modelBoard = []

    for row in range(len(board)):
        modelBoard.append([])
        for col, Tile in enumerate(board[row]):
            copyTile = ModelTile(Tile.player, Tile.pieceType)
            modelBoard[row].append(copyTile)

    return modelBoard


def makeModelMove(row1, col1, row2, col2, board):
    """Applies a move to a 2d list of ModelTile objects.

You have to call this function when making a move with ModelTiles. If the
user wishes to make multiple killing moves in a chain then they have to be
excecuted with successive calls to the function. This function does not check
for the validity of the move asked. If a move is being requested by the
checker computer then it is assumed that it was correctly calculated."""

    origin = board[row1][col1]
    dest = board[row2][col2]

    if abs(row1 - row2) == 1:
        #simple move
        
        dest.player = origin.player
        dest.pieceType = origin.pieceType
        
        
        origin.player = cfg.UNOCCUPIED
        origin.pieceType = cfg.NO_PIECE

    else:
        #kill move

        #find middle tile
        mid = None
        if row1 < row2:
            #forward movement
            if col1 < col2:
                #to the right
                mid = board[row1 + 1][col1 + 1]
            else:
                #to the left
                mid = board[row1 + 1][col1 - 1]
        else:
            #backward movement
            if col1 < col2:
                #to the right
                mid = board[row1 - 1][col1 + 1]
            else:
                #to the left
                mid = board[row1 - 1][col1 - 1]

        #make kill
        dest.player = origin.player
        dest.pieceType = origin.pieceType
        
        origin.player = cfg.UNOCCUPIED
        origin.pieceType = cfg.NO_PIECE

        mid.player = cfg.UNOCCUPIED
        mid.pieceType = cfg.NO_PIECE

        
        

def killPathsAux(
    row, col, player, piece, path, moves
    ):

    #check if the piece should now be treated as a king
    if player == cfg.PLAYER_1 and row == 7:
        piece = cfg.CHECKER_KING
    elif player == cfg.PLAYER_2 and row == 0:
         piece = cfg.CHECKER_KING
         

    connections = whereCanIKill(row, col, player, piece)

    #add myself onto the path. Now path points to a new object
    path = path + [(row, col)]

    if len(connections) == 0:
        #this path is now a dead end, so add the finalized path to the result
        moves.append(path)
    else:
        originalBoard = cfg.boardTiles
        
        for tile in connections:
            #deep copy board
            copyBoard = produceModelBoard(originalBoard)
            #apply kill move to copyBoard
            makeModelMove(row, col, tile[0], tile[1], copyBoard)
            #make boardTiles point to the copied board
            cfg.boardTiles = copyBoard
            
            killPathsAux(tile[0], tile[1], player, piece, path, moves)

        #return original board
        cfg.boardTiles = originalBoard

def killPaths(row, col, player, piece=cfg.CHECKER_MAN):
    """recursively searches down the board starting from the given piece
and finds all of the different killing paths that could be taken with the
given piece."""

    moves = []

    originalBoard = cfg.boardTiles
    
    #produce a deep copy of the original game board
    copyBoard = produceModelBoard(originalBoard)

    #temporarily swap the original board with the model
    cfg.boardTiles = copyBoard

    if len(whereCanIKill(row, col, player, piece)) != 0: 
        killPathsAux(row, col, player, piece, [],  moves)

    #return the original game board
    cfg.boardTiles = originalBoard

    return moves



def possibleMoves(player):
    """returns a list of all possible moves that could be performed on the
given board for the given player and returns a list of tuple lists (a move)
where each tuple represents a location on the board.

The default board used is the active
game board. Another board can be passed in in order to simulate what moves
a player can make after another player has (hypothetically) made a move."""

    moveList = []

    board = cfg.boardTiles

    #step one is to look for kill moves
    for row in range(len(board)):
        for col, tile in enumerate(board[row]):
            if tile.player == player:
                killMoves = killPaths(row, col, player, tile.pieceType)
                for move in killMoves:
                    moveList.append(move)

    if len(moveList) != 0:
        #if there are any kill moves, only return those
        return moveList
    

    #since there are no kill moves available now look for simple one space jumps
    for row in range(len(board)):
        for col, tile in enumerate(board[row]):

            if tile.player == player:
                result = whereCanIMove(row, col, player, tile.pieceType)
                
                for coords in result:
                    #the original location + the destination
                    moveList.append([(row, col)] + [coords])
                

    return moveList
                
    
def makeComputerMove(moveList):
    """takes a list of lists of tuples (row, col) ie a move, and
asks makeMove() to excecute each move in the list"""

    if(len(moveList) == 0):
        #this shouldn't happen
        print("this move is empty")
        return

    moveIsMultiStep = False
    
    for i in range(len(moveList)-1):
        #makes the move and stops if there is an error
        curr = moveList[i+1]
        prev = moveList[i]
        if makeMove(prev[0], prev[1], curr[0], curr[1]) == False:
            chb.updateDisplay1("error in cpu move computation")
            return False

        #sleep for a bit on repeated jumps so they are not as abrupt
        if moveIsMultiStep:
            if cfg.delayTime < .5:
                #if the player has the game on a very fast setting
                #just delay as normal
                time.sleep(cfg.delayTime)
            else:
                #on slower move times this looks better
                time.sleep(.5)

        moveIsMultiStep = True

    return True


def rankMove(move, board=None):
    """takes a move (a list of tuples in the form (row, col) indicating
a sequences of one or more jumps across the board) as its parameter
and returns out a ranked move (a list of the form [move, move ranking]).
This move is naively ranked in that it only counts how many kills are
carried out in the move. Additionally moves that aim towards an enemy are
ranked higher than moves that do not aim towards the enemy.

If the board parameter is None then only kill moves will be assesed and
not simple jumps. If assesing enemy moves then the board parameter should
be left as None as the main players moves are assesed differently from
the oponent player's moves."""
    
    rankedMove = [move, 0]

    if abs(move[0][0] - move[1][0]) != 1:
            #if the move is a killing move
            for jump in move:
                #every kill in the move increases the score
                rankedMove[1] += 1

            #remove the extra point from the starting position
            rankedMove[1] -= 1
            
    elif board != None:
        #else this move is a simple jump

        
        currPiece = board[move[0][0]][move[0][1]]
        #this is the piece that is being moved
        
        if (
            currPiece.player == cfg.PLAYER_1 and move[1][0] == cfg.NUM_ROWS - 1
            and currPiece.pieceType == cfg.CHECKER_MAN
            ):
            #if the piece will become a king, the move is worth one point
            rankedMove[1] = 1

        elif (
            currPiece.player == cfg.PLAYER_2 and move[1][0] == 0
            and currPiece.pieceType == cfg.CHECKER_MAN
            ):
            #if the piece will become a king, the move is worth one point
            rankedMove[1] = 1
        else:
            #checks if the move is aimed at at least one enemy piece

            #set the bounds of where we will be checking on the board
            if move[1][0] > move[0][0]:
                #if the movement goes up a row
                rowStart = move[1][0]
                rowStop = cfg.NUM_ROWS
            else:
                #the piece is moving down a row
                rowStart = 0
                rowStop = move[0][0]

            if move[1][1] > move[0][1]:
                #if the movement goes up a column
                colStart = move[1][1]
                colStop = cfg.NUM_COLS
            else:
                #the piece is moving down a column
                colStart = 0
                colStop = move[0][1]
            
            for row in range(rowStart, rowStop):
                for col in range(colStart, colStop):
                    tile = board[row][col]

                    if (
                        tile.player != cfg.UNOCCUPIED
                        and tile.player != currPiece.player
                        ):
                        #if the piece belongs to the enemy, then reward
                        #the points
                        rankedMove[1] = .5
                    
        
    return rankedMove

def computeComputerMove():
    """Analyzes the board and computes the ideal move based on the computer's
difficulty.

The dumb computer player just gathers a list of all the possible moves
and picks a random one to use. The smart computer player performs a more
complicated assesment in which it applies each move to a model checker
board and determines which move will produce the most kills and the least
deaths and chooses a random move out of the equally best moves."""
    
    moves = possibleMoves(cfg.activePlayer)

    if cfg.playerType[cfg.activePlayer] == cfg.PLAYER_CPU_DUMB:
        #the dumb player should just pick a random move right away
        
        #choose a random move
        random.seed(a=None, version=2)
        move = random.choice(moves)

        if makeComputerMove(move) == False:
            #makes move; if there is an error, stop the game
            cfg.activePlayer = cfg.GAME_OVER
            
        #if the dumb player has made its move, then stop
        return


    ##now the calculations for the smart player

    #a list of lists in the form of [move, score of move]
    #where each kill adds 1 to the moves score and each death removes 1 from it
    rankedMoves = []
    
    for move in moves:
        
        #calculate the initial value of the move
        rankedMove = rankMove(move, cfg.boardTiles)

        #now apply the move to a copy of the board to see how many kills
        #the enemy can get, each kill for the enemy removes a point
        #from the move's ranking
        
        
        #apply each move to a copy of the board
        originalBoard = cfg.boardTiles
        modelBoard = produceModelBoard(originalBoard)

        #apply move to model board
        for i in range(len(move)-1):
            #applies the move, each tile at a time
            curr = move[i+1]
            prev = move[i]
            makeModelMove(prev[0], prev[1], curr[0], curr[1], modelBoard)

        #replace the board variable with the model board for the
        #neccessary calculations
        cfg.boardTiles = modelBoard


        #generate all the possible moves for the enemy player on the new
        #model board we have generated
        enemyMoves = possibleMoves(cfg.nonActivePlayer)
        

        #we need to find the most deadly move that the enemy can make
        #and use that as our baseline for how good our own move is
        mostDamagingMoveRank = 0
        
        for enemyMove in enemyMoves:
            
            #first give the enemy move a ranking based on the number of kills
            #it can make
            rankedEnemyMove = rankMove(enemyMove)
            
            if rankedEnemyMove[1] == 0:
                #if the rank of the current move is 0 then the move is not a
                #kill and we can assume that all the moves will have
                #a score of zero (no kills) as none of the possible enemy moves
                #can be kills
                mostDamagingMoveRank = 0
                break

            #see if the move is more damaging than the last
            if rankedEnemyMove[1] > mostDamagingMoveRank:
                mostDamagingMoveRank = rankedEnemyMove[1]


        #subtract our computer move's score from the most damaging move that
        #the enemy can make after we have made our theoretical move
        rankedMove[1] -= mostDamagingMoveRank
            

        #add the ranked move to the main list
        rankedMoves.append(rankedMove)


        #bring back the old board
        cfg.boardTiles = originalBoard
    

    #now we have a list of rankedMoves to choose from
    #we will gather the highest ranking of these moves and choose one of
    #them to excecute at random

    ##debug
    #print()
    #print("here are the ranked moves:")
    #print(rankedMoves)
    ##

    bestMoves = []
    #find the best (highest scoring) moves
    for rankedMove in rankedMoves:
        if len(bestMoves) == 0:
            bestMoves.append(rankedMove)
        else:
            if rankedMove[1] > bestMoves[0][1]:
                #if the new move has a higher rank, then dump
                #the old best moves and append the new move
                bestMoves = []
                bestMoves.append(rankedMove)
            elif rankedMove[1] == bestMoves[0][1]:
                bestMoves.append(rankedMove)

    
    ##debug
    #print("here are the best moves:")
    #print(bestMoves)
    #print()
    ##
    
    #choose a random best move and make it
    random.seed(a=None, version=2)
    move = random.choice(bestMoves)
    #we only want the move itself, not the ranking here
    move = move[0]

    if makeComputerMove(move) == False:
        #makes move; if there is an error, stop the game
        cfg.activePlayer = cfg.GAME_OVER



