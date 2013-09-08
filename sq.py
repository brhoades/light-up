#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (sym, gt, lprets)

class sq:
    def __init__( self, puz, x, y, type, owner=[] ):
        # Our coordinates
        self.x = x
        self.y = y
        
        # Our type
        self.type = type

        # The puzzle this square belongs to. Reference.
        self.parent = puz
        
        # Update our parent's coutner with our type
        puz.sqgt[type].add( self )
        
        self.black = self.type > gt.BLACK_THRESHOLD

        ######################## Caches ###############################
        #### These are all initilized at graph generation and copied as
        ####   the board modifies these at a whim.
        # Used for black tiles. The lights that are currently bordering 
        #    us.
        self.lights = set()
        # References to neighbors are stored here
        self.neighbors = set()
        # Owner squares--- used for lit tiles so we can decide
        #   whether to remove it or not. References to other squares.
        self.owner = set()
        for sq in owner:
            self.owner.add(sq)
        # Where this square shines when it's a bulb. References to other
        #   squares on the board. Initilized on graph generation. Not filled
        #   for black tiles or squares that are black on startup.
        self.shine = set()
        ###############################################################
        
        # Whether a bulb can place here or not. Flipped when this tile
        #   is bordered by a "0" black tile or full black tile.
        self.bad = set()
        
    def __str__( self ):
        return sym.tb[self.type]
    
    def copy( self, other, sameBoard=False ):
        self.newType( other.type )
        self.black = other.black

        self.lights.clear( )
        for lits in other.lights:
            self.lights.add(self.parent.data[lits.x][lits.y])
            
        self.neighbors.clear( )
        for i in other.neighbors:
            self.neighbors.add(self.parent.data[i.x][i.y])
        
        self.bad.clear( )
        for sqr in other.bad:
            self.bad.add( self.parent.data[sqr.x][sqr.y] )
            
        self.owner.clear( )
        for own in other.owner:
            self.owner.add(self.parent.data[own.x][own.y])
        
        if not sameBoard:
            self.shine.clear( )
            for sqr in other.shine:
                self.shine.add( self.parent.data[sqr.x][sqr.y] )
                
    def rmLight( self ):
        puz = self.parent
        self.newType( gt.UNLIT )

        for sqr in self.neighbors:
            chk = False
            if sqr.isBlack( ) and sqr.atCapacity( ):
                self.parent.decBlackSats( )
                chk = True
            sqr.lights.discard( self )
            if chk:
                sqr.chkCapacity( )
            
        for sqr in self.shine:
            sqr.rmLit( self )
    
    #called by outsider light us up
    def light( self, other ):
        self.newType( gt.LIT )
        self.owner.add( other )

    def newType( self, type ):
        if self.type == type:
            return
        self.parent.sqgt[self.type].remove(self)
        self.type = type
        self.parent.sqgt[self.type].add(self)

    def rmLit( self, other ):
        self.owner.remove( other )
        
        if len(self.owner) == 0:
            self.newType( gt.UNLIT )
            
    def isOwner( self, other ):
        if other in self.owner:
            return True
        else:
            return False
    
    def isBlack( self ):
        return self.black
        
    def atCapacity( self ):
        if not self.isBlack( ) or self.type == gt.BLACK:
            return False
        
        if self.type == gt.BLACK0:
            return True
        
        if len(self.lights) >= self.type-gt.TRANSFORM:
            return True
        return False
    
    def addLight( self ):
        self.newType( gt.BULB )
        
        for sqr in self.neighbors:
            if sqr.isBlack( ):
                sqr.lights.add( self )
                if sqr.atCapacity( ):
                    sqr.chkCapacity( )
        
        for sqr in self.shine:
            sqr.light( self )
        return True

    def addNeighbor( self, other ):
        if other.isBlack( ):
            self.neighbors.add( other )
            self.parent.bbsq.add( self )
            if other.type == gt.BLACK0:
                self.bad.add( other )
                self.parent.bbsq.discard( self )

        self.neighbors.add( other )

    def chkCapacity( self ):
        if self.type == gt.BLACK or self.type == gt.BLACK0:
            return
        if self.atCapacity( ):
            self.parent.incBlackSats( )
            for sqr in self.neighbors:
                sqr.bad.add( self )
        else:
            self.parent.decBlackSats( )
            for sqr in self.neighbors:
                sqr.bad.discard( self )
        
    def isBad( self ):
        if not self.parent.ignoreBlacks and len(self.bad) > 0:
            return True
        return False
