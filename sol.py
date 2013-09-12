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
import math

class sol:
    def __init__( self, gen, **args ):
        self.graph = graph.graph( )
        self.graph.copy( gen.puz )
        
        # Fitness
        self.fit=-1
        
        # Bad sol
        self.bad = False
        
        # Generation of origin
        self.gen = gen
        
        if 'mate' in args:
            self.breed( args['mate'][0], args['mate'][1] )
        
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
        for i in range(0,math.floor(random.uniform(0,x*y+1))):
            #we're evolving placement of bulbs on unlit cells ("white") so we are careful
            self.graph.addLight( math.floor(random.uniform(0, x)), math.floor(random.uniform(0, y)), True )

        self.fitness( )
        
    # Quick and lame fitness
    def fitness( self ):
        if self.fit != -1:
            return self.fit
        
        # ( num of lit tiles / num of possible lit tiles )
        fit = self.graph.litsq( )  / self.graph.posLitsq( )
        # * ( num of satisfied black squares / number of (satisifiable) black squares )
        if not self.graph.ignoreBlacks:
            fit *= self.graph.blackSats / self.graph.blacksSb( )
        
        self.fit = fit
        return fit
    
    # We're going to take a random amount of data from our parents and "melt" them
    #   into one solution. This solution isn't allowed to be invalid.
    def breed( self, p1, p2 ):
        gamete1 = random.sample( p1.graph.sqgt[gt.BULB], math.ceil(p1.graph.lights( )/2) )
        gamete2 = random.sample( p2.graph.sqgt[gt.BULB], math.ceil(p2.graph.lights( )/2) )
        
        #In a disgusting mess of hot sex, throw half of our squares in with 
        #  the other side.
        pchro = list( )
        pchro.extend( gamete1 )
        pchro.extend( gamete2 )
        
        print ( "\nParent 1, b:", p1.graph.lights( ), "f:", p1.fitness( ) )
        print( p1.graph )
        print ( "Parent 2, b:", p2.graph.lights( ), "f:", p2.fitness( ) )
        print( p2.graph ) 
        
        minn = min(p1.graph.lights( ), p2.graph.lights( ))
        
        random.shuffle( pchro )
        
        for sqr in pchro:
            self.graph.addLight( sqr.x, sqr.y, True )
        
        print ( "Babby, b:", self.graph.lights( ), "f:", self.fitness( ) )
        print( self.graph )
