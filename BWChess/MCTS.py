import math

# chessboard
# player play this step now
# black or white

MCTSConstant = 1.414



class MCState:
	def __init__(self, chessboard, player):
		self.chessboard = chessboard
		# black white
		self.player = player
		self.visits = 0
		self.scores = 0.0
		self.uct = None
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
			cur = max(cur.children, key = lambda x: x.state.uct)

		# cur is not extended fully
		simulateBegin = self.extend(cur)
		assert simulateBegin != None
		score = self.simulate(simulateBegin)

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
		
	def generate(self):
		pass