function updateFrom(chessboardJSON, row, col) {
    updateFromWithStep(chessboardJSON, row, col, 1, 0);
    updateFromWithStep(chessboardJSON, row, col, -1, 0);
    updateFromWithStep(chessboardJSON, row, col, 0, 1);
    updateFromWithStep(chessboardJSON, row, col, 0, -1);

    // right-bottom
    updateFromWithStep(chessboardJSON, row, col, 1, 1);
    updateFromWithStep(chessboardJSON, row, col, 1, -1);
    updateFromWithStep(chessboardJSON, row, col, -1, -1);
    // right-top
    updateFromWithStep(chessboardJSON, row, col, -1, 1);
}

function updateFromWithStep(chessboardJSON, row, col, rowStep, colStep) {
    let minRow = chessboardJSON['minRow'];
    let maxRow = chessboardJSON['maxRow'];
    let minCol = chessboardJSON['minCol'];
    let maxCol = chessboardJSON['maxCol'];
    let data = chessboardJSON['data'];
    let positive = data[row][col].state;
    let opponent = [ ];
    row += rowStep;
    col += colStep;
    while(row >= minRow && row < maxRow && col >= minCol && col < maxCol) {
        let cur = data[row][col];
        if(!cur.state) {
            break;
        } else if(cur.state !== positive) {
            opponent.push([row, col])
            console.log('push', row, col);
        } else {
            console.log('reverse', opponent);
            for(let [i, j] of opponent) {
                data[i][j] = {
                    'state': positive
                };
            }
            if(positive === 'black') {
                chessboardJSON['blackCount'] += opponent.length;
                chessboardJSON['whiteCount'] -= opponent.length;
            } else {
                chessboardJSON['whiteCount'] += opponent.length;
                chessboardJSON['blackCount'] -= opponent.length;
            }
            break;
        }
        row += rowStep;
        col += colStep;
    }
    return;
}

function checkMinMaxCoords(chessboardJSON, row, col) {
    if(chessboardJSON['minRow'] === chessboardJSON['maxRow']) {
        chessboardJSON['minRow'] = row;
        chessboardJSON['maxRow'] = row + 1;
        chessboardJSON['minCol'] = col;
        chessboardJSON['maxCol'] = col + 1;
    } else {
        if(row < chessboardJSON['minRow']) chessboardJSON['minRow'] = row;
        if(row >= chessboardJSON['maxRow']) chessboardJSON['maxRow'] = row + 1;

        if(col < chessboardJSON['minCol']) chessboardJSON['minCol'] = col;
        if(col >= chessboardJSON['maxCol']) chessboardJSON['maxCol'] = col + 1;
    }
}

class Reversi {
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

        this.init();
    }

    // 初始化数据
    init () {
        this.initCanvas();
        this.renderUi();
    }

    // 设置棋盘的宽高
    initCanvas () {
        this.canvas.width = this.width;
        this.canvas.height = this.height;
    }


    renderUi() {
        //清除之前的画布
        this.ctx.clearRect(0,0,this.width,this.height);

        // 重绘画布
        this.drawMap();
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
        this.ctx.arc(x, y, r, 0, 2*Math.PI);
        this.ctx.closePath();

        this.ctx.fillStyle = color;
        this.ctx.fill();
    }

    // 画棋盘
    drawMap() {
        // 背景
        this.ctx.beginPath();
        this.ctx.rect(0,0,this.width,this.height);
        this.ctx.closePath();
        this.ctx.fillStyle = "#ffa5e8";
        this.ctx.fill();

        // 画横线
        this.ctx.beginPath();
        for(let i=0;i<this.rowCount;i++) {
            this.ctx.moveTo(0,this.cellWidth*i);
            this.ctx.lineTo(this.cellWidth*this.rowCount,this.cellWidth*i);
        }
        this.ctx.stroke();

        // 画纵线
        this.ctx.beginPath();
        for(let i=0;i<this.colCount;i++) {
            this.ctx.moveTo(this.cellWidth*i,0);
            this.ctx.lineTo(this.cellWidth*i,this.cellWidth*this.colCount);
        }
        this.ctx.stroke();
    }

    // 画所有的棋子
    // Python nested list -> JavaScript 2-deminsion array
    drawChesses(chessboardJSON) {
        this.renderUi();
        this.chesses = chessboardJSON.data;
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
}