import graph, sol
from util import *
from const import *

class nsga2:
    def __init__( self, population ):
        #Where we'll store our hierarchy
        self.data = []
        
        #Parent generation ref
        self.gen = population
        
    #FIXME: We should do this more intelligently
    def reRank( self ):
       #Clear our data for now, later we'll intelligently do this.
       self.data = []
       
       #Clear solutions dominating tables
       for sol in self.gen.ind:
           sol.dominates = []
       
       for sol in self.gen.ind:
           self.add( sol )
           
       print( self.data )
       exit(0)
        
    def add( self, sol ):
        #Whom do we dominate?
        redist = []

        if len(self.data) == 0:
            self.data.append([])
            self.data[0].append(sol)
            return

        for rank in self.data:
            dominates = []
            dominated = []
            
            print("COMPARING: ", len(self.data), self.data.index(rank))
            #For each rank compare ourselves to all of them
            for cmp2 in rank:
                if self.dominates(sol, cmp2):
                    sol.dominates.append(cmp2)
                    dominates.append(cmp2)
                else:
                    cmp2.dominates.append(sol)
                    dominated.append(cmp2)
                
            #Next, see if any of them dominate us
            if len(dominated) > 0:
                #If they do, this isn't our level
                if len(dominates) > 0:
                    #But we're going to take any of them we dominate down with us
                    for worse in dominates:
                        rank.remove(worse)
                    redist.extend(dominates)
                    #We're at the bottom, so make a home for ourselves
                    if self.data.index(rank) == len(self.data):
                        self.data.append( )
                        self.data[len(self.data)].append(sol)
                continue
            else:
                #No one dominates us, so add ourselves
                rank.append(sol)
                #And move around anyone whom we dominate on this level
                if len(dominates) > 0:
                    for worse in dominates:
                        rank.remove(worse)
                    for worse in dominates:
                        self.add(worse) 
                    sol.dominates.extend(dominates)
            
            #Readd those whom we displaced
            for worse in redist:
                self.add(worse)
            
    def dominates( self, sol, comprd2 ):
        ret = True
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
            print("DOMINATES");
            return ret