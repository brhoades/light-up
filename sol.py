#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Solution Class File
# This file houses the solution class (sol) which contains arrangments
#   for bulbs on a graph and related values.

from util import flip,delprn,maxLights
from const import gt, ci, opp
import graph
import random
import math

class sol:
    def __init__( self, gen, **args ):
        self.graph = graph.graph( )
        self.graph.copy( gen.puz )
        
        # Fitness
        self.fit=-1
        
        # Cached human-readable fitness array
        self.hfit = []
        ## First entry == human fitness
        self.hfit.append( 0 )
        ## Second entry == fitness when calculated
        self.hfit.append( self.fit )
        
        # Birth Generation
        self.birth=gen.num
        
        # Bad sol
        self.bad = False
        
        # Generation of origin
        self.gen = gen
        
        if 'mate' in args:
            self.breed( args['mate'][0], args['mate'][1] )
    
    # Removes references to our graph and to our gen so we can be collected by the gc
    def delete( self ):
        self.gen = None
        self.graph.delete( )
    
    # Random graph solver
    def rng( self, forceValid ):
        x = self.graph.x
        y = self.graph.y
        if forceValid:
            blacktiles = []
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK1]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK2]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK3]))
            blacktiles.extend(list(self.graph.sqgt[gt.BLACK4]))
            
            random.shuffle(blacktiles)
            
            #go through all satisifiable black tile's neighbors
            #if they have #neighbors = requirement, add bulbs
            for sqr in blacktiles:
                if len(sqr.neighbors) == sqr.type-gt.TRANSFORM:
                    for hsqr in sqr.neighbors:
                        if hsqr.type == gt.LIT or hsqr.type == gt.UNLIT:
                            hsqr.addLight( )
        
        # Bulbs used are related to # of black tiles and size of board.
        # This is a rough approximation. Overshooting it causes the board to be solved very quickly and
        #   statistically isn't interesting at all.
        maxbulbs = max(x,y)
        maxbulbs += self.graph.blacks( )
        
        #Place a random number of bulbs
        for i in range(random.randint(0,maxbulbs)):
            #(last arg) is only true when we're doing forceValid
            tx = math.floor(random.uniform(0, x))
            ty = math.floor(random.uniform(0, y))
            if not self.graph.data[tx][ty].isBlack( ) and self.graph.data[tx][ty].type != gt.BULB:
                self.graph.addLight(tx, ty, forceValid )

    # Returns a human-readable fitness. Does not evaluate, just calculates and caches.
    def getFit( self ):
        if self.hfit[1] != self.fit:            
            #Cache was out of date, so calculate
            self.hfit[1] = self.fit
            self.hfit[0] = self.fit/self.gen.fitDenom
            
            if self.hfit[0] < 0:
                self.hfit[0] = 0
        
        return self.hfit[0]

    # Quick and lame fitness
    # Denomintor for fitness is ignored as it only adds floats into the mess.
    #   We're going to give everyone a rating based on their black tiles satisfied + 
    #   their lit squares.
    def fitness( self ):
        # numerator: number of lit tiles + black tiles satisfied
        self.fit = self.graph.litsq( )
        if not self.graph.ignoreBlacks:
            self.fit += self.graph.blackSats( )
        
        # denom: static and predefined self.parent.fitDenom, called when humans need it
        self.gen.fitEvals += 1
        return self.fit

    # Trash things and use them again later. Save a crapton of time not allocating memory and recursively
    #   destroying / creating things.
    def trash( self ):
        self.graph.clear( )
        self.birth = -1
        self.bad = False
        self.fit = 0
        
        self.gen.ind.remove(self)
        self.gen.trash.append(self)
  
    # Combine two objects with something akin to crossover.
    #   ideal and is completely random.
    def breed( self, p1, p2 ):
        unlitsq = list( self.graph.sqgt[gt.UNLIT] )
        random.shuffle( unlitsq )
        self.birth=self.gen.num
        
        while len(unlitsq) > 0:
            sqr = unlitsq.pop( )
            if sqr.isBlack( ):
                continue
            if flip( ):
                if p1.graph.data[sqr.x][sqr.y].type == gt.BULB:
                    self.graph.addLight( sqr.x, sqr.y, True )
            elif p2.graph.data[sqr.x][sqr.y].type == gt.BULB:
                self.graph.addLight( sqr.x, sqr.y, True )            
