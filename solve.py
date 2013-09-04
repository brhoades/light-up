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
    return False
    
def ideal( puz, timeout=1 ):        
    back = 0
    
    best = graph.graph( )
    best.copy( puz )
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)
    try:
        if len(puz.bbRange( ) ) <= 0:
            for i in range(0,self.x):
                for j in range(0,self.y):
                    back = puz.lfIdeal( puz, best, i, j )
                    if back == solv.BEST:
                        break
                if back == solv.BEST:
                    break
        else:
            for [i,j] in puz.bbRange( ):
                if puz.data[i][j].type == gt.UNLIT:
                    back = bbIdeal( puz, best, i, j )
                    if back == solv.BEST:
                        break
                        
        signal.alarm(0)
        #print( "Found! lamps: ", best.lights(), " lit tiles: ", best.litsq(), "/", best.posLitsq(), "black tiles: ", best.blackSats, "/", best.blacksSb( ), "(", best.blacks( ), ")" )
        print( best )
        if back == solv.BEST:
            return True
        else:
            return False
    except Exception as e:
        raise e
    except: 
        return False

def bbIdeal( puz, best, x, y ):
    if not puz.addLight( x, y, True ):
        return solv.DONE
    
    ran = solv.DONE
        
    for [i, j] in puz.bbRange( ):
        if puz.data[i][j].type == gt.UNLIT:
            ran=bbIdeal( puz, best, i, j )
        if ran > solv.DONE:
            break
    
    if ran == solv.DONE:
        if betterSol( puz, best, "b" ):
            best.copy( puz )
            if bestSol( best, "b" ):
                if bestSol( best, "l" ):
                    ran = solv.BEST
                clean = graph.graph( )
                clean.copy( best )
                for i in range(0, puz.x):
                    for j in range( 0, puz.y):
                        if puz.data[i][j].type == gt.UNLIT:
                            if ran > solv.DONE:
                                break
                            best.copy( clean )
                            ran = lfIdeal( puz, best, i, j )
                    if ran > solv.DONE:
                        break
            else:
                ran = solv.DONE
            
    puz.rmLight( x, y )
    return ran

def lfIdeal( puz, best, x, y ):
    if not puz.addLight( x, y, True ):
        return solv.DONE

    ran = solv.DONE

    for i in range(0, puz.x):
        for j in range( 0, puz.y):
            if puz.data[i][j].type == gt.UNLIT:
                ran=lfIdeal( puz, best, i, j )
                if ran > solv.DONE:
                    break
        if ran > solv.DONE:
            break
    
    if ran == solv.DONE:
        if betterSol( puz, best, "l" ):
            best.copy( puz )

            if bestSol( puz, "l" ):
                ran = solv.BEST

    puz.rmLight( x, y )
    return ran    

def betterSol( puz, best, chk="a" ):
    if chk == "b" or chk=="a":
        if puz.blackSats > best.blackSats or puz.ignoreBlacks:
            return True
    if chk == "l" or chk=="a":
        if puz.litsq( ) > best.litsq( ):
            return True
    return False

def bestSol( puz, chk="a" ):
    if chk == "b" or chk == "a":
        if puz.blackSats == puz.blacksSb( ) or puz.ignoreBlacks:
            return True
    if chk == "l" or chk == "a":
        if puz.litsq( ) == puz.posLitsq( ):
            return True

    return False
            
        
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
    
    slh = plh[lh.SOL]
    rlh = plh[lh.RES]
    
    i = 0
    area = puz.x*puz.y
    lastline=""
    count = run*int(cfg['solve']['fitevals'])
    
    logSeperate( rlh, run )
    print( "Run #", run+1, "/", cfg['solve']['runs'] )
    best = graph.graph( )
    best.copy( puz )
    while i < runs:
        sol = graph.graph( )
        sol.copy(puz)
        rng( sol, chance )
        
        if sol.isValid( ):
            i += 1
            if sol.fit > best.fit:
                best.copy(sol)
                sol.logResult( i, rlh )
        
            if ( area < 100 and i % sol.x ) or area >= 100:
                print('\b'*len(lastline), end='')
                    
                lastline = status(cfg['solve'], i, count)
                print(lastline, end='')
    print( "" )
    puz.copy( best )

def status( cfg, i, count ):
    #(numgoodruns/totalruns) (%done)
    line = str(i)
    line += ''.join( ["/", cfg['fitevals'], " (", str(round(i/int(cfg['fitevals'])*100, 1)), "%)"] )
    #Spacer
    line +=" "*4
    #numoftotalpossibleruns/max (%done)
    line += str(count+i)
    maxn = int(cfg['runs'])*int(cfg['fitevals'])
    line += ''.join( ["/", str(maxn), " (", str(round((count+i)/maxn*100, 3)), "%)" ] )
    return line
    
def logSeperate( rlf, run ):
    rlf.flush( )
    rlf.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )
