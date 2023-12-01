from cmu_graphics import *
from PIL import Image
import os, pathlib
import math

def onAppStart(app):    
    # source: https://openclipart.org/detail/215080/retro-character-sprite-sheet
    playerSpritestrip = Image.open('Images/player sprite.png')
    # resize to actual size used in game
    newWidth, newHeight = (playerSpritestrip.width * 10 // 98, playerSpritestrip.height*10 // 98)
    # playerSpritestrip = playerSpritestrip.resize((newWidth, newHeight))
    
    app.playerSprites = [ ]
    for i in range(4):
        # Split up the spritestrip into its separate sprites
        # then save them in a list
        sprite = CMUImage(playerSpritestrip.crop((383 * i, 1510,383 + 383 * i, 2000)))
        app.playerSprites.append(sprite)
        
    # app.spriteCounter shows which sprite (of the list) 
    # we should currently display
    app.playerSpriteCounter = 0
    app.stepsPerSecond = 1
    app.coordinates = [[105, 23], [27, 105], [27, 280], [0, 300], [0, 390], 
                       [70, 490], [315, 490], [385, 390], [385, 300], [358, 280], [358, 23], [105, 23]]
    
    for coordinate in app.coordinates:
        coordinate[0] += 100
        coordinate[1] += 100
                       
    # angles measured with Geogebra graphing calculator
    app.angles = [(0, 28.3), (28.3, 81.3), (81.3, 84.5), (84.5, 107), (107, 132.6), 
                  (132.6, 185.7), (185.7, 212.2), (212.2, 232.7), (232.7, 237.2), (237.2, 301.7), (301.7, 360)]

    app.projectileX = 0
    app.projectileY = 0
    app.obstacleX = 0
    app.obstacleY = 0
    
def onStep(app):
    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)

'''
rationale for irregular polygon-circle intersection:
1. determine angle of circle center relative to irregular polygon center (300, 300)
2. Check if the distance between angle center and selected line segment
is less than circle's radius
'''
# vector calculation using dot product
# source: https://stackoverflow.com/questions/1211212/how-to-calculate-an-angle-from-three-points
# only returns 0 to 180 degrees since it's calculating the angle between 2 vectors
def angleCalc(p1, p2, p3):
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

def drawPlayerBox(app):
    for i in range(len(app.coordinates)):
        if i < len(app.coordinates) - 1:
            drawLine(app.coordinates[i][0],app.coordinates[i][1],app.coordinates[i+1][0],app.coordinates[i+1][1])
        
def playerProjectileEnemyCollison(app):
    size = 25
    projectile = (app.projectileX, app.projectileY)
    center = (291.5, 345)

    # adjust for the fact that 0 degrees is first coordainte in list
    # calculated exact point on irregular polygon where angle is 180 with desmos
    p180 = (388, 590)

    for i in range(len(app.angles)):
        angle = angleCalc(center, app.coordinates[0], projectile)
        '''
        basically points to the right side of the line formed by the 180 degrees 
        point and p1 will have their angles changed to 180 to 360 degrees
        '''
        if projectile[0] >= p180[0] or projectile[0] >= app.coordinates[0][0] and projectile[1] <= app.coordinates[0][1]:
            angle = 360 - angle
        
        if angle >= app.angles[i][0] and angle <= app.angles[i][1]:
            print(angle)
            lineSegment = (app.coordinates[i], app.coordinates[i + 1])
            if distancePointToLine(lineSegment, projectile) <= size:
                return True
    return False

'''
rationale for irregular polygon-rectangle intersection:
similar to irregular polygon-square intersection except radius changes based on
the angle
'''
# source: https://math.stackexchange.com/questions/924272/find-multiple-of-radius-of-square-given-angle-of-line
def playerObstacleCollison(app):
    length = 100
    obstacleCenter = (app.obstacleX, app.obstacleY)
    center = (291.5, 345)
    obstacle0Point = (app.obstacleX + length/2, app.obstacleY)

    # adjust for the fact that 0 degrees is first coordainte in list
    # calculated exact point on irregular polygon where angle is 180 with desmos
    p180 = (288, 490)

    for i in range(len(app.angles)):
        angle = angleCalc(center, app.coordinates[0], obstacleCenter)
        '''
        basically points to the right side of the line formed by the 180 degrees 
        point and p1 will have their angles changed to 180 to 360 degrees
        '''
        if obstacleCenter[0] >= p180[0] or obstacleCenter[0] >= app.coordinates[0][0] and obstacleCenter[1] <= app.coordinates[0][1]:
            angle = 360 - angle

        if angle >= app.angles[i][0] and angle <= app.angles[i][1]:
            lineSegment = (app.coordinates[i], app.coordinates[i + 1])
            angleR = angleCalc(obstacleCenter, center, obstacle0Point)
            if center[1] >= obstacleCenter[1]:
                angleR = 360 - angleR

            while angleR >= 45:
                angleR -= 90

            print(angleR)

            # python has no built in secant or cosecant function
            if angleR == 0:
                radius = length / 2
            else:
                angleR *= math.pi/180
                sec = 1/math.cos(angleR)
                csc = 1/math.sin(angleR)
                radius = length /2 * min(abs(sec), abs(csc))
            
            print(radius)
            # distance from the center of the square towards the direction of player center
            if distancePointToLine(lineSegment, obstacleCenter) <= radius:
                print(True)
                

def onMousePress(app, mouseX, mouseY):
    # app.projectileX = mouseX
    # app.projectileY = mouseY
    app.obstacleX = mouseX
    app.obstacleY = mouseY

def redrawAll(app):
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawPlayerBox(app)
    # drawImage(sprite, 0, 0)
    drawCircle(291.5, 345, 5)
    # drawCircle(app.projectileX, app.projectileY, 25)
    drawRect(app.obstacleX, app.obstacleY, 100, 100, align = 'center')
    drawCircle(388, 590, 5)
    # print(playerProjectileEnemyCollison(app))
    print(playerObstacleCollison(app))

def main():
    runApp(width=600, height=600)

if __name__ == '__main__':
    main()