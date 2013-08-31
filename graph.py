#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (gt, lprets, sym)
import fileinput
from copy import deepcopy
from sq import sq

#Graph class
class graph:
    def __init__( self, conf, cpy=False ):
        self.data=[]

        #Is this an invalid graph?
        self.invalid=False
        #Have we made a bad placement?
        self.bad=False
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #Fitness
        self.fit=-1
        #"Ideal" solution
        self.solu=None

        if cpy == True:
            self.x = puz.x
            self.y = puz.y
            self.blank()
            self.data=deepcopy(puz.data)
            self.bad=puz.bad
            self.invalid=puz.invalid
            self.lights=puz.lights
            self.litsq=puz.litsq
            self.fit=puz.fit
            self.solu=puz.solu
            return
        
        if conf['gen'] != 'True':
            self.readGraph(conf['gen'])
            print("Loaded graph from:", conf['gen'])
        else:
            self.genGraph(conf)    
            print("Generated graph from seed:", conf['seed'])

    def __str__(self):
        ret = ""
        ret += "┌"
        for i in range( 0, self.x):
            ret += "─"
        ret += "┐\n" #\n

        for j in range(0, self.y):
            ret += "│"
            for i in range(0, self.x):
                ret += self.data[i][j].__str__( )
            ret += "│\n"#\n
            
        ret += "└"
        for i in range( 0, self.x):
            ret += "─"
        ret +="┘\n" #\n
        
        return ret

    def readGraph( self, filename ):
        with fileinput.input(files=(filename)) as fh:
            for line in fh:
                ln = fh.filelineno()
                if ln == 1:
                    self.x=int(line)
                if ln == 2:
                    self.y=int(line)
                    self.blank()
                if ln > 2:
                    rawLine = line.split(' ')
                    #1 10 5
                    #(x) (y) (black #)
                    x = int(rawLine[0])-1
                    y = int(rawLine[1])-1
                    b = int(rawLine[2])
                    
                    #90 degree ccw rotation about origin
                    x = x
                    y = (self.y-1)-y
                    
                    #Skip this line if it's invalid and complain
                    if x > self.x or y > self.y or x < 0 or y < 0 or b > 5 or b < 0:
                        print("Line is invalid (", (x+1), ",", (y+1), ") w/ Black of: ", b)
                        next
                    
                    #print("Transposed (", (x+1), ",", (y+1), ",", b, ") as (", x, ",", y, ", ", b+gt.TRANSFORM,")" ) 
                    self.data[x][y] = sq( x, y, b+gt.TRANSFORM )
                    
            fh.close()
        return

    def genGraph( self, conf ):
        self.x = conf['x']
        self.y = conf['y']
        self.blank()
        return
    
    def blank( self ):        
        #Initilize "blank" graph
        for i in range(0,self.x):
            self.data.append([])
            for j in range(0,self.y):
                self.data[i].append( sq( i, j, gt.UNLIT ) )
        return
    
    def addLight( self, x, y, careful=False ):
        #Check surrounding spots for validation
        if self.badBulbSpot( x, y ):
            if careful:
                return False
            self.bad = True
                
        self.data[x][y].type = gt.BULB
        
        self.data[x][y].addNeighbors( self )
        
        self.lights += 1
        #Light up a line vertically and horizontally
        self.lightUpPlus( x, y )

        return True
        
    def lightUpPlus( self, x, y, ):
        if x > 0:
            for i in range(x-1, -1, -1):
                ret = self.data[i][y].light( x, y )
                if ret == lprets.STOPPED:
                    if i-x == 1 and self.data[i][y].isBlack():
                        self.data[i][y].blackN.append([x, y])
                        break
        if x < self.x-1:
            for i in range(x+1, self.x ):
                ret = self.data[i][y].light( x, y )
                if ret == lprets.STOPPED:
                    if x-i == 1 and self.data[i][y].isBlack():
                        self.data[i][y].blackN.append([x, y])
                    break
        if y > 0:
            for i in range(y-1, -1, -1):
                ret = self.data[x][i].light( x, y )
                if ret == lprets.STOPPED:
                    if y-i == 1 and self.data[x][i].isBlack():
                        self.data[x][i].blackN.append([x, y])
                    break
        if y < self.y-1:
            for i in range(y+1, self.y):
                ret = self.data[x][i].light( x, y )
                if ret == lprets.STOPPED:
                    if i-y == 1 and self.data[x][i].isBlack():
                        self.data[x][i].blackN.append([x, y])
                    break
        return lprets.LIT
    
    def badBulbSpot( self, x, y ):
        if self.data[x][y].type != gt.UNLIT:
            return True
        if not self.checkNeighbors( x, y ):
            return False
        
    def unlitTiles( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j] == gt.UNLIT:
                    count += 1
        return count
    
    def checkNeighbors( self, x, y ):
        if len(self.data[x][y].blackN) == 0:
            return False
        
        for ea in self.data[x][y].blackN:
            if self.data[ea[0]][ea[1]].lightBorder > self.data[ea[0]][ea[1]].type - gt.TRANSFORM:
                return True
