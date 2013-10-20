#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1D
#Square Class File
#  This file houses the functions and class for the square (sq) type, which holds tile info.

from const import sym, gt

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
        puz.sqgt[type].append( self )
        
        # A simple boolean to indicate if this is a black tile.
        #   Mostly redundant as black tiles are never, currently,
        #   initilized, they're changed.
        self.black = self.type > gt.BLACK_THRESHOLD

        ######################## Caches ###############################
        #### These are all initilized at graph generation and copied as
        ####   the board modifies these at a whim.
        # Used for black tiles. The lights that are currently bordering 
        #    us.
        self.lights = []
        # References to neighbors are stored here
        self.neighbors = []
        # Owner squares--- used for lit tiles so we can decide
        #   whether to remove it or not. References to other squares.
        self.owner = []
        for sq in owner:
            self.owner.append(sq)
        # Where this square shines when it's a bulb. References to other
        #   squares on the board. Initilized on graph generation. Not filled
        #   for black tiles or squares that are black on startup.
        self.shine = []
        ###############################################################
        
        # Whether a bulb can place here or not. Flipped when this tile
        #   is bordered by a "0" black tile or full black tile.
        self.bad = []
    
    # A sub function for graph's print string that looks up our symbol
    #   in our constant list.
    def __str__( self ):
        return sym.tb[self.type]
    
    # Clean up references so the gc will delete us and anything we referenced.
    def delete( self ):
        self.parent = None
        self.lights = []
        self.neighbors = []
        self.bad = []
        self.owner = []
        self.shine = []

    
    # Copy ourself over. A sub function for clear / copy in graph.
    def copy( self, other ):
        self.newType( other.type )
        self.black = other.black
    
        # All copied entries are interpolated from our parent, otherwise
        #   we get references to a different graph and things get nasty, fast.
        #   Additonally since we're relocating we don't copy our parent, we use
        #   our current one.
        
        # Lights have to be cleared here regardless. If we're a black
        #   tile we have to have them cleared so that we may "start fresh."
        #   If we're not, we shouldn't have any lights anyway.
        self.lights = []
        if self.black:
            for lits in other.lights:
                self.lights.append(self.parent.data[lits.x][lits.y])
            
        # Neighbors are always cleared so that we don't think tiles on other
        #   graphs are our neighbors still.
        self.neighbors = []
        for i in other.neighbors:
            self.neighbors.append(self.parent.data[i.x][i.y])
        
        # Bad is cleared, as black squares are considered no longer satisifed.
        self.bad = []
        for sqr in other.bad:
            self.bad.append( self.parent.data[sqr.x][sqr.y] )
            
        # Any old unlit tiles are no longer unlit. This is a just in case.
        self.owner = []
        for own in other.owner:
            self.owner.append(self.parent.data[own.x][own.y])
        
        # We can't skip optimization information if we're "the same board"
        #   as it may still point to different squares.
        self.shine = []
        for sqr in other.shine:
            self.shine.append( self.parent.data[sqr.x][sqr.y] )
    
    # Removes a light then removes its lit cells in "shine". Sometimes
    #   we make bad placements, to notice this we'll know if a bulb has an owner.
    def rmLight( self ):
        puz = self.parent
        if len(self.owner) == 0:
            self.newType( gt.UNLIT )
        else:
            self.newType( gt.LIT )

        for sqr in self.neighbors:
            chk = False
            if sqr.isBlack( ) and sqr.atCapacity( ):
                chk = True
            if self in sqr.lights:
                sqr.lights.remove( self )
            if chk:
                sqr.chkCapacity( )
            
        for sqr in self.shine:
            sqr.rmLit( self )
    
    # Called by another function to light us up, and subsequently, claim ownership.
    def light( self, other ):
        #We change black tiles or bulbs to lights
        if self.type == gt.UNLIT:
            self.newType( gt.LIT )
            
        if not other in self.owner:
            self.owner.append( other )

    # Switch our types and update our parent's list
    def newType( self, type ):
        if self.type == type:
            return
        if type > gt.BLACK_THRESHOLD:
            self.parent.sqgt[gt.BLACK_THRESHOLD].append(self)
        self.parent.sqgt[self.type].remove(self)
        self.type = type
        self.parent.sqgt[self.type].append(self)

    # Unlight this cell if the caller is our owner and there are no other
    #   owners.
    def rmLit( self, other ):
        self.owner.remove( other )
        
        if len(self.owner) == 0 and self.type != gt.BULB:
            self.newType( gt.UNLIT )
    
    # Returns whether or not owner is (one of) our owner(s).
    def isOwner( self, other ):
        if other in self.owner:
            return True
        else:
            return False

    # Returns whether or not we're a black tile.
    def isBlack( self ):
        return self.black
    
    # Returns true if this tile is at capacity (no more lights around it)
    #   and false if it isn't.
    def atCapacity( self ):
        if not self.isBlack( ) or self.type == gt.BLACK:
            return False
        
        if self.type == gt.BLACK0:
            return True
        
        if len(self.lights) >= self.type-gt.TRANSFORM:
            return True
        return False
    
    # Turns us into a light with no checks. If there are any black squares
    #   around us we add ourself to their lights counter.
    def addLight( self ):
        if self.type == gt.BULB:
            raise TypeError("Can't place a bulb on a bulb @ (", self.x, self.y,")",
                   self.parent )
        self.newType( gt.BULB )
        
        for sqr in self.neighbors:
            if sqr.isBlack( ):
                sqr.lights.append( self )
                if sqr.atCapacity( ):
                    sqr.chkCapacity( )
        
        for sqr in self.shine:
            sqr.light( self )
        return True

    # Add ourself as a neighbor to other.
    def addNeighbor( self, other ):
        if other.isBlack( ):
            self.neighbors.append( other )
            self.parent.bbsq.append( self )
            if other.type == gt.BLACK0:
                self.bad.append( other )
                self.parent.bbsq.remove( self )

        self.neighbors.append( other )

    # Recheck capacity of a black tile, called when we add a light and its
    #   capacity flips from False to True or the other way.
    def chkCapacity( self ):
        if self.type == gt.BLACK or self.type == gt.BLACK0:
            return
        if self.atCapacity( ):
            for sqr in self.neighbors:
                sqr.bad.append( self )
        else:
            for sqr in self.neighbors:
                if self in sqr.bad:
                    sqr.bad.remove( self )
    
    # Return true or false if we're a bad pick.
    def isBad( self ):
        if not self.parent.ignoreBlacks and len(self.bad) > 0:
            return True
        return False
