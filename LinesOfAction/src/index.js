import ChessBoard from './ChessBoard';
import MCTS from './MCTS';
function playerReverse(player) {
    if(player === 'black') {
        return 'white';
    } else if(player === 'white') {
        return 'black';
    } else {
        return null;
    }
}

class LinesOfAction {
    constructor (canvasId){
        this.canvasId = canvasId;
        this.resetData();
    }

    // 重置数据，再来一局
    resetData (){
        var body = document.documentElement || document.body;
        var minWidth = Math.min(body.clientWidth, body.clientHeight);
        // 属性
        this.chesses = null; // 棋子数组 二位数组[[],[]]

        this.rowCount = 8; // 行数

        this.colCount = this.rowCount;// 列数

        this.cellWidth = minWidth/this.rowCount; //每个格子的宽

        this.width = this.rowCount * this.cellWidth; // 棋盘的宽

        this.height = this.width; // 棋盘的高

        this.R = this.cellWidth * 0.4; // 棋子半径

        this.positive = 'black'; // 当前走棋方
        this.canvas = document.getElementById(this.canvasId); // canvas DOM
        this.ctx = this.canvas.getContext("2d"); // canvas环境
        this.chessBoard = new ChessBoard(8);

        this.init();
    }

    // 初始化数据
    init () {
        this.initCanvas();
        this.renderUI();
    }

    // 设置棋盘的宽高
    initCanvas () {
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        
        // IoC & IoD
        this.canvas.addEventListener('click', e => {
            let offset = this.canvas.getBoundingClientRect();
            let x = Math.floor((e.clientX - offset.left) / this.cellWidth);
            let y = Math.floor((e.clientY - offset.top) / this.cellWidth);

            // console.log(x, y, 'click position(X, Y)');
            if(!this.fromRow && !this.fromCol) {
                // have no chess chosen
                if(this.chessBoard.data[y][x].state === this.positive) {
                    this.renderUI();
                    this.fromRow = y;
                    this.fromCol = x;
                    this.allNextStep = this.chessBoard.getAllNextStepAt(y, x);
                    for(let s of this.allNextStep) {
                        let { fromRow, fromCol, toRow, toCol, chessBoard } = s;
                        this.drawNextPosition(toRow, toCol);
                    }                                  
                }
            } else if(this.fromRow === y && this.fromCol === x){
                // have chess and the same with before
                // 1st invalidate
                this.fromRow = null;
                this.fromCol = null;
                this.renderUI();               
            } else {
                // have chess and different from before

                // reselect 1st chess
                if(this.chessBoard.data[y][x].state === this.positive) {
                    this.renderUI();
                    this.fromRow = y;
                    this.fromCol = x;
                    this.allNextStep = this.chessBoard.getAllNextStepAt(y, x);
                    for(let s of this.allNextStep) {
                        let { fromRow, fromCol, toRow, toCol, chessBoard } = s;
                        this.drawNextPosition(toRow, toCol);
                    }   
                } else if(!this.validateStep(y, x)) {
                    // select 2nd chess error
                    // 1st also validate
                    alert('落子错误');
                } else {
                    // select 2nd chess successfully
                    // 1st invalidate, at last
                    //window.setTimeout(() => {
                        this.chessBoard.moveFromTo(this.fromRow, this.fromCol, y, x);
                        this.renderUI();      
                        console.log('winner:', this.chessBoard.isTerminal(this.positive));
                        this.fromRow = null;
                        this.fromCol = null;
                    //}, 1);

                    let temp = this.chessBoard.isTerminal(this.positive);
                    if(temp !== 'none') {
                        window.setTimeout(() => {
                            alert('游戏结束, ' + temp + '胜');
                            this.chessBoard = new ChessBoard(8);
                            this.renderUI();
                        }, 1);

                        // this reture is necessary
                        // MCTS raise error if terminal
                        return;
                    }
                    
                    window.setTimeout(() => {
                        let mcts = new MCTS(this.chessBoard, this.positive);
                        let { chessBoard, firstStep, duration } = mcts.generate();
                        this.chessBoard = chessBoard;
                        this.renderUI();
                        this.drawLastPosition(firstStep.fromRow, firstStep.fromCol);
                        let textDiv = document.getElementById('textDiv');
                        textDiv.innerHTML = duration + 'ms';

                        temp = this.chessBoard.isTerminal(this.positive);
                        if(temp !== 'none') {
                            window.setTimeout(() => {
                                alert('游戏结束, ' + temp + '胜');
                                this.chessBoard = new ChessBoard(8);
                                this.renderUI();
                            }, 1);
                            return;
                        }
                    }, 1);

                    console.log('after AI winner:', this.chessBoard.isTerminal(this.positive));
                    console.log('black CC:', this.chessBoard.getCC('black'));
                    console.log('white CC:', this.chessBoard.getCC('white'));

                    console.log('black count:', this.chessBoard.blackCount);
                    console.log('white count:', this.chessBoard.whiteCount);
                }
            }
            return;
        }, false);
    }


