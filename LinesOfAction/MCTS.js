import ChessBoard from './ChessBoard';

var MCTSConstant = 1.414;

class MCState {
    // player for the lastStep in this cheesboard
    constructor(chessBoard, player) {
        this.chessBoard = chessBoard;
        // black/white
        this.player = player;
        this.visits = 0;
        this.scores = 0.0;
        this.uct = 0.0;
    }
    copy() {
        const ret = new MCState(this.chessBoard.copy(), String(this.player));
        ret.visits = Number(this.visits);
        ret.scores = Number(this.scores);
        ret.uct = Number(this.uct);
    }
    static playerReverse(player) {
        if(player === 'white') {
            return 'black';
        } else if(player === 'black') {
            return 'white';
        } else {
            return player;
        }
    }
}

class MCTNode {
    constructor(state, parent) {
        this.state = state;
        this.parent = parent;
        this.children = new Array();
        this.bestChild = null;
        // index in this.children
        this.evaluatedChildren = new Set();
    }
    /**
     * @note parent is not copied
     * why???
     * Is it safe?
     */
    copy() {
        const ret = new MCTNode(this.state.copy(), this.parent);
        if(this.bestChild !== null || this.children.length !== 0) {
            alert('shallow copy happened!');
        }
        for(let i = 0; i < this.children.length; i++)
            ret.children.push(this.children[i]);
        ret.bestChild = this.bestChild !== null ? this.bestChild.copy() : null;
        for(let key of this.evaluatedChildren)
            ret.evaluatedChildren.add(key);
    }

    isExtended() {
        return this.children.length && this.children.length === this.evaluatedChildren.size;
    }

    addChild(mctnode) {
        this.children.push(mctnode);
    }

    getChildren() {
        return this.children;
    }

    getUCT() {
        if(this.parent !== null && this.state.visits > 0) {
            t = this.parent.state.visits;
            return this.state.scores / this.state.visits + MCTSConstant * Math.sqrt(Math.log(t) / this.state.visits);
        } else {
            throw new Exception('MCTNode::getUCT() Exception');
        }
    }

    updateState(visitStep, scoreStep) {
        this.state.visits += visitStep;
        this.state.scores += scoreStep;
        this.state.uct = this.getUCT();
    }
}

class MCTS {
    /**
     * 
     * @param {*} chessBoard 
     * @param {*} player for the lastStep in this cheesboard
     */
    constructor(chessBoard, player) {
        let state = new MCState(chessBoard, player)
        this.root = new MCTNode(state, null);
        this.rootPlayer = player;
        this.winner = MCState.playerReverse(player);
        this.firstStepMap = new Array();
    }

    extend(cur) {
        if(!cur.children.length) {
            curChessBoard = cur.state.chessBoard;
            curPlayer = cur.state.player;

            nextPlayer = MCState.playerReverse(curPlayer);
            nextSteps = curChessBoard.getAllNextStep(nextPlayer);
            for(let e of nextSteps) {
                let { fromRow, fromCol, toRow, toCol, chessBoard } = e;
                let state = new MCState(chessBoard, nextPlayer);
                let mctnode = new MCTNode(state, cur);
                cur.addChild(mctnode);
                if(cur.parent === null)
                    this.firstStepMap.push({
                        fromRow: fromRow,
                        fromCol: fromCol,
                        toRow: toRow,
                        toCol: toCol
                    });
            }
        }
        let ret = null;
        for(let i = 0; i < cur.children.length; i++) {
            if(!cur.evaluatedChildren.has(i)) {
                cur.evaluatedChildren.add(i);
                ret = cur.children[i];
            }
        }
        return ret;
    }

    simulate(simulateBegin) {
        let player = simulateBegin.state.player;
        let me = this.winner;
        let chessBoard = simulateBegin.state.chessBoard;

        while(chessBoard.isTerminal(player) === 'none') {
            player = MCState.playerReverse(player);
            chessBoard = chessBoard.getRandomNextChessBoard(player);
            if(chessBoard.isTerminal(player) !== 'none')
                break;
            player = MCState.playerReverse(player);
            chessBoard = chessBoard.getRandomNextChessBoard(player);
        }
        return Number(chessBoard.isTerminal(player) === me);
    }
    search() {
        if(this.root.state.chessBoard.isTerminal(this.rootPlayer) !== 'none') return;
        cur = this.root;
        cur.state.visits++;
        /**
         * tree policy
         * bestChild with the most UCT
         */
        while(cur.isExtended()) {
            cur = cur.bestChild;
            cur.state.visits++;
        }
        /**
         * default policy by random/ordering
         * cur is not extended fully
         * simulation begins with its one child
         */
        simulateBegin = this.extend(cur);
        let score = 0;
        let bpBegin = null;
        if(simulateBegin === null) {
            // cur.state.chessBoard.isTerminal()
            score = Number(cur.state.chessBoard.isTerminal(this.rootPlayer) === this.winner);
            bpBegin = cur;
        } else {
            // cur.state.chessBoard.isTermial() not
            // simulate until terminal
            score = this.simulate(simulateBegin.copy());
            simulateBegin.state.visits += 1;
            bpBegin = simulateBegin;
        }
        let bpCur = bpBegin;
        while(bpCur.parent !== null) {
            bpCur.updateState(0, score);
            let parent = npCur.parent;
            for(let c of parent.children) {
                // compare by reference
                if(c !== bpCur && c.state.visits) {
                    c.updateState(0, 0);
                }
                let tempUCT = c.state.uct;
                if(parent.bestChild === null ||
                   parent.bestChild.state.uct < tempUCT) {
                       parent.bestChild = c;
                }
            }
            beCur = parent;
        }
    }

    generate() {
        let date = new Date();
        let c1 = date.getTime();
        let c2 = date.getTime();
        while(Number(c2 - c1) <= 6000) {
            this.search();
            c2 = date.getTime();
        }
        let children = this.root.children;
        // index for maximal state.visits in children
        let firstStepIndex = children.reduce((previous, curElement, curIndex, arr) => {
            return curElement.state.visits > arr[previous].state.visits ? curIndex : previous;
        }, 0);
        let chessBoard = children[firstStepIndex].state.chessBoard;
        let firstStep = this.firstStepMap[firstStepIndex];

        return {
            chessBoard: chessBoard,
            firstStep: firstStep
        }
    }
}