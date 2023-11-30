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

def onStep(app):
    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)

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

def redrawAll(app):
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawPlayerBox(app)
    drawImage(sprite, 0, 0)

def main():
    runApp(width=600, height=600)

if __name__ == '__main__':
    main()