#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Generation class file
# This file houses the class for generations (gen).

import math

import graph, sol
from util import *
from const import gt, ci, opp

class gen:

    #argument is the previous generation's number
    def __init__( self, **args ):
        #Store all of our populace here
        self.ind = set( )
        
        #Store recycled graphs here
        self.trash = []
        
        #Store for the clean, master puzzle
        self.puz = args['puz']
                
        self.num=args['genNum']+1
        
        cfg = args['conf']
        
        self.strat = cfg[ci.MAIN][ci.SURVIVAL_STRATEGY]
        
        self.mu = int(cfg[ci.POP][ci.MU])
        self.lamb = int(cfg[ci.POP][ci.LAMBDA])
        
        #Penalty control
        self.penalty = (cfg[ci.MAIN][ci.FITNESS_TYPE] == opp.PENALTY_FUNCTION)
        
        #These are specific to generations and needed by ops--- copy these
        copyover = [ci.INIT, ci.PARENT_SEL, ci.MUTATE, ci.SURVIVAL_SEL, ci.TERMINATION, ci.MAIN]
        self.cfg = {}
        for typ in copyover:
            self.cfg[typ] = cfg[typ]
        
        #Catches for ints and whatnot
        self.cfg[ci.PARENT_SEL][ci.K] = int(self.cfg[ci.PARENT_SEL][ci.K])
        self.cfg[ci.SURVIVAL_SEL][ci.K] = int(self.cfg[ci.SURVIVAL_SEL][ci.K])
        self.cfg[ci.MUTATE][ci.ALPHA] = int(self.cfg[ci.MUTATE][ci.ALPHA])

        # Termination Counters
        self.fitEvals = 0
        self.sameTurns = 0
        self.lastBestAvg = 0
        self.sameTurns = 0
        
        # Fitness denominator, static
        #   When we spit out a human-readable fitness we divide by this
        self.fitDenom = 0
        if not self.puz.ignoreBlacks:
            self.fitDenom += self.puz.blacksSb( )
        self.fitDenom += self.puz.posLitsq( )

        self.generate( )
        
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
        for sol in self.trash:
            if sol is not expt:
                sol.delete( )
        self.ind = []
        self.trash = []
        self.puz = None
    
    # Add a single individual to our pool
    def add( self, ind ):
        self.ind.add( ind )
    
    # Randomly generates a generation (hehe) from scratch
    def generate( self ):
        delprn( "Generating Initial Pop.\t" )
        citz = []
        
        for i in range(0,self.mu):            
            citizen = sol.sol( self )
            citz.append( citizen )
            delprn( ''.join([perStr(i/(self.mu+self.lamb))]), 3 )
        
        for i in range(0,self.lamb):
            trash = sol.sol( self )
            trash.fit=0
            self.trash.append( trash )
            delprn( ''.join([perStr((self.mu+i)/(self.mu+self.lamb))]), 3 )
            
        delprn( "Randomly Solving Pop\t" )
        forcevalid = (self.cfg[ci.INIT][ci.TYPE] == opp.VALIDITY_ENFORCED_PLUS_UNIFORM_RANDOM)
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
    
    # drops the worst individuals down to µ
    def truncate( self ):
        if self.strat == opp.COMMA:
            left = self.lamb - self.mu
        else:
            left = self.lamb
            
        for i in range(0,left):
            delprn(perStr(i/left), 3)
            worst = self.worst( )
            worst.trash( )
        
    # Creates some new babbies and adds them to the generation
    def reproduce( self ):
        delprn( "Choosing Parents\t" )
        newkids = set( )
        parents = []
        
        if self.cfg[ci.PARENT_SEL][ci.TYPE] == opp.TOURNAMENT_WITH_REPLACEMENT:
            for i in range(0,self.lamb):
                pair = []
                pair.append( self.tournament(True, self.cfg[ci.PARENT_SEL][ci.K], i*2-1, self.lamb*2) )
                pair.append( self.tournament(True, self.cfg[ci.PARENT_SEL][ci.K], i*2, self.lamb*2, [pair[0]]) )
                
                #Store them up and get ready for babby makin'
                parents.append( pair )
        elif self.cfg[ci.PARENT_SEL][ci.TYPE] == opp.FITNESS_PROPORTIONAL:
            landscape = probDist( self.ind )
            for i in range(self.lamb):
                delprn(perStr(i/self.lamb), 3)
                pair = []
                pair.extend( landscape.get( 2 ) )
                
                #Store them up and get ready for babby makin'
                parents.append( pair )    
        elif self.cfg[ci.PARENT_SEL][ci.TYPE] == opp.UNIFORM_RANDOM:
            for i in range(self.lamb):
                delprn(perStr(i/self.lamb), 3)
                pair = random.sample( self.ind, 2 )
                
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
        
        
        delprn( "Integrating New Kids\t" )
        # (µ+λ)-EA, Default, tried and true. Merge kids with parents then go through hell.
        i = 0
        if self.strat == opp.PLUS:
            for solu in newkids:
                delprn(perStr(i/len(newkids)), 3)
                solu.fitness( )
                self.ind.add(solu)
                i += 1
        # (µ,λ)-EA, Drop all parents and start with our kids. Status quo after that.
        elif self.strat == opp.COMMA:
            starting = len(self.ind)
            while len(self.ind) != 0:
                # This is the only way I know of to deal with this if set size changes.
                # THIS WORKS
                for sol in self.ind:
                    delprn(perStr(i/starting*.5), 3)
                    sol.trash( )
                    i += 1
                    break
            i = 0
            for solu in newkids:
                delprn(perStr(i/len(newkids)*.5+.5), 3)
                solu.fitness( )
                self.ind.add( solu )
                i += 1
                
    # Mutates some individuals randomly, whatever is passed in
    #   Uses alpha and a special distribution (documentation in default.cfg)
    def mutate( self, babbies ):
        i = 0
        for sol in babbies: 
            squares = mutateSq( self.cfg[ci.MUTATE][ci.ALPHA] )
            j = squares
            if j > 0:
                places = []
                places.extend(sol.graph.sqgt[gt.LIT])
                places.extend(sol.graph.sqgt[gt.UNLIT])
                places.extend(sol.graph.sqgt[gt.BULB])
                while j > 0:
                    delprn( perStr((i+j)/(len(babbies)+squares)), 3 )
                    #Look through unlit squares first
                    if not self.penalty:
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
                    else:
                        sqr = random.sample( places, 1 )
                        if sqr[0].type == gt.BULB:
                            sqr[0].rmLight( )
                        else:
                            sqr[0].addLight( )
                    j -= 1
            i += 1
            
    # Deletes those who don't survive natural selection
    def natSelection( self ):
        delprn( "Selecting Survivors\t" )
        i = 0
        
        if self.cfg[ci.SURVIVAL_SEL][ci.TYPE] == opp.TOURNAMENT_WITHOUT_REPLACEMENT:
            while len(self.ind) > self.mu:
                # Neg tournament
                loser = self.tournament(False, self.cfg[ci.SURVIVAL_SEL][ci.K], i, self.mu)
                loser.trash( )
                i += 1
        elif self.cfg[ci.SURVIVAL_SEL][ci.TYPE] == opp.FITNESS_PROPORTIONAL:
            landscape = probDist( self.ind, self.cfg[ci.SURVIVAL_SEL][ci.FITNESS_PROPORTIONAL_TYPE] == opp.REMOVAL, True )
            save = landscape.get( self.mu )
            trash = []
            for solu in self.ind:
                if solu not in save:
                    trash.append(solu)
            for i in range(len(trash)):
                trash.pop( ).trash( )            
        elif self.cfg[ci.SURVIVAL_SEL][ci.TYPE] == opp.UNIFORM_RANDOM:
            i = 0
            max = len(self.ind)-self.mu
            while len(self.ind) > self.mu:
                delprn(perStr(i/max), 3)
                random.sample(self.ind, 1)[0].trash( )
        elif self.cfg[ci.SURVIVAL_SEL][ci.TYPE] == opp.TRUNCATION:
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
    # NOT HUMAN-READABLE FITNESS, which is between [0,1]
    def average( self ):
        fits = 0
        for sol in self.ind:
            fits += sol.fit
        return fits/len(self.ind)
    
    # A human readable average: [0,1]
    def hAverage( self ):
        return self.average( )/self.fitDenom
        