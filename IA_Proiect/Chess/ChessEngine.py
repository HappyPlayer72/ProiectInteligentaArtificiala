'''
This module is responsible for all the information about the current state of a chess game. 
It will also be responsible for determining the valid moves at the current state.
'''

'''
This class is responsible for stating all the information about the current chess game. 
It will also responsible for the valid moves at the current state. It will also keep a move log. 
'''
class GameState():
    def __init__(self):
        # Board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'.
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', 'P'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                               'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () # coordinates for the square where en passant capture is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        # castling rights
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant).
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players

        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # pawn promotion
        if move.isPawnPromotion:
            promotedPiece = 'Q'
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" # capturing the pawn
        
        # update enPassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = () # reset enPassantPossible if not a 2 square pawn advance

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # KingSide castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else: # QueenSide castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        self.enPassantPossibleLog.append(self.enPassantPossible)

    '''
    Undo the last move made.
    ''' 
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swap players back

            # update the king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # KingSide
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: # QueenSide
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # reset the checkmate and stalemate flags
            self.checkMate = False
            self.staleMate = False

    '''
    Update the castle rights given the move.
    '''
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: # right rook
                    self.currentCastlingRights.bks = False

        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    '''
    All moves considering checks.
    '''
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        # Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # For each move, make the move
        for i in range(len(moves)-1, -1, -1): # when removing from a list, go backwards
            self.makeMove(moves[i])
            # Generate all opponent's moves
            # For each of opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # If they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRights = tempCastleRights

        return moves
    
    ''' 
    Determine if the current player is in check.
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    Determine if the enemy can attack the square row, col.
    '''
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turns back
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: # square is under attack
                return True
        return False
    
    ''' 
    All moves without considering checks.
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)): # number of rows '8'
            for col in range(len(self.board[row])): # number of cols in given row '8'
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) # call the appropriate move function based on piece type
        return moves
                    
    ''' 
    Get all the pawn moves for the pawn located at row, col and add these moves to the list.
    '''
    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove: # white pawn moves
            if self.board[row-1][col] == "--": # 1 square move
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--": # 2 square move
                    moves.append(Move((row, col), (row-2, col), self.board))
            if col - 1 >= 0: # captures to the left
                if self.board[row-1][col-1][0] == 'b': # enemy piece to capture
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, isEnpassantPossible = True))
            if col + 1 <= 7: # captures to the right
                if self.board[row-1][col+1][0] == 'b': # enemy piece to capture
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, isEnpassantPossible = True))
    
        else: # black pawn moves
            if self.board[row+1][col] == "--": # 1 square move
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--": # 2 square move
                    moves.append(Move((row, col), (row+2, col), self.board))
            if col - 1 >= 0: # captures to the left
                if self.board[row+1][col-1][0] == 'w': # enemy piece to capture
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row+1, col-1), self.board, isEnpassantPossible = True))
            if col + 1 <= 7: # captures to the right
                if self.board[row+1][col+1][0] == 'w': # enemy piece to capture
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enPassantPossible:
                    moves.append(Move((row, col), (row+1, col+1), self.board, isEnpassantPossible = True))
        
    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list. 
    '''
    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for dir in directions:
            for i in range(1, 8):
                endRow = row + dir[0] * i
                endCol = col + dir[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board
                    break

    ''' 
    Get all the knight moves for the knight located at row, col and add these moves to the list.
    '''
    def getKnightMoves(self, row, col, moves):
        knightMoves = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
        allyColor = "w" if self.whiteToMove else "b" # friendly piece
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not a friendly piece (empty or enemy piece)
                    moves.append(Move((row, col), (endRow, endCol), self.board))
                    
    ''' 
    Get all the bishop moves for the bishop located at row, col and add these moves to the list.
    '''
    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8): # bishop can move max 7 squares
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board
                    break

    ''' 
    Get all the queen moves for the queen located at row, col and add these moves to the list.
    '''
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    ''' 
    Get all the king moves for the king located at row, col and add these moves to the list.
    '''
    def getKingMoves(self, row, col, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b" # friendly piece
        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not a friendly piece (empty or enemy piece)
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    '''
    Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
    '''
    def getCastleMoves(self, row, col, moves):
        if self.inCheck():
            return # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(row, col, moves)

    '''
    Generate all valid KingSide castle moves for the king at (row, col) and add them to the list of moves. 
    '''
    def getKingsideCastleMoves(self, row, col, moves):
        # ensure squares exist on board to avoid IndexError
        if col + 2 > 7:
            return
        # squares between king and rook must be empty
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            # rook expected at col+3 for kingside; ensure it's on board and is a rook of the right color
            rookCol = col + 3
            if rookCol <= 7:
                rookPiece = self.board[row][rookCol]
                expectedColor = 'w' if self.whiteToMove else 'b'
                if rookPiece[1] == 'R' and rookPiece[0] == expectedColor:
                    # ensure squares king moves through/into are not under attack
                    if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                        moves.append(Move((row, col), (row, col+2), self.board, isCastleMove = True))

    '''
    Generate all valid QueenSide castle moves for the king at (row, col) and add them to the list of moves.
    '''
    def getQueenSideCastleMoves(self, row, col, moves):
        # ensure squares exist on board to avoid IndexError
        if col - 3 < 0:
            return
        # squares between king and rook must be empty
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--":
            # rook expected at col-4 for queen side; ensure it's on board and is a rook of the right color
            rookCol = col - 4
            if rookCol >= 0:
                rookPiece = self.board[row][rookCol]
                expectedColor = 'w' if self.whiteToMove else 'b'
                if rookPiece[1] == 'R' and rookPiece[0] == expectedColor:
                    # ensure squares king moves through/into are not under attack
                    if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                        moves.append(Move((row, col), (row, col-2), self.board, isCastleMove = True))

'''
This class keeps track of the current castling rights.
'''
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

'''
This class is responsible for storing information about a move.
'''
class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0} 
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2  , "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    '''
    Init method that will take in a start square and an end square in the form of (row, col) tuples.
    Example: (6, 4) -> (4, 4) means moving a piece from row 6, column 4 to row 4, column 4
    Also takes in the board so we can determine what piece is being moved and what piece is being captured.
    '''
    def __init__(self, startSq, endSq, board, isEnpassantPossible = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        
        # en passant
        self.isEnpassantMove = isEnpassantPossible
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # castle move
        self.isCastleMove = isCastleMove
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #print(self.moveID)

    '''
    Overriding the equals method.
    Two moves are equal if they have the same moveID.
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    '''
    Shortened chess notation for the move.
    '''
    def getChessNotation(self):
        # Make this like real chess notation later
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    '''
    Get the rank and file of the square.
    0 0 -> a8
    '''
    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
    
    '''
    Overriding the string method.
    '''
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
            # king side castle is O-O and queen side castle is O-O-O
        
        endSquare = self.getRankFile(self.endRow, self.endCol) # target square

        # pawn moves
        if self.pieceMoved[1] == 'P':
            if self.pieceCaptured != "--":
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # other pieces
        moveString = self.pieceMoved[1]
        if self.pieceCaptured != "--":
            moveString += "x"
        return moveString + endSquare
