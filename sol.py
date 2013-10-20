#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1D
#Solution Class File
# This file houses the solution class (sol) which contains arrangments
#   for bulbs on a graph and related values.

from util import flip,delprn,maxLights
from const import *
import graph
import random
import math

class sol:
    def __init__( self, gen, **args ):
        self.graph = graph.graph( )
        self.graph.copy( gen.puz )
        
        # This will be our the inverse of our level on the table
        self.fit=-1
        
        # Our level
        self.level=-1
        
        #our old fit for caching
        self.oldFit = -1
        
        #We store our metrics in here for easy usage
        #these are our MOEA constraints
        self.moeaf = []

        #Who we dominate goes here, references to them
        self.dominates = []
        
        #Who dominates us goes here, references
        self.domee = []

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
        self.moeaf = []
        self.dominates = []
        self.graph.delete( )
    
    # Random graph solver
    def rng( self, forceValid ):
        x = self.graph.x
        y = self.graph.y
        if forceValid:
            blacktiles = []
            blacktiles += self.graph.sqgt[gt.BLACK1]
            blacktiles += self.graph.sqgt[gt.BLACK2]
            blacktiles += self.graph.sqgt[gt.BLACK3]
            blacktiles += self.graph.sqgt[gt.BLACK4]
            
            random.shuffle(blacktiles)
            
            #go through all satisifiable black tile's neighbors
            #if they have #neighbors = requirement, add bulbs
            for sqr in blacktiles:
                if len(sqr.lights) < sqr.type-gt.TRANSFORM:
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
                self.graph.addLight(tx, ty)

    #FIXME: DESCRIBE
    def fitness( self ):
        self.moeaf = []
        
        for i in moeacon:
            #MAXIMIZE LIT SQUARES
            if i == LITSQ:
                self.moeaf.append(self.graph.litsq( ))
            #MINIMIZE BULBS SHINING ON EACH OTHER
            elif i == BULBCONFLICT:
                violations = 0
                for sqr in self.graph.sqgt[gt.BULB]:
                    if len(sqr.owner) > 0 :
                        violations += 1
                self.moeaf.append(violations)
            #MINIMIZE BLACK TILE SATISFICATION VIOLATIONS
            elif i == BLACKVIO:
                violations = 0
                for sqr in self.graph.sqgt[gt.BLACK_THRESHOLD]:
                    if maxLights(sqr.type)-len(sqr.lights) > 0:
                        violations += 1
                self.moeaf.append(violations)
                
        self.gen.fitEvals += 1
        
        #return self.level
    
    def getFit( self, type ):
        if type == LITSQ:
            return self.moeaf[LITSQ]/self.graph.posLitsq( )
        elif type == BULBCONFLICT:
            if self.graph.lights( ) != 0:
                return 1-self.moeaf[BULBCONFLICT]/self.graph.lights( )
            else:
                return 1
        elif type == BLACKVIO:
            if self.graph.blacks( ) != 0:
                return 1-self.moeaf[BLACKVIO]/self.graph.blacks( )
            else:
                return 1
    
    #Not really old fitness, but this is very similar to our previous function that now
    #  takes into account the bulb conflicts
    def oldFitness( self ):
        if self.oldFit < 0:
            self.oldFit = (self.getFit(LITSQ) + (self.getFit(BULBCONFLICT)) + (self.getFit(BLACKVIO)))/3
        return self.oldFit

    # Trash things and use them again later. Save a crapton of time not allocating memory and recursively
    #   destroying / creating things.
    def trash( self, table=True ):        
        self.gen.ind.remove(self)
        if table:
            self.gen.fitTable.rm(self)
        self.gen.trash.append(self)
        
        self.graph.clear( )
        self.birth = -1
        self.bad = False
        self.fit = -1
        self.moeaf = []
        self.oldFit = -1
        
    # Combine two objects with something akin to crossover.
    #   ideal and is completely random.
    def breed( self, p1, p2 ):
        unlitsq = self.graph.sqgt[gt.UNLIT].copy( )
        random.shuffle( unlitsq )
        self.birth=self.gen.num
        
        while len(unlitsq) > 0:
            sqr = unlitsq.pop( )
            if sqr.isBlack( ):
                continue
            if flip( ):
                if p1.graph.data[sqr.x][sqr.y].type == gt.BULB:
                    self.graph.addLight( sqr.x, sqr.y, False )
                    if self.graph.data[sqr.x][sqr.y].type != gt.BULB:
                        raise TypeError("NOT A BULB!")
            elif p2.graph.data[sqr.x][sqr.y].type == gt.BULB:
                self.graph.addLight( sqr.x, sqr.y, False )            
                if self.graph.data[sqr.x][sqr.y].type != gt.BULB:
                    raise TypeError("NOT A BULB!")