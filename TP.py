from cmu_graphics import *
import random
from PIL import Image
import math
import os, pathlib
import copy

class Player: 
    def __init__(self, size, x, y):
        self.size = size
        self.x = x
        self.y = y

class Enemy:
    nextId = 0

    def __init__(self, health, size, direction, follow, shoot):
        self.health = health
        self.size = size
        self.direction = direction
        self.follow = follow
        self.shoot = shoot
        self.id = Enemy.nextId
        Enemy.nextId += 1
    
    # for debugging
    def __repr__(self):
        return f'{self.id, self.follow}'
    
    # needs to be able to be stored in dictionaries
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
        self.health = size // 5
    
def newGame(app):
    app.width = 600
    app.height = 600
    app.startMenu = True
    app.stepsPerSecond = 10
    app.gameOver = False
    app.player = Player(25, 300, 300)
    app.bullet = Projectile(7.5, 4, 1)
    app.enemyDict = dict()
    app.obstacleDict = dict()
    app.projectileList = []
    app.spawnCounter = 0
    app.shadowCounter = 0
    app.forwardCounter = 0
    app.score = 0
    app.nextScoreLine = 300
    app.backgroundImageX = 0
    app.backgroundImageY = 0

    # source: https://images.fineartamerica.com/images/artworkimages/mediumlarge/3/pixel-art-of-80s-retro-sci-fi-background-herbert.jpg
    app.backgroundImage = Image.open(r"C:\Users\zheng\OneDrive\Documents\CMU\F23\15112\TP\Images\background image.jpg")
    app.backgroundImageWidth,app.backgroundImageHeight = app.backgroundImage.width, app.backgroundImage.height
    app.backgroundImage = CMUImage(app.backgroundImage)

    '''
    tried implementing images as obstacles (resize in function then convert to CMU image)
    but slowed down program significantly
    '''
    # source: https://i.pinimg.com/550x/20/84/42/208442642ff691ac20846b9376db3830.jpg
    app.obstacleImage = Image.open(r"C:\Users\zheng\OneDrive\Documents\CMU\F23\15112\TP\Images\obstacle.jpg")
    app.obstacleImageWidth,app.obstacleImageHeight = app.obstacleImage.width, app.obstacleImage.height

def onAppStart(app):
    app.highScore = 0
    newGame(app)

def checkCollison(app):
    enemyDict = app.enemyDict.copy()
    for enemy in enemyDict:
        for projectile in app.projectileList:
            if ((distance(app.player.x, app.player.y, projectile[0], projectile[1]) 
                <= app.player.size + app.bullet.size) or
                (distance(app.player.x, app.player.y, enemyDict[enemy][0], enemyDict[enemy][1])
                <= app.player.size + enemy.size)):
                app.gameOver = True
            elif (distance(enemyDict[enemy][0], enemyDict[enemy][1], projectile[0], projectile[1]) 
                <= enemy.size + app.bullet.size):
                enemy.health -= app.bullet.damage
                if enemy.health == 0:
                    app.enemyDict.pop(enemy)
                    if enemy.follow == False:
                        app.score += 1
                    elif enemy.follow == True:
                        app.score += 2
                app.projectileList.remove(projectile)
    
    obstacleDict = app.obstacleDict.copy()
    for obstacle in obstacleDict:
        for projectile in app.projectileList:
            closestX = max(obstacleDict[obstacle][0], 
                           min(projectile[0], obstacleDict[obstacle][0] + obstacle.size))
            closestY = max(obstacleDict[obstacle][1], 
                           min(projectile[1], obstacleDict[obstacle][1] + obstacle.size))                
            if (distance(closestX, closestY, projectile[0], projectile[1]) <= app.bullet.size):
                obstacle.health -= app.bullet.damage
                if obstacle.health == 0:
                    app.obstacleDict.pop(obstacle)
                app.projectileList.remove(projectile)

# square circle collison
def playerObstacleCollison(app):
    obstacleDict = app.obstacleDict.copy()
    for obstacle in obstacleDict:
        closestX = max(obstacleDict[obstacle][0], 
                        min(app.player.x, obstacleDict[obstacle][0] + obstacle.size))
        closestY = max(obstacleDict[obstacle][1], 
                        min(app.player.y, obstacleDict[obstacle][1] + obstacle.size))
        if (distance(closestX, closestY, app.player.x, app.player.y) <= app.player.size):
            if app.player.x > closestX:
                return 'left'
            elif app.player.x < closestX:
                return 'right'
            elif app.player.y > closestY:
                return 'up'
            elif app.player.y < closestY:
                return 'down'
            else:
                return None
                
def createNewEnemies(app):
    # twice as likely to spawn enemies that move down
    directions = [(1, 0), (-1, 0), (0, 1), (0, 1)]
    # 30% chance of special enemy spawning
    num = random.randint(1, 10)
    shoot = False
    if num <= 7:
        follow = False
    else:
        follow = True
        if num == 10:
            shoot = True
    newEnemy = Enemy(1, 15, random.choice(directions), follow, shoot)
    return newEnemy

