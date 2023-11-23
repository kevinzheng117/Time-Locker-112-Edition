from cmu_graphics import *

def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True
    app.enemyList = [[200, 100]]
    app.stepsPerSecond = 1

def drawEnemy(app):
    for dx, dy in app.enemyList:
        drawCircle(dx, dy, 10, fill = 'red')

def drawMenu():
    drawLabel('Time Locker: 112 Edition', 200, 150, size = 24)
    drawLabel('Press any key to start!', 200, 400, size = 18)

def onAppStart(app):
    newGame(app)

def onStep(app):
    # enemy starts as paused since player hasn't moved
    if app.startMenu != True and app.stepsPerSecond != 1:
        for enemy in app.enemyList:
            enemy[0] += 10

def onKeyPress(app, key):
    while app.startMenu == True:
        if key != None:
            app.startMenu = False

def onKeyHold(app, keys):   
    if 'right' in keys:
        for enemy in app.enemyList:
            enemy[0] -= 20
        if app.stepsPerSecond < 10:
            app.stepsPerSecond += 0.5
    if 'left' in keys:
        for enemy in app.enemyList:
            enemy[0] += 20
        if app.stepsPerSecond < 10:
            app.stepsPerSecond += 0.5
    if 'up' in keys:
        for enemy in app.enemyList:
            enemy[1] += 20
        if app.stepsPerSecond < 10:
            app.stepsPerSecond += 0.5
    if 'down' in keys:
        for enemy in app.enemyList:
            enemy[1] -= 20
        if app.stepsPerSecond < 10:
            app.stepsPerSecond += 0.5
    
    
def redrawAll(app):
    # draw start menu
    if app.startMenu == True:
        drawMenu()
    else:
        drawEnemy(app)
    
    # draw player character
    drawCircle(200, 300, 25, fill = 'blue')

def main():
    runApp()
    
main()