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
        sprite = CMUImage(playerSpritestrip.crop((383 * i/app.playerScaleFactor, 
                                                1510/app.playerScaleFactor,
                                                (383 + 383 * i)/app.playerScaleFactor,
                                                2000/app.playerScaleFactor)))
        app.playerSprites.append(sprite)

    app.playerSpriteCounter = 0

    # coordinates to irregular polygon; written in a separate file so dimensions are different
    app.coordinates = [[105, 23], [27, 105], [27, 280], [0, 300], [0, 390], 
                       [70, 490], [315, 490], [385, 390], [385, 300], [358, 280], 
                       [358, 23], [105, 23]]
    for coordinate in app.coordinates:
        coordinate[0] /= app.playerScaleFactor
        coordinate[1] /= app.playerScaleFactor
        # to adjust the coordinates to be at the center of the canvas
        coordinate[0] += 280
        coordinate[1] += 275

    # angles measured using Geogebra graphing calculator
    app.angles = [(0, 28.3), (28.3, 81.3), (81.3, 84.5), (84.5, 107), 
                  (107, 132.6), (132.6, 185.7), (185.7, 212.2), (212.2, 232.7), 
                  (232.7, 237.2), (237.2, 301.7), (301.7, 360)]

def onAppStart(app):
    app.highScore = 0
    newGame(app)

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True and app.gameOver == False:
        # makes sure the player is not paused
        if app.stepsPerSecond > 10:
            app.spawnCounter += 1

            # spawns enemies, moreso as time moves on
            if app.forwardCounter < 4000:
                enemySpawnRate = 5 - app.forwardCounter // 1000
            else:
                enemySpawnRate = 1
            if app.spawnCounter % enemySpawnRate == 0:
                spawnEnemies(app)

            moveEnemies(app)

            # spawns player projectiles
            if app.spawnCounter % 4 == 0:
                spawnPlayerProjectiles(app)

            if app.spawnCounter % 12 == 0:
                spawnEnemyProjectiles(app)
            
            moveProjectiles(app)

            # spawns obstacles, moreso as time moves on
            if app.forwardCounter < 6000:
                obstacleSpawnRate = 30 - app.forwardCounter // 300
            else:
                obstacleSpawnRate = 10
            if app.spawnCounter % obstacleSpawnRate == 0:
                spawnObstacles(app)

            # move sprite
            app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)
        # shadow should have constant speed regardless of game time
        app.shadowCounter += 75 / app.stepsPerSecond 

        # checks for any collisions then removes the projectile and enemy
        enemyProjectileCollision(app)

        playerEnemyProjectileCollision(app)
        
        playerObstacleCollision(app)

        projectileObstacleCollision(app)

        crossScoreLine(app)

        updateHighScore(app)

        removesObjects(app)

        checkShadow(app)

# circle-circle collision
def enemyProjectileCollision(app):
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

# vector calculation using dot product
# source: https://stackoverflow.com/questions/1211212/how-to-calculate-an-angle-from-three-points
# only returns 0 to 180 degrees since it's calculating the angle between 2 vectors
def angleCalc(app, p1, p2, p3):
    # p1 is center point, p2 is first point in app.coordinates
    vectorA = (p1[0] - p2[0], p1[1] - p2[1])
    vectorB = (p1[0] - p3[0], p1[1] - p3[1])

    # angle in radians
    angle = math.acos((vectorA[0] * vectorB[0] + vectorA[1] * vectorB[1]) / 
    (math.sqrt(vectorA[0] ** 2 + vectorA[1] ** 2) * math.sqrt(vectorB[0] ** 2 + vectorB[1] ** 2)))

    # convert to degrees
    angle *= 180 / math.pi
    return angle

# uses point-line distance formula
# source: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
def distancePointToLine(line, point):
    p0 = point
    p1 = line[0]
    p2 = line[1]
    d = abs((p2[0] - p1[0]) * (p1[1] - p0[1]) - (p1[0] - p0[0]) * (p2[1] - p1[1])) / distance(p1[0], p1[1], p2[0], p2[1]) 
    return d

