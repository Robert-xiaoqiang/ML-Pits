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
		self.bestChild = None
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
		ret.bestChild = self.bestChild.copy() if self.bestChild is not None else None
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
		return self.state.scores / self.state.visits + MCTSConstant * math.sqrt(math.log(t) / self.state.visits)

	def updateState(self, visitStep, scoreStep):
		self.state.visits += visitStep
		self.state.scores += scoreStep
		self.state.uct = self.getUCT()

class MCTS:
	def __init__(self, chessboard, player):
		state = MCState(chessboard, player)
		self.root = MCTNode(state, None)
		self.winner = MCState.playerReverse(player)
		# the same index with children
		# why not hashtable ?
		self.firstStepMap = [ ]

	def search(self):
		if self.root.state.chessboard.isTerminal() != None:
			return
		cur = self.root
		cur.state.visits += 1
		while cur.isExtended():
			# multiple maximums ?
			# cur = max(cur.children, key = lambda x: x.state.uct)
			cur = cur.bestChild
			cur.state.visits += 1

		# cur is not extended fully
		# simlateBegin is not evaluated
		simulateBegin = self.extend(cur)
		score = 0
		inode = None
		if simulateBegin is None:
			assert cur.state.chessboard.isTerminal() != None
			score = int(cur.state.chessboard.isTerminal() == self.winner)
			inode = cur
		else:
			# this is an unnecessary copy for simulateBegin.parent/children/bestChild/evaluateChildren
			# but necessary for state.chessboard
			score = self.simulate(simulateBegin.copy())
			simulateBegin.state.visits += 1
			inode = simulateBegin

		# UCT of root is meaningless
		while inode.parent != None:
			inode.updateState(0, score)
			tempParent = inode.parent
			for c in tempParent.children:
				if c is not inode and c.state.visits:
					c.updateState(0, 0)
				tempUCT = c.state.uct
				if tempParent.bestChild is None or tempParent.bestChild.state.uct < tempUCT:
					tempParent.bestChild = c
			inode = tempParent
		# print(*map(lambda x: x.state.scores, self.root.children))

	def extend(self, cur: MCTNode) -> MCTNode:
		# where is its children?
		if not len(cur.children):
			curChessboard = cur.state.chessboard

			nextPlayer = MCState.playerReverse(cur.state.player)
			# list of chessboard, position
			nextSteps = curChessboard.getAllNextStep(nextPlayer)
			for ns in nextSteps:
				state = MCState(ns[0], nextPlayer)
				tnode = MCTNode(state, cur)
				cur.addChild(tnode)
				if cur.parent is None:
					self.firstStepMap.append(ns[1])

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
		me = self.winner
		chessboard = simulateBegin.state.chessboard
		while chessboard.isGood() == None and chessboard.isTerminal() == None:
			player = MCState.playerReverse(player)
			chessboard.setAndUpdateRandom(player)
			if chessboard.isGood() != None or chessboard.isTerminal() != None:
				break
			player = MCState.playerReverse(player)
			chessboard.setAndUpdateRandom(player)
		flag1 = chessboard.isGood()
		flag2 = chessboard.isTerminal()
		return int(flag1 == me if flag1 != None else flag2 == me)

	def generate(self):
		c1 = time.time()
		c2 = time.time()
		while int(c2 - c1) <= 6:
			self.search()
			c2 = time.time()
		children = self.root.children
		firstStepIndex = max(range(len(children)), key = lambda x: children[x].state.visits)
		chessboard, firstStep = children[firstStepIndex].state.chessboard, self.firstStepMap[firstStepIndex]
		return chessboard, firstStep