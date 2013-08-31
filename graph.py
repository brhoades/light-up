#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (gt, lprets, sym)
import fileinput
from copy import deepcopy

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
                ret += sym.tb[self.data[i][j]]
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
                    self.data[x][y] = b+gt.TRANSFORM
                    
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
                self.data[i].append(gt.UNLIT)
        return
    
    def addLight( self, x, y, careful=False ):
        #Add the light to the data list
        #print( "x:", x, " y:", y, " self.x: ", self.x, " self.y", y )
        
        #Check surrounding spots for validation
        if self.badBulbSpot( x, y ):
            if careful:
                return lprets.BAD
            self.bad = True

        self.data[x][y] = gt.BULB
        startLit = self.litsq
        
        self.lights += 1
        #Light up a line vertically and horizontally
        ret = self.lightUpPlus( x, y )

        return not self.bad
            
    def lightUpPlus( self, x, y, ):
        if x > 0:
            for i in range(x-1, -1, -1):
                ret = self.lightSq( i, y )
                if ret == lprets.STOPPED:
                    break
        if x < self.x-1:
            for i in range(x+1, self.x):
                ret = self.lightSq( i, y)
                if ret == lprets.STOPPED:
                    break
        if y > 0:
            for i in range(y-1, -1, -1):
                ret = self.lightSq( x, i )
                if ret == lprets.STOPPED:
                    break
        if y < self.y-1:
            for i in range(y+1, self.y):
                ret = self.lightSq( x, i )
                if ret == lprets.STOPPED:
                    break
        return lprets.LIT

    def lightSq( self, x, y ):
        #Unlit, light
        if self.data[x][y] == gt.UNLIT:
            self.litsq += 1
            self.data[x][y] = gt.LIT 
            return lprets.LIT
        #Do nothing if lit
        if self.data[x][y] == gt.LIT:
            return lprets.YALIT
        #Bulb == invalid
        if self.data[x][y] == gt.BULB:
            #Should never happen
            self.bad=True
            return lprets.BAD
        #Black space stopped us
        if self.data[x][y] >= gt.BLACK_THRESHOLD:
            return lprets.STOPPED
    
    def badBulbSpot( self, x, y ):
        if x > 0:
            tx = x-1
            ty = y
            if self.data[tx][ty] >= gt.BLACK_THRESHOLD:
                if self.blackIsFull( tx, ty ):
                    return True
                
        if y > 0:
            tx = x
            ty = y-1
            if self.data[tx][ty] >= gt.BLACK_THRESHOLD:
                if self.blackIsFull( tx, ty ):
                    return True
                
        if x < (self.x-1):
            tx = x+1
            ty = y
            if self.data[tx][ty] >= gt.BLACK_THRESHOLD:
                if self.blackIsFull( tx, ty ):
                    return True 

        if y < (self.y-1):
            tx = x
            ty = y+1
            if self.data[tx][ty] >= gt.BLACK_THRESHOLD:
                if self.blackIsFull( tx, ty ):
                    return True      
                    
        if self.willLightBulb( x, y ):
            return True
        return False
        
    def unlitTiles( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j] == gt.UNLIT:
                    count += 1
        return count
        
    def blackIsFull( self, x, y ):
        maximum = self.data[x][y]-10
        if maximum == gt.BLACK:
            return False
        elif maximum == gt.BLACK0:
            print( "Black is 0" )
            return True

        lamps = 0
        
        if x > 0:
            tx = x-1
            ty = y
            if self.data[tx][ty] == gt.BULB:
                lamps += 1
        if y > 0:
            tx = x
            ty = y-1
            if self.data[tx][ty] == gt.BULB:
                lamps += 1
        if x < (self.x-1):
            tx = x+1
            ty = y
            if self.data[tx][ty] == gt.BULB:
                lamps += 1
        if y < (self.y-1):
            tx = x
            ty = y+1
            if self.data[tx][ty] == gt.BULB:
                lamps += 1
        print( lamps, ">=", maximum )
        return lamps >= maximum
    
    def willLightBulb( self, x, y ):
        print( "BULB CHECK: ", x, y )
        
        if self.data[x][y] != gt.UNLIT:
            print( "LIT" )
            return True
        return False
