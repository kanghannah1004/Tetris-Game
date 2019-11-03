#################################################
# hw7.py: Tetris!
#
# Your name: Roshan Ram 
#################################################

import cs112_f19_week7_linter
import math, copy, random

from cmu_112_graphics import *
from tkinter import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Functions for you to write
#################################################

def timerFired(app):
    if app.isGameOver:
        return

    if not moveFallingPiece(app, +1, 0):
        placeFallingPiece(app)
        newFallingPiece(app)
    
    if not fallingPieceisLegal(app):
        app.isGameOver = True



def gameDimensions():
    rows = 15
    cols = 10
    cellSize = 20
    margin = 25 
    return (rows, cols, cellSize, margin)

def playTetris(): # plays game
    rows, cols, cellSize, margin = gameDimensions()
    width = cols*cellSize + margin
    height = rows*cellSize + margin
    runApp(width = width, height = height)

def appStarted(app): #intialize values needed 
    app.score = 0
    app.timerDelay = 150
    app.counter = 0
    rows, cols, cellSize, margin = gameDimensions()
    app.rows = rows
    app.cols = cols
    app.cellSize = cellSize
    app.margin = margin
    app.emptyColor = "blue"
    app.board = [ ([app.emptyColor] * app.cols) for row in range(app.rows) ]
    app.width = app.cols*app.cellSize + app.margin
    app.height = app.rows*app.cellSize + app.margin
    app.isGameOver = False


    # Seven "standard" pieces (tetrominoes)

    iPiece = [
        [  True,  True,  True,  True ]
    ]

    jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]

    lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]

    oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]

    sPiece = [
        [ False,  True,  True ],
        [  True,  True, False ]
    ]

    tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]

    zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]

    app.tetrisPieces = [ iPiece, jPiece, lPiece, oPiece, sPiece, 
    tPiece, zPiece ]
    app.tetrisPieceColors = [ "red", "yellow", "magenta", "pink", "cyan", 
    "green", "orange" ]

    newFallingPiece(app)

def pointInGrid(app, x, y): 
    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html

    # return True if (x, y) is inside the grid defined by app.
    return ((app.margin <= x <= app.width-app.margin) and
            (app.margin <= y <= app.height-app.margin))

def getCell(app, x, y):
    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html

    # aka "viewToModel"
    # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
    if (not pointInGrid(app, x, y)):
        return (-1, -1)
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows

    # Note: we have to use int() here and not just // because
    # row and col cannot be floats and if any of x, y, app.margin,
    # cellWidth or cellHeight are floats, // would still produce floats.
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)

    return (row, col)


def keyPressed(app, event):


    app.counter += 1

    if (event.key == 'Left'):    moveFallingPiece(app, 0, -1)
    elif (event.key == 'Right'): moveFallingPiece(app, 0, +1)
    elif (event.key == 'Up'):    rotateFallingPiece(app)
    elif (event.key == 'Down'):  moveFallingPiece(app, +1, 0)
    elif (event.key == 'r'): appStarted(app)
    elif (event.key == 'Space'): hardDrop(app) #PRESS SPACE FOR HARD DROP
    elif app.isGameOver: return 
    # else: newFallingPiece(app)

    

def getCellBounds(app, row, col):
    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    columnWidth = gridWidth / app.cols
    rowHeight = gridHeight / app.rows
    x0 = app.margin + col * columnWidth
    x1 = app.margin + (col+1) * columnWidth
    y0 = app.margin + row * rowHeight
    y1 = app.margin + (row+1) * rowHeight
    return (x0, y0, x1, y1)

def drawCell(app, canvas, rows, cols, color):
    x0, y0, x1, y1 = getCellBounds(app, rows, cols)
    canvas.create_rectangle(x0, y0, x1, y1, fill = color,
                            width = 3)

def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, canvas, row, col, app.board[row][col])

def redrawAll(app, canvas):
    canvas.create_rectangle(0, 0, 
                            app.width, app.height, 
                            fill = "orange")
    drawBoard(app, canvas)
    drawFallingPiece(app, canvas)
    drawScore(app, canvas)

    if app.isGameOver:
        canvas.create_text(app.width/2, app.height/2, text='Game over!',
                           font='Arial 26 bold',
                           fill = 'ghost white')
        canvas.create_text(app.width/2, app.height/2+40,
                           text='Press r to restart!',
                           font='Arial 26 bold',
                           fill = 'ghost white')


