
import sys
import os
import pyglet
import numpy as np
from pyglet.gl import *

import grafica.shaders as sh
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg

from grafica.gpu_shape import createGPUShape
from grafica.obj_handler import read_OBJ2
from grafica.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# A class to store the application control

# Se asigna el ancho y alto de la ventana y se crea.
WIDTH, HEIGHT = 1280, 800


# Controlador que permite comunicarse con la ventana de pyglet
class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="naves uwu"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.showAxis = True
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()
        self.repeats = 0

controller = Controller(width=WIDTH, height=HEIGHT)
# Se asigna el color de fondo de la ventana
glClearColor(0.0, 0.0, 0.0, 1.0)
# Como trabajamos en 3D, necesitamos chequear cuáles objetos están en frente, y cuáles detrás.
glEnable(GL_DEPTH_TEST)

# Se configura el pipeline y se le dice a OpenGL que utilice ese shader
glUseProgram(controller.pipeline.shaderProgram)

# El controlador puede recibir inputs del usuario. Estas funciones define cómo manejarlos.
@controller.event
def on_key_press(symbol, modifiers):

    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif symbol == pyglet.window.key.LCTRL:
        controller.showAxis = not controller.showAxis

    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

    else:
        print('Unknown key')

class nave:
    def __init__(self,obj,textura, pipeline):
        self.shape = createGPUShape(pipeline,read_OBJ2(obj))
        self.shape.texture = sh.textureSimpleSetup(textura, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        self.x = 0
        self.y = 0
        self.z = 0
        self.x_direction_avance = 0
        self.y_direction_rot = 0#theta
        self.z_direction_rot = 0#phi
        self.x_speed = 0.12
        self.y_speed = 0.12
        self.z_speed = 0.12
        self.anguloy = 0
        self.anguloz = 0

    def update(self):#(r,theta=zdirect,phi=ydirect)
        self.anguloy += self.y_direction_rot
        self.anguloz += self.z_direction_rot

        self.x += np.cos(self.anguloy)*np.cos(self.anguloz)*self.x_direction_avance*self.x_speed
        self.y += np.cos(self.anguloy)*self.x_direction_avance*np.sin(self.anguloz)*self.y_speed
        newZ = self.z + -np.sin(self.anguloy)*self.x_direction_avance*self.z_speed
        if newZ >= 0:
            self.z = newZ
        
class camara:
    def __init__(self, at=np.array([0.0, 0.0, 0.0]), eye=np.array([5.0, 5.0, 5.0]), up=np.array([0.0, 0.0, 1.0])) -> None:
        self.at = at
        self.eye = eye
        self.up = up

        self.x = np.square(self.eye[0])
        self.y = np.square(self.eye[1])
        self.z = np.square(self.eye[2])

        self.projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

    def update(self,coordenadas):

        self.eye[0] = coordenadas[0]+self.x
        self.eye[1] = coordenadas[1]+self.y
        self.eye[2] = coordenadas[2]+self.z

        self.at[0] = coordenadas[0]
        self.at[1] = coordenadas[1]
        self.at[2] = coordenadas[2]
        
obj=getAssetPath("naveultintento.obj")
nave_tex = getAssetPath("Ship_texture.png")
sombra_tex = getAssetPath("sombra_texture.png")
naveshape = nave(obj,nave_tex,controller.pipeline)
navesombra = nave(obj,sombra_tex,controller.pipeline)

obj2 = getAssetPath("plano2.obj")
planotex= getAssetPath("fondo.png")
planoshape = createGPUShape(controller.pipeline, read_OBJ2(obj2))
planoshape.texture=sh.textureSimpleSetup(planotex, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj3 =getAssetPath("pochita3.obj")
pochitatex = getAssetPath("pochita.png")
pochitashape = createGPUShape(controller.pipeline, read_OBJ2(obj3))
pochitashape.texture = sh.textureSimpleSetup(pochitatex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj4 = getAssetPath("anillo.obj")
anillotex = getAssetPath("anillo.png")
anilloshape = createGPUShape(controller.pipeline, read_OBJ2(obj4))
anilloshape.texture = sh.textureSimpleSetup(anillotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj5 = getAssetPath("astronauta.obj")
astrotex = getAssetPath("astro.png")
astroshape = createGPUShape(controller.pipeline, read_OBJ2(obj5))
astroshape.texture = sh.textureSimpleSetup(astrotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj6 = getAssetPath("estrella.obj")
startex = getAssetPath("estrella.png")
starshape = createGPUShape(controller.pipeline, read_OBJ2(obj6))
starshape.texture = sh.textureSimpleSetup(startex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj7 =getAssetPath("Oso2.obj")
osotex = getAssetPath("oso.png")
ososhape= createGPUShape(controller.pipeline, read_OBJ2(obj7))
ososhape.texture = sh.textureSimpleSetup(osotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

def CreateScene(naveShape):

    nave = sg.SceneGraphNode("naveNode")
    nave.transform = tr.matmul([tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave.childs += [naveShape.shape]
    
    nave2 = sg.SceneGraphNode("nave2Node")
    nave2.transform = tr.matmul([tr.translate(-2,-1,0),tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave2.childs += [naveShape.shape]

    nave3 = sg.SceneGraphNode("nave3Node")
    nave3.transform =tr.matmul([tr.translate(-2,1,0),tr.rotationX(np.pi),tr.uniformScale(0.1)])
    nave3.childs += [naveShape.shape]

    navesombra1 = sg.SceneGraphNode("navesombra")
    navesombra1.transform = tr.matmul([tr.translate(0,0,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra1.childs += [navesombra.shape]

    navesombra2 = sg.SceneGraphNode("navesombra2")
    navesombra2.transform = tr.matmul([tr.translate(-2,-1,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra2.childs += [navesombra.shape]

    navesombra3 = sg.SceneGraphNode("navesombra3")
    navesombra3.transform = tr.matmul([tr.translate(-2,1,-1.9),tr.scale(0.1,0.1,0.0)])
    navesombra3.childs += [navesombra.shape]

    sombrarot = sg.SceneGraphNode("sombrarot")
    sombrarot.childs += [navesombra1,navesombra2,navesombra3]

    sombratrasl = sg.SceneGraphNode("sombratrasl")
    sombratrasl.childs += [sombrarot]

    naverot = sg.SceneGraphNode("naverot")
    naverot.childs += [nave,nave2,nave3]

    navetrasl = sg.SceneGraphNode("navetrasl")
    navetrasl.childs += [naverot]

    anillomov = sg.SceneGraphNode("anillomov")
    anillomov.childs += [anilloshape]

    anillo = sg.SceneGraphNode("anillo")
    anillo.transform = tr.matmul([tr.translate(5,0,1)])
    anillo.childs += [anillomov]

    astronauta = sg.SceneGraphNode("astronauta")
    astronauta.transform = tr.matmul([tr.translate(-4,-7,1),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    astronauta.childs += [astroshape]

    astromov = sg.SceneGraphNode("astromov")
    astromov.childs += [astronauta]

    pochitauwu = sg.SceneGraphNode("Pochita")
    pochitauwu.transform = tr.matmul([tr.translate(-5,4,0),tr.uniformScale(2.0),tr.rotationX(np.pi/2),tr.rotationY(np.pi/2)])
    pochitauwu.childs += [pochitashape]

    star = sg.SceneGraphNode("star")
    star.transform = tr.matmul([tr.translate(-3,-3,0),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    star.childs += [starshape]

    star2 = sg.SceneGraphNode("star2")
    star2.transform = tr.matmul([tr.translate(-3,3,0),tr.rotationX(np.pi/2),tr.uniformScale(0.5)])
    star2.childs += [starshape]

    plano = sg.SceneGraphNode("plano")
    plano.transform = tr.matmul([tr.translate(0,0,-1),tr.uniformScale(20),tr.rotationX(np.pi/2)])
    plano.childs += [planoshape]

    oso = sg.SceneGraphNode("oso")
    oso.transform = tr.matmul([tr.translate(-5,-4,0),tr.uniformScale(0.3), tr.rotationX(np.pi/2)])
    oso.childs += [ososhape]

    scene = sg.SceneGraphNode("scene")

    scene.childs += [sombratrasl]
    scene.childs += [navetrasl]
    scene.childs += [plano]
    scene.childs += [pochitauwu,anillo,astromov,star,star2,oso]

    return scene

#creamos la escena
escena = CreateScene(naveshape)
camera= camara()

# Esta función se ejecuta aproximadamente 60 veces por segundo, dt es el tiempo entre la última
# ejecución y ahora
def update(dt, window):
    window.total_time += dt

@controller.event
def on_key_press(symbol,modifiers):
    if symbol == pyglet.window.key.A:
        naveshape.z_direction_rot = np.pi/30
        navesombra.z_direction_rot = np.pi/30
    if symbol == pyglet.window.key.D:
        naveshape.z_direction_rot = -np.pi/30
        navesombra.z_direction_rot = -np.pi/30
    if symbol == pyglet.window.key.W:
        naveshape.x_direction_avance = 1
        navesombra.x_direction_avance = 1
    if symbol == pyglet.window.key.S:
        naveshape.x_direction_avance = -1
        navesombra.x_direction_avance = 1    
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

@controller.event
def on_mouse_motion(x,y,dx,dy):
    if dy > 0:
        naveshape.y_direction_rot = -np.pi/30
        navesombra.y_direction_rot = -np.pi/30
    if dy < 0:
        naveshape.y_direction_rot = np.pi/30
        navesombra.y_direction_rot = np.pi/30

@controller.event
def on_key_release(symbol,modifiers):
    if symbol == pyglet.window.key.A:
        naveshape.z_direction_rot = 0
        navesombra.z_direction_rot =0
    if symbol == pyglet.window.key.D:
        naveshape.z_direction_rot = 0
        navesombra.z_direction_rot =0
    if symbol == pyglet.window.key.W:
       naveshape.x_direction_avance = 0
       navesombra.x_direction_avance = 0
    if symbol == pyglet.window.key.S:
       naveshape.x_direction_avance = 0
       navesombra.x_direction_avance = 0

# Cada vez que se llama update(), se llama esta función también
@controller.event
def on_draw():
    controller.clear()

    naveshape.update()
    navesombra.update()

    navemover = sg.findNode(escena, "naverot")
    sombramover = sg.findNode(escena,"sombrarot")
    navemover2 = sg.findNode(escena, "navetrasl")
    sombramover2 = sg.findNode(escena,"sombratrasl")
    anillomov = sg.findNode(escena,"anillomov")
    astromov = sg.findNode(escena,"astromov")

    navemover.transform = tr.matmul([tr.rotationZ(naveshape.anguloz),tr.rotationY(naveshape.anguloy)])
    sombramover.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0), tr.rotationZ(navesombra.anguloz),tr.rotationY(navesombra.anguloy)])

    navemover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,naveshape.z)])
    sombramover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,0)])

    coordenadasnave = sg.findPosition(escena,"navetrasl")
    camera.update(coordenadasnave)

    astromov.transform = tr.rotationZ(np.pi/20*controller.total_time)
    anillomov.transform = tr.rotationZ(np.pi/5*controller.total_time)
    # Si el controller está en modo fillPolygon, dibuja polígonos. Si no, líneas.
    if controller.fillPolygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Using the same view and projection matrices in the whole application
    #projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       camera.projection)

    view = tr.lookAt(
            camera.eye,
            camera.at,
            camera.up
        )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    naveshape.y_direction_rot = 0
    navesombra.y_direction_rot = 0
    # Drawing the scene
    sg.drawSceneGraphNode(escena, controller.pipeline, "model")

# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
# Se ejecuta la aplicación
pyglet.app.run()
