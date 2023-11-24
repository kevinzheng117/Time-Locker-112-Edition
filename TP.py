from cmu_graphics import *
import random

class Player: 
    def __init__(self, size):
        self.size = size

class Enemy:
    nextId = 0

    def __init__(self, health, size, direction):
        self.health = health
        self.size = size
        self.direction = direction
        self.id = Enemy.nextId
        Enemy.nextId += 1
    
    def __repr__(self):
        return f'{self.id}'
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id

class Projectile:
    def __init__(self, size, duration, damage):
        self.size = size
        self.duration = duration
        self.damage = damage

class Obstacle:
    def __init__(self, size):
        self.size = size
    
def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True
    app.stepsPerSecond = 10
    app.playerX = 200
    app.playerY = 300
    app.bx = 0
    app.by = 0
    app.gameOver = False
    app.player = Player(25)
    app.bullet = Projectile(7.5, 4, 1)
    app.enemyDict = dict()
    app.obstacleDict = dict()
    app.projectileList = []
    app.spawnCounter = 0
    app.shadowCounter = 0
    app.forwardCounter = 0
    app.score = 0
    app.nextScoreLine = 300

def onAppStart(app):
    app.highScore = 0
    newGame(app)

def checkCollison(app):
    enemyDict = app.enemyDict.copy()
    for enemy in enemyDict:
        for projectile in app.projectileList:
            if ((distance(app.playerX, app.playerY, projectile[0], projectile[1]) 
                   <= app.player.size+ app.bullet.size) or
                  (distance(app.playerX, app.playerY, enemyDict[enemy][0], enemyDict[enemy][1])
                   <= app.player.size + enemy.size)):
                app.gameOver = True
            elif (distance(enemyDict[enemy][0], enemyDict[enemy][1], projectile[0], projectile[1]) 
                <= enemy.size + app.bullet.size):
                enemy.health -= app.bullet.damage
                if enemy.health == 0:
                    app.enemyDict.pop(enemy)
                    app.score += 1
                app.projectileList.remove(projectile)

def createNewEnemies(app):
    directions = [(1, 0), (-1, 0), (0, 1)]
    newEnemy = Enemy(1, 15, random.choice(directions))
    return newEnemy

def createNewObstacles(app):
    newObstacle = Obstacle(random.randint(50, 100))
    return newObstacle

def moveEnemies(app):
    for enemy in app.enemyDict:
        app.enemyDict[enemy][0] += 5 * enemy.direction[0]
        app.enemyDict[enemy][1] += 5 * enemy.direction[1]

def movePlayerProjectiles(app):
    for projectile in app.projectileList:
        projectile[1] -= 30

def crossScoreLine(app):
    if app.forwardCounter == app.nextScoreLine:
        app.score += 5
        app.nextScoreLine += 2000

def updateHighScore(app):
    if app.score > app.highScore:
        app.highScore = app.score

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True:
        if app.stepsPerSecond != 10:
            app.spawnCounter += 1

            # adds enemies
            if app.spawnCounter % 5 == 0:
                if createNewEnemies(app).direction == (1, 0):
                    app.enemyDict[createNewEnemies(app)] = [0, random.randint(0, 150)]
                elif createNewEnemies(app).direction == (-1, 0):
                    app.enemyDict[createNewEnemies(app)] = [400, random.randint(0, 150)]
                elif createNewEnemies(app).direction == (0, -1):
                    app.enemyDict[createNewEnemies(app)] = [random.randint(0, 400), 0]

            moveEnemies(app)

            # adds player projectiles
            if app.spawnCounter % app.bullet.duration == 0:
                app.projectileList.append([app.playerX, app.playerY - app.player.size])
            
            movePlayerProjectiles(app)

            if app.spawnCounter % 20 == 0:
                app.obstacleDict[createNewObstacles(app)] = [random.randint(0, 400), random.randint(0, 150)]
        
        # shadow should have constant speed regardless of game time
        app.shadowCounter += 50 / app.stepsPerSecond 

        # checks for any collisons then removes the projectile and enemy
        checkCollison(app)

        crossScoreLine(app)

        updateHighScore(app)

    # checks if the shadow has caught up to the player
    if app.shadowCounter >= app.playerY:
        app.gameOver = True

def onKeyPress(app, key):
    if app.gameOver == True:
        if key != None:
            newGame(app)
            app.gameOver = False
    elif app.startMenu == True:
        if key != None:
            app.startMenu = False
    
def onKeyRelease(app, key):
    if key in {'right', 'left', 'up', 'down'}:
        app.stepsPerSecond = 10