def newFallingPiece(app):
    import random
    randomIndex = random.randint(0, len(app.tetrisPieces) - 1)
    app.fallingPiece = app.tetrisPieces[randomIndex]
    app.fallingPieceColor = app.tetrisPieceColors[randomIndex]
    app.fallingPieceRow = 0
    app.numFallingPieceRows = len(app.fallingPiece)
    app.numFallingPieceCols = len(app.fallingPiece[0])
    app.fallingPieceCol = app.cols//2 - app.numFallingPieceCols//2 

def drawFallingPiece(app, canvas):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
          if app.fallingPiece[row][col] == True:
            drawCell(app, canvas, app.fallingPieceRow+row, 
            app.fallingPieceCol+col, app.fallingPieceColor)

def moveFallingPiece(app, drow, dcol):
        app.fallingPieceRow += drow
        app.fallingPieceCol += dcol

        (app.fallingPieceX, app.fallingPieceY, 
        app.X0, app.Y0) = getCellBounds(app, 
                                    app.fallingPieceRow, 
                                    app.fallingPieceCol)

        if not fallingPieceisLegal(app):
            app.fallingPieceRow -= drow
            app.fallingPieceCol -= dcol
            return False #step 6
        return True #step 6
    

def fallingPieceisLegal(app):
    for row in range(len(app.fallingPiece)):
            for col in range(len(app.fallingPiece[0])):
                if app.fallingPiece[row][col] == True:
                    tempRow = app.fallingPieceRow + row
                    tempCol = app.fallingPieceCol + col
                    if (tempRow < 0 or tempRow >= app.rows or tempCol < 0 
                    or tempCol >= app.cols):
                        return False
                    if (app.board[tempRow][tempCol] != app.emptyColor):
                        return False
    return True


def rotateFallingPiece(app): 
    oldPiece = copy.deepcopy(app.fallingPiece)
    numOldRows, numOldCols = len(app.fallingPiece), len(app.fallingPiece[0])
    numNewRows, numNewCols = numOldCols, numOldRows #swap rows and cols
    newPiece = make2dList(numNewRows, numNewCols)

    for row in range(numOldRows):
        for col in range(numOldCols):
            newRow = numOldCols - 1 - col
            newCol = row 
            newPiece[newRow][newCol] = app.fallingPiece[row][col]
    
    newFallingPieceRow = app.fallingPieceRow \
    + numOldRows//2 - numNewRows//2 

    newFallingPieceCol = app.fallingPieceCol \
    + numOldCols//2 - numNewCols//2 

    oldFallingPieceRow = app.fallingPieceRow # temp variables for row and col
    oldFallingPieceCol = app.fallingPieceCol # ^

    app.fallingPieceRow = newFallingPieceRow
    app.fallingPieceCol = newFallingPieceCol

    app.fallingPiece = newPiece #set falling piece to calculated new piece


    if not fallingPieceisLegal(app):
        app.fallingPiece = oldPiece
        app.fallingPieceRow = oldFallingPieceRow
        app.fallingPieceCol = oldFallingPieceCol


    

def placeFallingPiece(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
          if app.fallingPiece[row][col] == True:
            app.board[app.fallingPieceRow + row][app.fallingPieceCol + col] = \
            app.fallingPieceColor

    removeFullRows(app) #immediately remove any full rows at first instance 
                        # possible 

def removeFullRows(app):
    numNotFullCells = 0
    fullRows = 0
    for row in range(len(app.board)): 
        for val in app.board[row]:
            if val == app.emptyColor:
                numNotFullCells += 1
        if numNotFullCells == 0:
            fullRows += 1
            app.board.remove(app.board[row])
            app.board.insert(0, [app.emptyColor] * app.cols)
            fullRows += 1
        numNotFullCells = 0

    app.score = app.score + (fullRows**2)

def drawScore(app, canvas):
        canvas.create_text(app.width/2, app.height/10,
                           text=f'Score: {app.score}',
                           font='Arial 26 bold',
                           fill = 'steel blue')

def hardDrop(app):
    while fallingPieceisLegal(app):
        if not moveFallingPiece(app, +1, 0):
            placeFallingPiece(app)

def make2dList(rows, cols):
    #from http://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
    return [ ([0] * cols) for row in range(rows) ]



#################################################
# main
#################################################

def main():
    cs112_f19_week7_linter.lint()
    playTetris()

if __name__ == '__main__':
    main()