'''
rationale for irregular polygon-circle intersection:
1. determine angle of circle center relative to irregular polygon center
2. Check if the distance between angle center and selected line segment
is less than circle's radius
'''
def playerEnemyProjectileCollision(app):
    enemyDict = app.enemyDict.copy()
    projectileDict = app.projectileDict.copy()

    # to adjust for the fact that we said the first coordinate in our list is 0 degrees
    # calculated exact point on irregular polygon where angle is 180 with desmos
    p180 = [288, 490]
    # same kind of adjustments as app.coordinates
    p180[0] //= app.playerScaleFactor
    p180[1] // app.playerScaleFactor
    p180[0] += 280
    p180[1] += 275

    for enemy in enemyDict:
        for i in range(len(app.angles)):
            angle = angleCalc(app, (app.player.x, app.player.y), app.coordinates[0], enemyDict[enemy])
            ''' 
            basically points to the right side of the line formed by the 180 degrees 
            point and p1 will have their angles changed to 180 to 360 degrees
            '''
            if (enemyDict[enemy][0] >= p180[0] or 
                enemyDict[enemy][0] >= app.coordinates[0][0] and 
                enemyDict[enemy][1] <= app.coordinates[0][1]):
                angle = 360 - angle

            if angle >= app.angles[i][0] and angle <= app.angles[i][1]:
                lineSegment = (app.coordinates[i], app.coordinates[i + 1])
                if distancePointToLine(lineSegment, enemyDict[enemy]) <= enemy.size:
                    app.gameOver = True

    for projectile in projectileDict:
        for i in range(len(app.angles)):
            angle = angleCalc(app, (app.player.x, app.player.y), app.coordinates[0], projectileDict[projectile])
            if (projectileDict[projectile][0] >= p180[0] or 
                projectileDict[projectile][0] >= app.coordinates[0][0] and 
                projectileDict[projectile][1] <= app.coordinates[0][1]):
                angle = 360 - angle

            if angle >= app.angles[i][0] and angle <= app.angles[i][1]:
                lineSegment = (app.coordinates[i], app.coordinates[i + 1])
                if distancePointToLine(lineSegment, projectileDict[projectile]) <= projectile.size:
                    app.gameOver = True

'''
rationale for irregular polygon-rectangle intersection:
similar to irregular polygon-square intersection except radius changes based on
the angel
'''
# source: https://math.stackexchange.com/questions/924272/find-multiple-of-radius-of-square-given-angle-of-line
# very buggy
def playerObstacleCollision(app):
    obstacleDict = app.obstacleDict.copy()

    # to adjust for the fact that we said the first coordinate in our list is 0 degrees
    # calculated exact point on irregular polygon where angle is 180 with desmos
    p180 = [288, 490]
    # same kind of adjustments as app.coordinates
    p180[0] //= app.playerScaleFactor
    p180[1] // app.playerScaleFactor
    p180[0] += 280
    p180[1] += 275

    for obstacle in obstacleDict:
        obstacleCenter = (obstacleDict[obstacle][0] + obstacle.size / 2, 
                          obstacleDict[obstacle][1] + obstacle.size / 2)
        obstacle0Point = (obstacleDict[obstacle][0] + obstacle.size, obstacleDict[obstacle][1] + obstacle.size / 2) 
        for i in range(len(app.angles)):
            angle = angleCalc(app, (app.player.x, app.player.y), app.coordinates[0], obstacleCenter)
            ''' 
            basically points to the right side of the line formed by the 180 degrees 
            point and p1 will have their angles changed to 180 to 360 degrees
            '''
            if (obstacleCenter[0] >= p180[0] or 
                obstacleCenter[0] >= app.coordinates[0][0] and 
                obstacleCenter[1] <= app.coordinates[0][1]):
                angle = 360 - angle

            if angle >= app.angles[i][0] and angle <= app.angles[i][1]:
                lineSegment = (app.coordinates[i], app.coordinates[i + 1])
                angleR = angleCalc(app, obstacleCenter, (app.player.x, app.player.y), obstacle0Point)

                # adjusts angles past 180 degrees
                if app.player.y >= obstacleCenter[1]:
                    angleR = 360 - angleR

                newAngleR = angleR
                # algorithm only works for angles in between -45 and 45
                while newAngleR >= 45:
                    newAngleR -= 90

                # python has no built in secant or cosecant function
                if almostEqual(0, newAngleR):
                    radius = obstacle.size / 2
                else:
                    newAngleR *= math.pi/180
                    # python trig function takes in radians
                    sec = 1/math.cos(newAngleR)
                    csc = 1/math.sin(newAngleR)
                    radius = obstacle.size / 2 * min(abs(sec), abs(csc))
            
                # distance from the center of the square towards the direction of player center
                # 15 is the amount everything moves
                if distancePointToLine(lineSegment, obstacleCenter) <= radius + 15:
                    if angleR >= 315 or angleR <= 45:
                        return 'left'
                    elif angleR >= 45 and angleR <= 135:
                        return 'down'
                    elif angleR >= 135 and angleR <= 225:
                        return 'right'
                    elif angleR >= 225 and angleR <= 315:
                        return 'up'
                    return None
                    
# circle-rectangle collison
# source: https://www.jeffreythompson.org/collision-detection/circle-rect.php
def projectileObstacleCollision(app):
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
    if ('right' in keys and playerObstacleCollision(app) != 'right' and 
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
    elif ('left' in keys and playerObstacleCollision(app) != 'left' and
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
    elif ('up' in keys and playerObstacleCollision(app) != 'up' and
          app.gameOver == False and app.startMenu == False):
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
    elif ('down' in keys and playerObstacleCollision(app) != 'down' and 
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
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawImage(sprite, 280.5, 275)

# could be used for debugging
def drawPlayerBox(app):
    for i in range(len(app.coordinates)):
        if i < len(app.coordinates) - 1:
            drawLine(app.coordinates[i][0],app.coordinates[i][1],app.coordinates[i+1][0],app.coordinates[i+1][1], fill = 'white')

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