'''
This is the main driver file. This will be responsible for handling user input 
and displaying the current GameState object.
'''

import pygame as p
import ChessEngine, ChessAI

BOARD_WITH = BOARD_HIGHT = 580
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HIGHT = BOARD_HIGHT
SIDE_PANEL_WIDTH = 64  # new left-side panel width for evaluation
BOARD_ORIGIN_X = SIDE_PANEL_WIDTH  # board is shifted right by this amount
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = BOARD_HIGHT // DIMENSION
MAX_FPS = 30  # for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main.
''' 
def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("imagini/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # Note: Can access an image by saying 'IMAGES['wP']'

'''
This is the main driver for our code. This will handle user input and updating the graphics.
'''
def main():
    p.init()
    # include left side panel when setting window size
    screen = p.display.set_mode((SIDE_PANEL_WIDTH + BOARD_WITH + MOVE_LOG_PANEL_WIDTH, BOARD_HIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    loadImages()  # only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: (row,col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6,4), (4,4)])
    gameOver = False
    playerOne = True  # if a human is playing white, then this will be True. If an AI is playing, then False
    playerTwo = False  # same as above but for black
    moveLogFont = p.font.SysFont("Arial", 13, False, False)

    # while game is running
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    board_x = location[0] - BOARD_ORIGIN_X
                    # ignore clicks outside board area
                    if board_x < 0 or board_x >= BOARD_WITH:
                        sqSelected = ()  # deselect
                        playerClicks = []
                    else:
                        col = board_x // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if sqSelected == (row, col) or col >= 8:  # the user clicked the same square twice
                            sqSelected = ()  # deselect
                            playerClicks = [] # clear player clicks
                        else:
                            sqSelected = (row, col) # select the square
                            playerClicks.append(sqSelected)  # append for both 1st and 2nd clicks
                        if len(playerClicks) == 2:  # after 2nd click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            #print(move.getChessNotation())
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    animate = True
                                    sqSelected = ()  # reset user clicks
                                    playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False

                if e.key == p.K_r:  # reset the game when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate:
            gameOver = True
            drawEndGameText(screen, 'Stalemate' if gs.staleMate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and moves for piece selected.
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved

            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (BOARD_ORIGIN_X + col*SQ_SIZE, row*SQ_SIZE))

            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (BOARD_ORIGIN_X + move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs, getValidMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, getValidMoves, sqSelected)  # highlight square selected and moves
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)

'''
Draws the move log.
'''
def drawMoveLog(screen, gs, font):
    # right-side move log
    moveLogRect = p.Rect(BOARD_ORIGIN_X + BOARD_WITH, 0, MOVE_LOG_PANEL_WIDTH, BOARD_HIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog

    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + "   "
        if i + 1 < len(moveLog):  # make sure black made a move
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)
    padding = 5

    movePerRow = 3
    for i in range(len(moveTexts)//movePerRow + 1):
        text = ""
        for j in range(movePerRow):
            if i*movePerRow + j < len(moveTexts):
                text += moveTexts[i*movePerRow + j] + "   "
        textObject = font.render(text, True, p.Color('Gray'))
        textLocation = moveLogRect.move(padding, padding + i * textObject.get_height())
        screen.blit(textObject, textLocation)

    # Evaluation panel on left side
    leftPanelRect = p.Rect(0, 0, SIDE_PANEL_WIDTH, BOARD_HIGHT)
    p.draw.rect(screen, p.Color('black'), leftPanelRect)  # panel background


    # compute evaluation that takes material into consideration
    try:
        # material in pawn units (e.g. +1 means white up one pawn)
        material = ChessAI.scoreMaterial(gs.board)
        # full evaluation from scoreBoard (includes material + positional in pawn units)
        full_score = ChessAI.scoreBoard(gs)
    except Exception:
        material = 0
        full_score = 0

    # positional component (pawn units)
    positional = full_score - material
    # material prioritized (centipawns), positional as secondary (scaled)
    eval_centipawns = material * 100 + positional * 10  # material*100cp + positional*10cp

    # realistic cap: starting material difference is 39 pawn-units -> 39*100 = 3900 centipawns
    MATERIAL_PAWN_CAP = 39
    CAP_CENTIPAWNS = MATERIAL_PAWN_CAP * 100
    normalized = max(-1.0, min(1.0, float(eval_centipawns) / float(CAP_CENTIPAWNS)))  # -1..1

    # bar geometry inside left panel
    bar_width = 20
    bar_margin_x = (SIDE_PANEL_WIDTH - bar_width) // 2
    bar_margin_y = 12
    bar_height = BOARD_HIGHT - 2 * bar_margin_y
    bar_rect = p.Rect(bar_margin_x, bar_margin_y, bar_width, bar_height)

    # Create gradient surface (top = green (white advantage), bottom = red (black advantage))
    green = (70, 200, 120)
    red = (220, 80, 80)
    bar_surf = p.Surface((bar_width, bar_height))
    for y in range(bar_height):
        t = y / max(1, bar_height - 1)  # 0..1 from top to bottom
        r = int(green[0] * (1 - t) + red[0] * t)
        g = int(green[1] * (1 - t) + red[1] * t)
        b = int(green[2] * (1 - t) + red[2] * t)
        bar_surf.fill((r, g, b), rect=p.Rect(0, y, bar_width, 1))
    # add subtle center neutral overlay to mimic engine bar center contrast
    center_line_y = bar_height // 2
    p.draw.line(bar_surf, (50, 50, 50), (0, center_line_y), (bar_width - 1, center_line_y), 1)

    # blit the gradient to the left panel
    screen.blit(bar_surf, (bar_rect.x, bar_rect.y))
    # outline
    p.draw.rect(screen, p.Color('black'), bar_rect, 1)

    # knob position: normalized=1 -> top, -1 -> bottom
    knob_rel = (1 - normalized) / 2  # 0..1 where 0 is top
    knob_y = bar_rect.y + int(knob_rel * bar_height)
    knob_x = bar_rect.x + bar_rect.width // 2

    # draw knob (circle) with outline and small shadow
    knob_radius = max(5, bar_width // 2 + 2)
    # shadow
    p.draw.circle(screen, (0, 0, 0, 80), (knob_x + 1, knob_y + 1), knob_radius)
    # knob fill - use contrasting color depending on side
    if normalized >= 0:
        knob_color = (255, 255, 255)
    else:
        knob_color = (230, 230, 230)
    p.draw.circle(screen, knob_color, (knob_x, knob_y), knob_radius)
    p.draw.circle(screen, p.Color('black'), (knob_x, knob_y), knob_radius, 1)

    # numeric evaluation label (show combined centipawn converted to pawn units for readability)
    # show "MATE" if very large
    if abs(eval_centipawns) >= CAP_CENTIPAWNS:
        eval_label = "MATE"
    else:
        # show in pawn units with two decimals (centipawn -> pawn)
        eval_label = f"{eval_centipawns/100.0:+.2f}"
    evalFont = p.font.SysFont("Arial", 12, True, False)
    evalTextObj = evalFont.render(eval_label, True, p.Color('White'))
    text_x = (SIDE_PANEL_WIDTH - evalTextObj.get_width()) // 2
    text_y = bar_rect.bottom + 6
    if text_y + evalTextObj.get_height() > BOARD_HIGHT - 4:
        text_y = BOARD_HIGHT - evalTextObj.get_height() - 4
    screen.blit(evalTextObj, (text_x, text_y))

    # small percentage bar below numeric label for quick glance
    pct_h = 6
    pct_w = SIDE_PANEL_WIDTH - 12
    pct_x = (SIDE_PANEL_WIDTH - pct_w) // 2
    pct_y = text_y + evalTextObj.get_height() + 6
    pct_rect = p.Rect(pct_x, pct_y, pct_w, pct_h)
    p.draw.rect(screen, (80, 80, 80), pct_rect)
    # fill percent based on normalized (map -1..1 => 0..1 where 0 = full black, 1 = full white)
    pct_fill = int(((normalized + 1) / 2) * pct_w)
    if pct_fill > 0:
        p.draw.rect(screen, (200, 200, 200), p.Rect(pct_x, pct_y, pct_fill, pct_h))

'''
Draw the squares on the board. The top left square is always light.
'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for coll in range(DIMENSION):
            color = colors[((row + coll) % 2)]
            # shift board drawing by BOARD_ORIGIN_X
            p.draw.rect(screen, color, p.Rect(BOARD_ORIGIN_X + coll * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":  # not an empty square
                screen.blit(IMAGES[piece], p.Rect(BOARD_ORIGIN_X + col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animate moves
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5  # frames to move one square
    frameCount = max(1, (abs(dR) + abs(dC)) * framesPerSquare)
    for frame in range(frameCount + 1):
        row, col = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(BOARD_ORIGIN_X + move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                if move.pieceMoved[0] == 'w':
                    endSquare = p.Rect(BOARD_ORIGIN_X + (move.endCol) * SQ_SIZE, (move.endRow + 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                else:
                    endSquare = p.Rect(BOARD_ORIGIN_X + (move.endCol) * SQ_SIZE, (move.endRow - 1) * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # draw moving piece (apply BOARD_ORIGIN_X to interpolated column)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(BOARD_ORIGIN_X + col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

'''
Draw the end game text.
'''
def drawEndGameText(screen, text):
    # use a common font name and center the rendered text surface correctly relative to the board
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, True, p.Color('White'))
    # center the text on the board area using the surface width/height
    board_area = p.Rect(BOARD_ORIGIN_X, 0, BOARD_WITH, BOARD_HIGHT)
    textLocation = board_area.move(BOARD_ORIGIN_X + BOARD_WITH/2 - textObject.get_width()/2 - BOARD_ORIGIN_X,
                                   BOARD_HIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    # render a black shadow/outline for contrast and blit offset
    textObject = font.render(text, True, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()
