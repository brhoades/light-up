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
        
        #Who is present
        self.here = []
    
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

    def rank( self ):
        self.data = []
        self.here = []

        #Clear solutions dominating tables
        for sol in self.gen.ind:
            sol.dominates = []
            sol.domee = []
        
        #Initialize who dominates whom
        for sol in self.gen.ind:
            for cmp2 in self.gen.ind:
                if self.dominates( sol, cmp2 ):
                    if sol in cmp2.dominates:
                        raise TypeError("Circular Domination")
                    sol.dominates.append( cmp2 )
                    cmp2.domee.append( sol )
        
        i = 0
        for sol in self.gen.ind:
            delprn( ''.join([(perStr(i/len(self.gen.ind)))]), 3 )
            self.add( sol )
            i += 1
           
    def add( self, sol ):
        #Who do we dominate?
        redist = []
        if len(self.data) == 0:
            self.data.append([])
            self.data[0].append(sol)
            self.here.append( sol )
            return

        for rank in self.data:             
            doesDom = False
            for cmp2 in rank:
                if cmp2 in sol.dominates:
                    rank.remove(cmp2)
                    redist.append(cmp2)
                elif cmp2 in sol.domee:
                    doesDom = True
            
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
                
        #Set our new fitness
        sol.fit = self.data.index(rank)
        self.here.append( sol )

    def whereAmI( self, sol ):
        for i in range(len(self.data)):
            if sol in self.data[i]:
                return i

    def refreshFit( self ):
        for i in range(len(self.data)):
            for sol in self.data[i]:
                if sol.fit != i:
                    sol.fit = i

    def rm( self, sol ):
        if sol in self.data[sol.fit]:
            self.data[sol.fit].remove(sol)
            if len(self.data[sol.fit]) == 0:
                self.data.remove(self.data[sol.fit])
                self.refreshFit( )
            self.here.remove(sol)
        else:
            print("TRIED TO DELETE OURSELVES, ALREADY GONE", sol.fit, len(sol.dominates))
            return
        
        for solu in sol.dominates:
            remove = True
            for tsolu in solu.domee:
                if tsolu != sol and tsolu.fit == sol.fit:
                    remove = False
            if remove:
                self.move( solu )

        for solu in sol.domee:
            if sol in solu.dominates:
                solu.dominates.remove(sol)
        for solu in sol.dominates:
            if sol in solu.domee:
                solu.domee.remove(sol)
        sol.domee = []
        sol.dominates = []
    
    def move( self, sol ):
        #FIXME: WHY IS THIS HAPPENING
        if not sol in self.data[sol.fit]:
            self.refreshFit( )
            #for i in range(len(self.data)):
                #if sol in self.data[i]:
                    #print("Actually in:", i, "w/", sol.fit)
                    #print(sol in self.gen.ind)
        self.data[sol.fit].remove(sol)
        if len(self.data[sol.fit]) == 0:
                self.data.remove(self.data[sol.fit])
                self.refreshFit( )
        self.here.remove(sol)
        self.add(sol) #add takes care of updating any domees we displace
    
    def dominates( self, sol, comprd2 ):
        eq = 0
        for i in range(len(sol.moeaf)):
            #MAXIMIZE LIT SQUARES
            if i == LITSQ:
                if sol.moeaf[i] < comprd2.moeaf[i]:
                    #print( sol.moeaf[i], "<", comprd2.moeaf[i] )
                    return False
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
            #MINIMIZE BULBS SHINING ON EACH OTHER
            #MINIMIZE BLACK TILE SATISFICATION VIOLATIONS
            else:
                if sol.moeaf[i] > comprd2.moeaf[i]:
                    #print( sol.moeaf[i], ">", comprd2.moeaf[i] )
                    return False
                elif sol.moeaf[i] == comprd2.moeaf[i]:
                    eq += 1
        #if we're equal we don't dominate them
        if eq == len(sol.moeaf):
            #print("EQUAL")
            return False
        else:
            #print("DOMINATES")
            return True