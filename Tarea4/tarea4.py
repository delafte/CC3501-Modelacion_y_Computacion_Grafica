from socket import has_ipv6
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
import random

from grafica.gpu_shape import createGPUShape
from grafica.obj_handler import read_OBJ2
from grafica.assets_path import getAssetPath
#from pyglet.graphics.shader.Shader import Shader, ShaderProgram
from pathlib import Path
from itertools import chain
#from pyglet.graphics.shader import Shader, ShaderProgram

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 1280, 800

with open(Path(os.path.dirname(__file__)) / "grafica/vertex_shader.glsl") as f:
    vertex_program = f.read()

with open(Path(os.path.dirname(__file__)) / "grafica/point_fragment_program.glsl") as f:
    fragment_program = f.read()
vert_shader = pyglet.graphics.shader.Shader(vertex_program, "vertex")
frag_shader = pyglet.graphics.shader.Shader(fragment_program, "fragment")

class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="naves"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.showAxis = True
        self.pipeline = sh.MultipleLightTexturePhongShaderProgram()
        self.pipeline2 =  pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        self.repeats = 0
        self.step = 0

controller = Controller(width=WIDTH, height=HEIGHT)

glClearColor(0.0, 0.0, 0.0, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)

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

        self.camino = False
        self.guardarp = False
        
        self.puntos = []
        self.orientacionesy = []
        self.orientacionesz = []
        self.anterior = None
        self.graficarcurve = False
        self.haycurva = False
        self.curva = None
        self.pirueta = False
        self.angpiru=None
        self.ang = None
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

        self.projection = "ortho"
        self.projection2 = "perspective"
        self.proactual = "ortho"
        self.infopro = tr.ortho(-8, 8, -8, 8, 0.1, 100)

        self.anguloy =0
        self.anguloz=0
        self.speed = 0.12
        self.avance = 0

    def update(self,coordenadas,anguloz,anguloy):
        if self.proactual == self.projection:
            self.eye[0] = coordenadas[0]+self.x
            self.eye[1] = coordenadas[1]+self.y
            self.eye[2] = coordenadas[2]+self.z
            self.up = np.array([0.0, 0.0, 1.0])
            self.at[0] = coordenadas[0]
            self.at[1] = coordenadas[1]
            self.at[2] = coordenadas[2]
        else:
            x = float(coordenadas[0])
            y = float(coordenadas[1])
            z = float(coordenadas[2])
            nave_position = np.array([x, y, z, 1])
            camera_transform = tr.matmul([tr.rotationZ(anguloz),tr.rotationY(anguloy),tr.translate(-5,0,0), tr.rotationY(-anguloy), tr.rotationZ(-anguloz)])
            camera_position = np.matmul(camera_transform,nave_position)
            self.eye = camera_position[0:3]
            if np.cos(anguloy)>=0:
                self.up = np.array([0.0, 0.0, 1.0])
            else: 
                self.up = np.array([0.0, 0.0, -1.0])
            self.at[0] = coordenadas[0]
            self.at[1] = coordenadas[1]
            self.at[2] = coordenadas[2]
