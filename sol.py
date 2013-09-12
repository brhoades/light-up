#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Solution Class File
# This file houses the solution class (sol) which contains arrangments
#   for bulbs on a graph and related values.

from util import flip
from const import gt
import graph
import random
from math import floor

class sol:
    def __init__( self, solution ):
        self.graph = graph.graph( )
        self.graph.copy( solution )
        
        # Fitness
        self.fit=-1
        
        # Bad sol
        self.bad = False
        
    # Random graph solver
    def rng( self, forceValid ):
        x = self.graph.x
        y = self.graph.y
        if forceValid:
            blacktiles = set( )
            blacktiles.union(self.graph.sqgt[gt.BLACK1])
            blacktiles.union(self.graph.sqgt[gt.BLACK2])
            blacktiles.union(self.graph.sqgt[gt.BLACK3])
            blacktiles.union(self.graph.sqgt[gt.BLACK4])
            
            #go through all satisifiable black tile's neighbors
            #if they have #neighbors = requirement, add bulbs
            for sqr in blacktiles:
                if len(sqr.neighbors) == sqr.type-gt.BLACK_TRANSFORM:
                    for hsqr in sqr.neighbors:
                        hsqr.addLight( )
        
        # Place a random number of bulbs
        for i in range(0,floor(random.uniform(0,x*y+1))):
            #we're evolving placement of bulbs on unlit cells ("white") so we are careful
            self.graph.addLight( floor(random.uniform(0, x)), floor(random.uniform(0, y)), True )

        self.fitness( )
        
    # Quick and lame fitness
    def fitness( self ):
        # ( num of lit tiles / num of possible lit tiles )
        fit = self.graph.litsq( )  / self.graph.posLitsq( )
        # * ( num of satisfied black squares / number of (satisifiable) black squares )
        if not self.graph.ignoreBlacks:
            fit *= self.graph.blackSats / self.graph.blacksSb( )
        
        self.fit = fit
        return fit
    
