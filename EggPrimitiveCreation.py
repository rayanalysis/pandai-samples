from panda3d.core import Point3D, deg2Rad, NodePath, Filename, CSZupRight
from panda3d.egg import EggPolygon, EggGroup, EggVertexPool, EggData, EggVertex, loadEggData, EggCoordinateSystem
import math


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

    '''
    # define a single navmesh square
    square_list = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]

    for vert in square_list:
        v = EggVertex()
        v.setPos(Point3D(vert[0], vert[1], vert[2]))
        poly.addVertex(vp.addVertex(v))
    '''
    # define a line of squares
    square_list = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    
    for x in range(gridX):
        square_list = [[0+x,0,0],[1+x,0,0],[1+x,1,0],[0+x,1,0]]

        for vert in square_list:
            v = EggVertex()
            v.setPos(Point3D(vert[0], vert[1], vert[2]))
            poly.addVertex(vp.addVertex(v))
    '''
    # define a grid of squares
    square_list = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]

    for y in range(gridY):
        for x in range(gridX):
            square_list = [[0+x,0+y,0],[1+x,0+y,0],[1+x,1+y,0],[0+x,1+y,0]]

            for vert in square_list:
                v = EggVertex()
                v.setPos(Point3D(vert[0], vert[1], vert[2]))
                poly.addVertex(vp.addVertex(v))
    '''
    '''
    # define a grid of scaled squares
    square_list = [[0,0,0],[scale,0,0],[scale,scale,0],[0,scale,0]]

    for y in range(gridY):
        for x in range(gridX):
            square_list = [[x*scale,y*scale,0],[scale+x*scale,y*scale,0],
                           [scale+x*scale,scale+y*scale,0],[x*scale,scale+y*scale,0]]

            for vert in square_list:
                v = EggVertex()
                v.setPos(Point3D(vert[0], vert[1], vert[2]))
                poly.addVertex(vp.addVertex(v))
    '''
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
