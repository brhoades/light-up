#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from graph import graph
from const import (gt, lprets, solv, method)
from copy import deepcopy
from math import (ceil,floor)
import time

def ideal( puz, accuracy ):        
    print( "Finding ideal solution: " )
    back = 0
    
    puz.accuracy = accuracy
    done = False
    best = None
    clean = graph( True, puz )
    
    for [i,j] in puz.bbRange( ):
        if puz.data[i][j].type == gt.UNLIT:
            back = 0
            del best
            best = graph( True, puz )
            back = bbIdeal( puz, best, i, j )
            if back == 1:
                break

    print( "Found! lamps: ", best.lights(), " lit tiles: ", best.litsq(), "/", puz.posLitsq(), "black tiles: ", best.blackSats, "/", best.blacksSb( ), "(", best.blacks( ), ")" )
    if best.data != puz.data:
        return best
    else:
        return False


def bbIdeal( puz, best, x, y ):
    if not puz.addLight( x, y, True ):
        return 0
    
    ran = 0
        
    for [i, j] in puz.bbRange( ):
        if puz.data[i][j].type == gt.UNLIT:
            ran=bbIdeal( puz, best, i, j )
        if ran > 0:
            break
    
    if ran == 0:
        if betterSol( puz, best, "b" ):
            print( puz )
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if best.data[i][j].type == gt.BULB:
                        best.rmLight( i, j )
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if puz.data[i][j].type == gt.BULB:
                        best.addLight( i, j )
            #thisIdeal( puz, best, x, y, deep ) Why was this here?
            if bestSol( best, "b" ):
                for i in range(0, puz.x):
                    for j in range( 0, puz.y):
                        if puz.data[i][j].type == gt.UNLIT:
                            ran = lfIdeal( puz, best, i, j )
                            if ran == 2:
                                ran = 1
                                break
                        if ran == 1:
                            break
            else:
                ran = 2
            
    puz.rmLight( x, y )
    return ran

def lfIdeal( puz, best, x, y ):
    if not puz.addLight( x, y, True ):
        return 0
    
    ran = 0

    if not betterSol( puz, best, "l" ):
        ran = -1

    if ran == 0:
        for i in range(0, puz.x):
            for j in range( 0, puz.y):
                if puz.data[i][j].type == gt.UNLIT:
                    ran=lfIdeal( puz, best, i, j )
                if ran > 0:
                    break
    
    if ran == 0:
        if betterSol( puz, best, "l" ):
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if best.data[i][j].type == gt.BULB:
                        best.rmLight( i, j )
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if puz.data[i][j].type == gt.BULB:
                        best.addLight( i, j )
        #thisIdeal( puz, best, x, y, deep ) Why was this here?
        if bestSol( best, "l" ):
            ran = 2
            
    puz.rmLight( x, y )
    if ran == -1:
        return 0
    return ran    

def betterSol( puz, best, chk="a" ):
    if chk == "b":
        if puz.blackSats > best.blackSats:
            return True
    elif chk == "l":
        if puz.litsq( ) > best.litsq( ):
            return True
    return False

def bestSol( puz, chk="a" ):
    ret = 0
    if chk == "b" or chk == "a":
        print( puz.blackSats, "<", puz.blacksSb() )
        if puz.blackSats < puz.blacksSb( ):
            return False
    if chk == "l" or chk == "a":
        print( puz.litsq( ), "<", puz.posLitsq( ) )
        if puz.litsq( ) < puz.posLitsq( ):
            return False

    return True
            
            
    ########################################################
    #Random solver
    ########################################################
    #def solve( 
