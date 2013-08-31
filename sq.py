#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (sym, gt, lprets)
from copy import deepcopy

class sq:
    def __init__( self, x, y, type, owner=[] ):
        self.x = x
        self.y = y
        self.type = type
        self.lightBorder = 0
        self.blackN = []
        self.owner = deepcopy( owner )
        
    def __str__( self ):
        return sym.tb[self.type]
        
    def rmLight( self, puz ):
        self.type = gt.UNLIT
        if self.x > 0:
            for i in range(self.x-1, -1, -1):
                if puz.data[i][self.y].isBlack():
                    break
                puz.data[i][self.y].rmLit( self.x, self.y )
                
        if self.x < puz.x-1:
            for i in range(self.x+1, puz.x):
                if puz.data[i][self.y].isBlack():
                    break
                puz.data[i][self.y].rmLit( self.x, self.y )

        ##################
        if self.y > 0:
            for i in range(self.y-1, -1, -1):
                if puz.data[self.x][i].isBlack():
                    break
                puz.data[self.x][i].rmLit( self.x, self.y )
                    
        if self.y < puz.y-1:
            for i in range(self.y+1, puz.y):
                if puz.data[self.x][i].isBlack():
                    break
                puz.data[self.x][i].rmLit( self.x, self.y )

        for [x, y] in self.blackN:
            if puz.data[x][y].atCapacity():
                puz.blackSats -= 1
            puz.data[x][y].lightBorder -= 1

    #Called by outsider to remove us, if we're a lit square
    def rmLit( self, x, y ):
        if self.type != gt.LIT:
            return False
        if not self.isOwner( x, y ):
            return False
        ret = False
        
        if len(self.owner) == 1:
            ret = True
            self.type = gt.UNLIT

        self.owner.remove( [x, y] )
        return ret
    
    #called by outsider light us up
    def light( self, px, py ):
        #Unlit, light
        if self.type == gt.UNLIT:
            #FIXME: Light squares up... inc counter
            self.type= gt.LIT
            self.owner.append( [px, py] )
            return lprets.LIT
        #Add owner if lit
        if self.type == gt.LIT:
            self.owner.append( [px, py] )
            return lprets.YALIT
        #Bulb == invalid
        if self.type == gt.BULB:
            return lprets.BAD
        #Black space stopped us
        if self.isBlack():
            return lprets.STOPPED
            
    def isOwner( self, x, y ):
        if [x, y] in self.owner:
            return True
        else:
            return False
    
    def isBlack( self ):
        return self.type >= gt.BLACK_THRESHOLD
        
    def atCapacity( self ):
        if self.isBlack( ):
            return( self.lightBorder >= self.type-gt.TRANSFORM )
        else:
            return False
    
    def addNeighbors( self, puz ):
        x = self.x
        y = self.y

        if x > 0:
            tx = x-1
            ty = y
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lightBorder =+ 1
                if puz.data[tx][ty].atCapacity( ):
                    puz.blackSats += 1
                
        if y > 0:
            tx = x
            ty = y-1
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lightBorder =+ 1
                if puz.data[tx][ty].atCapacity( ):
                    puz.blackSats += 1
                    
        if x < (puz.x-1):
            tx = x+1
            ty = y
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lightBorder =+ 1
                if puz.data[tx][ty].atCapacity( ):
                    puz.blackSats += 1
        
        if y < (puz.y-1):
            tx = x
            ty = y+1
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lightBorder =+ 1
                if puz.data[tx][ty].atCapacity( ):
                    puz.blackSats += 1
