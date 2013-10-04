#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
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
        puz.sqgt[type].add( self )
        
        # A simple boolean to indicate if this is a black tile.
        #   Mostly redundant as black tiles are never, currently,
        #   initilized, they're changed.
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
    
    # A sub function for graph's print string that looks up our symbol
    #   in our constant list.
    def __str__( self ):
        return sym.tb[self.type]
    
    # Clean up references so the gc will delete us and anything we referenced.
    def delete( self ):
        self.parent = None
        self.lights = set()
        self.neighbors = set()
        self.bad = set()
        self.owner = set()
        self.shine = set()

    
    # Copy ourself over. A sub function for clear / copy in graph.
    def copy( self, other ):
        self.newType( other.type )
        self.black = other.black
    
        # All copied entries are interpolated frmo our parent, otherwise
        #   we get references to a different graph and things get nasty, fast.
        #   Additonally since we're relocating we don't copy our parent, we use
        #   our current one.
        
        # Lights have to be cleared here regardless. If we're a black
        #   tile we have to have them cleared so that we may "start fresh."
        #   If we're not, we shouldn't have any lights anyway.
        self.lights = set()
        if self.black:
            for lits in other.lights:
                self.lights.add(self.parent.data[lits.x][lits.y])
            
        # Neighbors are always cleared so that we don't think tiles on other
        #   graphs are our neighbors still.
        self.neighbors = set()
        for i in other.neighbors:
            self.neighbors.add(self.parent.data[i.x][i.y])
        
        # Bad is cleared, as black squares are considered no longer satisifed.
        self.bad = set()
        for sqr in other.bad:
            self.bad.add( self.parent.data[sqr.x][sqr.y] )
            
        # Any old unlit tiles are no longer unlit. This is a just in case.
        self.owner = set()
        for own in other.owner:
            self.owner.add(self.parent.data[own.x][own.y])
        
        # We can't skip optimization information if we're "the same board"
        #   as it may still point to different squares.
        self.shine = set()
        for sqr in other.shine:
            self.shine.add( self.parent.data[sqr.x][sqr.y] )
    
    # Removes a light then recursively removes its lit cells in "shine". Sometimes
    #   we make bad placements, to notice this we'll know if a bulb has an owner.
    def rmLight( self ):
        puz = self.parent
        if len(self.owner) <= 0:
            self.newType( gt.UNLIT )
        else:
            self.newType( gt.LIT )

        for sqr in self.neighbors:
            chk = False
            if sqr.isBlack( ) and sqr.atCapacity( ):
                chk = True
            sqr.lights.discard( self )
            if chk:
                sqr.chkCapacity( )
            
        for sqr in self.shine:
            sqr.rmLit( self )
    
    # Called by another function to light us up, and subsequently, claim ownership.
    def light( self, other ):
        self.newType( gt.LIT )
        self.owner.add( other )

    # Switch our types and update our parent's list
    def newType( self, type ):
        if self.type == type:
            return
        if self.type > gt.BLACK_THRESHOLD and type < gt.BLACK_THRESHOLD:
            self.parent.sqgt[gt.BLACK_THRESHOLD].remove(self)
        if type > gt.BLACK_THRESHOLD and self.type < gt.BLACK_THRESHOLD:
            self.parent.sqgt[gt.BLACK_THRESHOLD].add(self)
        self.parent.sqgt[self.type].remove(self)
        self.type = type
        self.parent.sqgt[self.type].add(self)

    # Unlight this cell if the caller is our owner and there are no other
    #   owners.
    def rmLit( self, other ):
        self.owner.remove( other )
        
        if len(self.owner) == 0:
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
        self.newType( gt.BULB )
        
        for sqr in self.neighbors:
            if sqr.isBlack( ):
                sqr.lights.add( self )
                if sqr.atCapacity( ):
                    sqr.chkCapacity( )
        
        for sqr in self.shine:
            sqr.light( self )
        return True

    # Add ourself as a neighbor to other.
    def addNeighbor( self, other ):
        if other.isBlack( ):
            self.neighbors.add( other )
            self.parent.bbsq.add( self )
            if other.type == gt.BLACK0:
                self.bad.add( other )
                self.parent.bbsq.discard( self )

        self.neighbors.add( other )

    # Recheck capacity of a black tile, called when we add a light and its
    #   capacity flips from False to True or the other way.
    def chkCapacity( self ):
        if self.type == gt.BLACK or self.type == gt.BLACK0:
            return
        if self.atCapacity( ):
            self.parent.blackSats += 1
            for sqr in self.neighbors:
                sqr.bad.add( self )
        else:
            self.parent.blackSats -= 1
            for sqr in self.neighbors:
                sqr.bad.discard( self )
    
    # Return true or false if we're a bad pick.
    def isBad( self ):
        if not self.parent.ignoreBlacks and len(self.bad) > 0:
            return True
        return False
