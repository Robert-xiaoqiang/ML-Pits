class Cell {
    constructor(state = 'none') {
        this.state = state;
    }
    toString() {
        return String(state);
    }
    copy() {
        return new Cell(this.state);
    }
    setBlack() {
        this.state = 'black';
    }
    setWhite() {
        this.state = 'white';
    }
    setColor(state) {
        this.state = state;
    }
    isBlack() {
        return this.state === 'black';
    }
    isWhite() {
        return this.state === 'white';
    }
    isNone() {
        return this.state === 'none';
    }
    clear() {
        this.state = 'none';
    }
}

class ChessBoard {
    constructor(n) {
        this.data = new Array(n);
        for(let i = 0; i < this.data.length; i++)
            this.data[i] = new Array(n);
        for(let i = 0; i < n; i++)
            for(let j = 0; j < n; j++)
                this.data[i][j] = new Cell();
        this.n = n;
        this.whites = new Map([
            [ '0', { row: 1, col: 0 } ],
            [ '1', { row: 2, col: 0 } ],
            [ '2', { row: 3, col: 0 } ],
            [ '3', { row: 4, col: 0 } ],
            [ '4', { row: 5, col: 0 } ],
            [ '5', { row: 6, col: 0 } ],
            [ '6', { row: 1, col: 7 } ],
            [ '7', { row: 2, col: 7 } ],
            [ '8', { row: 3, col: 7 } ],
            [ '9', { row: 4, col: 7 } ],
            [ '10', { row: 5, col: 7 } ],
            [ '11', { row: 6, col: 7 } ],
        ]);
        this.blacks = new Map([
            [ '0', { row: 0, col: 1 } ],
            [ '1', { row: 0, col: 2 } ],
            [ '2', { row: 0, col: 3 } ],
            [ '3', { row: 0, col: 4 } ],
            [ '4', { row: 0, col: 5 } ],
            [ '5', { row: 0, col: 6 } ],
            [ '6', { row: 7, col: 1 } ],
            [ '7', { row: 7, col: 2 } ],
            [ '8', { row: 7, col: 3 } ],
            [ '9', { row: 7, col: 4 } ],
            [ '11', { row: 7, col: 5 } ],
            [ '12', { row: 7, col: 6 } ],
        ]);
    }
    copy() {
        const ret = ChessBoard(this.n)
        for(let i = 0; i < n; i++)
            for(let j = 0; j < n; j++)
                ret.data[i][j] = new Cell(this.data[i][j].state);
        ret.n = this.n;
        ret.blackCount = this.blackCount;
        ret.whiteCount = this.whiteCount;
        return ret;
    }
    setBlackAt(row, col) {        
        if(this.data[row][col].isWhite) {
            this.blackCount++;
            this.whiteCount--;
        } else if(this.data[row][col].isNone) {
            this.blackCount++;
        } else {
            throw new Exception('ChessBoard::setBlackAt() Exception');
        }
        this.data[row][col].setBlack();
    }
    setWhiteAt(row, col) {
        if(this.data[row][col].isBlack) {
            this.whiteCount++;
            this.blackCount--;
        } else if(this.data[row][col].isNone) {
            this.whiteCount++;
        } else {
            throw new Exception('ChessBoard::setWhiteAt() Exception');
        }
        this.data[row][col].setWhite();
    }
    setAt(row, col, color) {
        if(color === 'black') {
            this.setBlackAt(row, col);
        } else if(color === 'white') {
            this.setWhiteAt(row, col);
        }
    }
    resetAt(row, col) {
        this.data[row][col].clear();
    }
    moveFromTo(fromRow, fromCol, toRow, toCol) {
        this.setAt(toRow, toCol, this.data[fromRow][fromCol]);
        this.resetAt(fromRow, fromCol);
    }
    getAllNextStepAt(row, col) {
        if()
    }
    /**
     * @param player for next step
     * @return array of ChesssBoards
     */
    getAllNextStep(player) {

    }
}