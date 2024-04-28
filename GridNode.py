class GridNode():     
    def __init__(self, nodeNo, v1, v2, v3, v4):
        self.nodeNo = nodeNo
        
        self.vertex = []
        self.vertex.append(v1.getPos4())
        self.vertex.append(v2.getPos4())
        self.vertex.append(v3.getPos4())
        self.vertex.append(v4.getPos4())
        
        self.quad = []
        for i in range(4):
            self.quad.append(self.nodeNo * 4 + i)
            self.vertex[i].setY(0)
            
        self.neighbors = []
        for i in range(8):
            self.neighbors.append(None)
            
    def setRC(self, r, c):
        self.r = r
        self.c = c
        
