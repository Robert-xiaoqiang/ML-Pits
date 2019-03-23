from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

import json

from .ChessBoard import ChessBoard, ChessBoardEncoder
from .MCTS import MCTS

def index(request):
	chessboard = ChessBoard(8)
	chessboard.setAndUpdateBlackAt(0, 0)
	chessboard.setAndUpdateWhiteAt(0, 1)	
	if request.method == 'GET':
		# for template, dict is enough
		# for JS, JSON is necessary
		context = {
			'chessboard': json.dumps(chessboard, cls = ChessBoardEncoder)
		}
		return render(request, 'ChessAI/index.html', context)
	elif request.method == 'POST':
		row, col, player = request.POST.get('row'), request.POST.get('col'), request.POST.get('player')
		chessboard.setAndUpdateAt(int(row), int(col), player)
		context = {
			'chessboard': json.dumps(chessboard, cls = ChessBoardEncoder)
		}
		print(chessboard.blackCount, chessboard.whiteCount)
		return render(request, 'ChessAI/index.html', context)

