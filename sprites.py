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
    app.coordinates = [[105, 23], [27, 105], [27, 280], [0, 300], [0, 390], [70, 490], [315, 490], [385, 390], [385, 300], [358, 280], [358, 23], [105, 23]]
    # angles measured with Geogebra graphing calculator
    app.angles = [(0, 28.3), (28.3, 81.3), (81.3, 84.5), (84.5, 107), (107, 132.6), (132.6, 185.7), (185.7, 212.2), (212.2, 232.7), (232.7, 237.2), (237.2, 301.7), (301.7, 360)]

def onStep(app):
    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)

# rationale for irregular circle intersection:
# 1. determine angle of circle center relative to irregular polygon center (300, 300)
# 2. Check if the distance between angle center and selected line segment (which will be in a dict mapped to a range of angles)
# is less than circle's radius
# DONE!

# vector calculation using dot product
# source: https://stackoverflow.com/questions/1211212/how-to-calculate-an-angle-from-three-points
def angleCalc(p1, p2, p3):
    # p1 is center point
    vectorA = (p1[0] - p2[0], p1[1] - p2[1])
    vectorB = (p1[0] - p3[0], p1[1] - p3[1])
    # angle in radians
    angle = math.acos((vectorA[0] * vectorB[0] + vectorA[1] * vectorB[1]) / 
    (math.sqrt(vectorA[0] ** 2 + vectorA[1] ** 2) * math.sqrt(vectorB[0] ** 2 + vectorB[1] ** 2)))
    # convert to degrees
    angle *= 180 / math.pi
    return angle

def drawPlayerBox(app):
    for i in range(len(app.coordinates)):
        if i < len(app.coordinates) - 1:
            drawLine(app.coordinates[i][0],app.coordinates[i][1],app.coordinates[i+1][0],app.coordinates[i+1][1])
        

def redrawAll(app):
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawPlayerBox(app)
    # drawImage(sprite, 0, 0)
    drawCircle(191.5, 245, 5)

def main():
    runApp(width=600, height=600)

if __name__ == '__main__':
    main()