def onKeyHold(app, keys):   
    if 'right' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][0] -= 15
        for obstacle in app.obstacleDict:
            app.obstacleDict[obstacle][0] -= 15
        for projectile in app.projectileList:
            projectile[0] -= 15
        app.bx -= 1 
        if app.bx - 10 < 0:
            app.bx += app.width 
    elif 'left' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][0] += 15
        for obstacle in app.obstacleDict:
            app.obstacleDict[obstacle][0] += 15
        for projectile in app.projectileList:
            projectile[0] += 15
        app.bx += 1
        if app.bx >= app.width + 10:
            app.bx = 10
    elif 'up' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][1] += 15
        for obstacle in app.obstacleDict:
            app.obstacleDict[obstacle][1] += 15
        for projectile in app.projectileList:
            projectile[1] += 15
        app.shadowCounter -= 10
        app.forwardCounter += 10
        app.by += 1
    elif 'down' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][1] -= 15
        for obstacle in app.obstacleDict:
            app.obstacleDict[obstacle][1] -= 15
        for projectile in app.projectileList:
            projectile[1] -= 15
        app.shadowCounter += 10
        app.forwardCounter -= 10
        app.by -= 1
    if 'right' or 'left' or 'up' or 'down' in keys:
        if app.stepsPerSecond < 40:
            app.stepsPerSecond += 2

# move drawEnemy and drawProjectile into their classes
def drawEnemy(app):
    for enemy in app.enemyDict:
        drawCircle(app.enemyDict[enemy][0], app.enemyDict[enemy][1], enemy.size, fill = 'red')

def drawObstacle(app):
    for obstacle in app.obstacleDict:
        drawRect(app.obstacleDict[obstacle][0], app.obstacleDict[obstacle][1], obstacle.size, obstacle.size, fill = 'green')

def drawProjectile(app):
    for dx, dy in app.projectileList:
        drawCircle(dx, dy, app.bullet.size, fill = 'orange')

def drawShadow(app):
    if app.shadowCounter > 0:
        drawRect(0, app.height - app.shadowCounter, app.width, app.shadowCounter)

def drawMenu(app):
    drawLabel('Time Locker: 112 Edition', 200, 150, size = 24)
    drawLabel('Press any key to start!', 200, 400, size = 18)

def drawGameOver(app):
    drawLabel(f'SCORE: {app.score}', 200, 300, size = 36)
    drawLabel('Press any key to go back to menu!', 200, 400, size = 18)

def drawPlayerScore(app):
    drawLabel(f'HIGH: {app.highScore}', 50, 20, size = 20)
    drawLabel(f'Score: {app.score}', 50, 50, size = 20)

def drawScoreLine(app):
    if (app.forwardCounter % 2000 >= 0 and 
        app.forwardCounter % 2000 <= 300 and
        app.forwardCounter // 2000 >= app.nextScoreLine // 2000):
        drawLine(0, app.forwardCounter % 2000, 350, app.forwardCounter % 2000, dashes = True)
        drawRect(350, app.forwardCounter % 2000 - 15, 50, 30, fill = None, border = 'black')
        drawLabel('+5', 375, app.forwardCounter % 2000, size = 12)

def drawPlayer(app):
    drawCircle(app.playerX, app.playerY, app.player.size, fill = 'blue')

# background with partial wraparound right to left (does not work)
def drawBackground(app):
    for j in range(2):
        for i in range(6):
            # horizontal line
            drawLine(app.bx + j * 200 - 10, app.by + i * 100, 
                     app.bx + j * 200 + 10, app.by + i * 100)
            # vertical line
            drawLine(app.bx + j * 200, app.by + i * 100 - 10, 
                     app.bx + j * 200, app.by + i * 100 + 10)
    if app.bx > app.width - 10:
        pixelsBeyondRightEdge = (app.bx + 10) - app.width
        bx = -10 + pixelsBeyondRightEdge
        for j in range(2):
            for i in range(6):
                # horizontal line
                drawLine(bx + j * 200 - 10, app.by + i * 100, 
                        bx + j * 200 + 10, app.by + i * 100)
                # vertical line
                drawLine(bx + j * 200, app.by + i * 100 - 10, 
                        bx + j * 200, app.by + i * 100 + 10)
                     
def redrawAll(app):
    if app.gameOver == False:
        # draw start menu
        if app.startMenu == True:
            drawMenu(app)
        else:
            drawPlayerScore(app)
            drawEnemy(app)
            drawProjectile(app)
            drawObstacle(app)
            drawShadow(app)
            drawScoreLine(app)
            drawBackground(app)
        
        drawPlayer(app)
    else:
        drawGameOver(app)

def main():
    runApp()
    
main()