class contador:
    def __init__(self,obj,tex,pipeline):
        self.shape = createGPUShape(pipeline, read_OBJ2(obj))
        self.shape.texture=sh.textureSimpleSetup(tex, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        self.reiniciar = False
        self.num = 1
    def update(self,tex):
        self.shape.texture=sh.textureSimpleSetup(tex, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)


class anillo:
    def __init__(self, obj,tex,pipeline):
        self.shape = createGPUShape(pipeline,read_OBJ2(obj))
        self.shape.texture = sh.textureSimpleSetup(tex, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
        self.x=0
        self.y=0
        self.z=0
        self.atrapar=False
    def update(self):
        self.x = random.randint(-10,10)
        self.y =random.randint(-10,10)
        self.z =random.randint(-10,10)
    def dist(self,anillo,coordenadasnave):
        xa=anillo[0]
        ya=anillo[1]
        za=anillo[2]
        xn=coordenadasnave[0]
        yn=coordenadasnave[1]
        zn=coordenadasnave[2]
        return np.sqrt(((xa-xn)**2) +((ya-yn)**2) + ((za-zn)**2))


class PointLight:
    def __init__(self, pos: list) -> None:
        self.attribs = {
            "position": np.array(pos),
            "ambient": np.array([0.2, 0.2, 0.2]),
            "diffuse": np.array([0.9, 0.9, 0.9]),
            "specular": np.array([1.0, 1.0, 1.0]),
            "constant": 0.1,
            "linear": 0.1,
            "quadratic": 0.01
        }

    def set_pos(self, x, y, z):
        self.attribs["position"] = np.array([x, y, z])

    def set_ambient(self, r, g, b):
        self.attribs["ambient"] = np.array([r, g, b])

    def set_diffuse(self, r, g, b):
        self.attribs["diffuse"] = np.array([r, g, b])

    def set_specular(self, r, g, b):
        self.attribs["specular"] = np.array([r, g, b])

    def show_colors(self):
        colors = f"ambient: ({self.attribs['ambient']})\n"
        colors += f"diffuse: ({self.attribs['diffuse']})\n"
        colors += f"specular: ({self.attribs['specular']})\n"
        return colors
pointlights = []

pointlights.append(PointLight([0.0, 0.0, 10.0]))
pointlights.append(PointLight([-15.0, -7.0, 10.0]))
pointlights.append(PointLight([8.0, -3.0, 10.0]))
pointlights.append(PointLight([-8.0, 3.0, 10.0]))

glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.ambient"), 0.7, 0.7, 0.7)
glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.diffuse"), 0.9, 0.9, 0.9)
glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.specular"), 1.0, 1.0, 1.0)
glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "material.shininess"), 32)
for i, pointlight in enumerate(pointlights):
    pointlight.set_ambient(1.0,0.9,0.9)
    pointlight.set_diffuse(1.0,0.9,0.9)
    pointlight.set_specular(1.0,0.9,0.9)
    for key in pointlight.attribs.keys():
        attrib = pointlight.attribs[key]
        if isinstance(attrib, float):
            glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, f"pointLights[{i}].{key}"), attrib)
        elif isinstance(attrib, np.ndarray):
            glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, f"pointLights[{i}].{key}"), *attrib)
        
obj=getAssetPath("naveultintento.obj")
nave_tex = getAssetPath("Ship_texture.jpg")
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
anillotex = getAssetPath("anillo.jpg")
anilloshape = anillo(obj4,anillotex,controller.pipeline)
anillo2shape=anillo(obj4,anillotex,controller.pipeline)
anillo3shape=anillo(obj4,anillotex,controller.pipeline)
anillo4shape=anillo(obj4,anillotex,controller.pipeline)