def createNewObstacles(app):
    newObstacle = Obstacle(random.randint(50, 100))
    return newObstacle

# uses 2D unit vector to determine player direction
def moveToPlayer(app, enemy):
    directionX = app.enemyDict[enemy][0] - app.player.x
    directionY = app.enemyDict[enemy][1] - app.player.y
    magnitude = math.sqrt(directionX ** 2 + directionY ** 2)
    directionX /= magnitude
    directionY /= magnitude
    app.enemyDict[enemy][0] -= directionX * 7.5
    app.enemyDict[enemy][1] -= directionY * 7.5

def moveEnemies(app):
    for enemy in app.enemyDict:
        if enemy.follow == False:
            app.enemyDict[enemy][0] += 7.5 * enemy.direction[0]
            app.enemyDict[enemy][1] += 7.5 * enemy.direction[1]
        else:
            moveToPlayer(app, enemy)

def movePlayerProjectiles(app):
    for projectile in app.projectileList:
        projectile[1] -= 30

def moveEnemyProjectiles(app):
    # for enemy in app.enemyDict:
    #     if enemy.shoot == True:
    #         app.projectileList.append(app.enemyDict[enemy][0] - enemy.size, app.enemyDict[1] - enemy.size)
    pass

def crossScoreLine(app):
    if app.forwardCounter == app.nextScoreLine:
        app.score += 5
        app.nextScoreLine += 2000

def updateHighScore(app):
    if app.score > app.highScore:
        app.highScore = app.score

# prevents overlapping obstacles from spawning
def spawnObstacles(app):
    newObstacle = createNewObstacles(app)
    left = random.randint(0, 600)
    top = random.randint(0, 150)
    for obstacle in app.obstacleDict:
        right0 = left + newObstacle.size
        bottom0 = top + newObstacle.size
        right1 = app.obstacleDict[obstacle][0] + obstacle.size
        bottom1 = app.obstacleDict[obstacle][1] + obstacle.size
        while ((right1 >= left) and (right0 >= app.obstacleDict[obstacle][0]) and
            (bottom1 >= top) and (bottom0 >= app.obstacleDict[obstacle][1])):
            left = random.randint(0, 600)
            top = random.randint(0, 150)
    app.obstacleDict[newObstacle] = [left, top]

def spawnEnemies(app):
    if createNewEnemies(app).direction == (1, 0):
        app.enemyDict[createNewEnemies(app)] = [0, random.randint(0, 150)]
    elif createNewEnemies(app).direction == (-1, 0):
        app.enemyDict[createNewEnemies(app)] = [600, random.randint(0, 150)]
    elif createNewEnemies(app).direction == (0, 1):
        app.enemyDict[createNewEnemies(app)] = [random.randint(0, 600), 0]

# speed game up by removing offscreen objects
def removesObjects(app):
    for projectile in app.projectileList:
        # remove player projectiles that move off screen
        if projectile[1] < -10:
            app.projectileList.remove(projectile)

    enemyDict = app.enemyDict.copy()
    for enemy in enemyDict:
        # removes enemies that are 300 pixels offscreen behind or 600 pixels right or left
        if app.enemyDict[enemy][1] > 900:
            app.enemyDict.pop(enemy)
        elif app.enemyDict[enemy][0] > 1200 or app.enemyDict[enemy][0] < -600:
            app.enemyDict.pop(enemy)
        # removes enemies that get caught by the shadow
        elif app.enemyDict[enemy][1] >= app.height - app.shadowCounter:
            app.enemyDict.pop(enemy)

