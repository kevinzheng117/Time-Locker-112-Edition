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
        return f'{self.id}'
    
    # needs to be able to be stored in dictionaries
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id

class Projectile:
    nextId = 0

    def __init__(self, size, damage, direction):
        self.size = size
        self.damage = damage
        self.direction = direction
        self.id = Projectile.nextId
        Projectile.nextId += 1
    
    # for debugging
    def __repr__(self):
        return f'{self.id}'
    
    # needs to be able to be stored in dictionaries
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return self.id

class Obstacle:
    def __init__(self, size):
        self.size = size
        # health is proportional to its size
        self.health = size // 5
    
def newGame(app):
    app.width = 600
    app.height = 600
    app.startMenu = True
    app.stepsPerSecond = 10
    app.gameOver = False
    app.player = Player(25, 300, 300)
    app.enemyDict = dict()
    app.obstacleDict = dict()
    app.projectileDict = dict()
    app.spawnCounter = 0
    app.shadowCounter = 0
    app.forwardCounter = 0
    app.score = 0
    app.nextScoreLine = 300
    app.backgroundImageX = 0
    app.backgroundImageY = 0

    ''' 
    source: https://images.fineartamerica.com/images/artworkimages/mediumlarge
    /3/pixel-art-of-80s-retro-sci-fi-background-herbert.jpg
    '''
    app.backgroundImage = Image.open("Images/background image.jpg")
    app.backgroundImageWidth = app.backgroundImage.width
    app.backgroundImageHeight =  app.backgroundImage.height
    app.backgroundImage = CMUImage(app.backgroundImage)

    '''
    tried implementing images as obstacles 
    (resize in function then convert to CMU image)
    but slowed down program significantly
    '''
    # source: https://i.pinimg.com/550x/20/84/42/208442642ff691ac20846b9376db3830.jpg
    app.obstacleImage = Image.open("Images/obstacle.jpg")
    app.obstacleImageWidth = app.obstacleImage.width
    app.obstacleImageHeight = app.obstacleImage.height

    # source: https://openclipart.org/detail/215080/retro-character-sprite-sheet
    playerSpritestrip = Image.open('Images/player sprite.png')
    newWidth, newHeight = (playerSpritestrip.width * 10 // 98, playerSpritestrip.height*10 // 98)
    playerSpritestrip = playerSpritestrip.resize((newWidth, newHeight))
    app.playerScaleFactor = 9.8

    app.playerSprites = [ ]
    for i in range(4):
        # Split up the spritestrip into its separate sprites
        # then save them in a list
        sprite = CMUImage(playerSpritestrip.crop((383 * i/app.playerScaleFactor, 
                                                1510/app.playerScaleFactor,
                                                (383 + 383 * i)/app.playerScaleFactor,
                                                2000/app.playerScaleFactor)))
        app.playerSprites.append(sprite)
        
    # app.spriteCounter shows which sprite (of the list) 
    # we should currently display
    app.playerSpriteCounter = 0

def onAppStart(app):
    app.highScore = 0
    newGame(app)

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True and app.gameOver == False:
        # makes sure the player is not paused
        if app.stepsPerSecond > 10:
            app.spawnCounter += 1

            # spawns enemies
            if app.spawnCounter % 5 == 0:
                spawnEnemies(app)

            moveEnemies(app)

            # spawns player projectiles
            if app.spawnCounter % 4 == 0:
                spawnPlayerProjectiles(app)

            if app.spawnCounter % 12 == 0:
                spawnEnemyProjectiles(app)
            
            moveProjectiles(app)

            # spawns obstacles
            if app.spawnCounter % 30 == 0:
                spawnObstacles(app)

            # move sprite
            app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)
        # shadow should have constant speed regardless of game time
        app.shadowCounter += 75 / app.stepsPerSecond 

        # checks for any collisons then removes the projectile and enemy
        enemyProjectileCollison(app)

        playerEnemyProjectileCollison(app)

        projectileObstacleCollison(app)

        crossScoreLine(app)

        updateHighScore(app)

        removesObjects(app)

        checkShadow(app)

