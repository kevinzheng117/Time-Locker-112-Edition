from cmu_graphics import *
from PIL import Image
import os, pathlib

def onAppStart(app):
    
    spritestrip = Image.open('Images/characterstripe.png')
    
    app.sprites = [ ]
    for i in range(6):
        # Split up the spritestrip into its separate sprites
        # then save them in a list
        sprite = CMUImage(spritestrip.crop((30+260*i, 30, 230+260*i, 250)))
        app.sprites.append(sprite)
        
    # app.spriteCounter shows which sprite (of the list) 
    # we should currently display
    app.spriteCounter = 0
    app.stepsPerSecond = 10

def onStep(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)

def redrawAll(app):
    sprite = app.sprites[app.spriteCounter]
    drawImage(sprite,200, 200)

def main():
    runApp(width=400, height=400)

if __name__ == '__main__':
    main()