'''
This is the AI module for a chess game.
'''

piecesScore = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'P': 1}

# Piece-Square Tables for positional evaluation
pawnScores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 5, 5, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

bishopScores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

knightScores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

rookScores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

queenScores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 4, 2, 1],
    [1, 1, 2, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

kingScores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 1, 0, 0, 1, 2, 2],
    [4, 4, 3, 1, 1, 3, 4, 4]
]

piecePositionScores = {
	'P': pawnScores,
    'N': knightScores,
    'B': bishopScores,
    'R': rookScores,
    'Q': queenScores,
    'K': kingScores
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4
'''
This is a helper function to make the best move using the minimax algorithm.
'''
def findBestMove(gs, validMoves):
    bestMove = None
    # iterative deepening
    maxDepth = DEPTH
    for depth in range(1, maxDepth + 1):
        alpha = -CHECKMATE
        beta = CHECKMATE
        # order root moves for better pruning
        orderedMoves = orderMoves(validMoves, gs)
        bestScore = -CHECKMATE
        rootTurn = 1 if gs.whiteToMove else -1
        for move in orderedMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            # pass the current root search depth so mate distance can be computed
            score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -rootTurn, depth)
            gs.undoMove()
            if score > bestScore:
                bestScore = score
                bestMove = move
            if bestScore > alpha:
                alpha = bestScore
            if alpha >= beta:
                break
    return bestMove

'''
This function uses the NegaMax algorithm with alpha-beta pruning to find the best move.
'''
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, rootDepth):
     # prefer faster mates: if this position is terminal, return mate score adjusted by distance
     if gs.checkMate:
         # if side to move is checkmated, it's a loss for the side to move
         mate_distance = rootDepth - depth
         if gs.whiteToMove:
             return - (CHECKMATE - mate_distance)
         else:
             return CHECKMATE - mate_distance
     if gs.staleMate:
         return STALEMATE
     if depth == 0:
         # use quiescence search at leaf; pass rootDepth for mate-distance accounting
         return turnMultiplier * quiescence(alpha, beta, gs, turnMultiplier, rootDepth)
 
     # order moves to improve pruning
     orderedMoves = orderMoves(validMoves, gs)
     maxScore = -CHECKMATE
     for move in orderedMoves:
         gs.makeMove(move)
         nextMoves = gs.getValidMoves()
         score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier, rootDepth)
         if score > maxScore:
             maxScore = score
         gs.undoMove()
         if maxScore > alpha:  # pruning
             alpha = maxScore
         if alpha >= beta:
             break
     return maxScore

'''
Ordering (MVV-LVA + promotion bonus).
'''
def orderMoves(moves, gs):
	# prefer captures (victim value - attacker value) and promotions
	def score(move):
		score_val = 0
		# capture: higher victim value -> higher priority, lower attacker value -> higher priority
		if move.pieceCaptured != "--":
			victim = piecesScore.get(move.pieceCaptured[1], 0)
			attacker = piecesScore.get(move.pieceMoved[1], 0)
			score_val += 1000 + (victim * 10 - attacker)  # MVV-LVA style
		# pawn promotions
		if move.isPawnPromotion:
			score_val += 900
		# small tie-breaker: prefer center moves (optional)
		center_bonus = 3 - (abs(3.5 - move.endRow) + abs(3.5 - move.endCol)) 
		score_val += int(center_bonus)
		return -score_val  # negative because we'll sort ascending
	return sorted(moves, key=score)

'''
Quiescence search (captures only).
'''
def quiescence(alpha, beta, gs, turnMultiplier, rootDepth):
    # terminal check first so mates discovered in quiescence are distance-weighted
    if gs.checkMate:
        mate_distance = rootDepth  # quiescence is called at depth == 0 so use rootDepth
        if gs.whiteToMove:
            return - (CHECKMATE - mate_distance)
        else:
            return CHECKMATE - mate_distance
    if gs.staleMate:
        return STALEMATE

    stand_pat = turnMultiplier * scoreBoard(gs)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # generate captures only
    capture_moves = [m for m in gs.getAllPossibleMoves() if m.pieceCaptured != "--" or m.isEnpassantMove]
    capture_moves = orderMoves(capture_moves, gs)
    for move in capture_moves:
        gs.makeMove(move)
        score = -quiescence(-beta, -alpha, gs, -turnMultiplier, rootDepth)
        gs.undoMove()
        if score >= beta:
            return score
        if score > alpha:
            alpha = score
    return alpha

'''
Simple material-only scorer used by the UI (returns pawn-units, white positive).
'''
def scoreMaterial(board):
    material = 0
    for r in range(len(board)):
        for c in range(len(board[r])):
            piece = board[r][c]
            if piece != "--":
                color = piece[0]
                ptype = piece[1]
                val = piecesScore.get(ptype, 0)
                if color == 'w':
                    material += val
                else:
                    material -= val
    return material

'''
A positive score is good for white, a negative score is good for black.
'''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for coll in range(len(gs.board[row])):
            square= gs.board[row][coll]
            if square != "--":
                #score it positionally
                if square[1] in piecePositionScores:
                    piecePositionScore = piecePositionScores[square[1]]
                    if square[0] == 'w':
                        score += piecePositionScore[row][coll]
                    elif square[0] == 'b':
                        score -= piecePositionScore[7 - row][7 - coll]
                #score it by piece value
                if square[0] == 'w':
                    score += piecesScore[square[1]]
                elif square[0] == 'b':
                    score -= piecesScore[square[1]]
    return score
