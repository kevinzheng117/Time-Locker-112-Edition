from cmu_graphics import *
import random
import copy

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
    def __init__(self, size, speed, duration):
        self.size = size
        self.speed = speed
        self.duration = duration
    
def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True
    app.stepsPerSecond = 10
    app.playerX = 200
    app.playerY = 300
    app.gameOver = False
    app.player = Player(25)
    app.bullet = Projectile(7.5, 1, 4)
    app.enemyDict = dict()
    app.projectileList = []
    app.spawnCounter = 0
    app.shadowCounter = 0
    app.forwardCounter = 0
    app.score = 0

def onAppStart(app):
    newGame(app)

def checkCollison(app):
    enemyDict = app.enemyDict.copy()
    for enemy in enemyDict:
        for projectile in app.projectileList:
            if (distance(enemyDict[enemy][0], enemyDict[enemy][1], projectile[0], projectile[1]) 
                <= enemy.size + app.bullet.size):
                app.enemyDict.pop(enemy)
                app.projectileList.remove(projectile)
                app.score += 1
            elif ((distance(app.playerX, app.playerY, projectile[0], projectile[1]) 
                   <= app.player.size+ app.bullet.size) or
                  (distance(app.playerX, app.playerY, enemyDict[enemy][0], enemyDict[enemy][1])
                   <= app.player.size + enemy.size)):
                app.gameOver = True

def createNewEnemies(app):
    directions = [(1, 0), (-1, 0), (0, 1)]
    newEnemy = Enemy(10, 15, random.choice(directions))
    return newEnemy

def moveEnemies(app):
    for enemy in app.enemyDict:
        app.enemyDict[enemy][0] += 10 * enemy.direction[0]
        app.enemyDict[enemy][1] += 10 * enemy.direction[1]

def movePlayerProjectiles(app):
    for projectile in app.projectileList:
        projectile[1] -= 30

def crossScoreLine(app):
    if app.forwardCounter % 1000 == 300:
        app.score += 10

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True:
        if app.stepsPerSecond != 10:
            app.spawnCounter += 1

            # adds enemies
            if app.spawnCounter % 5 == 0:
                app.enemyDict[createNewEnemies(app)] = [random.randint(0, 400), random.randint(0, 150)]

            moveEnemies(app)

            # adds player projectiles
            if app.spawnCounter % app.bullet.duration == 0:
                app.projectileList.append([app.playerX, app.playerY - app.player.size])
            
            movePlayerProjectiles(app)
        
        # shadow should have constant speed regardless of game time
        app.shadowCounter += 50 / app.stepsPerSecond 

        # checks for any collisons then removes the projectile and enemy
        checkCollison(app)

        crossScoreLine(app)

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
        for projectile in app.projectileList:
            projectile[0] -= 15
    elif 'left' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][0] += 15
        for projectile in app.projectileList:
            projectile[0] += 15
    elif 'up' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][1] += 15
        for projectile in app.projectileList:
            projectile[1] += 15
        app.shadowCounter -= 10
        app.forwardCounter += 10
    elif 'down' in keys:
        for enemy in app.enemyDict:
            app.enemyDict[enemy][1] -= 15
        for projectile in app.projectileList:
            projectile[1] -= 15
        app.shadowCounter += 10
        app.forwardCounter -= 10
    if 'right' or 'left' or 'up' or 'down' in keys:
        if app.stepsPerSecond < 25:
            app.stepsPerSecond += 2

# move drawEnemy and drawProjectile into their classes
def drawEnemy(app):
    for enemy in app.enemyDict:
        drawCircle(app.enemyDict[enemy][0], app.enemyDict[enemy][1], enemy.size, fill = 'red')

def drawProjectile(app):
    for dx, dy in app.projectileList:
        drawCircle(dx, dy, app.bullet.size, fill = 'orange')

def drawShadow(app):
    if app.shadowCounter > 0:
        drawRect(0, app.height - app.shadowCounter, app.width, app.shadowCounter)

def drawMenu():
    drawLabel('Time Locker: 112 Edition', 200, 150, size = 24)
    drawLabel('Press any key to start!', 200, 400, size = 18)

def drawGameOver():
    drawLabel('Game Over...', 200, 300, size = 36)
    drawLabel('Press any key to go back to menu!', 200, 400, size = 18)

def drawPlayerScore(app):
    drawLabel(f'Score: {app.score}', 50, 30, size = 20)

def drawScoreLine(app):
    if app.forwardCounter % 1000 >= 0 and app.forwardCounter % 1000 <= 300 :
        drawLine(0, app.forwardCounter % 1000, 400, app.forwardCounter % 1000, dashes = True)

def redrawAll(app):
    if app.gameOver == False:
        # draw start menu
        if app.startMenu == True:
            drawMenu()
        else:
            drawPlayerScore(app)
            drawEnemy(app)
            drawProjectile(app)
            drawShadow(app)
            drawScoreLine(app)
        
        # draw player character
        drawCircle(app.playerX, app.playerY, app.player.size, fill = 'blue')
    else:
        drawGameOver()

def main():
    runApp()
    
main()