import math
import random
import time
import json
from .ChessBoard import ChessBoard, ChessBoardEncoder
# chessboard
# player play this step now
# black or white

MCTSConstant = 1.414
random.seed()


class MCState:
	def __init__(self, chessboard, player):
		self.chessboard = chessboard
		# black white
		self.player = player
		self.visits = 0
		self.scores = 0.0
		self.uct = 0.0

	def copy(self) -> 'MCState':
		ret = MCState(None, None)
		ret.chessboard = self.chessboard.copy()
		ret.player = str(self.player)
		ret.visits = int(self.visits)
		ret.scores = float(self.scores)
		ret.uct = float(self.uct)
		return ret
	@classmethod
	def playerReverse(cls, player):
		if player == 'black':
			return 'white'
		elif player == 'white':
			return 'black'

class MCTNode:
	def __init__(self, state, parent):
		self.state = state
		self.parent = parent
		self.children = []
		self.evaluatedChildren = set()

	#
	# parent is not copied
	#
	def copy(self) -> 'MCTNode':
		assert len(self.children) == 0
		ret = MCTNode(None, None)
		ret.state = self.state.copy()
		ret.parent = self.parent
		ret.children = self.children.copy()
		ret.evaluatedChildren = self.evaluatedChildren.copy()
		return ret

	def isExtended(self):
		return len(self.children) and len(self.evaluatedChildren) == len(self.children)

	def addChild(self, mctnode: 'MCTNode'):
		self.children.append(mctnode)

	def getChildren(self):
		return self.children

	def getUCT(self) -> float:
		assert self.parent != None and self.state.visits > 0
		t = self.parent.state.visits
		return self.state.scores / self.state.visits + MCTSConstant * math.sqrt(math.log(t / self.state.visits))

	def updateState(self, visitStep, scoreStep):
		self.state.visits += visitStep
		self.state.scores += scoreStep
		self.state.uct = self.getUCT()

class MCTS:
	def __init__(self, chessboard, player):
		state = MCState(chessboard, player)
		self.root = MCTNode(state, None)
	def search(self):
		if self.root.state.chessboard.isTerminal() != None:
			return
		cur = self.root
		cur.state.visits += 1
		while cur.isExtended():
			# multiple maximums ?
			cur = max(cur.children, key = lambda x: x.state.uct)
			cur.state.visits += 1

		# cur is not extended fully
		# simlateBegin is not evaluated
		simulateBegin = self.extend(cur)
		assert simulateBegin != None
		score = self.simulate(simulateBegin.copy())

		simulateBegin.state.visits += 1
		inode = simulateBegin
		# UCT of root is meaningless
		while inode.parent != None:
			inode.updateState(0, score)
			inode = inode.parent

	def extend(self, cur: MCTNode) -> MCTNode:
		# where is its children?
		if not len(cur.children):
			curChessboard = cur.state.chessboard

			nextPlayer = MCState.playerReverse(cur.state.player)
			# list of chessboard
			nextSteps = curChessboard.getAllNextStep(nextPlayer)
			for np in nextSteps:
				state = MCState(np, nextPlayer)
				tnode = MCTNode(state, cur)
				cur.addChild(tnode)

		# choose unvisted, visit/evaluate it
		simulateBegin = None
		for ci in range(len(cur.children)):
			if ci not in cur.evaluatedChildren:
				cur.evaluatedChildren.add(ci)
				simulateBegin = cur.children[ci]
				break

		return simulateBegin

	''' 
	roll out from it
	@note
	they are still unvisited
	'''
	def simulate(self, simulateBegin: MCTNode):
		player = simulateBegin.state.player
		me = player
		chessboard = simulateBegin.state.chessboard
		while chessboard.isTerminal() == None:
			player = MCState.playerReverse(player)
			chessboard.setAndUpdateRandom(player)
			if chessboard.isTerminal() != None:
				break
			player = MCState.playerReverse(player)
			chessboard.setAndUpdateRandom(player)
		return int(chessboard.isTerminal() == me)

	def generate(self):
		c1 = time.time()
		c2 = time.time()
		while int(c2 - c1) <= 5:
			self.search()
			c2 = time.time()
		return max(self.root.children, key = lambda x: x.state.visits).state.chessboard