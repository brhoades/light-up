#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Generation class file
# This file houses the class for generations (gen).

import graph, sol
from util import *
import math

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
        
        self.parseltorun = (args['conf']['pop']['parseltourn'] == "True")
        self.parseltorun = args['conf']['pop']['surseltourn']
        self.parseltorun = args['conf']['pop']
        self.parseltorun = args['conf']['pop']
        
        self.generate(args['conf'])
        
    # Add a single individual to our pool
    def add( self, ind ):
        self.ind.add( ind )
    
    # Randomly generates a generation (hehe) from scratch
    def generate( self, cfg ):
        delprn( "generating init. pop. " )
        
        forcevalid = (cfg['pop']['forcevalid'] == "True")
        for i in range(0,self.mu):            
            citizen = sol.sol( self )
            citizen.rng( forcevalid )
            self.ind.add( citizen )
            delprn( ''.join([perStr(i/self.mu), "%"]), 2 )
    
    # Creates a random tournament and returns a single individual
    #   Disqualified peeps in ineg. Other parent, usually.
    def tournament( self, curnum=1, totnum=1, ineg=[] ):
        top = random.randint(2, len(self.ind))
        parents = random.sample(self.ind, top)
        for sqr in ineg:
            if sqr in parents:
                parents.remove( sqr )
            
        while len(parents) > 1:
            plist = parents.copy( )
            delprn(''.join([perStr(((top-len(parents))/top)*(curnum/totnum)), "%"]), 2)
            
            while len(plist) > 1:
                bracket = random.sample(plist, 2)
                p1 = bracket.pop( )
                p2 = bracket.pop( )
                plist.remove( p1 )
                plist.remove( p2 )

                if p1.fitness( ) > p2.fitness( ):
                    parents.remove( p2 )
                elif p1.fitness( ) <= p2.fitness( ):
                    parents.remove( p1 )
                    
        return parents.pop( )

    # Returns two parents
    def reproduce( self ):
        delprn( "making babbies " )
        newkids = []
        
        for i in range(0,self.lamb):
            parents = []
            parents.append( self.tournament(i*2-1, self.lamb*2) )
            parents.append( self.tournament(i*2, self.lamb*2, [parents[0]]) )
            #Wait to add the babbies
            newkids.append( sol.sol( self, mate=parents ) )
            
        self.ind.extend( newkids )
