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
        for i in range(0,math.floor(random.uniform(0,x*y/2))):
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
  
    def breed( self, p1, p2 ):
        #print ( "\nParent 1, b:", p1.graph.lights( ), "f:", p1.fitness( ) )
        #print( p1.graph )
        #print ( "Parent 2, b:", p2.graph.lights( ), "f:", p2.fitness( ) )
        #print( p2.graph ) 
        
        unlitsq = list( self.graph.sqgt[gt.UNLIT] )
        random.shuffle( unlitsq )
        
        while len(unlitsq) > 0:
            sqr = unlitsq.pop( )
            if sqr.type != gt.UNLIT:
                continue
            if flip( ) and p1.graph.data[sqr.x][sqr.y].type == gt.BULB:
                sqr.addLight( )
            elif p2.graph.data[sqr.x][sqr.y].type == gt.BULB:
                sqr.addLight( )
                
        #print ( "Babby, b:", self.graph.lights( ), "f:", self.fitness( ) )
        #print( self.graph )