obj5 = getAssetPath("astronauta.obj")
astrotex = getAssetPath("astro.jpg")
astroshape = createGPUShape(controller.pipeline, read_OBJ2(obj5))
astroshape.texture = sh.textureSimpleSetup(astrotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj6 = getAssetPath("estrella.obj")
startex = getAssetPath("estrella.jpg")
starshape = createGPUShape(controller.pipeline, read_OBJ2(obj6))
starshape.texture = sh.textureSimpleSetup(startex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj7 =getAssetPath("Oso2.obj")
osotex = getAssetPath("oso.jpg")
ososhape= createGPUShape(controller.pipeline, read_OBJ2(obj7))
ososhape.texture = sh.textureSimpleSetup(osotex,GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

obj8 = getAssetPath("contador.obj")
conttex=getAssetPath("Contador0.png")
contshape=contador(obj8,conttex,controller.pipeline)

obj9 = getAssetPath("sphere.obj")
sphtx=getAssetPath("uni.png")
sphshape=createGPUShape(controller.pipeline,read_OBJ2(obj9))
sphshape.texture=sh.textureSimpleSetup(sphtx, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

def CreateScene(naveShape):
    sp=sg.SceneGraphNode("esfera")
    sp.transform=tr.matmul([tr.translate(0,0,20),tr.uniformScale(60)])
    sp.childs+=[sphshape]

    contador1=sg.SceneGraphNode("contador1")
    contador1.transform=tr.matmul([tr.translate(20,0,-0.5),tr.uniformScale(1.2), tr.rotationZ(np.pi),tr.rotationX(np.pi/2)])
    contador1.childs += [contshape.shape]

    contador2=sg.SceneGraphNode("contador2")
    contador2.transform=tr.matmul([tr.translate(-20,0,-0.5),tr.uniformScale(1.2),tr.rotationX(np.pi/2)])
    contador2.childs += [contshape.shape]

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

    anillo = sg.SceneGraphNode("anillo")
    anillo.transform = tr.matmul([tr.translate(random.randint(-20,20),random.randint(-20,20),random.randint(5,10)),tr.uniformScale(1.5),tr.rotationZ(random.uniform(0,np.pi/4))])
    anillo.childs += [anilloshape.shape]
    anillotrsl=sg.SceneGraphNode("anillotrsl")
    anillotrsl.childs+=[anillo]

    anillo2 = sg.SceneGraphNode("anillo2")
    anillo2.transform = tr.matmul([tr.translate(random.randint(-20,20),random.randint(-20,20),random.randint(5,10)),tr.uniformScale(1.5),tr.rotationZ(random.uniform(0,np.pi/4))])
    anillo2.childs += [anillo2shape.shape]
    anillotrsl2=sg.SceneGraphNode("anillo2trsl")
    anillotrsl2.childs+=[anillo2]

    anillo3 = sg.SceneGraphNode("anillo3")
    anillo3.transform = tr.matmul([tr.translate(random.randint(-20,20),random.randint(-20,20),random.randint(5,10)),tr.uniformScale(1.5),tr.rotationZ(random.uniform(0,np.pi/4))])
    anillo3.childs += [anillo3shape.shape]
    anillotrsl3=sg.SceneGraphNode("anillo3trsl")
    anillotrsl3.childs+=[anillo3]

    anillo4 = sg.SceneGraphNode("anillo4")
    anillo4.transform = tr.matmul([tr.translate(random.randint(-20,20),random.randint(-20,20),random.randint(5,10)),tr.uniformScale(1.5),tr.rotationZ(random.uniform(0,np.pi/4))])
    anillo4.childs += [anillo4shape.shape]
    
    anillotrsl4=sg.SceneGraphNode("anillo4trsl")
    anillotrsl4.childs+=[anillo4]

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
    plano.transform = tr.matmul([tr.translate(0,0,-1),tr.uniformScale(30),tr.rotationX(np.pi/2)])
    plano.childs += [planoshape]

    oso = sg.SceneGraphNode("oso")
    oso.transform = tr.matmul([tr.translate(-5,-4,0),tr.uniformScale(0.3), tr.rotationX(np.pi/2)])
    oso.childs += [ososhape]

    scene = sg.SceneGraphNode("scene")

    scene.childs += [sombratrasl]
    scene.childs += [navetrasl]
    scene.childs += [plano]
    scene.childs += [contador1,contador2,pochitauwu,anillotrsl,anillotrsl2,anillotrsl3,anillotrsl4,astromov,star,star2,oso,sp]

    return scene

#creamos la escena
escena = CreateScene(naveshape)
camera= camara()

def update(dt, window):
    window.total_time += dt

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def hermiteMatrix(P1, P2, T1, T2):
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])
    return np.matmul(G, Mh)
def evalCurve(M, N):
    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(N, 3), dtype=float)
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve


@controller.event
def on_key_press(symbol,modifiers):
    if naveshape.camino == False and naveshape.pirueta==False:
        if symbol == pyglet.window.key.A:
            naveshape.z_direction_rot = np.pi/50
            navesombra.z_direction_rot = np.pi/50
        if symbol == pyglet.window.key.D:
            naveshape.z_direction_rot = -np.pi/50
            navesombra.z_direction_rot = -np.pi/50
        if symbol == pyglet.window.key.W:
            naveshape.x_direction_avance = 1
            navesombra.x_direction_avance = 1
        if symbol == pyglet.window.key.S:
            naveshape.x_direction_avance = -1
            navesombra.x_direction_avance = 1 
        if symbol == pyglet.window.key.X:
            contshape.reiniciar=True
            if contshape.num == 6:
                txt =getAssetPath("Contador0.png")
                contshape.update(txt)
                contshape.num=1
                contshape.reiniciar=False

        if symbol == pyglet.window.key.R:
            naveshape.guardarp = True
        if symbol == pyglet.window.key._1:
            if len(naveshape.puntos) >= 4:
                naveshape.camino = True
            else:
                print("faltan puntos de control, deben ser 4 mínimo para Catmull-Rom")
    if symbol == pyglet.window.key.C:
        if camera.proactual == camera.projection:
            camera.proactual = camera.projection2
        else:
            camera.proactual = camera.projection
    if symbol==pyglet.window.key.V:
        if len(naveshape.puntos) >= 4:
            naveshape.graficarcurve = True
        else:
            print("faltan puntos de control, deben ser 4 mínimo para Catmull-Rom")
    if naveshape.camino == False:
        if symbol == pyglet.window.key.P:
            naveshape.pirueta = True
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

@controller.event
def on_mouse_motion(x,y,dx,dy):
    if naveshape.camino == False and naveshape.pirueta==False:
        if dy > 0:
            naveshape.y_direction_rot = -np.pi/50
            navesombra.y_direction_rot = -np.pi/50
        if dy < 0:
            naveshape.y_direction_rot = np.pi/50
            navesombra.y_direction_rot = np.pi/50

@controller.event
def on_key_release(symbol,modifiers):
    if naveshape.camino == False and naveshape.pirueta==False:
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

N=150
@controller.event
def on_draw():
    controller.clear()

    if naveshape.pirueta==True and naveshape.angpiru != None:
        naveshape.y_direction_rot = np.pi/30
        naveshape.x_direction_avance = 2
        navesombra.y_direction_rot = np.pi/30
        navesombra.x_direction_avance = 2

    naveshape.update()
    navesombra.update() 

    
    if naveshape.camino == False and naveshape.pirueta == False:
        navemover = sg.findNode(escena, "naverot")
        sombramover = sg.findNode(escena,"sombrarot")
        navemover2 = sg.findNode(escena, "navetrasl")
        sombramover2 = sg.findNode(escena,"sombratrasl")
        

        navemover.transform = tr.matmul([tr.rotationZ(naveshape.anguloz),tr.rotationY(naveshape.anguloy)])
        sombramover.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0), tr.rotationZ(navesombra.anguloz),tr.rotationY(navesombra.anguloy)])

        navemover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,naveshape.z)])
        sombramover2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,0)])

    coordenadasnave = sg.findPosition(escena,"navetrasl")
    anguloz=naveshape.anguloz
    anguloy=naveshape.anguloy
    camera.update(coordenadasnave, anguloz,anguloy)
    astromov = sg.findNode(escena,"astromov")
    astromov.transform = tr.rotationZ(np.pi/20*controller.total_time)
    #if anilloshape.atrapar == True:
    anillos=[]
    posanillo=sg.findPosition(escena, "anillo")
    anillos.append(posanillo)
    posanillo2=sg.findPosition(escena,"anillo2")
    anillos.append(posanillo2)
    posanillo3=sg.findPosition(escena,"anillo3")
    anillos.append(posanillo3)
    posanillo4 = sg.findPosition(escena,"anillo4")
    anillos.append(posanillo4)

    i=1
    for anillo in anillos:
        if i==1:
            dist=anilloshape.dist(anillo,coordenadasnave)
        elif i == 2:
            dist=anillo2shape.dist(anillo,coordenadasnave)
        elif i == 3:
            dist=anillo3shape.dist(anillo,coordenadasnave)
        else:
            dist=anillo4shape.dist(anillo,coordenadasnave)
        if dist <= 0.7:
            if i==1:
                anilloshape.update()
                trs=sg.findNode(escena,"anillotrsl")
                if anillo[2]+anilloshape.z <0:
                    anilloshape.z=3
                trs.transform=tr.matmul([tr.translate(anilloshape.x,anilloshape.y,anilloshape.z)])
                txt=getAssetPath(f"Contador{contshape.num}.png")
                contshape.update(txt)
                contshape.num+=1
            elif i==2:
                anillo2shape.update()
                if anillo[2]+anilloshape.z <0:
                    anilloshape.z=3
                trs=sg.findNode(escena,"anillo2trsl")
                trs.transform=tr.matmul([tr.translate(anillo2shape.x,anillo2shape.y,anillo2shape.z)])
                txt=getAssetPath(f"Contador{contshape.num}.png")
                contshape.update(txt)
                contshape.num+=1
            elif i==3:
                anillo3shape.update()
                trs=sg.findNode(escena,"anillo3trsl")
                if anillo[2]+anilloshape.z <0:
                    anilloshape.z=3
                trs.transform=tr.matmul([tr.translate(anillo3shape.x,anillo3shape.y,anillo3shape.z)])
                txt=getAssetPath(f"Contador{contshape.num}.png")
                contshape.update(txt)
                contshape.num+=1
            else:
                anillo4shape.update()
                trs=sg.findNode(escena,"anillo4trsl")
                if anillo[2]+anilloshape.z <0:
                    anilloshape.z=3
                trs.transform=tr.matmul([tr.translate(anillo4shape.x,anillo4shape.y,anillo4shape.z)])
                txt=getAssetPath(f"Contador{contshape.num}.png")
                contshape.update(txt)
                contshape.num+=1
        i+=1

    if naveshape.guardarp == True:
        coordenada2 = sg.findPosition(escena, "naverot")
        coordenada2 = coordenada2 / coordenada2[3]
        coordenada2 = coordenada2[0:3]
        naveshape.puntos.append(coordenada2)
        naveshape.orientacionesy.append(naveshape.anguloy)
        naveshape.orientacionesz.append(naveshape.anguloz)
 
    if controller.fillPolygon:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    if camera.proactual == camera.projection:
        camera.infopro = tr.ortho(-8, 8, -8, 8, 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       tr.ortho(-8, 8, -8, 8, 0.1, 100))
    else:
        camera.infopro = tr.perspective(60, float(WIDTH)/float(HEIGHT), 1, 1000)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE,
                       tr.perspective(60, float(WIDTH)/float(HEIGHT), 1, 1000))
    view = tr.lookAt(
            camera.eye,
            camera.at,
            camera.up
        )
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    naveshape.y_direction_rot = 0
    navesombra.y_direction_rot = 0

    #----------------------pirueta
    if naveshape.pirueta == True:
        if naveshape.angpiru == None:
            naveshape.angpiru = naveshape.anguloy

        elif naveshape.anguloy >= naveshape.angpiru + (2*np.pi):
           naveshape.pirueta = False
           naveshape.y_direction_rot = 0
           naveshape.x_direction_avance = 0
           naveshape.anguloy = naveshape.angpiru
           navesombra.anguloy =naveshape.angpiru
           naveshape.angpiru = None
           naveshape.ang = None
           navesombra.y_direction_rot=0
           navesombra.x_direction_avance=0
           naveshape.update()
           navesombra.update() 
        else:
            navemove = sg.findNode(escena, "naverot")
            sombramove = sg.findNode(escena,"sombrarot")
            navemove2 = sg.findNode(escena, "navetrasl")
            sombramove2 = sg.findNode(escena,"sombratrasl")
            
            navemove.transform = tr.matmul([tr.rotationZ(naveshape.anguloz),tr.rotationY(naveshape.anguloy)])
            sombramove.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.rotationZ(naveshape.anguloz), tr.rotationY(navesombra.anguloy)])

            navemove2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,naveshape.z)])
            sombramove2.transform = tr.matmul([tr.translate(naveshape.x,naveshape.y,0)])


    # ------------------------------------------------------------CURVA
    if naveshape.graficarcurve == True or naveshape.camino == True:
        if naveshape.haycurva == False:
            t0=np.array([[np.cos(naveshape.orientacionesy[0])*np.cos(naveshape.orientacionesz[0]),np.cos(naveshape.orientacionesy[0])*np.sin(naveshape.orientacionesz[0]), -np.sin(naveshape.orientacionesy[0])]]).T
            t1= (naveshape.puntos[2]-naveshape.puntos[0])/2
            M0 = hermiteMatrix(naveshape.puntos[0],naveshape.puntos[1],t0,t1)
            hermiteCurve0 = evalCurve(M0,N)
            naveshape.curva=hermiteCurve0

            for i in range(1,len(naveshape.puntos)-1):
                if i+1==len(naveshape.puntos)-1:
                    angy = naveshape.orientacionesy[i+1]
                    angz = naveshape.orientacionesz[i+1]
                    ti22 = np.array([[np.cos(angy)*np.cos(angz),np.cos(angy)*np.sin(angz), -np.sin(angy)]]).T
                    ti2= ti22/np.linalg.norm(ti22)
                    ti = (naveshape.puntos[i+1]-naveshape.puntos[i-1])/2
                    M1 = hermiteMatrix(naveshape.puntos[i],naveshape.puntos[i+1],ti,ti2)
                    hermiteCurve1 = evalCurve(M1,N)
                    naveshape.curva=np.concatenate((naveshape.curva[:-1],hermiteCurve1))
                else:
                    ti2= (naveshape.puntos[i+2]-naveshape.puntos[i])/2
                    ti = (naveshape.puntos[i+1]-naveshape.puntos[i-1])/2
                    M1 = hermiteMatrix(naveshape.puntos[i],naveshape.puntos[i+1],ti,ti2)
                    hermiteCurve1 = evalCurve(M1,N)
                    naveshape.curva=np.concatenate((naveshape.curva[:-1],hermiteCurve1))
            naveshape.haycurva = True
 
        elif naveshape.graficarcurve == True and naveshape.guardarp == True:
            i = len(naveshape.puntos)-1
            tiprev = (naveshape.puntos[i-1]-naveshape.puntos[i-3])/2
            ti =(naveshape.puntos[i]-naveshape.puntos[i-2])/2
            angy = naveshape.orientacionesy[i]
            angz = naveshape.orientacionesz[i]
            tm1 = np.array([[np.cos(angy)*np.cos(angz),np.cos(angy)*np.sin(angz), -np.sin(angy)]]).T
            tm=tm1/np.linalg.norm(tm1)
            M2 =hermiteMatrix(naveshape.puntos[i-2], naveshape.puntos[i-1],tiprev, ti)
            M3 = hermiteMatrix(naveshape.puntos[i-1], naveshape.puntos[i],ti, tm)
            hermiteCurvednv=evalCurve(M2,N)
            hermiteCurve3 = evalCurve(M3,N)
            naveshape.curva= np.concatenate((naveshape.curva[:-N],hermiteCurvednv[:-1],hermiteCurve3))

        if naveshape.camino == True:
            movernave = sg.findNode(escena, "navetrasl")
            movernave2 = sg.findNode(escena, "naverot")
            moversombra = sg.findNode(escena,"sombratrasl")
            moversombra2 = sg.findNode(escena, "sombrarot")
            naveshape.x = naveshape.curva[controller.step,0]
            naveshape.y = naveshape.curva[controller.step,1]
            naveshape.z = naveshape.curva[controller.step,2]
            navesombra.x = naveshape.curva[controller.step,0]
            navesombra.y = naveshape.curva[controller.step,1]
            navesombra.z = naveshape.curva[controller.step,2]
            movernave.transform = tr.matmul([tr.translate(naveshape.curva[controller.step, 0],naveshape.curva[controller.step, 1], naveshape.curva[controller.step, 2])])
            moversombra.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.translate(naveshape.curva[controller.step, 0],naveshape.curva[controller.step, 1], 0)])
            
            if controller.step == 0:
                movernave2.transform = tr.matmul([tr.rotationZ(naveshape.orientacionesz[0]),tr.rotationY(naveshape.orientacionesy[0]),tr.rotationY(-naveshape.anguloy),tr.rotationZ(-naveshape.anguloz)])
                naveshape.anguloy += naveshape.orientacionesy[0] - naveshape.anguloy
                naveshape.anguloz += naveshape.orientacionesz[0] - naveshape.anguloz
            
            if controller.step<(N*(len(naveshape.puntos)-1)-(len(naveshape.puntos)-1)-1):
                z = naveshape.curva[controller.step+1,2]-naveshape.curva[controller.step,2]
                y = naveshape.curva[controller.step+1,1]-naveshape.curva[controller.step,1]
                x = naveshape.curva[controller.step+1,0]-naveshape.curva[controller.step,0]
                rho=np.sqrt((x*x)+(y*y)+(z*z))

                anguloy = np.sign(-x)*np.arcsin(z/rho)
                anguloz = np.sign(y)*np.arccos(x/np.sqrt((x*x)+(y*y)))
                
                navesombra.anguloz = anguloz
                navesombra.anguloy = anguloy
                naveshape.anguloy = anguloy
                naveshape.anguloz = anguloz
     
                movernave2.transform = tr.matmul([tr.rotationY(naveshape.anguloy),tr.rotationZ(naveshape.anguloz)])
                moversombra2.transform = tr.matmul([tr.translate(0,0,-0.9),tr.scale(1,1,0),tr.rotationY(navesombra.anguloy),tr.rotationZ(navesombra.anguloz)])
                coordenadasnave = sg.findPosition(escena,"navetrasl")
                anguloz=naveshape.anguloz
                anguloy=naveshape.anguloy
                camera.update(coordenadasnave, anguloz,anguloy)
            if controller.step>=(N*(len(naveshape.puntos)-1)-(len(naveshape.puntos)-1)-1):
                naveshape.camino = False
                controller.step = 0
                naveshape.puntos = []
                naveshape.tangentes = []
                naveshape.orientacionesy = []
                naveshape.orientacionesz = []
                naveshape.graficarcurve = False
                naveshape.curva = None
                naveshape.haycurva = False
            controller.step+=1 
    
        if naveshape.graficarcurve == True:
            controller.node_data= controller.pipeline2.vertex_list(
            len(naveshape.curva), pyglet.gl.GL_POINTS, position="f"
            )
            controller.joint_data = controller.pipeline2.vertex_list_indexed(
            len(naveshape.curva),
            pyglet.gl.GL_LINES,
            tuple(chain(*(j for j in [range(len(naveshape.curva))]))),
            position="f",
            )
            controller.node_data.position[:] = tuple(
                chain(*((p[0], p[1], p[2]) for p in naveshape.curva))
            )

            controller.joint_data.position[:] = tuple(
                chain(*((p[0], p[1], p[2]) for p in naveshape.curva))
            )
            controller.pipeline2["projection"] = camera.infopro.reshape(16, 1, order="F")
            controller.pipeline2["view"] = view.reshape(16, 1, order="F")
            
            controller.pipeline2.use()
            controller.node_data.draw(pyglet.gl.GL_POINTS)
            controller.joint_data.draw(pyglet.gl.GL_LINES)
    naveshape.guardarp=False
    glUseProgram(controller.pipeline.shaderProgram)
    sg.drawSceneGraphNode(escena, controller.pipeline, "model")
pyglet.clock.schedule(update, controller)
pyglet.app.run()
