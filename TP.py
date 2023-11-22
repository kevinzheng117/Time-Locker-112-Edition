from cmu_graphics import *

def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True

def drawMenu():
    drawLabel('Time Locker: 112 Edition', 200, 150, size = 24)
    drawLabel('Press any key to start!', 200, 400, size = 18)

def onAppStart(app):
    newGame(app)

def onStep(app):
    pass

def onKeyPress(app, key):
    while app.startMenu == True:
        if key != None:
            app.startMenu = False

def redrawAll(app):
    # draw start menu
    if app.startMenu == True:
        drawMenu()
    else:
        pass
    
    drawCircle(200, 300, 25, fill = 'blue')

def main():
    runApp()
    
main()