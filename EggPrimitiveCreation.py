from panda3d.core import Point3D, deg2Rad, NodePath, Filename, CSZupRight
from panda3d.egg import EggPolygon, EggGroup, EggVertexPool, EggData, EggVertex, loadEggData, EggCoordinateSystem
import math


def makeWedge(angleDegrees = 360, numSteps = 16, evp_name = 'fan'):
    z_up = EggCoordinateSystem()
    z_up.setValue(CSZupRight)

    dataGroup = EggGroup()
    data = EggData()
    dataGroup.addChild(data)
    data.addChild(z_up)

    vp = EggVertexPool(evp_name)
    data.addChild(vp)

    poly = EggPolygon()
    data.addChild(poly)

    v = EggVertex()
    v.setPos(Point3D(0, 0, 0))
    poly.addVertex(vp.addVertex(v))

    angleRadians = deg2Rad(angleDegrees)

    for i in range(numSteps):
        a = angleRadians * i / numSteps
        y = math.sin(a)
        x = math.cos(a)

        v = EggVertex()
        v.setPos(Point3D(x, 0, y))
        poly.addVertex(vp.addVertex(v))

    return data
