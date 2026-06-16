import math
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

# Create the HTML/JavaScript game file
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tank Game</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #222;
            font-family: Arial, sans-serif;
        }
        
        #gameContainer {
            position: relative;
            width: 1000px;
            height: 600px;
        }
        
        canvas {
            border: 3px solid #fff;
            background: #404040;
            display: block;
        }
        
        #menu, #gameOver, #paused {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 100;
            text-align: center;
        }
        
        #gameOver, #paused {
            display: none;
        }
        
        h1 {
            font-size: 48px;
            margin: 20px;
            color: #ffff00;
        }
        
        h2 {
            font-size: 36px;
            margin: 20px;
        }
        
        .controls {
            display: flex;
            justify-content: space-around;
            width: 100%;
            margin: 40px 0;
        }
        
        .player-controls {
            flex: 1;
            padding: 20px;
        }
        
        .player-controls h3 {
            font-size: 24px;
            margin: 10px 0;
        }
        
        .player-controls p {
            font-size: 16px;
            line-height: 1.8;
            margin: 5px 0;
        }
        
        .p1 {
            color: #00ffff;
        }
        
        .p2 {
            color: #ff0000;
        }
        
        button {
            padding: 15px 40px;
            font-size: 20px;
            background: #00aa00;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            margin-top: 20px;
        }
        
        button:hover {
            background: #00dd00;
        }
        
        .winner {
            color: #ffff00;
            font-size: 32px;
            margin: 20px 0;
        }
        
        #hud {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            color: white;
            font-family: monospace;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="1000" height="600"></canvas>
        
        <div id="hud">
            <div>
                <div style="color: #00ffff;">P1 Health: <span id="p1Health">100</span></div>
                <div style="color: #00ffff;">P1 Ammo: <span id="p1Ammo">20</span></div>
            </div>
            <div style="text-align: right;">
                <div style="color: #ff0000;">P2 Health: <span id="p2Health">100</span></div>
                <div style="color: #ff0000;">P2 Ammo: <span id="p2Ammo">20</span></div>
            </div>
        </div>
        
        <div id="menu">
            <h1>TANK GAME</h1>
            <div class="controls">
                <div class="player-controls p1">
                    <h3>Player 1 (Cyan)</h3>
                    <p>Arrows: Move</p>
                    <p>Z/X: Rotate</p>
                    <p>Right Ctrl: Shoot</p>
                </div>
                <div class="player-controls p2">
                    <h3>Player 2 (Red)</h3>
                    <p>WASD: Move</p>
                    <p>Q/E: Rotate</p>
                    <p>Space: Shoot</p>
                </div>
            </div>
            <button onclick="startGame()">Press ENTER or Click to Start</button>
        </div>
        
        <div id="paused">
            <h1>PAUSED</h1>
            <p style="font-size: 24px;">Press ESC to Resume</p>
        </div>
        
        <div id="gameOver">
            <h1>GAME OVER</h1>
            <div class="winner" id="winnerText"></div>
            <button onclick="restartGame()">Press ENTER or Click to Restart</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Game states
        const GameState = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over'
        };
        
        // Colors
        const Colors = {
            BLACK: '#000000',
            WHITE: '#ffffff',
            RED: '#ff0000',
            CYAN: '#00ffff',
            GREEN: '#00ff00',
            GRAY: '#808080',
            DARK_GRAY: '#404040',
            YELLOW: '#ffff00',
            ORANGE: '#ffa500'
        };
        
        let gameState = GameState.MENU;
        let keys = {};
        
        class Tank {
            constructor(x, y, color, keysConfig) {
                this.x = x;
                this.y = y;
                this.color = color;
                this.width = 40;
                this.height = 30;
                this.angle = 0;
                this.health = 100;
                this.maxHealth = 100;
                this.keys = keysConfig;
                this.ammo = 20;
                this.maxAmmo = 20;
                this.cooldown = 0;
                this.speed = 3;
                this.rotationSpeed = 3;
            }
            
            handleInput(keys) {
                if (keys[this.keys.left]) this.x -= this.speed;
                if (keys[this.keys.right]) this.x += this.speed;
                if (keys[this.keys.up]) this.y -= this.speed;
                if (keys[this.keys.down]) this.y += this.speed;
                
                this.x = Math.max(this.width / 2, Math.min(this.x, canvas.width - this.width / 2));
                this.y = Math.max(this.height / 2, Math.min(this.y, canvas.height - this.height / 2));
            }
            
            rotate(direction) {
                this.angle += direction * this.rotationSpeed;
                this.angle = (this.angle + 360) % 360;
            }
            
            takeDamage(amount) {
                this.health -= amount;
                return this.health <= 0;
            }
            
            draw(ctx) {
                // Tank body
                ctx.fillStyle = this.color;
                ctx.fillRect(
                    this.x - this.width / 2,
                    this.y - this.height / 2,
                    this.width,
                    this.height
                );
                
                // Turret (barrel)
                const barrelLength = 25;
                const radians = (this.angle * Math.PI) / 180;
                const barrelX = this.x + Math.cos(radians) * barrelLength;
                const barrelY = this.y + Math.sin(radians) * barrelLength;
                
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(barrelX, barrelY);
                ctx.stroke();
                
                // Health bar
                this.drawHealthBar(ctx);
            }
            
            drawHealthBar(ctx) {
                const barWidth = 40;
                const barHeight = 5;
                const fill = (this.health / this.maxHealth) * barWidth;
                
                ctx.fillStyle = Colors.RED;
                ctx.fillRect(this.x - barWidth / 2, this.y - this.height / 2 - 10, barWidth, barHeight);
                
                let healthColor = Colors.GREEN;
                if (this.health <= 50) healthColor = Colors.YELLOW;
                if (this.health <= 25) healthColor = Colors.RED;
                
                ctx.fillStyle = healthColor;
                ctx.fillRect(this.x - barWidth / 2, this.y - this.height / 2 - 10, fill, barHeight);
            }
        }
        
        class Bullet {
            constructor(x, y, angle, owner) {
                this.x = x;
                this.y = y;
                this.angle = angle;
                this.owner = owner;
                this.speed = 7;
                this.radius = 4;
                const radians = (angle * Math.PI) / 180;
                this.vx = Math.cos(radians) * this.speed;
                this.vy = Math.sin(radians) * this.speed;
                this.lifetime = 300;
            }
            
            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.lifetime--;
            }
            
            isAlive() {
                return (this.x > 0 && this.x < canvas.width &&
                        this.y > 0 && this.y < canvas.height &&
                        this.lifetime > 0);
            }
            
            draw(ctx) {
                ctx.fillStyle = Colors.YELLOW;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        class Explosion {
            constructor(x, y, radius = 30) {
                this.x = x;
                this.y = y;
                this.radius = radius;
                this.maxRadius = radius;
                this.lifetime = 30;
                this.maxLifetime = 30;
            }
            
            update() {
                this.lifetime--;
                this.radius = (this.lifetime / this.maxLifetime) * this.maxRadius;
            }
            
            isAlive() {
                return this.lifetime > 0;
            }
            
            draw(ctx) {
                ctx.strokeStyle = Colors.ORANGE;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
        
        // Game variables
        let player1, player2;
        let bullets = [];
        let explosions = [];
        let winner = null;
        
        function initGame() {
            player1 = new Tank(150, canvas.height / 2, Colors.CYAN, {
                left: 'ArrowLeft',
                right: 'ArrowRight',
                up: 'ArrowUp',
                down: 'ArrowDown',
                rotateLeft: 'z',
                rotateRight: 'x',
                shoot: 'Control'
            });
            
            player2 = new Tank(canvas.width - 150, canvas.height / 2, Colors.RED, {
                left: 'a',
                right: 'd',
                up: 'w',
                down: 's',
                rotateLeft: 'q',
                rotateRight: 'e',
                shoot: ' '
            });
            
            bullets = [];
            explosions = [];
            winner = null;
        }
        
        function startGame() {
            gameState = GameState.PLAYING;
            document.getElementById('menu').style.display = 'none';
        }
        
        function restartGame() {
            gameState = GameState.MENU;
            document.getElementById('gameOver').style.display = 'none';
            document.getElementById('menu').style.display = 'flex';
            initGame();
        }
        
        function shoot(tank) {
            if (tank.cooldown <= 0 && tank.ammo > 0) {
                const bullet = new Bullet(tank.x, tank.y, tank.angle, tank);
                bullets.push(bullet);
                tank.ammo--;
                tank.cooldown = 10;
            }
        }
        
        function checkCollisions() {
            for (let i = bullets.length - 1; i >= 0; i--) {
                const bullet = bullets[i];
                
                // Check collision with player 1
                if (bullet.owner !== player1) {
                    const dx = bullet.x - player1.x;
                    const dy = bullet.y - player1.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < player1.width) {
                        explosions.push(new Explosion(bullet.x, bullet.y, 25));
                        if (player1.takeDamage(10)) {
                            winner = player2;
                            gameState = GameState.GAME_OVER;
                            showGameOver();
                        }
                        bullets.splice(i, 1);
                        continue;
                    }
                }
                
                // Check collision with player 2
                if (bullet.owner !== player2) {
                    const dx = bullet.x - player2.x;
                    const dy = bullet.y - player2.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance < player2.width) {
                        explosions.push(new Explosion(bullet.x, bullet.y, 25));
                        if (player2.takeDamage(10)) {
                            winner = player1;
                            gameState = GameState.GAME_OVER;
                            showGameOver();
                        }
                        bullets.splice(i, 1);
                        continue;
                    }
                }
                
                if (!bullet.isAlive()) {
                    bullets.splice(i, 1);
                }
            }
        }
        
        function showGameOver() {
            const winnerName = winner === player1 ? 'Player 1 (Cyan)' : 'Player 2 (Red)';
            document.getElementById('winnerText').textContent = winnerName + ' WINS!';
            document.getElementById('gameOver').style.display = 'flex';
        }
        
        function update() {
            if (gameState !== GameState.PLAYING) return;
            
            player1.cooldown = Math.max(0, player1.cooldown - 1);
            player2.cooldown = Math.max(0, player2.cooldown - 1);
            
            // Handle input
            player1.handleInput(keys);
            player2.handleInput(keys);
            
            if (keys[player1.keys.rotateLeft]) player1.rotate(-1);
            if (keys[player1.keys.rotateRight]) player1.rotate(1);
            if (keys[player1.keys.shoot]) shoot(player1);
            
            if (keys[player2.keys.rotateLeft]) player2.rotate(-1);
            if (keys[player2.keys.rotateRight]) player2.rotate(1);
            if (keys[player2.keys.shoot]) shoot(player2);
            
            // Update bullets
            for (let bullet of bullets) {
                bullet.update();
            }
            
            // Update explosions
            for (let i = explosions.length - 1; i >= 0; i--) {
                explosions[i].update();
                if (!explosions[i].isAlive()) {
                    explosions.splice(i, 1);
                }
            }
            
            // Check collisions
            checkCollisions();
            
            // Regenerate ammo
            if (player1.ammo < player1.maxAmmo) player1.ammo += 0.02;
            if (player2.ammo < player2.maxAmmo) player2.ammo += 0.02;
        }
        
        function draw() {
            // Clear canvas
            ctx.fillStyle = Colors.DARK_GRAY;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = Colors.GRAY;
            ctx.lineWidth = 1;
            for (let x = 0; x < canvas.width; x += 50) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += 50) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
            
            if (gameState === GameState.PLAYING || gameState === GameState.PAUSED) {
                // Draw tanks
                player1.draw(ctx);
                player2.draw(ctx);
                
                // Draw bullets
                for (let bullet of bullets) {
                    bullet.draw(ctx);
                }
                
                // Draw explosions
                for (let explosion of explosions) {
                    explosion.draw(ctx);
                }
                
                // Update HUD
                document.getElementById('p1Health').textContent = Math.max(0, Math.floor(player1.health));
                document.getElementById('p1Ammo').textContent = Math.floor(player1.ammo);
                document.getElementById('p2Health').textContent = Math.max(0, Math.floor(player2.health));
                document.getElementById('p2Ammo').textContent = Math.floor(player2.ammo);
            }
        }
        
        // Keyboard event listeners
        document.addEventListener('keydown', (e) => {
            keys[e.key] = true;
            
            if (e.key === 'Enter') {
                if (gameState === GameState.MENU) startGame();
                else if (gameState === GameState.GAME_OVER) restartGame();
            }
            
            if (e.key === 'Escape') {
                if (gameState === GameState.PLAYING) {
                    gameState = GameState.PAUSED;
                    document.getElementById('paused').style.display = 'flex';
                } else if (gameState === GameState.PAUSED) {
                    gameState = GameState.PLAYING;
                    document.getElementById('paused').style.display = 'none';
                }
            }
        });
        
        document.addEventListener('keyup', (e) => {
            keys[e.key] = false;
        });
        
        // Game loop
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        
        // Initialize and start
        initGame();
        gameLoop();
    </script>
</body>
</html>
'''

def create_game():
    """Create the HTML game file"""
    with open('tank_game.html', 'w') as f:
        f.write(html_content)
    print("✓ Created tank_game.html")

def serve_game(port=8000):
    """Serve the game on a local server"""
    create_game()
    
    class GameHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/tank_game.html'
            return SimpleHTTPRequestHandler.do_GET(self)
    
    server = HTTPServer(('localhost', port), GameHandler)
    print(f"\n🎮 Tank Game Server")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Open your browser and go to:")
    print(f"👉 http://localhost:{port}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")

if __name__ == "__main__":
    serve_game()
