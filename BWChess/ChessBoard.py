class Cell:
	def __init__(self, state = None):
		self.state = state;

	def copy(self) -> 'Cell':
		return Cell(self.state)

	def isBlack(self) -> bool:
		return self.state == 'black'

	def isWhite(self) -> bool:
		return self.state == 'white'

	def setBlack(self):
		self.state = 'black'

	def setWhite(self):
		self.state = 'white'

	def clear(self):
		self.state = None

# n * n Cells (0, 0) left-top
# initialize to None state
# just nested list
# why not ndarray
class ChessBoard:
	def __init__(self, n: int):
		# basic information
		self.data = [[Cell() for i in range(n)] for i in range(n)]
		self.n = n
		self.minRow = 0      # inclusive
		self.maxRow = self.n # exclusive
		self.minCol = 0
		self.maxCol = self.n
		
		# game information
		self.blackCount = 0
		self.whiteCount = 0

	def __init__(self, clone: 'ChessBoard'):
		self.n = int(clone.n)
		self.data = [[clone.at(i, j).copy() for i in range(n)] for j in range(n)]
		self.minRow = int(clone.minRow)
		self.maxRow = int(clone.maxRow)
		self.minCol = int(clone.minCol)
		self.maxCol = int(clone.maxCol)

		self.blackCount = int(clone.blackCount)
		self.whiteCount = int(clone.whiteCount)

	def copy(self) -> 'ChessBoard':
		return ChessBoard(self)

	def checkMinMaxCoords(self, row, col):
		if row < self.minRow: self.minRow = row
		elif row > self.maxRow: self.maxRow = row + 1

		if col < self.minCol: self.minCol = col
		elif col > self.maxCol: self.maxCol = col + 1

	def setAndUpdateBlackAt(self, row: int, col: int):
		self.at(row, col).setBlack()
		self.checkMinMaxCoords(row, col)
		self.blackCount += 1
		self.updateFrom(row, col)

	def setAndUpdateWhiteAt(self, row: int, col: int):
		self.at(row, col).setWhite()
		self.checkMinMaxCoords(row, col)
		self.whiteCount += 1
		self.updateFrom(row, col)

	def setAndUpdateAt(self, row, col, player):
		if player == 'black':
			self.setAndUpdateBlackAt(row, col)
		elif player == 'white':
			self.setAndUpdateWhiteAt(row, col)

	def setAndUpdateOppositeAt(self, row, col):
		positive = self.at(row, col)
		assert positive != None
		if positive == 'black':
			self.setAndUpdateWhiteAt(row, col)
			self.blackCount -= 1
			self.whiteCount += 1
		else:
			self.setAndUpdateBlackAt(row, col)
			self.whiteCount -= 1
			self.blackCount += 1

	def clearAt(self, row, col):
		p = self.at(row, col)
		if p == 'black':
			self.blackCount -= 1
		elif p == 'white':
			self.whiteCount -= 1
		p.clear()
		# self.checkMinMaxCoords(row, col)

	def at(self, row, col):
		return self.data[row][col]
    
    # B eat W
    # W eat B
	def updateFrom(self, row, col):
		# bottom
		updateFromWithStep(row, col, 1, 0)
		# top
		updateFromWithStep(row, col, -1, 0)
		# right
		updateFromWithStep(row, col, 0, 1)
		# left
		updateFromWithStep(row, col, 0, -1)
		# right-bottom
		updateFromWithStep(row, col, 1, 1)
		# left-bottom
		updateFromWithStep(row, col, 1, -1)
		# left-top
		updateFromWithStep(row, col, -1, -1)
		# right-top
		updateFromWithStep(row, col, -1, 1)
	def updateFromWithStep(self, row, col, rowStep, colStep):
		positive = self.at(row, col)
		assert positive != None
		opponent = []
		while self.minRow <= row < self.maxRow and self.minCol <= col < self.maxCol:
			if self.at(row, col) == None:
				break
			elif self.at(row, col) != positive:
				opponent.append((row, col))
			else:
				for r, c in opponent:
					self.setAndUpdateOppositeAt(r, c)
				break;
			row += rowStep
			col += colStep
		return

	# None not terminal
	# black
	# white
	# blank
	def isTerminal():
		flag1 = self.whiteCount + self.blackCount == n * n
		if self.blackCount > self.whiteCount and \
		   (self.whiteCount == 0 or flag1):
			return 'black'
		elif self.whiteCount > self.blackCount and \
		   (self.blackCount == 0 or flag1):
			return 'white'
		elif self.whiteCount == self.blackCount and flag1:
			return 'blank'
		else:
			return None

	def gatAllNextStep(self, player):
		assert player != None
		ret = []
		if self.isTerminal() != None:
			return ret
		for i in range(n):
			for j in range(n):
				if self.get(i, j) == None:
					temp = ChessBoard(self)
					temp.setAndUpdateAt(i, j, player)
					ret.append(temp)
		return ret
