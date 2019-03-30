from django.http import HttpResponse
from django.shortcuts import render

import json

from .ChessBoard import ChessBoard, ChessBoardEncoder, ChessBoardObjectHook
from .MCTS import MCTS, MCState, MCTNode

chessboard = ChessBoard(8)
chessboard.setWithoutUpdateBlackAt(3, 3)
chessboard.setWithoutUpdateBlackAt(4, 4)
chessboard.setWithoutUpdateWhiteAt(3, 4)
chessboard.setWithoutUpdateWhiteAt(4, 3)

def index(request):
	global chessboard
	# set default if it doesn't exist
	# request.session.setdefault('chessboard', json.dumps(ChessBoard(8), cls = ChessBoardEncoder))
	# JSON without excaped
	# chessboardDict = json.loads(request.session['chessboard'])
	# JSON with excaped
	# chessboard = json.loads(chessboardDict, object_hook = ChessBoardObjectHook)
	if request.method == 'POST':
		# row, col, player = request.POST.get('row'), request.POST.get('col'), request.POST.get('player')
		# chessboard.setAndUpdateAt(int(row), int(col), player)
		chessboardJSONStr, player = request.POST.get('chessboard'), request.POST.get('player')
		chessboard = ChessBoard.contructorFromJSONStr(chessboardJSONStr)
		chessboard, firstStep = MCTS(chessboard, player).generate()
		cs = json.dumps(chessboard, cls = ChessBoardEncoder)
		resDict = { 'chessboard': cs, 'row': firstStep[0], 'col': firstStep[1] }
		res = json.dumps(resDict)
		# request.session['chessboard'] = s
		return HttpResponse(res, content_type = 'application/json')
	else:
		context = {
			'chessboard': json.dumps(chessboard, cls = ChessBoardEncoder)
		}
		return render(request, 'ChessAI/index.html', context)
