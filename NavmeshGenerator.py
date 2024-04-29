from panda3d.egg import EggPolygon, EggGroupNode, EggVertexPool, EggData, EggVertex, loadEggData, EggCoordinateSystem
from GridNode import *
from math import sqrt
import sys

 
class NavMeshGenerator():
    def __init__(self, prim_1_name, prim_2_name):
        #initialize lists
        self.oldList = []
        self.oldCollList = []
        
        self.newList = []
        self.newCollList = []
        
        self.finalList = []
        
        self.nodeCount = 0
        self.collNodeCount = 0
        self.firstNode = None
        self.lowestVertex = -1
        
        # Process the egg file and iterate 
        # through it
        self.egg = EggData()
        self.fname = prim_1_name
        self.egg.resolveEggFilename(self.fname) 
        self.egg.read(self.fname, "Full")
        
        self.eggColl = EggData()
        self.cname = prim_2_name
        self.eggColl.resolveEggFilename(self.cname) 
        self.eggColl.read(self.cname, "Coll")
        
        print("Creating full node list...")
        self.iterateEggPoly(self.egg, "Full")
        
        print("Correcting full node list...")
        self.createNewFullList()
        
        print("Creating coll node list...")
        self.iterateEggPoly(self.eggColl, "Coll")
        
        print("Creating a proper grid with collisions...")
        self.createCombinedGrid()
        
        print("Creating neighbors for the grid...")
        self.createNeighbors()
        
        print("Write to csv file...")
        self.writeToCSV()
    
    # Iterates through the Egg file and
    # extracts all the quads and stores them
    # as nodes
    def iterateEggPoly(self, egg, type): 
      # Create a node for each quad
      if isinstance(egg, EggPolygon):
        node = GridNode(self.nodeCount, egg.getVertex(0), egg.getVertex(1), 
                    egg.getVertex(2), egg.getVertex(3))
        
        if type == "Full":
            self.oldList.append(node)
            # Find the correct vertex number to use
            if (self.lowestVertex == -1):
                 self.analyzeVertex(node)        
            
            # Store the bottom left node
            if (self.firstNode == None):
                self.firstNode = node             
            else:
                if node.vertex[self.lowestVertex].getX() < self.firstNode.vertex[self.lowestVertex].getX() and node.vertex[self.lowestVertex].getZ() < self.firstNode.vertex[self.lowestVertex].getZ():
                    self.firstNode = node
             
            self.nodeCount = self.nodeCount + 1
        else:
            self.oldCollList.append(node)
            self.collNodeCount = self.collNodeCount + 1

      if isinstance(egg, EggGroupNode): 
        child = egg.getFirstChild() 
        while child != None: 
          self.iterateEggPoly(child, type)
          child = egg.getNextChild()
        
    # Creates a new List which has the correctly
    # ordered nodes for the Full nodes
    def createNewFullList(self):
        # Find the next node based on edge 0-3
        currentRowNode = self.firstNode
        currentColNode = self.firstNode
        self.newList.append(currentRowNode)
        
        for r in range(int(sqrt(self.nodeCount))): #sqrt
            nextColNode = None
            for c in range(int(sqrt(self.nodeCount))-1): #sqrt
                # Processing next col
                for i in range(self.nodeCount):
                    if currentColNode.vertex[self.rightVertex] == self.oldList[i].vertex[self.lowestVertex] and currentColNode.vertex[self.toprightVertex] == self.oldList[i].vertex[self.topVertex]:
                            nextColNode = self.oldList[i]
                self.newList.append(nextColNode)
                currentColNode = nextColNode

            # Processing next row
            if r == sqrt(self.nodeCount):
                break
            
            nextRowNode = None
            for i in range(self.nodeCount):
                if currentRowNode.vertex[self.toprightVertex] == self.oldList[i].vertex[self.rightVertex] and currentRowNode.vertex[self.topVertex] == self.oldList[i].vertex[self.lowestVertex]:
                    nextRowNode = self.oldList[i]
            self.newList.append(nextRowNode)
            currentRowNode = nextRowNode
            currentColNode = nextRowNode

    
    # Creates a combined List which has the correctly
    # ordered nodes with collisions as None           
    def createCombinedGrid(self):
       for r in range(int(sqrt(self.nodeCount))): 
            temp = []
            self.finalList.append(temp)
            for c in range(int(sqrt(self.nodeCount))): 
                tempNode = self.newList[r * int(sqrt(self.nodeCount)) + c]
                if(self.CollContains(tempNode)):
                    self.finalList[r].append(tempNode)
                else:
                    self.finalList[r].append(None)
    
    # Creates neighbor lists for each node
    def createNeighbors(self):
        for r in range(int(sqrt(self.nodeCount))): 
         for c in range(int(sqrt(self.nodeCount))):
            self.setNeighbors(self.finalList[r][c], r, c)
 
    # Writes the grid in the correct format to the .csv
    def writeToCSV(self):
        file = open('navmesh.csv', 'wb')
        
        # Grid Size
        file.write(bytes('Grid Size,', 'utf-8'))
        file.write(bytes(str(int(sqrt(self.nodeCount))), 'utf-8'))
        file.write(b'\nNULL,NodeType,GridX,GridY,Length,Width,Height,PosX,PosY,PosZ')
        file.write(b'\n')
        
        for r in range(int(sqrt(self.nodeCount))): 
          for c in range(int(sqrt(self.nodeCount))):
            node = self.finalList[r][c]
            if node == None:
                file.write(b'1,1,0,0,0,0,0,0,0,0')
                file.write(b'\n')
            else:
                ## For the nodes                
                # NULL
                file.write(bytes(str('0' + ','), 'utf-8'))
                # Node Type (Main)
                file.write(bytes(str('0' + ','), 'utf-8'))
                # Grid X
                file.write(bytes(str(str(node.r) + ','), 'utf-8'))
                # Grid Y
                file.write(bytes(str(str(node.c) + ','), 'utf-8'))
                # Length
                file.write(bytes(str(str(round(node.vertex[0].getX() - node.vertex[1].getX(), 4)) + ','), 'utf-8'))
                # Width
                file.write(bytes(str(str(round(node.vertex[0].getZ() - node.vertex[3].getZ(), 4)) + ','), 'utf-8'))
                # Height
                file.write(bytes(str('0' + ',' ), 'utf-8'))
                # PosX
                file.write(bytes(str(str(round((node.vertex[0].getX() + node.vertex[1].getX())/2, 4)) + ','), 'utf-8'))
                # PosY
                file.write(bytes(str(str(round((node.vertex[0].getZ() + node.vertex[3].getZ())/2, 4)) + ','), 'utf-8'))
                # PosZ
                file.write(b'0')
                
                file.write(b'\n')
                
                ## For the nodes neighbors
                for i in range(8):
                    nnode = node.neighbors[i]
                    if nnode == None:
                        file.write(b'1,1,0,0,0,0,0,0,0,0')
                    else:
                        # NULL
                        file.write(bytes(str('0' + ','), 'utf-8'))
                        # Node Type (Neighbor)
                        file.write(bytes(str('1' + ','), 'utf-8'))
                        # Grid X
                        file.write(bytes(str(str(nnode.r) + ','), 'utf-8'))
                        # Grid Y
                        file.write(bytes(str(str(nnode.c) + ','), 'utf-8'))
                        # Length
                        file.write(bytes(str(str(round(nnode.vertex[0].getX() - nnode.vertex[1].getX(), 4)) + ','), 'utf-8'))
                        # Width
                        file.write(bytes(str(round(nnode.vertex[0].getZ() - nnode.vertex[3].getZ(), 4)) + ',', 'utf-8'))
                        # Height
                        file.write(bytes(str('0' + ','), 'utf-8'))
                        # PosX
                        file.write(bytes(str(str(round((nnode.vertex[0].getX() + nnode.vertex[1].getX())/2, 4)) + ','), 'utf-8'))
                        # PosY
                        file.write(bytes(str(str(round((nnode.vertex[0].getZ() + nnode.vertex[3].getZ())/2, 4)) + ','), 'utf-8'))
                        # PosZ
                        file.write(b'0')                    
                        
                    file.write(b'\n')

    ## HELPER FUNCTIONS 
    
    # Helper function which finds collisions
    def CollContains(self, chkNode):
        for node in self.oldCollList:
            if node.vertex == chkNode.vertex:
                return True
            
        return False
    
    # Helper function which finds collisions
    def setNeighbors(self, node, row, col):
        if not(node == None):
            # Setting the row and col parameters
            node.setRC(row, col)
            
            # left top 
            if col>0 and (row+1)<sqrt(self.nodeCount):
                node.neighbors[0] = self.finalList[row+1][col-1]

            # left mid  
            if col>0:
                node.neighbors[1] = self.finalList[row][col-1]

            # left bot     
            if col>0 and (row-1)>0:
                node.neighbors[2] = self.finalList[row-1][col-1]

            # bot mid
            if (row-1)>0:
                node.neighbors[3] = self.finalList[row-1][col]

            # bot right    
            if (row-1)>0 and (col+1)<sqrt(self.nodeCount):
                node.neighbors[4] = self.finalList[row-1][col+1]

            # right mid   
            if (col+1)<sqrt(self.nodeCount):
                node.neighbors[5] = self.finalList[row][col+1]

             # right top    
            if (row+1)<sqrt(self.nodeCount) and (col+1)<sqrt(self.nodeCount):
                node.neighbors[6] = self.finalList[row+1][col+1]

            # top mid   
            if (row+1)<sqrt(self.nodeCount):
                node.neighbors[7] = self.finalList[row+1][col]
                
    # Helper function to calculate the correct vertex
    def analyzeVertex(self, node):
        precision = 100.0
        self.lowestVertex = 0
        
        for i in range(4):
            if node.vertex[i].getX() < node.vertex[self.lowestVertex].getX() and node.vertex[i].getZ() < node.vertex[self.lowestVertex].getZ():
                self.lowestVertex = i
        
        # top, left, right
        for i in range(4):
            if not(i==self.lowestVertex):
                x1 = float(int(node.vertex[self.lowestVertex].getX()*precision)/precision)
                x2 = float(int(node.vertex[i].getX()*precision)/precision)
                z1 = float(int(node.vertex[self.lowestVertex].getZ()*precision)/precision)
                z2 = float(int(node.vertex[i].getZ()*precision)/precision)

                # self.rightVertex fails for y values other than 0 in the input mesh
                # so we'll initialize it at 0 before the check
                self.rightVertex = 0
                self.toprightVertex = 0
                self.topVertex = 0

                if x1 == x2 and z1 < z2:
                    self.topVertex = i
            
                if x1 < x2 and z1 == z2:
                    self.rightVertex = i
            
                if x1 < x2 and z1 < z2:
                    self.toprightVertex = i

