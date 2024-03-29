#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1D
# NSGA-I class file
#  This isn't really a NSGAII

import graph, sol
from util import *
from const import *
#import pprint

class nsga2:
    def __init__( self, population ):
        #Where we'll store our hierarchy
        self.data = []
        
        #Parent generation ref
        self.gen = population
        
        #Who is present
        self.here = []
    
    #def __str__( self ):
        #pdata = []
        #for rank in self.data:
            #pdata.append([])
            #pdata[len(pdata)-1].append(''.join(["LEVEL ", str(self.data.index(rank))]))
            #for sol in rank:
                #pdata[len(pdata)-1].append(''.join([str(sol.moeaf[0]), " and ", str(sol.moeaf[1]), " and ", str(sol.moeaf[2])]))
        #print("\n\n");
        #pp = pprint.PrettyPrinter(indent=4, depth=5)
        #pp.pprint(pdata)
        #print(len(self.data))
        #print("\n\n")
        #return( '' )

    def delete( self ):
        for rank in self.data:
            rank = []
        
        self.data = []
        self.gen = None
        self.here = []

    def domCheck( self, newSol ):
        newSol.dominates = []
        newSol.domee = []
        for cmp2 in self.gen.ind:
            if self.dominates( newSol, cmp2 ):
                newSol.dominates.append( cmp2 )
                if newSol not in cmp2.domee:
                    cmp2.domee.append( newSol )
            elif self.dominates( cmp2, newSol ):
                newSol.domee.append( cmp2 )
                if newSol not in cmp2.dominates:
                    cmp2.dominates.append( newSol )

    def rank( self, mod1=1, mod2=0 ):
        self.data = []
        self.here = []

        #Clear solutions dominating tables
        for sol in self.gen.ind:
            sol.dominates = []
            sol.domee = []
        
        i = 0
        for sol in self.gen.ind:
            delprn( ''.join([(perStr(i/len(self.gen.ind)*mod1+mod2))]), 3 )
            self.add( sol )
            i += 1
           
    def add( self, sol, new=True ):
        #Who do we dominate?
        if new:
            self.domCheck( sol )
        
        redist = []
        if len(self.data) == 0:
            self.data.append([])
            self.data[0].append(sol)
            sol.level = 0
            sol.fit = 1
            self.here.append( sol )
            return

        for rank in self.data:             
            doesDom = False
            for cmp2 in rank:
                if cmp2 in sol.dominates:
                    rank.remove(cmp2)
                    self.here.remove(cmp2)
                    redist.append(cmp2)
                elif cmp2 in sol.domee:
                    doesDom = True
            
            if doesDom:
                #We're at the bottom, so make a home for ourselves
                if self.data.index(rank) == len(self.data)-1:
                    #print("APPENDING OURSELVES")
                    self.data.append([])
                    self.data[len(self.data)-1].append(sol)
                    self.refreshFit( )
                    break
                continue
            else:
                rank.append(sol)
                break
        
        #Readd those whom we displaced
        for worse in redist:
            self.add(worse, False)
                
        #Set our new fitness
        #Index on rank here messed up royally
        sol.level = self.whereAmI( sol )
        sol.fit = len(self.data)-sol.level+1
        self.here.append( sol )

    def whereAmI( self, sol ):
        for i in range(len(self.data)):
            if sol in self.data[i]:
                return i

    def refreshFit( self ):
        for sol in self.here:
            sol.level = -1
        for i in range(0,len(self.data)):
            for sol in self.data[i]:
                sol.level = i
                sol.fit = len(self.data)-sol.level

    def rm( self, sol ):
        #print( sol.level, self.whereAmI( sol ), len(self.data))
        self.data[sol.level].remove(sol)
        if len(self.data[sol.level]) == 0:
            del self.data[sol.level]
            self.refreshFit( )
        self.here.remove(sol)
        
        for solu in sol.dominates:
            if solu.level == sol.level-1:
                self.move( solu, sol )

        for solu in sol.domee:
            if sol in solu.dominates:
                solu.dominates.remove(sol)
        for solu in sol.dominates:
            if sol in solu.domee:
                solu.domee.remove(sol)
        sol.domee = []
        sol.dominates = []
    
    def move( self, sol, tsol ):
        #if not sol in self.data[sol.level]:
            #print( sol.level, self.whereAmI( sol ), len(self.data) )
            #for i in range(len(self.data)):
                #if sol in self.data[i]:
                    #print("Actually in:", i, "w/", sol.level)
                    #print(sol in self.gen.ind)
                    
        #Is it worth moving ourselves?
        move = True
        for osol in sol.domee:
            if ( osol != tsol and osol.level == tsol.level ) or osol.level == sol.level+1:
                move = False
        if move:
            oldfit = sol.level
            self.data[sol.level].remove(sol)
            if len(self.data[sol.level]) == 0:
                    del self.data[sol.level]
                    self.refreshFit( )
            self.here.remove(sol)
            self.add(sol, False)
            
            if oldfit != sol.level:
                #we now have to recursively call move to our domees
                for domee in sol.domee:
                    if domee.level == oldfit-1:
                        self.move(domee, sol)
        
    def dominates( self, sol, comprd2 ):
        eq = 0
        for i in range(len(sol.moeaf)):
            #MAXIMIZE LIT SQUARES
            if i == LITSQ:
                if sol.moeaf[i] < comprd2.moeaf[i]:
                    return False
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
            #MINIMIZE BULBS SHINING ON EACH OTHER
            #MINIMIZE BLACK TILE SATISFICATION VIOLATIONS
            else:
                if sol.moeaf[i] > comprd2.moeaf[i]:
                    return False
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
                    
        #if we're equal we don't dominate them
        if eq == len(sol.moeaf):
            return False
        else:
            return True