def enemyProjectileCollison(app):
    # bug needs fixing, not sure why
    enemyDict = app.enemyDict.copy()
    projectileDict = app.projectileDict.copy()
    for enemy in enemyDict:
        for projectile in projectileDict:
            if (distance(enemyDict[enemy][0], enemyDict[enemy][1], projectileDict[projectile][0], projectileDict[projectile][1]) 
                <= enemy.size + projectile.size):
                enemy.health -= projectile.damage
                if enemy.health == 0:
                    app.enemyDict.pop(enemy)
                    if enemy.follow == True and enemy.shoot == True:
                        app.score += 3
                    elif enemy.follow == True:
                        app.score += 2
                    else:
                        app.score += 1
                app.projectileDict.pop(projectile)

# new function for integrating irregular polygon
def playerEnemyProjectileCollison(app):
    enemyDict = app.enemyDict.copy()
    projectileDict = app.projectileDict.copy()
    for enemy in enemyDict:
        for projectile in projectileDict:
            if ((distance(app.player.x, app.player.y, projectileDict[projectile][0], projectileDict[projectile][1]) 
                <= app.player.size + projectile.size) or
                (distance(app.player.x, app.player.y, enemyDict[enemy][0], enemyDict[enemy][1])
                <= app.player.size + enemy.size)):
                app.gameOver = True
    
def projectileObstacleCollison(app):
     # not perfect since circle can be in square
    projectileDict = app.projectileDict.copy()
    obstacleDict = app.obstacleDict.copy()
    for obstacle in obstacleDict:
        for projectile in projectileDict:
            closestX = projectileDict[projectile][0]
            closestY = projectileDict[projectile][1]

            if closestX < obstacleDict[obstacle][0]:
                closestX = obstacleDict[obstacle][0]
            elif closestX > obstacleDict[obstacle][0] + obstacle.size:
                closestX = obstacleDict[obstacle][0] + obstacle.size
            if closestY < obstacleDict[obstacle][1]:
                closestY = obstacleDict[obstacle][1]
            elif closestY > obstacleDict[obstacle][1] + obstacle.size:
                closestY = obstacleDict[obstacle][1] + obstacle.size

            if (distance(closestX, closestY, projectileDict[projectile][0], projectileDict[projectile][1]) <= projectile.size):
                obstacle.health -= projectile.damage
                if obstacle.health == 0:
                    app.obstacleDict.pop(obstacle)
                app.projectileDict.pop(projectile)

# square circle collison
# source: https://www.jeffreythompson.org/collision-detection/circle-rect.php
def playerObstacleCollison(app):
    obstacleDict = app.obstacleDict.copy()
    for obstacle in obstacleDict:
        closestX = app.player.x
        closestY = app.player.y

        if closestX < obstacleDict[obstacle][0]:
            closestX = obstacleDict[obstacle][0]
        elif closestX > obstacleDict[obstacle][0] + obstacle.size:
            closestX = obstacleDict[obstacle][0] + obstacle.size
        if closestY < obstacleDict[obstacle][1]:
            closestY = obstacleDict[obstacle][1]
        elif closestY > obstacleDict[obstacle][1] + obstacle.size:
            closestY = obstacleDict[obstacle][1] + obstacle.size
        
        ''' 
        checks if the shapes intersect and which side of the rectangle 
        the circle is on to prevent the user from moving farther from that side
        '''
        # add 15 (how much everything else moves) so player
        # cannot make the move that makes it intersect with the recatangle
        if (distance(closestX, closestY, app.player.x, app.player.y) <= app.player.size + 15):
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
    num = random.randint(1, 20)
    shoot = False
    if num <= 15:
        follow = False
    else:
        follow = True
        if num == 20:
            shoot = True
    newEnemy = Enemy(1, 15, random.choice(directions), follow, shoot)
    return newEnemy

def createNewObstacles(app):
    newObstacle = Obstacle(random.randint(50, 100))
    return newObstacle

# uses 2D unit vector to determine player direction
# source: https://www.youtube.com/watch?app=desktop&v=f5DHYCKyVRo
# utilized new algorithm but still buggy
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

def moveProjectiles(app):
    for projectile in app.projectileDict:
        app.projectileDict[projectile][0] += projectile.direction[0] * 30
        app.projectileDict[projectile][1] += projectile.direction[1] * 30

