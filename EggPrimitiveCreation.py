from panda3d.core import Point3D, deg2Rad, NodePath, Filename, CSZupRight
from panda3d.core import CollisionNode,CollisionPolygon, GeomVertexFormat, Point3
from panda3d.egg import EggPolygon, EggGroup, EggVertexPool, EggData, EggVertex, loadEggData, EggCoordinateSystem
import math


def makeCollisionModel(inputModel = "models/arena_1.bam", modelOffset = 0):
    # we can utilize a collision mesh generated directly for the built-in collision system
    # to obtain a varying heightfield, adapted from:
    # https://discourse.panda3d.org/t/collision-mesh-from-loaded-model-for-built-in-collision-system/27102
    # load model
    path_to_model = inputModel
    model_root = base.loader.loadModel(path_to_model)
    model_root.reparentTo(base.render)

    # create a temporary copy to generate the collision meshes from
    model_copy = model_root.copyTo(base.render)
    model_copy.detachNode()
    # "bake" the transformations into the vertices
    model_copy.flattenLight()

    # create root node to attach collision nodes to
    collision_root = NodePath("collision_root")
    collision_root.reparentTo(model_root)
    # offset the collision meshes from the model so they're easier to see
    collision_root.setX(modelOffset)
    collision_root.setY(modelOffset)

    # create a collision mesh for each of the loaded models
    for model in model_copy.findAllMatches("**/+GeomNode"):
        model_node = model.node()
        collision_node = CollisionNode(model_node.name)
        collision_mesh = collision_root.attachNewNode(collision_node)
        # collision nodes are hidden by default
        collision_mesh.show()

        for geom in model_node.modifyGeoms():
            geom.decomposeInPlace()
            vertex_data = geom.modifyVertexData()
            vertex_data.format = GeomVertexFormat.get_v3()
            view = memoryview(vertex_data.arrays[0]).cast("B").cast("f")
            index_list = geom.primitives[0].getVertexList()
            index_count = len(index_list)

            for indices in (index_list[i:i+3] for i in range(0, index_count, 3)):
                points = [Point3(*view[index*3:index*3+3]) for index in indices]
                coll_poly = CollisionPolygon(*points)
                collision_node.addSolid(coll_poly)

    # model_root.hide()
            
def makeSquares(gridX = 30, gridY = 30, scale = 1, evpName = 'square', startPos = Point3D(0, 0, 0)):
    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)

    dataGroup = EggGroup()
    data = EggData()
    dataGroup.addChild(data)
    data.addChild(z_up)

    vp = EggVertexPool(evpName)
    data.addChild(vp)

    poly = EggPolygon()
    data.addChild(poly)

    # define a line of squares
    square_list = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    
    for x in range(gridX):
        square_list = [[0+x,0,0],[1+x,0,0],[1+x,1,0],[0+x,1,0]]

        for vert in square_list:
            v = EggVertex()
            v.setPos(Point3D(vert[0], vert[1], vert[2]))
            poly.addVertex(vp.addVertex(v))

    return data

def makeSquaresEVP(gridX = 30, gridY = 30, scale = 1, evpName = 'square', hardZ = 0):
    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)

    data = EggData()
    data.addChild(z_up)

    # define a grid of scaled squares
    square_list = [[0,0,0],[scale,0,0],[scale,scale,0],[0,scale,0]]

    for y in range(gridY):
        for x in range(gridX):
            vp = EggVertexPool(evpName)
            data.addChild(vp)

            poly = EggPolygon()
            data.addChild(poly)

            square_list = [[x*scale,y*scale,hardZ],[scale+x*scale,y*scale,hardZ],
                           [scale+x*scale,scale+y*scale,hardZ],[x*scale,scale+y*scale,hardZ]]

            for vert in square_list:
                v = EggVertex()
                v.setPos(Point3D(vert[0], vert[1], vert[2]))
                poly.addVertex(vp.addVertex(v))
                
    return data

def makeSquaresEVPXZ(gridX = 30, gridY = 30, scale = 1, evpName = 'square', hardZ = 0):
    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)

    data = EggData()
    data.addChild(z_up)

    # define a grid of scaled squares
    square_list = [[0,0,0],[scale,0,0],[scale,scale,0],[0,scale,0]]

    for y in range(gridY):
        for x in range(gridX):
            vp = EggVertexPool(evpName)
            data.addChild(vp)

            poly = EggPolygon()
            data.addChild(poly)

            square_list = [[x*scale,hardZ,y*scale],[scale+x*scale,hardZ,y*scale],
                           [scale+x*scale,hardZ,scale+y*scale],[x*scale,hardZ,scale+y*scale]]

            for vert in square_list:
                v = EggVertex()
                v.setPos(Point3D(vert[0], vert[1], vert[2]))
                poly.addVertex(vp.addVertex(v))
                
    return data

def makeSquaresEVPXZSparse(gridX = 30, gridY = 30, scale = 1, evpName = 'square', hardZ = 0):
    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)

    data = EggData()
    data.addChild(z_up)

    # define a grid of scaled squares
    square_list = [[0,0,0],[scale,0,0],[scale,scale,0],[0,scale,0]]

    x = scale

    for y in range(gridY):
        vp = EggVertexPool(evpName)
        data.addChild(vp)

        poly = EggPolygon()
        data.addChild(poly)

        square_list = [[x*scale,hardZ,y*scale],[scale+x*scale,hardZ,y*scale],
                       [scale+x*scale,hardZ,scale+y*scale],[x*scale,hardZ,scale+y*scale]]

        for vert in square_list:
            v = EggVertex()
            v.setPos(Point3D(vert[0], vert[1], vert[2]))
            poly.addVertex(vp.addVertex(v))

    y = scale

    for x in range(gridX):
        vp = EggVertexPool(evpName)
        data.addChild(vp)

        poly = EggPolygon()
        data.addChild(poly)

        square_list = [[x*scale,hardZ,y*scale],[scale+x*scale,hardZ,y*scale],
                       [scale+x*scale,hardZ,scale+y*scale],[x*scale,hardZ,scale+y*scale]]

        for vert in square_list:
            v = EggVertex()
            v.setPos(Point3D(vert[0], vert[1], vert[2]))
            poly.addVertex(vp.addVertex(v))
                
    return data
