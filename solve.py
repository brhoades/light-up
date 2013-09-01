#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import graph
from const import (gt, lprets, solv, method)
from copy import deepcopy
from math import (ceil,floor)
import time
import signal

def handler(signum, frame):
    raise OSError()
    return False
    
def handlerc(signum, frame):
    quit

def ideal( puz, timeout=1 ):        
    back = 0
    
    best = None
    clean = graph.graph( True, puz )
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    try:
        back = 0
        if len(puz.bbRange( ) ) <= 0:
            for i in range(0,self.x):
                for j in range(0,self.y):
                    print( "blank: ", i, j )
                    back = puz.lfIdeal( puz, best, i, j )
                    if back == 3:
                        break
                if back == 3:
                    break
            
        for [i,j] in puz.bbRange( ):
            if puz.data[i][j].type == gt.UNLIT:
                back = 0
                puz.hitTopinc( True )
                best = graph.graph( True, puz )
                back = bbIdeal( puz, best, i, j )
                if back == 3:
                    break

        signal.alarm(0)
        #print( "Found! lamps: ", best.lights(), " lit tiles: ", best.litsq(), "/", best.posLitsq(), "black tiles: ", best.blackSats, "/", best.blacksSb( ), "(", best.blacks( ), ")" )
        if back == 3:
            return True
        else:
            return False
    except KeyboardInterrupt:
        quit
    except:
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
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if best.data[i][j].type == gt.BULB:
                        best.rmLight( i, j )
            for i in range(0, puz.x):
                for j in range( 0, puz.y):
                    if puz.data[i][j].type == gt.BULB:
                        best.addLight( i, j )

            if bestSol( best, "b" ):
                clean = graph.graph( True, best )
                for i in range(0, puz.x):
                    for j in range( 0, puz.y):
                        if puz.data[i][j].type == gt.UNLIT:
                            del best
                            best = graph.graph( True, clean )
                            puz.hitTopinc( True )
                            ran = lfIdeal( puz, best, i, j )
                            if ran > 1:
                                break
                    if ran > 1:
                        break
                if ran != 3:
                    ran = 2
            else:
                ran = 2
            
    puz.rmLight( x, y )
    return ran

def lfIdeal( puz, best, x, y ):
    if not puz.addLight( x, y, True ):
        return 0
    
    ran = 0

    if puz.hitTopLim( ):
        ran = 1

    if ran == 0:
        for i in range(0, puz.x):
            for j in range( 0, puz.y):
                if puz.data[i][j].type == gt.UNLIT:
                    ran=lfIdeal( puz, best, i, j )
                    if ran > 0:
                        break
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

        if bestSol( best, "l" ):
            ran = 3
        else:
            puz.hitTopinc( )

    puz.rmLight( x, y )
    return ran    

def betterSol( puz, best, chk="a" ):
    if chk == "b" or chk=="a":
        if puz.blackSats > best.blackSats:
            return True
    if chk == "l" or chk=="a":
        if puz.litsq( ) > best.litsq( ):
            return True
    return False

def bestSol( puz, chk="a" ):
    ret = 0
    if chk == "b" or chk == "a":
        #print( puz.blackSats, "<", puz.blacksSb() )
        if puz.blackSats < puz.blacksSb( ):
            return False
    if chk == "l" or chk == "a":
        #print( puz.litsq( ), "<", puz.posLitsq( ) )
        if puz.litsq( ) < puz.posLitsq( ):
            return False

    return True
            
            
    ########################################################
    #Random solver
    ########################################################
    #def solve( 
