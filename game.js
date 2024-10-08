var pong_arena = {
	canvas : document.getElementById("canvas"),
	keys : {},
	start : function() {
		this.canvas.width = 1000;
		this.canvas.height = 1000;
		this.context = this.canvas.getContext("2d");
		document.body.insertBefore(this.canvas, document.body.childNodes[0]);
		this.interval = setInterval(game_loop, 50);
		window.addEventListener('keydown', function (e) {
			pong_arena.keys = (pong_arena.keys || []);
			pong_arena.keys[e.keyCode] = true;
		});
		window.addEventListener('keyup', function (e) {
			pong_arena.keys[e.keyCode] = false;
		});
	},
	clear : function() {
		this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
	}
};

function paddel(width, height, color, x, y) {
	this.width = width;
	this.height = height;
	this.x = x;
	this.y = y;
	this.score = 0;
	this.name = "";
	var ctx = pong_arena.context;
	ctx.fillStyle = color;
	ctx.fillRect(this.x, this.y, this.width, this.height);
	
	this.update = function() {
		ctx = pong_arena.context;
		ctx.fillStyle = color;
		ctx.fillRect(this.x, this.y, this.width, this.height);
	}
}

function ball() {
	this.width = 10;
	this.height = 10;
	this.x = 500;
	this.y = 500;
	this.dirX = 0;
	this.dirY = 0;
	var ctx = pong_arena.context;
	ctx.fillStyle = "red";
	ctx.fillRect(this.x, this.y, this.width, this.height);
	
	this.update = function() {
		ctx = pong_arena.context;
		ctx.fillStyle = "red";
		ctx.fillRect(this.x, this.y, this.width, this.height);
	}
};

function score(width, height, color, x, y, player) {
	this.width = width;
	this.height = height;
	this.x = x;
	this.y = y;
	this.player = player;
	this.update = function() {
		this.text = player.score;
		ctx = pong_arena.context;
		ctx.font = this.width + " " + this.height;
		ctx.fillStyle = color;
		ctx.fillText(this.text, this.x, this.y);
	}
}

async function startGame() {
	pong_arena.start();
	player1 = new paddel(10, 100, "black", 100, 450);
	player2 = new paddel(10, 100, "black", 900, 450);
	score1 = new score("30px", "Consolas", "black", 100, 100, player1);
	score2 = new score("30px", "Consolas", "black", 900, 100, player2);
	ball = new ball();
}

function move_ball(ball) {
	ball.x += ball.dirX * 0.05;
	ball.y += ball.dirY * 0.05;
}

function handle_player_movement(player1) {
	if (pong_arena.keys[87])
		socket.send("up");
	if (pong_arena.keys[83])
		socket.send("down");
}

function game_loop() {
	handle_player_movement(player1);
	pong_arena.clear();
	player1.update();
	player2.update();
	score1.update();
	score2.update();
	move_ball(ball);
	ball.update();
}

var socket = new WebSocket("ws://localhost:8765"); // TODO Change this to the real HOST

let name = window.prompt("Pls type your name", "");
let opponent = "";

var controlled_player = undefined;
var other_player = undefined;
var game_running = false;

var player1, player2, canvas;

socket.onmessage = function (event) {
	if (event.data === "start")
		startGame();
	if (event.data === "youare:1")
	{
		controlled_player = player1;
		other_player = player2;
		other_player.name = name;
		controlled_player.name = temp_name;
	}
	if (event.data === "youare:2")
	{
		controlled_player = player2;
		other_player = player1;
		controlled_player.name = name;
		other_player.name = temp_name;
	}
	if (event.data.startsWith("score:"))
	{
		console.log(event.data);
		console.log(player1.name);
		console.log(player2.name);
		data = event.data.split(":");
		if (data[1] == player1.name)
			player1.score = parseInt(data[2]);
		else if (data[1] == player2.name)
			player2.score = parseInt(data[2]);
		score1.update();
		score2.update();
		ball.x = 500;
		ball.y = 500;
	}
	if (event.data.startsWith("opponent:"))
	{
		opponent = event.data.split(":", 2)[1];
		temp_name = opponent;
	}
	if (event.data.startsWith("mov:"))
	{
		newdir = event.data.split(":")
		ball.dirY = parseInt(newdir[1]);
		ball.dirX = parseInt(newdir[2]);
	}
	if (event.data.startsWith("pos:"))
	{
		newpos = event.data.split(":");
		ball.y = parseInt(newpos[1]);
		ball.x = parseInt(newpos[2]);
	}
	if (controlled_player === undefined || other_player === undefined)
		return ;
	if (event.data.startsWith(controlled_player.name + ":"))
	{
		newpos = event.data.split(":");
		controlled_player.y = parseInt(newpos[1]);
		controlled_player.x = parseInt(newpos[2]);
	}
	if (event.data.startsWith(other_player.name + ":"))
	{
		newpos = event.data.split(":");
		other_player.y = parseInt(newpos[1]);
		other_player.x = parseInt(newpos[2]);
	}
}

socket.send(name);
