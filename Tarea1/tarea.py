#Delaney Tello
import pyglet
from pyglet import shapes
from pyglet import clock
import random

window = pyglet.window.Window(930, 540)
batchestrella = pyglet.graphics.Batch()
batchnave = pyglet.graphics.Batch()
batchastronauta = pyglet.graphics.Batch()

starlist = list()
#creamos la clase de estrellas
class star():
    def __init__(self):
        self.sprite = shapes.Star(random.randint(50,900), random.randint(530,540), 10, 5, num_spikes=5, color=(random.randint(50,255), random.randint(50,255), random.randint(50,255)), batch=batchestrella)
    def draw(self):
        self.sprite.y -= 20
        self.sprite.draw()
#funciones para crear y actualizar posicion de estrellas
def newstar(t):
    s = star()
    starlist.append(s)
def update(t):
    window.clear()
    for star in starlist:
        star.draw()
        
pyglet.clock.schedule_interval(update,0.1)
pyglet.clock.schedule_interval(newstar,0.2)

#creamos la clase de nave
class nave():
    #despx = desplazamiento en eje x
    #despy = desplazamiento en eje y
    #cn con n un numero = para los colores de la nave
    def __init__(self, despx, despy, c1,c2,c3,c4,c5,c6):
        self.navecuerpo1 = shapes.Triangle(425 + despx, 220 + despy, 444 + despx, 300 + despy, 444 + despx, 180 + despy, color=(c1, c2, c3), batch=batchnave)
        self.navecuerpo2 = shapes.Triangle(465 + despx, 220 + despy, 446 + despx, 300 + despy, 446 + despx, 180 + despy, color=(c1, c2, c3), batch=batchnave)
        self.navecuerpo3 = shapes.Triangle(430 + despx, 220 + despy, 405 + despx, 225 + despy, 355 + despx, 160 + despy, color=(c1, c2, c3), batch=batchnave)
        self.navecuerpo4 = shapes.Triangle(460 + despx, 220 + despy, 485 + despx, 225 + despy, 535 + despx, 160 + despy, color=(c1, c2, c3), batch=batchnave)
        self.navecuerpo5 = shapes.Triangle(410 + despx, 160 + despy, 435 + despx, 220 + despy, 425 + despx, 260 + despy, color=(c4, c5, c6), batch=batchnave)
        self.navecuerpo6 = shapes.Triangle(480 + despx, 160 + despy, 455 + despx, 220 + despy, 465 + despx, 260 + despy, color=(c4, c5, c6), batch=batchnave)
#creamos las naves en la posicion correspondiente y asignando colores
nave1 = nave(0, 0, 220, 100, 150, 150, 200, 250)
nave2 = nave(-200, -100, 200, 80, 220, 100, 100, 200)
nave3 = nave(200, -100, 120, 200, 150, 240, 100, 200)

#creamos la clase astronauta
class astronauta():
    def __init__(self,x):
        #x es para luego crear astronautas en distintas partes del eje x
        self.brazoizq = shapes.Rectangle(456.5+x, 517, 9, 2, color=(220, 220, 255, 255), batch=batchastronauta)
        self.brazodere =shapes.Rectangle(480+x, 517, 9, 2, color=(220, 220, 255, 255), batch=batchastronauta)
        self.piernaizq =shapes.Rectangle(466.5+x, 493.5, 3, 8, color=(220, 220, 255, 255), batch=batchastronauta)
        self.piernadere =shapes.Rectangle(476.5+x, 493.5, 3, 8, color=(220, 220, 255, 255), batch=batchastronauta)
        self.torzo = shapes.Rectangle(465+x, 500, 15, 25, color=(250, 250, 255, 255), batch=batchastronauta)
        self.cabeza = shapes.Circle(472.3+x, 530, 10, segments=None, color=(200, 200, 255, 255), batch= batchastronauta)
    def draw(self):  
        self.brazoizq.y -= 5
        self.brazoizq.draw()
        self.brazodere.y -= 5
        self.brazodere.draw()
        self.piernaizq.y -= 5
        self.piernaizq.draw()
        self.piernadere.y -= 5
        self.piernadere.draw()
        self.torzo.y -=5
        self.torzo.draw()
        self.cabeza.y -= 5
        self.cabeza.draw()

astronautalist = list()
def newastronauta(t):
    x = random.randint(-400,400)
    a = astronauta(x)
    starlist.append(a)
def updateastronauta(t):
    window.clear()
    for astronauta in astronautalist:
        astronauta.draw()

pyglet.clock.schedule_interval(updateastronauta,0.1)
pyglet.clock.schedule_interval(newastronauta,5)

@window.event
def on_draw():
    window.clear()
    batchestrella.draw()
    batchnave.draw()
    batchastronauta.draw()

pyglet.app.run()