    renderUI() {
        // 清除之前的画布
        this.ctx.clearRect(0,0,this.width,this.height);

        // 重绘画布
        this.drawMap();

        // 绘制棋子
        this.drawChesses(this.chessBoard);
        return true;
    }

    /**
     * i row -> y height size
     * j col -> x width size
     * coordinate in window/screen
     */
    drawDot(i, j, r, color) {
        let x = j * this.cellWidth + this.cellWidth / 2;
        let y = i * this.cellWidth + this.cellWidth / 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, r, 0, 2 * Math.PI);
        this.ctx.closePath();

        this.ctx.fillStyle = color;
        this.ctx.fill();
    }

    // 画棋盘
    drawMap() {

        this.ctx.beginPath();
        this.ctx.rect(0,0,this.width,this.height);
        this.ctx.closePath();
        this.ctx.fillStyle = '#f4a460';
        this.ctx.fill();

        // 画横线
        this.ctx.beginPath();
        for(let i=0;i<this.rowCount;i++) {
            this.ctx.moveTo(0,this.cellWidth*i);
            this.ctx.lineTo(this.cellWidth*this.rowCount,this.cellWidth*i);
        }
        this.ctx.strokeStyle = 'blue';
        this.ctx.stroke();

        // 画纵线
        this.ctx.beginPath();
        for(let i=0;i<this.colCount;i++) {
            this.ctx.moveTo(this.cellWidth*i,0);
            this.ctx.lineTo(this.cellWidth*i,this.cellWidth*this.colCount);
        }
        this.ctx.strokeStyle = 'blue';
        this.ctx.stroke();
    }

    // 画所有的棋子
    // Python nested list -> JavaScript 2-deminsion array
    drawChesses(chessBoard) {
        this.chesses = chessBoard.data;
        for(let i = 0; i<this.chesses.length; i++){
            for(let j = 0; j<this.chesses[i].length; j++){
                if(typeof(this.chesses[i][j]) === 'string') {
                    this.chesses[i][j] = JSON.parse(this.chesses[i][j]);
                }
                if(this.chesses[i][j].state === 'black'){
                    this.drawDot(i, j, this.R, 'black');
                } else if(this.chesses[i][j].state === 'white') {
                    this.drawDot(i, j, this.R, 'white');
                }
            }
        }
    }

    drawNextPosition(row, col) {
        let x = col * this.cellWidth + this.cellWidth / 2;
        let y = row * this.cellWidth + this.cellWidth / 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, this.R, 0, 2 * Math.PI);
        this.ctx.closePath();
        this.ctx.strokeStyle = 'green';
        this.ctx.stroke();
    }

    drawLastPosition(row, col) {
        let x = col * this.cellWidth + this.cellWidth / 2;
        let y = row * this.cellWidth + this.cellWidth / 2;
        this.ctx.beginPath();
        this.ctx.arc(x, y, this.R, 0, 2 * Math.PI);
        this.ctx.closePath();
        this.ctx.strokeStyle = 'red';
        this.ctx.stroke();
    }

    validateStep(row, col) {
        let ret = false;
        for(let s of this.allNextStep) {
            let { fromRow, fromCol, toRow, toCol, chessBoard } = s;
            if(toRow === row && toCol === col) {
                ret = true;
                break;
            }
        }
        return ret;
    }
}

var loa = new LinesOfAction('blackWhite');