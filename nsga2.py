import graph, sol
from util import *
from const import *
import pprint

class nsga2:
    def __init__( self, population ):
        #Where we'll store our hierarchy
        self.data = []
        
        #Parent generation ref
        self.gen = population
    
    def __str__( self ):
        pdata = []
        for rank in self.data:
            pdata.append([])
            pdata[len(pdata)-1].append(''.join(["LEVEL ", str(self.data.index(rank))]))
            for sol in rank:
                pdata[len(pdata)-1].append(''.join([str(sol.moeaf[0]), " and ", str(sol.moeaf[1]), " and ", str(sol.moeaf[2])]))
        print("\n\n");
        pp = pprint.PrettyPrinter(indent=4, depth=5)
        pp.pprint(pdata)
        print(len(self.data))
        print("\n\n")
        return( '' )

    def reRank( self ):
        #Clear our data for now, later we'll intelligently do this.
        self.data = []

        #Clear solutions dominating tables
        for sol in self.gen.ind:
            sol.dominates = []

        for sol in self.gen.ind:
            self.add( sol )
            
    def add( self, sol ):
        #Who do we dominate?
        redist = []
        if len(self.data) == 0:
            self.data.append([])
            self.data[0].append(sol)
            return

        for rank in self.data:
            dominates = []
            dominated = []
            #print("COMPARING: ", len(self.data), self.data.index(rank))
            #For each rank compare ourselves to all of them
            for cmp2 in rank:
                res = self.dominates(sol, cmp2)
                if res == 1:
                    sol.dominates.append(cmp2)
                    dominates.append(cmp2)
                #If zero, we don't dominate each other
            
            if len(dominates) > 0:
                #Take any of them we dominate down with us
                for worse in dominates:
                    rank.remove(worse)
                redist.extend(dominates)
            
            doesDom = False
            for cmp2 in rank:
                res = self.dominates(cmp2, sol)
                #does anyone dominate us?
                if res == 1:
                    doesDom = True
                    break
            
            if doesDom:
                #We're at the bottom, so make a home for ourselves
                if self.data.index(rank) == len(self.data)-1:
                    #print("APPENDING OURSELVES")
                    self.data.append([])
                    self.data[len(self.data)-1].append(sol)
                    break
                continue
            else:
                rank.append(sol)
                break
        
            #Readd those whom we displaced
            for worse in redist:
                self.add(worse)
            
    def dominates( self, sol, comprd2 ):
        eq = 0
        for i in range(len(sol.moeaf)):
            #MAXIMIZE LIT SQUARES
            if i == LITSQ:
                if sol.moeaf[i] < comprd2.moeaf[i]:
                    #print( sol.moeaf[i], "<", comprd2.moeaf[i] )
                    return -1
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
            #MINIMIZE BULBS SHINING ON EACH OTHER
            #MINIMIZE BLACK TILE SATISFICATION VIOLATIONS
            else:
                if sol.moeaf[i] > comprd2.moeaf[i]:
                    #print( sol.moeaf[i], ">", comprd2.moeaf[i] )
                    return -1
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
        #if we're equal we don't dominate them
        if eq == len(sol.moeaf):
            #print("EQUAL")
            return 0
        else:
            #print("DOMINATES")
            return 1