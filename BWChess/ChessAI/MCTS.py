import math
import random
import time
from .ChessBoard import ChessBoard
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
		self.uct = None

	def __init__(self, copy):
		self.chessboard = ChessBoard(copy.chessboard)
		self.player = str(copy.player)
		self.visits = int(copy.visits)
		self.scores = float(copy.scores)
		self.uct = float(coyp.uct)

	@classmthod
	def playerReverse(player):
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
	def __init__(self, copy):
		assert len(copy.children) == 0
		self.state = MCState(copy.state)
		self.parent = copy.parent
		self.children = children.copy()
		self.evaluatedChildren = evaluatedChildren.copy()

	def isExtended(self):
		return len(self.evaluatedChildren) == len(self.children)

	def addChild(self, mctnode: 'MCTNode'):
		self.children.append(mctnode)

	def getChildren(self):
		return self.children

	def getUCT(self) -> float:
		assert self.parent != None and self.visits > 0
		t = self.parent.visits
		return scores / visites + MCTSConstant * math.sqrt(math.log(t / self.visits))

	def updateState(self, visitStep, scoreStep):
		self.state.visits += visitStep
		self.state.scores += scoreStep
		self.state.uct = self.getUCT()

class MCTS:
	def __init__(self, chessboard, player):
		state = MCState(chessboard, player)
		self.root = MCTNode(state, None)
	def search(self):
		if self.chessboard.isTerminal() != None:
			return
		cur = self.root
		while cur.isExtended():
			# multiple maximums ?
			cur = max(cur.children, key = lambda x: x.state.uct)

		# cur is not extended fully
		# simlateBegin is not evaluated
		simulateBegin = self.extend(cur)
		assert simulateBegin != None
		score = self.simulate(MCTNode(simulateBegin))

		inode = simulateBegin
		while inode != None:
			inode.updateState(1, score)
			inode = inode.parent

	def extend(self, cur: MCTNode) -> MCTNode:
		# where is its children?
		if not len(cur.children):
			curChessboard = cur.state.chessboard

			# list of chessboard
			nextSteps = curChessboard.getAllNextStep()
			for np in nextSteps:
				state = MCState(np, MCState.playerReverse(cur.state.player))
				tnode = MCTNode(state, cur)
				cur.addChild(tnode)

		# choose unvisted, visit/evaluate it
		simulateBegin = None
		for c in len(cur.children):
			if (c,) not in cur.evaluatedChildren:
				cur.evaluatedChildren.add((c,))
				simulateBegin = c

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
			chessboard.setAndUpdateRandom(player)
			if chessboard.isTerminal() != None:
				break
			player = MCTNode.playerReverse(player)
			chessboard.setAndUpdateRandom(player)
		return int(chessboard.isTerminal() == me)
	def generate(self):
		c1 = time.time()
		c2 = time.time()
		while int(c2 - c1) <= 10000:
			self.search()
			c2 = time.time()
		return max(self.root.children(), lambda x: x.state.visits).state.chessboard