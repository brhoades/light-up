#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import lh
from graph import graph
from util import *
import solve

def main():
    cfg = readConfig(gcfg( ))
    puz = graph(conf=cfg)
    print( puz )
    plh = initLogs( cfg, puz, gcfg( ) )
    best = graph()
    best.copy(puz)
    for i in range( 0, int(cfg['solve']['runs']) ):
        tester = graph( )
        tester.copy(puz)
        solve.manSeq( tester, cfg, plh, i )
        if tester.fit > best.fit:
            best.copy(tester)
    
    best.logSolution( plh[lh.SOL] )
    print( "Best found: " )
    print( best )
    
    for elh in plh:
        elh.close( )
    return 0

if __name__ == '__main__':
    main()
