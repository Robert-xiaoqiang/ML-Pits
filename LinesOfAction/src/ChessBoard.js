class Cell {
    constructor(state = 'none') {
        this.state = state;
    }
    toString() {
        return String(this.state);
    }
    copy() {
        return new Cell(String(this.state));
    }
    setBlack() {
        this.state = 'black';
    }
    setWhite() {
        this.state = 'white';
    }
    setState(state) {
        this.state = state;
    }
    getState() {
        return String(this.state);
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
    static playerReverse(player) {
        if(player === 'black') return 'white';
        else if(player === 'white') return 'black';
        else return player;
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
        this.whiteCount = 12;
        this.blackCount = 12;
        for(let i = 1; i <= 6; i++) {
            this.setWhiteAt(i, 0);
            this.setWhiteAt(i, 7);

            this.setBlackAt(0, i);
            this.setBlackAt(7, i);
        }
        //console.log('black CC:', this.getCC('black'));
        //console.log('white CC:', this.getCC('white'));
    }

    copy() {
        const ret = new ChessBoard(this.n)
        for(let i = 0; i < this.n; i++)
            for(let j = 0; j < this.n; j++)
                ret.data[i][j].setState(this.data[i][j].state);
        ret.n = Number(this.n);
        ret.blackCount = Number(this.blackCount);
        ret.whiteCount = Number(this.whiteCount);
        return ret;
    }

    setBlackAt(row, col) {        
        if(this.data[row][col].isWhite()) {
            ;
            this.whiteCount--;
        } else if(this.data[row][col].isNone()) {
            this.blackCount;
        } else {
            throw new Error('ChessBoard::setBlackAt() Exception');
        }
        this.data[row][col].setBlack();
    }

    setWhiteAt(row, col) {
        if(this.data[row][col].isBlack()) {
            ;
            this.blackCount--;
        } else if(this.data[row][col].isNone()) {
            this.whiteCount;
        } else {
            throw new Error('ChessBoard::setWhiteAt() Exception');
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
        this.setAt(toRow, toCol, this.data[fromRow][fromCol].state);
        this.resetAt(fromRow, fromCol);
    }

    getUpdownChessCountFrom(row, col) {
        let ret = 0;
        for(let r = 0; r < this.n; r++) {
            if(!this.data[r][col].isNone()) ret++;
        }
        return ret;
    }

    getLeftrightChessCountFrom(row, col) {
        let ret = 0;
        for(let c = 0; c < this.n; c++) {
            if(!this.data[row][c].isNone()) ret++;
        }
        return ret;
    }

    getDiagonalChessCountFrom(row, col) {
        let ret = 0;
        while(row !== 0 && col !== 0) {
            row--;
            col--;
        }
        for(let d = 0; row + d < this.n && col + d < this.n; d++) {
            if(!this.data[row + d][col + d].isNone()) ret++;
        }
        return ret;
    }
    // from left-bottom to right-top
    getCounterDiagonalChessCountFrom(row, col) {
        let ret = 0;
        while(row !== this.n - 1 && col !== 0) {
            row++;
            col--;
        }
        while(row >= 0 && col < this.n) {
            if(!this.data[row][col].isNone()) ret++;
            row--;
            col++;
        }
        return ret;
    }
    computeDestinationFrom(row, col, rowStep, colStep, count) {
        let isOk = true;
        let player = this.data[row][col].toString();
        let enemy = Cell.playerReverse(player);
        const fromRow = Number(row);
        const fromCol = Number(col);
        for(let i = 0; i < count - 1; i++) {
            row += rowStep;
            col += colStep;
            if(row < 0 || row >= this.n || col < 0 || col >= this.n ||
               this.data[row][col].toString() === enemy) {
                   isOk = false;
                   break;
            }
        }
        if(isOk) {
            row += rowStep;
            col += colStep;
            if(row < 0 || row >= this.n || col < 0 || col >= this.n ||
                this.data[row][col].toString() === player) {
                    isOk = false;
            }
        }
        if(isOk) {
            let ret = this.copy();
            ret.moveFromTo(fromRow, fromCol, row, col);
            return {
                fromRow: fromRow,
                fromCol: fromCol,
                toRow: row,
                toCol: col,
                chessBoard: ret
            };
        } else {
            return null;
        }
    }

    /**
     * @param {*} row
     * @param {*} col
     * 
     * @return array(maxsize 8) of ChessBoard and FromTo
     */
    getAllNextStepAt(row, col) {
        const ret = new Array();
        if(!this.data[row][col].isNone()) {
            let [updown, leftright, diagonal, counterDiagonal] = [
                this.getUpdownChessCountFrom(row, col),
                this.getLeftrightChessCountFrom(row, col),
                this.getDiagonalChessCountFrom(row, col),
                this.getCounterDiagonalChessCountFrom(row, col)
            ];
            let up = this.computeDestinationFrom(row, col, -1, 0, updown);
            if(up !== null) ret.push(up);
            let down = this.computeDestinationFrom(row, col, 1, 0, updown);
            if(down !== null) ret.push(down);

            let left = this.computeDestinationFrom(row, col, 0, -1, leftright);
            if(left !== null) ret.push(left);
            let right = this.computeDestinationFrom(row, col, 0, 1, leftright);
            if(right !== null) ret.push(right);
            
            let leftTop = this.computeDestinationFrom(row, col, -1, -1, diagonal);
            if(leftTop !== null) ret.push(leftTop);
            let rightBottom = this.computeDestinationFrom(row, col, 1, 1, diagonal);
            if(rightBottom !== null) ret.push(rightBottom);
            
            let rightTop = this.computeDestinationFrom(row, col, -1, 1, counterDiagonal);
            if(rightTop !== null) ret.push(rightTop);
            let leftBottom = this.computeDestinationFrom(row, col, 1, -1, counterDiagonal);
            if(leftBottom !== null) ret.push(leftBottom);
        }
        return ret;
    }

    /**
     * @param player for next step
     * @return array of ChesssBoards
     * 
     * @do search all players' position, why cache it before?
     * @then call getAllNextStepAt(position) and push
     */
    getAllNextStep(player) {
        const ret = new Array();
        if(player !== 'none') {
           for(let i = 0; i < this.n; i++) {
               for(let j = 0; j < this.n; j++) {
                   if(this.data[i][j].toString() === player) {
                       const temp = this.getAllNextStepAt(i, j);
                       ret.push(...temp);
                   }
               }
           } 
        }
        return ret;
    }

    // isTerminal() should check before here
    // or maybe undefined
    getRandomNextChessBoard(player) {
        let ans = this.getAllNextStep(player);
        let { fromRow,
        fromCol,
        toRow,
        toCol,
        chessBoard } = ans[Math.floor(Math.random() * ans.length)];
        return chessBoard;
    }
    /**
     * 
     * @param {*} queue 
     * @param {*} visit 
     * @param {*} row to be checked
     * @param {*} col to be checked
     * 
     * @return 0/1
     */
    BFSHelper(queue, visit, row, col, player) {
        if(row >= 0 && row < this.n &&
           col >= 0 && col < this.n &&
           this.data[row][col].state === player &&
           !visit[row][col]) {
            visit[row][col] = true;
            queue.push({ row: row, col: col });
            return 1;
        } else {
            return 0;
        }
    }
    /**
     * 
     * @param {*} row 
     * @param {*} col 
     * 
     * @return return sizeof(some connect component)
     */
    BFS(prow, pcol, visit) {
        let player = this.data[prow][pcol].state;
        let ret = 0;
        let queue = [];
        queue.push({ row: prow, col: pcol });
        visit[prow][pcol] = true;
        ret++;
        while(queue.length) {
            const top = queue.shift();
            let { row, col } = top;
            let topRow = row;
            let topCol = col;

            // up
            ret += this.BFSHelper(queue, visit, topRow - 1, topCol, player);
            // down
            ret += this.BFSHelper(queue, visit, topRow + 1, topCol, player);
            // left
            ret += this.BFSHelper(queue, visit, topRow, topCol - 1, player);
            // right
            ret += this.BFSHelper(queue, visit, topRow, topCol + 1, player);
            // left-top
            ret += this.BFSHelper(queue, visit, topRow - 1, topCol - 1, player);
            // right-bottom
            ret += this.BFSHelper(queue, visit, topRow + 1, topCol + 1, player);
            // right-top
            ret += this.BFSHelper(queue, visit, topRow - 1, topCol + 1, player);
            // left-bottom
            ret += this.BFSHelper(queue, visit, topRow + 1, topCol - 1, player);
        }
        return ret;
    }
    
    /**
     * 
     * @param {*} player 
     * @return Boolean
     */
    isConnect(player) {
        let ret = false;
        let visit = new Array(this.n);
        for(let i = 0; i < this.n; i++) {
            visit[i] = new Array(this.n);
            visit[i].fill(false, 0, this.end);
        }
        if(player !== 'none') {
            let count = 0;
            if(player === 'black') count = this.blackCount;
            else count = this.whiteCount;

            for(let i = 0; i < this.n; i++) {
                for(let j = 0; j < this.n; j++) {
                    if(this.data[i][j].toString() === player) {
                        // someone connect component(CC)
                        ret = this.BFS(i, j, visit) === count;
                        // console.log('BFS: ', this.BFS(i, j, visit), 'count: ', count);
                        break;
                    }
                }
                if(ret) break;
            }
        }
        return ret;
    }
    getCC(player) {
        let ret = 0;
        let nc = 0;
        let count = 0;
        if(player === 'black') count = this.blackCount;
        else count = this.whiteCount;
        let visit = new Array(this.n);
        for(let i = 0; i < this.n; i++) {
            visit[i] = new Array(this.n);
            visit[i].fill(false, 0, this.end);
        }
        for(let i = 0; i < this.n; i++) {
            for(let j = 0; j < this.n; j++) {
                if(this.data[i][j].toString() === player && !visit[i][j]) {
                    nc += this.BFS(i, j, visit);
                    ret += 1;
                    if(nc == count) {
                        break;
                    } else if(nc > count) {
                        console.log('connect error');
                    }
                }
            }
            if(nc == count) {
                break;
            }
        }
        return ret;
    }
    /**
     * @param lastStepPlayer for checking deadlock
     * 
     * @return JavaScript.String for winner
     * 'black', 'white', 'none'
     * @do check connect components of graph
     * @then whether the player has next step chessboard or not
     */
    isTerminal(lastStepPlayer) {
        let ret = 'none';
        let bl = this.getAllNextStep('black').length;
        let wl = this.getAllNextStep('white').length;

        if(this.whiteCount === 1) {
            ret = 'black';
        } else if(this.blackCount === 1) {
            ret = 'white';
        } else if(this.isConnect('black')) {
            ret = 'black';
        } else if(this.isConnect('white')) {
            ret = 'white';
        } else if(bl === 0) {
            if(wl > 0) {
                ret = 'white';
            } else {
                ret = lastStepPlayer;
            }
        } else if(wl === 0) {
            if(bl > 0) {
                ret = 'black';
            } else {
                ret = lstStepPalyer;
            }
        }

        return ret;
    }

    /**
     * @return JavaScript.String for indicative winner
     * 'black', 'white', 'none'
     */
    isGood() {
        // let wcc = this.getCC('white');
        // let bcc = this.getCC('black');
        // if(wcc >= bcc + 4) {
        //     return 'black';
        // } else if(bcc >= wcc + 4) {
        //     return 'white';
        // }
        // if(this.blackCount >= this.whiteCount + 6) {
        //     return 'black';
        // } else if(this.whiteCount >= this.blackCount + 6) {
        //     return 'white';
        // }
        return 'none';
    }
}

export default ChessBoard;