#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import graph
from const import gt, lprets, solv, method, lh

import time, signal, random
from copy import deepcopy
from math import ceil, floor

########################################################
#Random solver
########################################################
def rng( puz, prob ):
    for i in range(0,puz.x):
        for j in range(0,puz.y):
            sqr = puz.data[i][j]
            if sqr.type == gt.UNLIT and not sqr.isBad( ) and flip(prob):
                sqr.addLight( )
    puz.setFitness( )            

def flip( chance ):
    if( random.uniform(0, 100) <= chance*100 ):
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
    sol = graph.graph( )
    sol.copy( puz )
    while i < runs:
        sol.clear( )
        rng( sol, chance )
        
        if sol.isValid( ):
            i += 1
            if sol.fit > best.fit:
                best.copy(sol)
                sol.logResult( i, rlh )
            
            if i % 3 > 0:
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
