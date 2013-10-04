#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
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
        
        #Store recycled, cleared graphs here
        self.trash = []
        
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
        self.surseltourn = (args['conf']['pop']['surseltourn'] == "True")
        
        self.surseltrunc = (args['conf']['pop']['surtrunc'])
        if self.surseltrunc == 'lambda':
            self.surseltrunc = self.lamb
        else:
            self.surseltrunc = int(self.surseltrunc)
                                                
        # Termination Counters
        self.fitEvals = 0
        self.sameTurns = 0
        self.lastFit = -1
        
        # FIXME: This should be a const / config reg. For now, 1 = constraint satisfaction
        self.fitType = 1
        
        # Fitness denominator, static
        self.fitDenom = 0
        if not self.puz.ignoreBlacks:
            self.fitDenom += self.puz.blacksSb( )
        self.fitDenom += self.puz.posLitsq( )

        
        self.generate(args['conf'])
        
    def __str__(self):
        ret = ''
        for solu in self.ind:
            ret = ''.join([ret, solu.graph, '\n'])
            ret = ''.join([ret, "fit:", solu.fit, "birth:", solu.birth, '\n'])
            ret = ''.join([ret, "============================", '\n'])
            
        return ret
    # Remove references recursively so that we can be cleaned up by the gc
    def delete( self, expt=None ):
        for sol in self.ind:
            if sol is not expt:
                sol.delete( )
        self.ind = []
        self.puz = None
    
    # Add a single individual to our pool
    def add( self, ind ):
        self.ind.add( ind )
    
    # Randomly generates a generation (hehe) from scratch
    def generate( self, cfg ):
        delprn( "Generating Initial Pop.\t" )
        citz = []
        
        for i in range(0,self.mu):            
            citizen = sol.sol( self )
            citz.append( citizen )
            delprn( ''.join([perStr(i/(self.mu+self.lamb))]), 3 )
        
        for i in range(0,self.lamb):
            trash = sol.sol( self )
            trash.fit=0
            self.trash.append(trash)
            delprn( ''.join([perStr(self.mu+i/(self.mu+self.lamb))]), 3 )
            
        delprn( "Randomly Solving Pop\t" )

        forcevalid = (cfg['pop']['forcevalid'] == "True")
        for i in range(0,self.mu):
            citz[i].rng( forcevalid )
            citz[i].fitness( )
            self.ind.add(citz[i])
            delprn( ''.join([perStr(i/self.mu)]), 3 )
            
    # Creates a random tournament and returns a single individual
    #   Disqualified peeps in ineg.
    def tournament( self, pos=True, size=5, curnum=1, totnum=1, ineg=[] ):
        parents = random.sample(self.ind, size)
        for sqr in ineg:
            if sqr in parents:
                parents.remove( sqr )
            
        while len(parents) > 1:
            random.shuffle( parents )
            plist = parents.copy( )
            delprn(''.join([perStr(((size-len(parents))/size*(1/totnum))+(curnum/totnum))]), 3)
            
            while len(plist) > 1:
                p1 = plist.pop( )
                p2 = plist.pop( )

                if p1.fit > p2.fit:
                    if pos:
                        parents.remove( p2 )
                    else:
                        parents.remove( p1 )
                else:
                    if pos:
                        parents.remove( p1 )
                    else:
                        parents.remove( p2 )
        return parents.pop( )
    
    # drops #self.surseltrunc of the worst individuals
    def truncate( self ):
        for i in range(0,self.surseltrunc):
            delprn(perStr(i/self.surseltrunc), 3)
            worst = self.worst( )
            worst.trash( )
        
    # Creates some new babbies and adds them to the generation
    def reproduce( self ):
        delprn( "Choosing Parents\t" )
        newkids = set( )
        parents = []
        
        if self.parseltourn:
            for i in range(0,self.lamb):
                pair = []
                pair.append( self.tournament(True, self.tournMate, i*2-1, self.lamb*2) )
                pair.append( self.tournament(True, self.tournMate, i*2, self.lamb*2, [pair[0]]) )
                
                #Store them up and get ready for babby makin'
                parents.append( pair )
        else:
            landscape = probDist( self.ind )
            for i in range(0,self.lamb):
                delprn(perStr(i/self.lamb), 3)
                pair = []
                pair.extend( landscape.get( 2 ) )
                
                #Store them up and get ready for babby makin'
                parents.append( pair )    
                
        delprn( "Making Babbies\t\t" )
        i = 0
        for pair in parents:
            delprn(perStr(i/len(parents)), 3)
            if len(self.trash) > 0:
                newkid = self.trash.pop( )
                newkid.breed( pair[0], pair[1] )
                newkids.add( newkid )
            else:
                newkid = sol.sol( self, mate=pair )
                newkids.add( newkid )
            i += 1
            
        delprn( "Mutating\t\t" )
        #Mutate them
        self.mutate( newkids )
        
        for solu in newkids:
            solu.fitness( )
            self.ind.add(solu)
                
    # Mutates some individuals randomly
    def mutate( self, babbies ):
        i = 0
        for sol in babbies: 
            squares = mutateSq( self.muAlpha )
            j = squares
            while j > 0:
                delprn( ''.join([perStr((i/len(self.ind))+((squares-j)/squares))]), 3 )
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
                j -= 1
            i += 1
            
    # Deletes those who don't survive natural selection
    def natSelection( self ):
        delprn( "Selecting Survivors\t" )
        i = 0
        
        if self.surseltourn:
            while len(self.ind) > self.mu:
                # Neg tournament
                loser = self.tournament(False, self.tournNat, i, self.mu)
                loser.trash( )
                i += 1
        else:
            self.truncate( )
            
    # Returns our best solution. Returns the oldest if there's several
    def best( self ):
        best = False
        
        for sol in self.ind:
            if not best or sol.fit > best.fit:
                best = sol
            elif sol.fit == best.fit:
                if sol.birth < best.birth:
                    best = sol
        
        return best
      
    # Returns our worst solution. 
    def worst( self ):
        worst = random.sample( self.ind, 1 )
        worst = worst[0]
        
        for sol in self.ind:
            if sol.fit < worst.fit:
                worst = sol
        
        return worst
  
    # Average everything out.
    # NOT HUMAN-READABLE FITNESS, which is betweein [0,1]
    def average( self ):
        fits = 0
        for sol in self.ind:
            fits += sol.fit
        return fits/len(self.ind)
    
    # A human readable average: [0,1]
    def hAverage( self ):
        return self.average( )/self.fitDenom
        