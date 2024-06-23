# Modified 04/27/2024 as an effort to modernize panda3d.ai

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
from NavMeshGenerator import *
import EggPrimitiveCreation

import complexpbr
# import pandarecord


load_prc_file_data("", """
    win-size 1280 720
    window-title PandAI Pathfinding Demo
    framebuffer-multisample 1
    multisamples 4
    hardware-animated-vertices #t
    cursor-hidden #t
""")


ShowBase()
speed = 10.0
font = base.loader.loadFont("cmss12")

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), font=font,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale=.05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), font=font,
                        pos=(1.3, -0.95), align=TextNode.ARight, scale=.07)


class World:
    def __init__(self):
        complexpbr.apply_shader(render)
        # complexpbr.screenspace_init()
        # pandarecord.setup_sg(base,buff_hw=[1280,720],cust_fr=60,RAM_mode=True)

        self.keyMap = {"left": 0, "right": 0, "up": 0, "down": 0}

        addTitle("PandAI Tutorial: Adding Dynamic Obstacles Over Terrain")
        addInstructions(0.95, "[i]: Load Default Wall Boundaries")
        addInstructions(0.90, "[F3]: Toggle Wireframe")
        addInstructions(0.85, "[Enter]: Start Pathfinding")
        addInstructions(0.8, "[Arrow Keys]: Move Arrow")
        addInstructions(0.75, "[1]: Add Wall Boundary Section")
        addInstructions(0.7, "[ESC]: Quit")
        addInstructions(0.65, "[p]: Perspective View")
        addInstructions(0.6, "[r]: Top-Down View")

        # base.disableMouse()
        base.toggleWireframe()
        base.accept("f3", base.toggleWireframe)
        base.accept("escape", sys.exit, [0])
        base.accept("p", self.activateCam)
        base.accept("enter", self.setMove)
        base.accept("r", self.resetCamPos)
        base.accept("i", self.loadDefaultLevelWalls)
        base.accept("1", self.addStaticLevelWalls)
        base.accept("0", base.screenshot)

        self.camPositions = [Vec3(135,135,500),Vec3(-135,-135,250)]
        base.cam.setPos(135,135,500)
        base.cam.lookAt(135,135,0)
        # base.cam.setPosHpr(0, -30, 30, 0, 327, 0)
        self.box = loader.loadModel("models/1m_sphere_black_marble.bam")
        self.pointer_move = False
        self.loadModels()
        self.aiObstacleList = []

        # create built-in collision from loaded model
        EggPrimitiveCreation.makeCollisionModel("environ_1.bam")
        
        # create a box primitive for obstacle placement
        new_wall = loader.loadModel("models/wall_test.glb")
        new_wall.writeBamFile("models/wall_test.bam")

        # movement task
        taskMgr.add(self.Mover, "Mover")
        # taskMgr.add(self.updateRalphZ, "UpdateRalphZ")
        
        self.isMoving = False
        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # uncomment this line to see the collision rays
        self.ralphGroundColNp.show()
        self.camGroundColNp.show()
       
        # uncomment this line to show a visual representation of the 
        # collisions occuring
        self.cTrav.showCollisions(render)

        self.setAI()

    def activateCam(self):
        base.cam.setPos(self.camPositions[1])
        base.cam.lookAt(135,135,-20)

    def loadModels(self):
        # self.environ = loader.loadModel("models/arena_1.bam")
        # self.environ.setPos(100,100,0)
        # self.environ.reparentTo(render)
        self.environ = loader.loadModel("models/builtin_test.glb")
        self.environ.writeBamFile("environ_1.bam")
        self.visual_environ = loader.loadModel("environ_1.bam")
        self.visual_environ.reparentTo(render)

        # create the main character, Ralph
        # ralphStartPos = self.environ.find("**/start_point").getPos()
        ralphStartPos = Vec3(20, 20, 0)

        self.ralph = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})

        self.ralph.reparentTo(render)
        self.ralph.setScale(2)
        self.ralph.setPos(ralphStartPos)

        self.ralphVis = Actor("models/ralph",
                           {"run": "models/ralph-run",
                            "walk": "models/ralph-walk"})

        self.ralphVis.reparentTo(render)
        self.ralphVis.setScale(2)
        self.ralphVis.setPos(ralphStartPos)

        self.pointer = loader.loadModel("models/1m_sphere_black_marble.bam")
        self.pointer.setColor(1, 0, 0)
        self.pointer.setPos(100, 100, 0)
        self.pointer.setScale(3)
        self.pointer.reparentTo(render)

    def setAI(self):
        # creating AI World
        self.AIworld = AIWorld(render)

        # movement
        base.accept("arrow_left", self.setKey, ["left", 1])
        base.accept("arrow_right", self.setKey, ["right", 1])
        base.accept("arrow_up", self.setKey, ["up", 1])
        base.accept("arrow_down", self.setKey, ["down", 1])
        base.accept("arrow_left-up", self.setKey, ["left", 0])
        base.accept("arrow_right-up", self.setKey, ["right", 0])
        base.accept("arrow_up-up", self.setKey, ["up", 0])
        base.accept("arrow_down-up", self.setKey, ["down", 0])
        base.accept("u", self.setKey, ["pointerUp", 1])
        base.accept("u-up", self.setKey, ["pointerUp", 0])

        # AICharacter() setup is as follows
        # model_name_string, model_nodepath, mass, movement_force, max_force)
        self.AIchar = AICharacter("ralph", self.ralph, 60, 0.05, 20)
        self.AIworld.addAiChar(self.AIchar)
        # self.AIworld.removeAiChar(model_name_string)
        self.AIbehaviors = self.AIchar.getAiBehaviors()

        # the following loads in a "navmesh" .csv file
        # generated using an .egg primitive created on the fly
        # with built-in panda3d functions and some boutique
        # PandAI specific formatting for the 2D A* system
        prim_1_name = "squares"  # this is the navmesh primitive
        prim_2_name = "squares_coll"  # this is a copy of the navmesh primitive
        # we begin by making two meshes, one "Full" and one "Coll"
        # in order to build the 2D navigation mesh from .egg files
        primitive_data_1 = EggPrimitiveCreation.makeSquaresEVPXZ(30, 30, 10, "Full",0)
        primitive_data_2 = EggPrimitiveCreation.makeSquaresEVPXZ(30, 30, 10, "Coll",0)
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
        self.initializeStaticLevelWalls()

        slight_1 = Spotlight('slight_1')
        slight_1.setColor(Vec4(Vec3(5),1))
        slight_1.setShadowCaster(True, 4096, 4096)
        # slight_1.set_attenuation((0.5,0,0.000005))
        lens = PerspectiveLens()
        slight_1.setLens(lens)
        slight_1.getLens().setFov(120)
        slight_1_node = base.render.attachNewNode(slight_1)
        slight_1_node.setPos(0, 0, 90)
        slight_1_node.lookAt(100,100,0.5)
        base.render.setLight(slight_1_node)
        
    def setMove(self):
        # self.AIbehaviors.pathFindTo(LVecBase3(random.randint(-200,200),random.randint(-200,200),0))
        self.AIbehaviors.pathFindTo(self.pointer, "somePath")
        # self.AIbehaviors.seek(self.pointer)
        self.ralphVis.loop("run")
        self.ralph.hide()

    def move(self):
        self.cTrav.traverse(render)

        # adjust ralph's Z coordinate
        # if ralph's ray hit terrain, update his Z
        entries = list(self.ralphGroundHandler.entries)
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        for entry in entries:
            # discover what the collision node entry names are if we don't know already
            # print(entry.getIntoNode().name)
            if entry.getIntoNode().name == "Plane.001":
                self.ralphVis.setZ(entry.getSurfacePoint(render).getZ())

        # keep the camera at one unit above the terrain,
        # or two units above ralph, whichever is greater.
        entries = list(self.camGroundHandler.entries)
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        for entry in entries:
            if entry.getIntoNode().name == "Plane.001":
                base.camera.setZ(entry.getSurfacePoint(render).getZ() + 1.5)
        if base.camera.getZ() < self.ralphVis.getZ() + 2.0:
            base.camera.setZ(self.ralphVis.getZ() + 2.0)

        # self.ralphVis.setP(0)
        self.ralphVis.setX(self.ralph.getX())
        self.ralphVis.setY(self.ralph.getY())
        self.ralphVis.setH(self.ralph.getH())
        # print(base.cam.getP())
        
        return Task.cont
        
    def initializeStaticLevelWalls(self):
        new_wall = loader.loadModel("models/wall_test.bam")
        new_wall.setPos(0,0,0)
        new_wall.setScale(10)
        new_wall.reparentTo(render)
        self.AIbehaviors.addStaticObstacle(new_wall)

        new_wall_ref = ['new_wall', self.pointer.getPos(), new_wall.getScale().x]
        self.aiObstacleList.append(new_wall_ref)
        
    def addStaticLevelWalls(self):
        new_wall = loader.loadModel("models/wall_test.bam")
        # print(self.pointer.getPos())
        new_wall.setPos(self.pointer.getPos())
        new_wall.setScale(10)
        new_wall.reparentTo(render)
        self.AIbehaviors.addStaticObstacle(new_wall)

        new_wall_ref = ['new_wall', self.pointer.getPos(), new_wall.getScale().x]
        self.aiObstacleList.append(new_wall_ref)
        
        with open('wall_positions.txt','w') as out_v:
            for item in self.aiObstacleList:
                # print(item[1])
                out_v.write(str(int(item[1].x)) + ',' + str(int(item[1].y)) + '\n')

        out_v.close()
        
    def loadDefaultLevelWalls(self):
        wall_list = open('models/default_wall_positions.txt', 'r')
        wall_list = wall_list.read()

        for wall in wall_list.split('\n'):
            new_wall = loader.loadModel("models/wall_test.bam")

            wall_positions = wall.split(',')
            try:
                # print(wall_positions[0], wall_positions[1])
                new_wall.setPos(int(wall_positions[0]), int(wall_positions[1]), 0)
                new_wall.setScale(10)

                new_wall.reparentTo(render)
                self.AIbehaviors.addStaticObstacle(new_wall)
            except:
                print('Invalid static level wall position, continuing..')
        
    def loadStaticLevelWalls(self): 
        wall_list = open('wall_positions.txt', 'r')
        wall_list = wall_list.read()

        for wall in wall_list.split('\n'):
            new_wall = loader.loadModel("models/wall_test.bam")

            wall_positions = wall.split(',')
            try:
                # print(wall_positions[0], wall_positions[1])
                new_wall.setPos(int(wall_positions[0]), int(wall_positions[1]), 0)
                new_wall.setScale(10)
                new_wall.reparentTo(render)
                self.AIbehaviors.addStaticObstacle(new_wall)
            except:
                print('Invalid static level wall position, continuing..')

    def resetCamPos(self):
        base.cam.setPos(self.camPositions[0])
        base.cam.lookAt(135,135,0)

    # update the AIWorld
    def AIUpdate(self, task):
        self.AIworld.update()
        self.move()

        return Task.cont

    def setKey(self, key, value):
        self.keyMap[key] = value

    def Mover(self, task):
        startPos = self.pointer.getPos()
        dt = base.clock.getDt()

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

        self.environ.setPos(0,0,0)
        
        task.delay_time = 0.1
        return Task.again


w = World()
base.run()
