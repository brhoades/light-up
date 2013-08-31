#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from graph import graph
from const import (gt, lprets, solv, method)
from copy import deepcopy
from math import ceil

def ideal( puz, accuracy ):        
    print( "Finding ideal solution: " )
    
    puz.accuracy = accuracy
    best = graph( True, puz )
    for i in range(0, puz.x):
        for j in range(0, puz.y):
            if puz.data[i][j].type == gt.UNLIT:
                print( "START: ", i, j )
                thisIdeal( puz, best, i, j )
                
    print( "Found! lamps: ", best.lights(), " lit tiles: ", best.litsq(), "/", puz.posLit(), "black tiles: ", best.blackSats, "/", best.blacks( ) )
    return best

def thisIdeal( puz, best, x, y, deep=1 ):
    if not puz.addLight( x, y, True ):
        return -1
            
    ran = -1
    for i in range(0, puz.x):
        if ran > 0:
            ran -= 1
            break
        for j in range(0, puz.y):
            if puz.data[i][j].type == gt.UNLIT:
                ran=thisIdeal( puz, best, i, j, deep+1 )
            if ran > 0:
                break
    if deep > max( puz.x, puz.y ) and not betterSol( puz, best, "l" ):
        ran = max( puz.x, puz.y ) - int(puz.accuracy)

    if ran == -1:
        if betterSol( puz, best ):
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if best.data[i][j].type == gt.BULB:
                        best.rmLight( i, j )
            
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if puz.data[i][j].type == gt.BULB:
                        best.addLight( i, j, True )        
        #print( "BEST" )
    
    puz.rmLight( x, y )
    return ran
    
#Is our current solution (self) better than our best? (self.bestSol)
def betterSol( puz, best, t="" ):
    ret = 0
    if t == "l":
        return puz.lights( ) > best.lights( )
    if puz.blackSats >= best.blackSats:
        return True
    ########################################################
    #Random solver
    ########################################################
    #def solve( 
