from cmu_graphics import *
from PIL import Image
import os, pathlib

def onAppStart(app):    
    # source: https://openclipart.org/detail/215080/retro-character-sprite-sheet
    playerSpritestrip = Image.open('Images/player sprite.png')
    newWidth, newHeight = (playerSpritestrip.width * 10 // 98, playerSpritestrip.height*10 // 98)
    playerSpritestrip = playerSpritestrip.resize((newWidth, newHeight))
    
    app.playerSprites = [ ]
    for i in range(4):
        # Split up the spritestrip into its separate sprites
        # then save them in a list
        sprite = CMUImage(playerSpritestrip.crop((383 * i//9.8, 1510//9.8, (383 + 383 * i)//9.8, 2000//9.8)))
        app.playerSprites.append(sprite)
        
    # app.spriteCounter shows which sprite (of the list) 
    # we should currently display
    app.playerSpriteCounter = 0
    app.stepsPerSecond = 5

def onStep(app):
    app.playerSpriteCounter = (1 + app.playerSpriteCounter) % len(app.playerSprites)

def redrawAll(app):
    sprite = app.playerSprites[app.playerSpriteCounter]
    drawImage(sprite, 280.5, 275)

def main():
    runApp(width=600, height=600)

if __name__ == '__main__':
    main()