import random
import copy
import json

random.seed()
class Cell:
	def __init__(self, state = None):
		self.state = state;

	def copy(self) -> 'Cell':
		return Cell(self.state)

	def __str__(self):
		return self.state if self.state != None else 'None'

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

class CellEncoder(json.JSONEncoder):
	def dafault(self, obj):
		print(type(obj))
		if isinstance(obj, Cell):
			d = {
				'state': obj.state
			}
			return json.dumps(d)
		else:
			return super().default(obj)
# n * n Cells (0, 0) left-top
# initialize to None state
# just nested list
# why not ndarray
class ChessBoard:
	def __init__(self, n: int):
		# basic information
		self.data = [[Cell() for i in range(n)] for i in range(n)]
		self.n = n
		self.minRow = 0 # inclusive
		self.maxRow = 0 # exclusive
		self.minCol = 0
		self.maxCol = 0
		
		# game information
		self.blackCount = 0
		self.whiteCount = 0

	# def __init__(self, clone: 'ChessBoard'):
	# 	self.n = int(clone.n)
	# 	self.data = [[clone.at(i, j).copy() for i in range(n)] for j in range(n)]
	# 	self.minRow = int(clone.minRow)
	# 	self.maxRow = int(clone.maxRow)
	# 	self.minCol = int(clone.minCol)
	# 	self.maxCol = int(clone.maxCol)

	# 	self.blackCount = int(clone.blackCount)
	# 	self.whiteCount = int(clone.whiteCount)

	def copy(self) -> 'ChessBoard':
		ret = ChessBoard(self.n)
		ret.n = int(self.n)
		ret.data = [[self.at(i, j).copy() for j in range(self.n)] for i in range(self.n)]
		ret.minRow = int(self.minRow)
		ret.maxRow = int(self.maxRow)
		ret.minCol = int(self.minCol)
		ret.maxCol = int(self.maxCol)

		ret.blackCount = int(self.blackCount)
		ret.whiteCount = int(self.whiteCount)

		return ret

	@classmethod
	def constructorFromDict(cls, d):
		ret = ChessBoard(d['n'])
		ret.__dict__ = d
		return ret

	def checkMinMaxCoords(self, row, col):
		if row < self.minRow: self.minRow = row
		elif row > self.maxRow: self.maxRow = row + 1

		if col < self.minCol: self.minCol = col
		elif col > self.maxCol: self.maxCol = col + 1

	def setWithoutUpdateBlackAt(self, row: int, col: int):
		self.at(row, col).setBlack()
		self.checkMinMaxCoords(row, col)
		self.blackCount += 1

	def setAndUpdateBlackAt(self, row: int, col: int):
		self.setWithoutUpdateBlackAt(row, col)
		self.updateFrom(row, col)

	def setWithoutUpdateWhiteAt(self, row: int, col: int):
		self.at(row, col).setWhite()
		self.checkMinMaxCoords(row, col)
		self.whiteCount += 1

	def setAndUpdateWhiteAt(self, row: int, col: int):
		self.setWithoutUpdateWhiteAt(row, col)
		self.updateFrom(row, col)

	def setAndUpdateAt(self, row, col, player):
		if player == 'black':
			self.setAndUpdateBlackAt(row, col)
		elif player == 'white':
			self.setAndUpdateWhiteAt(row, col)
		else:
			print(player)

	def setAndUpdateOppositeAt(self, row, col):
		positive = self.at(row, col).state
		assert positive != None
		if positive == 'black':
			self.setAndUpdateWhiteAt(row, col)
			self.blackCount -= 1
		else:
			self.setAndUpdateBlackAt(row, col)
			self.whiteCount -= 1

	def setWithoutUpdateOppositeAt(self, row, col):
		positive = self.at(row, col).state
		assert positive != None
		if positive == 'black':
			self.setWithoutUpdateWhiteAt(row, col)
			self.blackCount -= 1
		else:
			self.setWithoutUpdateBlackAt(row, col)
			self.whiteCount -= 1

	def setAndUpdateRandom(self, player):
		noneCount = self.n * self.n - self.blackCount - self.whiteCount
		try:
			step = random.randrange(noneCount)
		except Exception as e:
			print(noneCount, self.n, self.blackCount, self.whiteCount)
		over = False
		for i in range(self.n):
			for j in range(self.n):
				if self.at(i, j).state == None:
					if not step:
						self.setAndUpdateAt(i, j, player)
						over = True
						break
					step -= 1
			if over:
				break

	def clearAt(self, row, col):
		p = self.at(row, col).state
		if p == 'black':
			self.blackCount -= 1
		elif p == 'white':
			self.whiteCount -= 1
		p.clear()
		# self.checkMinMaxCoords(row, col)

	def at(self, row, col):
		return self.data[row][col]

	def updateFromWithStep(self, row, col, rowStep, colStep):
		positive = self.at(row, col).state
		assert positive != None
		opponent = []
		row += rowStep
		col += colStep
		while self.minRow <= row < self.maxRow and self.minCol <= col < self.maxCol:
			if self.at(row, col).state == None:
				break
			elif self.at(row, col).state != positive:
				opponent.append((row, col))
			else:
				for r, c in opponent:
					# self.setAndUpdateOppositeAt(r, c)
					self.setWithoutUpdateOppositeAt(r, c)
				break;
			row += rowStep
			col += colStep
		return
    
    # B eat W
    # W eat B
	def updateFrom(self, row, col):
		# bottom
		self.updateFromWithStep(row, col, 1, 0)
		# top
		self.updateFromWithStep(row, col, -1, 0)
		# right
		self.updateFromWithStep(row, col, 0, 1)
		# left
		self.updateFromWithStep(row, col, 0, -1)
		# right-bottom
		self.updateFromWithStep(row, col, 1, 1)
		# left-bottom
		self.updateFromWithStep(row, col, 1, -1)
		# left-top
		self.updateFromWithStep(row, col, -1, -1)
		# right-top
		self.updateFromWithStep(row, col, -1, 1)

	# None not terminal
	# black
	# white
	# blank
	def isTerminal(self):
		flag1 = self.whiteCount + self.blackCount == self.n * self.n
		if self.blackCount > self.whiteCount and \
		   (flag1):
			return 'black'
		elif self.whiteCount > self.blackCount and \
		   (flag1):
			return 'white'
		elif self.whiteCount == self.blackCount and flag1:
			return 'blank'
		else:
			return None
	'''
	@param player: player for this step
	'''
	def getAllNextStep(self, player):
		assert player != None
		ret = []
		if self.isTerminal() != None:
			return ret
		imin, imax = self.minRow - 1 if self.minRow > 0 else self.minRow, \
					 self.maxRow + 1 if self.maxRow < self.n else self.maxRow
		jmin, jmax = self.minCol - 1 if self.minCol > 0 else self.minCol, \
					 self.maxCol + 1 if self.maxCol < self.n else self.maxCol
		for i in range(imin, imax):
			for j in range(jmin, jmax):
				if self.at(i, j).state == None:
					temp = self.copy()
					temp.setAndUpdateAt(i, j, player)
					ret.append(temp)
		return ret

def ChessBoardObjectHook(dct):
	if 'data' in dct and 'n' in dct and 'minRow' in dct:
		ret = ChessBoard(dct['n'])
		for i in range(dct['n']):
			for j in range(dct['n']):
				ret.data[i][j] = Cell(dct['data'][i][j])
		del dct['data']
		del dct['n']
		ret.__dict__.update(dct)
		return ret
	else:
		return dct

class ChessBoardEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ChessBoard):
			d = {
				'data': [[json.dumps(obj.data[i][j].__dict__) \
				 for j in range(obj.n)]
				 for i in range(obj.n)],
				'n': obj.n,
				'minRow': obj.minRow,
				'maxRow': obj.maxRow,
				'minCol': obj.minCol,
				'maxCol': obj.maxCol,

				'blackCount': obj.blackCount,
				'whiteCount': obj.whiteCount
			}
			return json.dumps(d)
		else:
			return super().default(obj)
