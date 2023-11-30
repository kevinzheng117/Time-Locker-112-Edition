from cmu_graphics import *
from PIL import Image
import os, pathlib

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
    app.coordinates = [[105, 23], [27, 105], [27, 280], [0, 300], [0, 390], [70, 490], [315, 490], [385, 380], [385, 300], [358, 280], [358, 23], [105, 23]]

def onStep(app):
    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)

# rationale for irregular circle intersection:
# 1. determine angle of circle center relative to irregular polygon center (300, 300)
# 2. Check if the distance between angle center and selected line segment (which will be in a dict mapped to a range of angles)
# is less than circle's radius
# DONE!

def drawPlayerBox(app):
    for i in range(len(app.coordinates)):
        if i < len(app.coordinates) - 1:
            drawLine(app.coordinates[i][0],app.coordinates[i][1],app.coordinates[i+1][0],app.coordinates[i+1][1])
        

def redrawAll(app):
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawPlayerBox(app)
    drawImage(sprite, 0, 0)

def main():
    runApp(width=600, height=600)

if __name__ == '__main__':
    main()