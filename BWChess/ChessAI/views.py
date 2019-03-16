from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render

from .ChessBoard import ChessBoard
from .MCTS import MCTS

def index(request):
	context = { }
	chessboard = ChessBoard()
	return render(request, 'ChessAI/index.html', context)
