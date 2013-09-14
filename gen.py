#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Generation class file
# This file houses the class for generations (gen).

import graph, sol
from util import *
import math
from const import gt

class gen:

    #argument is the previous generation's number
    def __init__( self, **args ):
        #Store all of our populace here
        self.ind = set( )
        
        #Store for the clean, master puzzle
        self.puz = args['puz']
                
        self.num=args['genNum']+1
        
        self.mu = int(args['conf']['pop']['mu'])
        self.lamb = int(args['conf']['pop']['lambda'])
        #Mutation chance
        self.muAlpha = int(args['conf']['pop']['mutatealpha'])
        
        self.tournNat = int(args['conf']['pop']['sursize'])
        self.tournMate = int(args['conf']['pop']['partsize'])
        
        self.parseltourn = (args['conf']['pop']['parseltourn'] == "True")
        
        # Termination Counters
        self.fitEvals = 0
        self.sameTurns = 0
        self.lastFit = -1
        
        self.generate(args['conf'])
        
    # Add a single individual to our pool
    def add( self, ind ):
        self.ind.add( ind )
    
    # Randomly generates a generation (hehe) from scratch
    def generate( self, cfg ):
        delprn( "Generating Initial Pop.\t" )
        
        forcevalid = (cfg['pop']['forcevalid'] == "True")
        for i in range(0,self.mu):            
            citizen = sol.sol( self )
            citizen.rng( forcevalid )
            self.ind.add( citizen )
            delprn( ''.join([perStr(i/self.mu)]), 3 )
    
    # Creates a random tournament and returns a single individual
    #   Disqualified peeps in ineg.
    def tournament( self, pos=True, size=5, curnum=1, totnum=1, ineg=[] ):
        parents = random.sample(self.ind, size)
        for sqr in ineg:
            if sqr in parents:
                parents.remove( sqr )
            
        while len(parents) > 1:
            plist = parents.copy( )
            delprn(''.join([perStr(((size-len(parents))/size*(1/totnum))+(curnum/totnum))]), 3)
            
            while len(plist) > 1:
                bracket = random.sample(plist, 2)
                p1 = bracket.pop( )
                p2 = bracket.pop( )
                plist.remove( p1 )
                plist.remove( p2 )

                if p1.fitness( ) > p2.fitness( ):
                    if pos:
                        parents.remove( p2 )
                    else:
                        parents.remove( p1 )
                elif p1.fitness( ) <= p2.fitness( ):
                    if pos:
                        parents.remove( p1 )
                    else:
                        parents.remove( p2 )
        return parents.pop( )

    # Proportional to fitness, this function chooses a single individual randomly where the higher
    #   the fitness, the more likely they are to be chosen
    
    def fitPropor( self, indv=1, rem=True):
        landscape = util.probDist( self.ind, rem )

    # Returns two parents
    def reproduce( self ):
        delprn( "Procreating\t\t" )
        newkids = set( )
        
        for i in range(0,self.lamb):
            parents = []
            if self.parseltourn:
                parents.append( self.tournament(True, self.tournMate, i*2-1, self.lamb*2) )
                parents.append( self.tournament(True, self.tournMate, i*2, self.lamb*2, [parents[0]]) )
            else:
                landscape = probDist( self.ind )
                parents.extend( landscape.get( 2 ) )
            #Wait to add the babbies
            newkids.add( sol.sol( self, mate=parents ) )
          
        self.ind = self.ind.union( newkids )
    
    # Mutates some individuals randomly
    def mutate( self ):
        delprn( "Mutating\t\t" )
        i = 0
        for sol in self.ind: 
            delprn( ''.join([perStr(i/len(self.ind))]) )
            squares = mutateSq( self.muAlpha )
            while squares > 0:
                sol.fit = -1
                #Look through unlit squares first
                if len(sol.graph.sqgt[gt.UNLIT]) > 0:
                    unlit = random.sample( sol.graph.sqgt[gt.UNLIT], 1 )
                    #Move a random light here if we have one
                    if flip( ) and len(sol.graph.sqgt[gt.BULB]) > 0:
                        bulb = random.sample( sol.graph.sqgt[gt.BULB], 1 )
                        bulb[0].rmLight( )
                        sol.graph.addLight( unlit[0].x, unlit[0].y, True )
                    else:
                        sol.graph.addLight( unlit[0].x, unlit[0].y, True )
                #Otherwise look through bulbs and delete one
                else:
                    bulb = random.sample( sol.graph.sqgt[gt.BULB], 1 )
                    bulb[0].rmLight( )
                squares -= 1
            i += 1
            
    # Deletes those who don't survive natural selection
    def natSelection( self ):
        delprn( "Selecting Survivors\t" )
        i = 0
        
        while len(self.ind) > self.mu:
            # Neg tournament
            self.ind.discard(self.tournament(False, self.tournNat, i, self.mu))
            i += 1
                
    # Returns our best solution. Returns a random one if there's more than one
    def best( self ):
        best = random.sample( self.ind, 1 )
        best = best[0]
        
        for sol in self.ind:
            if sol.fitness( ) > best.fitness( ):
                best = sol
        
        return best
  
    def average( self ):
        fits = 0
        for sol in self.ind:
            fits += sol.fitness( )
        
        return fits/len(self.ind)
