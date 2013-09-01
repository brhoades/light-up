#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (gt, lprets, sym)
import fileinput
from copy import deepcopy
from sq import sq
import solve
import random
import signal

#Graph class
class graph:
    def __init__( self, conf=False, cpy=False ):
        self.data=[]

        #Is this an invalid graph?
        self.invalid=False
        #Have we made a bad placement?
        self.bad=False
        #Satisfied Black Squares
        self.blackSats = 0
        #Fitness
        self.fit=-1
        #"Ideal" solution
        self.solu=None
        
        #cache of sqares bordering black boxes
        self.bbsq = []
        
        self.deep=0

        self.x = 0
        self.y = 0

        if conf == True:
            self.x = cpy.x
            self.y = cpy.y
            self.blank()
            self.data=deepcopy(cpy.data)
            self.bad=cpy.bad
            self.invalid=cpy.invalid
            self.fit=cpy.fit
            self.solu=cpy.solu
            self.blackSats=cpy.blackSats
            return 
        
        if conf['gen'] != 'True':
            self.blackSats = self.readGraph(conf['gen'])
            print("Loaded graph from:", conf['gen'])
        else:
            random.seed(conf['seed'])
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
                    self.addBlack( x, y, b )

            fh.close()
        return self.blackSats

    def genGraph( self, conf ):
        made = False
        self.x = int(conf['x'])
        self.y = int(conf['y'])
        
        while made == False or solve.ideal( self ) == False:
            self.blank()
            for i in range(0, self.x):
                if self.genCoinFlip( float(conf['noblackx']) ):
                    next
                for j in range(0, self.y):
                    if self.genCoinFlip( float(conf['placeblack']) ):
                        self.genRandBlack( i, j, float(conf['blackmod']) )
            made = True
                
    def genCoinFlip( self, prob ):
        if prob*100 >= random.randint( 0, 100 ):
            return True
        return False
    
    def genRandBlack( self, x, y, bprob ):
        #weighted towards non-requring blacks
        if self.genCoinFlip( bprob ):
            self.addBlack( x, y, gt.BLACK-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/1.5 ):
            self.addBlack( x, y, gt.BLACK1-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2 ):
            self.addBlack( x, y, gt.BLACK2-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2.5 ):
            self.addBlack( x, y, gt.BLACK3-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/3 ):
            self.addBlack( x, y, gt.BLACK4-gt.TRANSFORM )
        else:
            self.addBlack( x, y, gt.BLACK0-gt.TRANSFORM )
        
    def rmLight( self, x, y ):
        self.data[x][y].rmLight( self )
        return
    
    def blank( self ):        
        #Initilize "blank" graph
        if len(self.data) != 0:
            del self.data
            self.data = []
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
        
        #Light up a line vertically and horizontally
        self.lightUpPlus( x, y )

        return True
        
    def lightUpPlus( self, x, y ):
        if x > 0:
            for i in range(x-1, -1, -1):
                ret = self.data[i][y].light( x, y )
                if ret == lprets.STOPPED:
                    break
        if x < self.x-1:
            for i in range(x+1, self.x ):
                ret = self.data[i][y].light( x, y )
                if ret == lprets.STOPPED:
                    break
        if y > 0:
            for i in range(y-1, -1, -1):
                ret = self.data[x][i].light( x, y )
                if ret == lprets.STOPPED:
                    break
        if y < self.y-1:
            for i in range(y+1, self.y):
                ret = self.data[x][i].light( x, y )
                if ret == lprets.STOPPED:
                    break
        return lprets.LIT
    
    def badBulbSpot( self, x, y ):
        if self.data[x][y].type != gt.UNLIT:
            return True
        if self.fullNeighbors( x, y ):
            return True
    
    def fullNeighbors( self, x, y ):
        if len(self.data[x][y].blackN) == 0:
            return False
        
        for [tx, ty] in self.data[x][y].blackN:
            if self.data[tx][ty].atCapacity( ):
                return True
    
    def addBlack( self, x, y, b ):
        self.data[x][y] = sq( x, y, b+gt.TRANSFORM )
        ourType = b+gt.TRANSFORM
        if x > 0:
            self.data[x-1][y].blackN.append( [x, y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x-1, y] in self.bbsq ):
                self.bbsq.append( [x-1, y] )
            if ourType == gt.BLACK0:
                self.data[x-1][y].bad = True
        if x < self.x-1:
            self.data[x+1][y].blackN.append( [x, y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x+1, y] in self.bbsq ):
                self.bbsq.append( [x+1, y] )
            if ourType == gt.BLACK0:
                self.data[x+1][y].bad = True                    
        if y > 0:
            self.data[x][y-1].blackN.append( [x, y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x, y-1] in self.bbsq ):
                self.bbsq.append( [x, y-1] )
            if ourType == gt.BLACK0:
                self.data[x][y-1].bad = True
        if y < self.y-1:
            self.data[x][y+1].blackN.append( [x, y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x, y+1] in self.bbsq ):
                self.bbsq.append( [x, y+1] )
            if ourType == gt.BLACK0:
                self.data[x][y+1].bad = True

    def unLitsq( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.UNLIT:
                    count += 1
        return count
        
    def posLitsq( self ):
        return self.litsq( ) + self.unLitsq( )
        
    def litsq( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.LIT:
                    count += 1
        return count
        
    def blacks( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type >= gt.BLACK_THRESHOLD:
                    count += 1
        return count
        
    def blacksSb( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                mytype = self.data[i][j].type
                if mytype >= gt.BLACK1 and mytype <= gt.BLACK4:
                    count += 1
        return count
        
    def lights( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.BULB:
                    count += 1
        return count

    def incBlackSats( self ):
        self.blackSats += 1
        
    def decBlackSats( self ):
        self.blackSats -= 1

    #Bordered by a black cell that isn't full
    def bbRange( self ):
        ret = []
        for [i, j] in self.bbsq:
            for [x, y] in self.data[i][j].blackN:
                if not self.data[x][y].atCapacity( ) and \
                    not( [i, j] in ret ):
                    ret.append( [i, j] )
        return ret

    def isValid( self ):
        for i in self.data:
            for j in self.data[i]:
                if self.data[i][j].isBlack( ) and \
                    self.data[i][j].lightBorder > self.data[i][j].type-gt.TRANSFORM:
                    return False
    
    def hitTopinc( self, f=False ):
        if f:
            self.hitTop = 0
        else:
            self.hitTop += 1
            
    def hitTopLim( self ):
        return ( self.hitTop > (self.x*self.y) )