def crossScoreLine(app):
    if app.forwardCounter == app.nextScoreLine:
        app.score += 10
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
    
def spawnPlayerProjectiles(app):
    app.projectileDict[Projectile(7.5, 1, (0, -1))] = [app.player.x, app.player.y - app.player.size]

def spawnEnemyProjectiles(app):
    for enemy in app.enemyDict:
        if enemy.shoot == True:
            directionX = app.enemyDict[enemy][0] - app.player.x
            directionY = app.enemyDict[enemy][1] - app.player.y
            magnitude = math.sqrt(directionX ** 2 + directionY ** 2)
            directionX /= magnitude
            directionY /= magnitude
            direction = (-directionX, -directionY)
            app.projectileDict[Projectile(7.5, 1, direction)] = [app.enemyDict[enemy][0], app.enemyDict[enemy][1]]

# speed game up by removing offscreen objects
def removesObjects(app):
    projectileDict = app.projectileDict.copy()
    for projectile in projectileDict:
        # remove player projectiles that move off screen
        if projectileDict[projectile][1] < -10:
            app.projectileDict.pop(projectile)

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
            for projectile in app.projectileDict:
                app.projectileDict[projectile][0] -= 15
            
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
            for projectile in app.projectileDict:
                app.projectileDict[projectile][0] += 15

            app.backgroundImageX += 15
            if app.backgroundImageX == app.backgroundImageWidth:
                app.backgroundImageX = 0
    elif ('up' in keys and playerObstacleCollison(app) != 'up' 
          and app.gameOver == False and app.startMenu == False):
            for enemy in app.enemyDict:
                app.enemyDict[enemy][1] += 15
            for obstacle in app.obstacleDict:
                app.obstacleDict[obstacle][1] += 15
            for projectile in app.projectileDict:
                app.projectileDict[projectile][1] += 15
            
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
            for projectile in app.projectileDict:
                app.projectileDict[projectile][1] -= 15
            
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
        if enemy.follow == True and enemy.shoot == True:
            color = 'purple'
        elif enemy.follow == True:
            color = 'red'
        else:
            color = 'deepPink'

        drawCircle(app.enemyDict[enemy][0], app.enemyDict[enemy][1], enemy.size, fill = color)

def drawObstacle(app):
    for obstacle in app.obstacleDict:
        drawRect(app.obstacleDict[obstacle][0], app.obstacleDict[obstacle][1], 
                 obstacle.size, obstacle.size, fill = 'green')

def drawProjectile(app):
    for projectile in app.projectileDict:
        if projectile.direction == (0, -1):
            color = 'orange'
        else:
            color = 'cyan'
        
        drawCircle(app.projectileDict[projectile][0], app.projectileDict[projectile][1], projectile.size, fill = color)

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
        drawLine(0, app.forwardCounter % 2000, 550, app.forwardCounter % 2000,
                 dashes = True, fill = 'white')
        drawRect(550, app.forwardCounter % 2000 - 15, 50, 30, fill = None, border = 'white')
        drawLabel('+10', 575, app.forwardCounter % 2000, size = 12, fill = 'white')

def drawPlayer(app):
    drawCircle(app.player.x, app.player.y, app.player.size, fill = None, border = 'black')
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawImage(sprite, 280.5, 275)

def drawPlayerBox(app):
    drawLine(105, 23, 358, 23)
    drawLine(105, 23, 27, 105)
    drawLine(27, 105, 27, 280)
    drawLine(27, 280, 0, 300)
    drawLine(0, 300, 0, 390)
    drawLine(0, 390, 70, 490)
    drawLine(70, 490, 315, 490)
    drawLine(315, 490, 385, 380)
    drawLine(385, 380, 385, 300)
    drawLine(385, 300, 358, 280)
    drawLine(358, 23, 358, 280)

def drawBackground(app):
    for i in range(-1, 2):
        for j in range(-1, 2):
            drawImage(app.backgroundImage, (i * 600) + app.backgroundImageX, 
                      (j * 600) + app.backgroundImageY)
                         
def redrawAll(app):
    if app.gameOver == False:
        # want player and background to appear in the start menu
        drawBackground(app)
        drawPlayer(app)
        drawPlayerBox(app)
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