# checks if the shadow has caught up to the player
def checkShadow(app):
    if app.shadowCounter >= app.player.y:
        app.gameOver = True

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True and app.gameOver == False:
        # makes sure the player is not paused
        if app.stepsPerSecond != 10:
            app.spawnCounter += 1

            # spawns enemies
            if app.spawnCounter % 5 == 0:
                spawnEnemies(app)

            moveEnemies(app)

            # spawns player projectiles
            if app.spawnCounter % app.bullet.duration == 0:
                app.projectileList.append([app.player.x, app.player.y - app.player.size])
            
            movePlayerProjectiles(app)

            # spawns obstacles
            if app.spawnCounter % 30 == 0:
                spawnObstacles(app)
        
        # shadow should have constant speed regardless of game time
        app.shadowCounter += 75 / app.stepsPerSecond 

        # checks for any collisons then removes the projectile and enemy
        checkCollison(app)

        crossScoreLine(app)

        updateHighScore(app)

        removesObjects(app)

        checkShadow(app)

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
    if ('right' in keys and playerObstacleCollison(app) != 'right' and
        app.gameOver == False and app.startMenu == False):
            # moves enemies, obstacles, projectiles
            for enemy in app.enemyDict:
                app.enemyDict[enemy][0] -= 15
            for obstacle in app.obstacleDict:
                app.obstacleDict[obstacle][0] -= 15
            for projectile in app.projectileList:
                projectile[0] -= 15
            
            # moves background
            app.backgroundImageX -= 15
            if app.backgroundImageX == -app.backgroundImageWidth:
                app.backgroundImageX = 0
    elif ('left' in keys and playerObstacleCollison(app) != 'left' and 
          app.gameOver == False and app.startMenu == False):
            for enemy in app.enemyDict:
                app.enemyDict[enemy][0] += 15
            for obstacle in app.obstacleDict:
                app.obstacleDict[obstacle][0] += 15
            for projectile in app.projectileList:
                projectile[0] += 15

            app.backgroundImageX += 15
            if app.backgroundImageX == app.backgroundImageWidth:
                app.backgroundImageX = 0
    elif ('up' in keys and playerObstacleCollison(app) != 'up' 
          and app.gameOver == False and app.startMenu == False):
            for enemy in app.enemyDict:
                app.enemyDict[enemy][1] += 15
            for obstacle in app.obstacleDict:
                app.obstacleDict[obstacle][1] += 15
            for projectile in app.projectileList:
                projectile[1] += 15
            
            # keeps track for shadow and score line
            app.shadowCounter -= 10
            app.forwardCounter += 10

            # moves background (no up-down wrap around implemented yet)
            app.backgroundImageY += 15
            if app.backgroundImageY == app.backgroundImageHeight:
                app.backgroundImageY = 0
    elif ('down' in keys and playerObstacleCollison(app) != 'down' and 
          app.gameOver == False and app.startMenu == False):
            for enemy in app.enemyDict:
                app.enemyDict[enemy][1] -= 15
            for obstacle in app.obstacleDict:
                app.obstacleDict[obstacle][1] -= 15
            for projectile in app.projectileList:
                projectile[1] -= 15
            
            app.shadowCounter += 10
            app.forwardCounter -= 10

            app.backgroundImageY -= 15
            if app.backgroundImageY == -app.backgroundImageHeight:
                app.backgroundImageY = 0
    if 'right' or 'left' or 'up' or 'down' in keys and app.gameOver == False:
        if app.stepsPerSecond < 50:
            app.stepsPerSecond += 2

# move drawEnemy and drawProjectile into their classes
def drawEnemy(app):
    for enemy in app.enemyDict:
        if enemy.follow == False:
            color = 'red'
        else:
            color = 'purple'
        drawCircle(app.enemyDict[enemy][0], app.enemyDict[enemy][1], enemy.size, fill = color)

def drawObstacle(app):
    for obstacle in app.obstacleDict:
        drawRect(app.obstacleDict[obstacle][0], app.obstacleDict[obstacle][1], 
                 obstacle.size, obstacle.size, fill = 'green')

def drawProjectile(app):
    for dx, dy in app.projectileList:
        drawCircle(dx, dy, app.bullet.size, fill = 'orange')

def drawShadow(app):
    if app.shadowCounter > 0:
        drawRect(0, app.height - app.shadowCounter, app.width, app.shadowCounter)

def drawMenu(app):
    drawLabel('Time Locker: 112 Edition', 300, 150, size = 36, fill = 'white')
    drawLabel('Press any key to start!', 300, 400, size = 24, fill = 'white')

def drawGameOver(app):
    drawLabel(f'SCORE: {app.score}', 300, 300, size = 36, fill = 'white')
    drawLabel('Press any key to go back to menu!', 300, 400, size = 18, fill = 'white')

def drawPlayerScore(app):
    drawLabel(f'HIGH: {app.highScore}', 50, 20, size = 20, fill = 'white')
    drawLabel(f'Score: {app.score}', 50, 50, size = 20, fill = 'white')

def drawScoreLine(app):
    if (app.forwardCounter % 2000 >= 0 and 
        app.forwardCounter % 2000 <= 300 and
        app.forwardCounter // 2000 >= app.nextScoreLine // 2000):
        drawLine(0, app.forwardCounter % 2000, 550, app.forwardCounter % 2000, dashes = True, fill = 'white')
        drawRect(550, app.forwardCounter % 2000 - 15, 50, 30, fill = None, border = 'white')
        drawLabel('+5', 575, app.forwardCounter % 2000, size = 12, fill = 'white')

def drawPlayer(app):
    drawCircle(app.player.x, app.player.y, app.player.size, fill = 'blue')

def drawBackground(app):
    for i in range(-1, 2):
        for j in range(-1, 2):
            drawImage(app.backgroundImage, (i * 600) + app.backgroundImageX, (j * 600) + app.backgroundImageY)
                         
def redrawAll(app):
    if app.gameOver == False:
        # want player and background to appear in the start menu
        drawBackground(app)
        drawPlayer(app)
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
        
    else:
        drawBackground(app)
        drawGameOver(app)

def main():
    runApp()
    
main()