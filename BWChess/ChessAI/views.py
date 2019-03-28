from django.http import HttpResponse
from django.shortcuts import render

import json

from .ChessBoard import ChessBoard, ChessBoardEncoder, ChessBoardObjectHook
from .MCTS import MCTS, MCState, MCTNode

chessboard = ChessBoard(8)

def index(request):
	global chessboard
	# set default if it doesn't exist
	# request.session.setdefault('chessboard', json.dumps(ChessBoard(8), cls = ChessBoardEncoder))
	# JSON without excaped
	# chessboardDict = json.loads(request.session['chessboard'])
	# JSON with excaped
	# chessboard = json.loads(chessboardDict, object_hook = ChessBoardObjectHook)
	if request.method == 'POST':
		row, col, player = request.POST.get('row'), request.POST.get('col'), request.POST.get('player')
		chessboard.setAndUpdateAt(int(row), int(col), player)
		chessboard = MCTS(chessboard, player).generate()
		s = json.dumps(chessboard, cls = ChessBoardEncoder)
		# request.session['chessboard'] s= s
		return HttpResponse(s, content_type = 'application/json')
	else:
		context = {
			'chessboard': json.dumps(chessboard, cls = ChessBoardEncoder)
		}
		return render(request, 'ChessAI/index.html', context)
