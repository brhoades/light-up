#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (sym, gt, lprets)

class sq:
    def __init__( self, puz, x, y, type, owner=[] ):
        self.x = x
        self.y = y
        self.type = type
        self.lights = set()
        self.blackN = set()
        self.owner = set()
        self.parent = puz
        for sq in owner:
            self.owner.append(sq)
        self.bad = False
        
    def __str__( self ):
        return sym.tb[self.type]
    
    def copy( self, other, sameBoard=False ):
        self.type=other.type
        self.lights = set( )
        for lits in other.lights:
            self.lights.add(lits)
        if not sameBoard:
            self.parent = other.parent
            self.blackN = set( )
            for bln in other.blackN:
                self.blackN.add(bln)
            self.bad=other.bad
        self.owner = set( )
        for own in other.owner:
            self.owner.add(own)
        
    def rmLight( self ):
        puz = self.parent
        self.type = gt.UNLIT
        if self.x > 0:
            for i in range(self.x-1, -1, -1):
                if puz.data[i][self.y].isBlack():
                    break
                puz.data[i][self.y].rmLit( self )
                
        if self.x < puz.x-1:
            for i in range(self.x+1, puz.x):
                if puz.data[i][self.y].isBlack():
                    break
                puz.data[i][self.y].rmLit( self )

        ##################
        if self.y > 0:
            for i in range(self.y-1, -1, -1):
                if puz.data[self.x][i].isBlack():
                    break
                puz.data[i][self.y].rmLit( self )
                    
        if self.y < puz.y-1:
            for i in range(self.y+1, puz.y):
                if puz.data[self.x][i].isBlack():
                    break
                puz.data[i][self.y].rmLit( self )

        for sqr in self.blackN:
            if sqr.atCapacity( ):
                puz.decBlackSats( )
            sqr.lights.discard( self )

    #Called by outsider to remove us, if we're a lit square
    def rmLit( self, other ):
        if self.type != gt.LIT:
            return False
        if not self.isOwner( other ):
            return False
        ret = False
        
        if len(self.owner) == 1:
            ret = True
            self.type = gt.UNLIT

        self.owner.discard( other )
        return ret
    
    #called by outsider light us up
    def light( self, other ):
        #Unlit, light
        if self.type == gt.UNLIT:
            #FIXME: Light squares up... inc counter
            self.type= gt.LIT
            self.owner.add( other )
            return lprets.LIT
        #Add owner if lit
        if self.type == gt.LIT:
            self.owner.add( other )
            return lprets.YALIT
        #Bulb == invalid
        if self.type == gt.BULB:
            return lprets.BAD
        #Black space stopped us
        if self.isBlack():
            return lprets.STOPPED
            
    def isOwner( self, other ):
        if other in self.owner:
            return True
        else:
            return False
    
    def isBlack( self ):
        return self.type >= gt.BLACK_THRESHOLD
        
    def atCapacity( self ):
        if not self.isBlack( ):
            return False
        
        if self.type == gt.BLACK or self.type == gt.BLACK0:
            return True
        
        if len(self.lights) >= self.type-gt.TRANSFORM:
            return True
        else:
            return False
    
    def addNeighbors( self, puz ):
        x = self.x
        y = self.y

        if x > 0:
            tx = x-1
            ty = y
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lights.add( self )
                if puz.data[tx][ty].atCapacity( ):
                    puz.incBlackSats( )
                
        if y > 0:
            tx = x
            ty = y-1
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lights.add( self )
                if puz.data[tx][ty].atCapacity( ):
                    puz.incBlackSats( )
                    
        if x < (puz.x-1):
            tx = x+1
            ty = y
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lights.add( self )
                if puz.data[tx][ty].atCapacity( ):
                    puz.incBlackSats( )
        
        if y < (puz.y-1):
            tx = x
            ty = y+1
            if puz.data[tx][ty].isBlack():
                puz.data[tx][ty].lights.add( self )
                if puz.data[tx][ty].atCapacity( ):
                    puz.incBlackSats( )
