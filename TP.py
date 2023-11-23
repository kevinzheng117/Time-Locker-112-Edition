from cmu_graphics import *

class Player: 
    def __init__(self, size):
        self.size = size

class Enemy:
    def __init__(self, health, size, speed):
        self.health = health
        self.size = size
        self.speed = speed

class Projectile:
    def __init__(self, size, speed):
        self.size = size
        self.speed = speed
    
def newGame(app):
    app.width = 400
    app.height = 600
    app.startMenu = True
    app.stepsPerSecond = 5
    app.playerX = 200
    app.playerY = 300
    app.gameOver = False
    app.enemy1 = Enemy(1, 15, 1)
    app.player = Player(25)
    app.bullet = Projectile(7.5, 1)
    app.enemyList = [[200, 100]]
    app.projectileList = []
    app.counter = 0

def onAppStart(app):
    newGame(app)

def checkCollison(app):
    for enemy in app.enemyList:
        for projectile in app.projectileList:
            if distance(enemy[0], enemy[1], projectile[0], projectile[1]) <= app.enemy1.size + app.bullet.size:
                app.enemyList.remove(enemy)
                app.projectileList.remove(projectile)
            elif (distance(app.playerX, app.playerY, projectile[0], projectile[1]) <= app.player.size+ app.bullet.size or
                  distance(app.playerX, app.playerY, enemy[0], enemy[1]) <= app.player.size + app.enemy1.size):
                app.gameOver = True

def onStep(app):
    # everything starts as paused since player hasn't moved
    if app.startMenu != True and app.stepsPerSecond != 5:
        # moves enemies
        for enemy in app.enemyList:
            enemy[0] += 10

        # adds player projectiles
        app.counter += 1
        if app.counter % 3 == 0:
            app.projectileList.append([app.playerX, app.playerY - app.player.size])
        
        # moves player projectiles
        for projectile in app.projectileList:
            projectile[1] -= 30
    
    # checks for any collisons then removes the projectile and enemy
    checkCollison(app)

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
        for projectile in app.projectileList:
            projectile[0] -= 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'left' in keys:
        for enemy in app.enemyList:
            enemy[0] += 15
        for projectile in app.projectileList:
            projectile[0] += 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'up' in keys:
        for enemy in app.enemyList:
            enemy[1] += 15
        for projectile in app.projectileList:
            projectile[1] += 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1
    elif 'down' in keys:
        for enemy in app.enemyList:
            enemy[1] -= 15
        for projectile in app.projectileList:
            projectile[1] -= 15
        if app.stepsPerSecond < 15:
            app.stepsPerSecond += 1

def drawEnemy(app):
    for dx, dy in app.enemyList:
        drawCircle(dx, dy, app.enemy1.size, fill = 'red')

def drawProjectiles(app):
    for dx, dy in app.projectileList:
        drawCircle(dx, dy, app.bullet.size, fill = 'orange')

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
            drawProjectiles(app)
        
        # draw player character
        drawCircle(app.playerX, app.playerY, app.player.size, fill = 'blue')
    else:
        drawGameOver()

def main():
    runApp()
    
main()