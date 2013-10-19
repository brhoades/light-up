#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Generation class file
# This file houses the class for generations (gen).

import math

import graph, sol
from util import *
from const import *
from nsga2 import *
import pandas as pd

class gen:

    #argument is the previous generation's number
    def __init__( self, **args ):
        #Store all of our populace here
        self.ind = []
        
        #Store recycled graphs here
        self.trash = []
        
        #Dataframe for satistics
        self.dataframe = 0
        
        #NSGA-II Heirarchy
        #0 => best
        #...
        #5000 => worst (ex)
        #Each level contains references to a solution
        self.fitTable = nsga2( self )
        
        #Store for the clean, master puzzle
        self.puz = args['puz']
        
        #our generation number, rarely used
        self.num = args['genNum']+1
        
        cfg = args['conf']
        
        self.strat = cfg[MAIN][SURVIVAL_STRATEGY]
        
        self.mu = int(cfg[POP][MU])
        self.lamb = int(cfg[POP][LAMBDA])
        
        #These are specific to generations and needed by ops--- copy these
        copyover = [INIT, PARENT_SEL, MUTATE, SURVIVAL_SEL, TERMINATION, MAIN]
        self.cfg = {}
        for typ in copyover:
            self.cfg[typ] = cfg[typ]
        
        #Catches for ints and whatnot
        self.cfg[PARENT_SEL][K] = int(self.cfg[PARENT_SEL][K])
        self.cfg[SURVIVAL_SEL][K] = int(self.cfg[SURVIVAL_SEL][K])
        self.cfg[MUTATE][SIGMA] = int(self.cfg[MUTATE][SIGMA])
        self.cfg[MUTATE][MU] = int(self.cfg[MUTATE][MU])

        # Termination Counters
        self.fitEvals = 0
        self.sameTurns = 0
        self.lastBestAvg = 0
        self.sameTurns = 0
        
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
        self.fitTable.delete( )
        
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
        self.ind.append( ind )
    
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
        forcevalid = (self.cfg[INIT][TYPE] == VALIDITY_ENFORCED_PLUS_UNIFORM_RANDOM)
        for i in range(0,self.mu):
            citz[i].rng( forcevalid )
            citz[i].fitness( )
            self.ind.append(citz[i])
            delprn( ''.join([perStr(i/self.mu)]), 3 )
            
        delprn( "Ranking our Pop.\t" )
        self.fitTable.rank( )
            
    # Creates a random tournament and returns a single individual
    #   Disqualified peeps in ineg.
    def tournament( self, pos=True, size=5, curnum=1, totnum=1, ineg=[] ):
        parents = random.sample(self.ind, size)
        once = True
        while once or len(parents) < size:
            parents.extend( random.sample(self.ind,size-len(parents)) )
            for sqr in ineg:
                if sqr in parents:
                    parents.remove( sqr )
            once = False
            
        while len(parents) > 1:
            random.shuffle( parents )
            plist = parents.copy( )
            delprn(''.join([perStr(((size-len(parents))/size*(1/totnum))+(curnum/totnum))]), 3)
            
            while len(plist) > 1:
                p1 = plist.pop( )
                p2 = plist.pop( )

                if p1.fit < p2.fit:
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
        if self.strat == COMMA:
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
        newkids = []
        parents = []
        
        if self.cfg[PARENT_SEL][TYPE] == TOURNAMENT_WITH_REPLACEMENT:
            for i in range(0,self.lamb):
                pair = []
                pair.append( self.tournament(True, self.cfg[PARENT_SEL][K], i*2-1, self.lamb*2) )
                pair.append( self.tournament(True, self.cfg[PARENT_SEL][K], i*2, self.lamb*2, [pair[0]]) )
                                
                #Store them up and get ready for babby makin'
                parents.append( pair )
        elif self.cfg[PARENT_SEL][TYPE] == FITNESS_PROPORTIONAL:
            for i in range(self.lamb):
                delprn(perStr(i/self.lamb), 3)
                pair = []
                pair.extend( probSel( self.ind, 2, len(self.fitTable.data), False ) )
                
                #Store them up and get ready for babby makin'
                parents.append( pair )    
        elif self.cfg[PARENT_SEL][TYPE] == UNIFORM_RANDOM:
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
                newkids.append( newkid )
            else:
                newkid = sol.sol( self, mate=pair )
                newkids.append( newkid )
            i += 1
            
        delprn( "Mutating\t\t" )
        #Mutate them
        self.mutate( newkids )
        
        
        delprn( "Integrating New Kids\t" )
        # (µ+λ)-EA, Default, tried and true. Merge kids with parents then go through hell.
        i = 0
        if self.strat == PLUS:
            for solu in newkids:
                delprn(perStr(i/len(newkids)), 3)
                solu.fitness( )
                self.ind.append(solu)
                self.fitTable.add(solu)
                i += 1
        # (µ,λ)-EA, Drop all parents and start with our kids. Status quo after that.
        elif self.strat == COMMA:
            starting = len(self.ind)
            while len(self.ind) != 0:
                # This is the only way I know of to deal with this if set size changes.
                # THIS WORKS
                #FIXME: Trash needs special delete without rebuilding
                for solu in self.ind:
                    delprn(perStr(i/starting*.5), 3)
                    solu.trash( )
                    i += 1
                    break
            i = 0
            for solu in newkids:
                delprn(perStr(i/len(newkids)*.5+.5), 3)
                solu.fitness( )
                self.ind.append( solu )
                self.fitTable.add(solu)
                i += 1
                
    # Mutates some individuals randomly, whatever is passed in
    #   Uses alpha and a special distribution (documentation in default.cfg)
    def mutate( self, babbies ):
        i = 0
        #print( "\n\n" )
        for sol in babbies: 
            squares = mutateSq( self.cfg[MUTATE][MU], self.cfg[MUTATE][SIGMA] )
            if squares > 0:
                places = []
                places.extend(sol.graph.sqgt[gt.LIT])
                places.extend(sol.graph.sqgt[gt.UNLIT])
                places.extend(sol.graph.sqgt[gt.BULB])
                #print( squares, "===>", len(places) )
                
                tomutate = random.sample( places, squares )
                for sqr in tomutate:
                    #delprn( perStr((i+j)/(len(babbies)+squares)), 3 )
                    if sqr.type == gt.BULB:
                        sqr.rmLight( )
                    else:
                        sqr.addLight( )
            i += 1
            
    # Deletes those who don't survive natural selection
    def natSelection( self ):
        delprn( "Selecting Survivors\t" )
        
        if self.cfg[SURVIVAL_SEL][TYPE] == TOURNAMENT_WITHOUT_REPLACEMENT:
            for i in range(self.lamb):
                # Neg tournament
                loser = self.tournament(False, self.cfg[SURVIVAL_SEL][K], i, self.lamb )
                loser.trash( )
                #print(self.fitTable)
        elif self.cfg[SURVIVAL_SEL][TYPE] == FITNESS_PROPORTIONAL:
            save = probSel( self.ind, self.mu, len(self.fitTable.data), True )
            trash = []
            for solu in self.ind:
                if solu not in save:
                    trash.append(solu)
            for i in range(len(trash)):
                trash.pop( ).trash( )            
                
            print( self.fitTable, len(self.ind))
        elif self.cfg[SURVIVAL_SEL][TYPE] == UNIFORM_RANDOM:
            i = 0
            max = len(self.ind)-self.mu
            while len(self.ind) > self.mu:
                delprn(perStr(i/max), 3)
                random.sample(self.ind, 1)[0].trash( )
        elif self.cfg[SURVIVAL_SEL][TYPE] == TRUNCATION:
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
  
    # Setup our dataframe
    def statistics( self ):
        self.dataframe = pd.DataFrame( [sol.oldFitness( ) for sol in self.ind] )
  
    # Average everything out.
    def average( self ):
        return float(self.dataframe.mean( ))
    
    # Stddev
    def stdev( self ):
        return float(self.dataframe.std( ))
    
    # Skew, how far to the right (1, +) or left (0, -) the population is
    def skew( self ):
        return float(self.dataframe.skew( ))
    
    def max( self ):
        return float(self.dataframe.max( ))
        