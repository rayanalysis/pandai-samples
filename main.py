# Modified 4/27/2024 as an initial effort to modernize panda3d.ai

# This tutorial provides an example of creating a character and having it walk
# around using PandAI pathfinding with static obstacle avoidance

from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from direct.task import Task
from direct.actor.Actor import Actor
import sys
import os
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText

from panda3d.ai import *
import complexpbr
# import pandarecord

from NavMeshGenerator import *
import EggPrimitiveCreation

import random


base = ShowBase()
speed = 0.75
font = loader.loadFont("cmss12")


# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), font=font,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), font=font,
                        pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)


class World(ShowBase):
    def __init__(self):
        complexpbr.apply_shader(base.render)
        # pandarecord.setup_sg(base,cust_fr=144,max_screens=10000)

        self.keyMap = {"left": 0, "right": 0, "up": 0, "down": 0}

        addTitle("Pandai Tutorial: Adding Dynamic Obstacles")
        addInstructions(0.95, "[ESC]: Quit")
        addInstructions(0.90, "[Enter]: Start Pathfinding")
        addInstructions(0.85, "[Arrow Keys]: Move Arrow")
        addInstructions(0.80, "[1]: Small box")
        addInstructions(0.75, "[2]: Big box")
        addInstructions(0.70, "[Space]: Place box")
        addInstructions(0.65, "[F3]: Toggle Wireframe")

        # base.disableMouse()
        base.accept("f3", base.toggleWireframe)
        base.accept("escape", sys.exit, [0])

        base.cam.setPosHpr(0, -210, 135, 0, 327, 0)
        # base.cam.setPosHpr(0, -30, 30, 0, 327, 0)
        self.box = 0
        self.pointer_move = False
        self.loadModels()
        self.setAI()

    def loadModels(self):
        self.environ = loader.loadModel("models/arena_1.bam")
        self.environ.reparentTo(render)

        # Create the main character, Ralph
        # ralphStartPos = self.environ.find("**/start_point").getPos()
        ralphStartPos = Vec3(30, 30, 0)

        self.ralph = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})

        self.ralph.reparentTo(render)
        self.ralph.setScale(2)
        self.ralph.setPos(ralphStartPos)

        self.pointer = loader.loadModel("models/1m_sphere_black_marble.bam")
        self.pointer.setColor(1, 0, 0)
        self.pointer.setPos(35, 35, 0)
        self.pointer.setScale(3)
        self.pointer.reparentTo(render)

    def setAI(self):
        # Creating AI World
        self.AIworld = AIWorld(render)

        self.accept("enter", self.setMove)
        self.accept("1", self.addBlock)
        self.accept("2", self.addBigBlock)
        self.accept("space", self.addStaticObstacle)

        # Movement
        self.accept("arrow_left", self.setKey, ["left", 1])
        self.accept("arrow_right", self.setKey, ["right", 1])
        self.accept("arrow_up", self.setKey, ["up", 1])
        self.accept("arrow_down", self.setKey, ["down", 1])
        self.accept("arrow_left-up", self.setKey, ["left", 0])
        self.accept("arrow_right-up", self.setKey, ["right", 0])
        self.accept("arrow_up-up", self.setKey, ["up", 0])
        self.accept("arrow_down-up", self.setKey, ["down", 0])

        self.AIchar = AICharacter("ralph", self.ralph, 60, 0.05, 15)
        self.AIworld.addAiChar(self.AIchar)
        self.AIbehaviors = self.AIchar.getAiBehaviors()
        
        # the following loads in a "navmesh" .csv file
        # generated using an .egg primitive created on the fly
        # with built-in panda3d functions and some boutique
        # PandAI specific formatting for the 2D A* system
        prim_1_name = "squares"  # this is the navmesh primitive
        prim_2_name = "squares_coll"  # this is a copy of the navmesh primitive
        # we begin by making two meshes, one "Full" and one "Coll"
        # in order to build the 2D navigation mesh from .egg files
        # primitive_data_1 = EggPrimitiveCreation.makeWedge(360, 128, 200, "Full", 30)
        # primitive_data_2 = EggPrimitiveCreation.makeWedge(360, 128, 200, "Coll", 30)
        primitive_data_1 = EggPrimitiveCreation.makeSquaresEVPXZ(30, 30, 10, "Full",0)
        primitive_data_2 = EggPrimitiveCreation.makeSquaresEVPXZ(16, 16, 10, "Coll",0)
        # primitive_data_2 = EggPrimitiveCreation.makeSquaresEVPXZSparse(30, 30, 10, "Coll",0)
        primitive_data_1.writeEgg(Filename(prim_1_name + ".egg"))
        primitive_data_2.writeEgg(Filename(prim_2_name + ".egg"))

        # now we'll take these .egg files generated on the fly
        # and convert them to the 2D A* pathfinding system
        navmesh = NavMeshGenerator(prim_1_name + ".egg", prim_2_name + ".egg")
        # the navmesh has now been automatically created
        # and we can add it to the PandAI init_path_find()
        
        self.AIbehaviors.initPathFind("navmesh.csv")
        # self.AIbehaviors.initPathFind("models/navmesh.csv")

        # visually verify generated .egg files
        # egg_1 = loader.loadModel(prim_2_name + ".egg")
        # egg_1.reparentTo(base.render)
        # egg_1.setShaderOff()

        # AI World update
        taskMgr.add(self.AIUpdate, "AIUpdate")

        # Movement task
        taskMgr.add(self.Mover, "Mover")

        slight_1 = Spotlight('slight_1')
        slight_1.setColor(Vec4(Vec3(5),1))
        slight_1.setShadowCaster(True, 4096, 4096)
        # slight_1.set_attenuation((0.5,0,0.000005))
        lens = PerspectiveLens()
        slight_1.setLens(lens)
        slight_1.getLens().setFov(120)
        slight_1_node = base.render.attachNewNode(slight_1)
        slight_1_node.setPos(50, 50, 90)
        slight_1_node.lookAt(0,0,0.5)
        base.render.setLight(slight_1_node)

    def setMove(self):
        # self.AIbehaviors.pathFindTo(LVecBase3(random.randint(-200,200),random.randint(-200,200),0))
        self.AIbehaviors.pathFindTo(self.pointer)
        # self.AIbehaviors.seek(self.pointer)
        self.ralph.loop("run")

    def addBlock(self):
        self.pointer_move = True
        self.box = loader.loadModel("models/1m_sphere_black_marble.bam")
        self.box.setPos(0, -60, 0)
        self.box.setScale(1)
        self.box.reparentTo(render)

    def addBigBlock(self):
        self.pointer_move = True
        self.box = loader.loadModel("models/1m_sphere_black_marble.bam")
        self.box.setPos(0, -60, 0)
        self.box.setScale(2)
        self.box.setColor(1, 1, 0)
        self.box.reparentTo(render)

    def addStaticObstacle(self):
        if self.box != 0:
            self.AIbehaviors.addStaticObstacle(self.box)
            self.box = 0
            self.pointer_move = False

    # To update the AIWorld
    def AIUpdate(self, task):
        self.AIworld.update()
        #if self.AIbehaviors.behaviorStatus("pathfollow") == "done":
        #    self.ralph.stop("run")
        #    self.ralph.pose("walk", 0)

        return Task.cont

    def setKey(self, key, value):
        self.keyMap[key] = value

    def Mover(self, task):
        startPos = self.pointer.getPos()

        if self.keyMap["left"] != 0:
            self.pointer.setPos(startPos + Point3(-speed, 0, 0))

        if self.keyMap["right"] != 0:
            self.pointer.setPos(startPos + Point3(speed, 0, 0))

        if self.keyMap["up"] != 0:
            self.pointer.setPos(startPos + Point3(0, speed, 0))

        if self.keyMap["down"] != 0:
            self.pointer.setPos(startPos + Point3(0, -speed, 0))

        if self.pointer_move is True and self.box != 0:
            self.box.setPos(self.pointer.getPos())

        return Task.cont


w = World()
base.run()
