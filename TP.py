from cmu_graphics import *

def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True
    app.enemyList = [[200, 100]]
    app.stepsPerSecond = 5
    app.playerX = 200
    app.playerY = 300
    app.playerR = 25
    app.enemyR = 10
    app.gameOver = False

def onAppStart(app):
    newGame(app)

def checkCollison(app):
    # only works for player character
    for enemy in app.enemyList:
        if distance(app.playerX, app.playerY, enemy[0], enemy[1]) <= app.playerR + app.enemyR:
            return True
    return False

def onStep(app):
    # enemy starts as paused since player hasn't moved
    if app.startMenu != True and app.stepsPerSecond != 5:
        for enemy in app.enemyList:
            enemy[0] += 10
    if checkCollison(app):
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
        app.stepsPerSecond = 5

def onKeyHold(app, keys):   
    if 'right' in keys:
        for enemy in app.enemyList:
            enemy[0] -= 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'left' in keys:
        for enemy in app.enemyList:
            enemy[0] += 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'up' in keys:
        for enemy in app.enemyList:
            enemy[1] += 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'down' in keys:
        for enemy in app.enemyList:
            enemy[1] -= 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1

def drawEnemy(app):
    for dx, dy in app.enemyList:
        drawCircle(dx, dy, app.enemyR, fill = 'red')

def drawMenu():
    drawLabel('Time Locker: 112 Edition', 200, 150, size = 24)
    drawLabel('Press any key to start!', 200, 400, size = 18)

def drawGameOver():
    drawLabel('Game Over...', 200, 300, size = 36)
    drawLabel('Press any key to go back to menu!', 200, 400, size = 18)

def redrawAll(app):
    if app.gameOver == False:
        # draw start menu
        if app.startMenu == True:
            drawMenu()
        else:
            drawEnemy(app)
        
        # draw player character
        drawCircle(app.playerX, app.playerY, app.playerR, fill = 'blue')
    else:
        drawGameOver()

def main():
    runApp()
    
main()