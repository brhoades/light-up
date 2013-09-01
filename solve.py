#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import graph
from const import gt, lprets, solv, method, lh

import time, signal, random
from copy import deepcopy
from math import ceil, floor

########################################################
#Ideal Solver
#Returns true if a problem is solveable
#returns false if it's -really- hard / unsolveable
#  used to check randomly generated boards
########################################################
#def solve( 
def handler(signum, frame):
    raise OSError()
    return False
    
def ideal( puz, timeout=1 ):        
    back = 0
    
    best = None
    clean = graph.graph( True, puz )
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(ceil(timeout/5))
    try:
        back = 0
        if len(puz.bbRange( ) ) <= 0:
            for i in range(0,self.x):
                for j in range(0,self.y):
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
        if puz.blackSats < puz.blacksSb( ):
            return False
    if chk == "l" or chk == "a":
        if puz.litsq( ) < puz.posLitsq( ):
            return False

    return True
            
        
########################################################
#Random solver
########################################################
def rng( puz, prob ):
    for i in range(0, puz.x):
        for j in range(0, puz.y):
            if puz.data[i][j].type == gt.UNLIT and flip(prob):
                puz.addLight( i, j )
    puz.setFitness( )            

def flip( chance ):
    ran = random.uniform(0, 100)
    if( ran <= chance*100 ):
        return True
    return False
    
def manSeq( puz, cfg, plh, run ):
    runs = int(cfg['solve']['fitevals'])
    chance = float(cfg['solve']['chance'])
    countBlack = bool(cfg['solve']['ignoreblack'])
    
    slh = plh[lh.SOL]
    rlh = plh[lh.RES]
    
    i = 0
    lastline=""
    count = run*cfg['runs']['fitevals']
    
    logSeperate( rlh, run )
    print( "Run #", run+1, "/", cfg['solve']['runs'] )
    best = graph.graph( True, puz )

    while i < runs:
        sol = graph.graph( True, puz )
        rng( sol, chance )
        
        count += 1
        if sol.isValid( countBlack ):
            i += 1
            if sol.fit > best.fit:
                best = graph.graph( True, sol )
                sol.logResult( i, rlh )
        
        if count % 50:
            for j in range(0, len(lastline)):
                print('\b', end='')
                
            lastline = status(cfg['solve'], i, count)
            print(lastline, end='')
    print( "" )
    return best

def status( cfg, i, count ):
    #(numgoodruns/totalruns) (%done)
    line = str(i)
    line += ''.join( ["/", cfg['fitevals'], " (", str(round(i/int(cfg['fitevals'])*100, 1)), "%)"] )
    #Spacer
    line +=" "*4
    #numoftotalpossibleruns/max (%done)
    line += str(count)
    maxn = int(cfg['runs'])*int(cfg['fitevals'])
    line += ''.join( ["/", maxn, " (", str(round(count/maxn)*100, 3)), "%)" ] )
    return line
    
def logSeperate( rlf, run ):
    rlf.flush( )
    rlf.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )
