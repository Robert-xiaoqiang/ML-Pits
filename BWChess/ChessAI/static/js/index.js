   // 黑白棋  又叫反棋
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

            this.positive = "black"; // 当前走棋方
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
         * x width
         * y height
         * coordinate in window/screen
         */
        drawDot(x, y, r, color) {
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
        drawChesses(chessboardJSON) {
            this.chesses = chessboardJSON.data;
            for(let i = 0; i<this.chesses.length; i++){
                for(let j = 0; j<this.chesses[i].length; j++){
                    const a = this.chesses[i][j];
                    this.chesses[i][j] = JSON.parse(a);
                    // width x-coordinate
                    // height y-coordinate
                    var x = j * this.cellWidth + this.cellWidth / 2;

                    var y = i * this.cellWidth + this.cellWidth / 2;
                    if(this.chesses[i][j].state === 'black'){
                        this.drawDot(x, y, this.R, 'black');
                    } else if(this.chesses[i][j].state === 'white') {
                        this.drawDot(x, y, this.R, 'white');
                    }
                }
            }
        }
    }