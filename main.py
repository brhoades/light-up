#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C

from graph import graph
from util import *
from const import *
import runner

def main():
    cfg = readConfig(gcfg( ))
    
    cseed = 0
    if cfg[GRAPH][SEED] == 'random':
        cseed = seed( )
    else:
        cseed = float(cfg[GRAPH][SEED])
    
    random.seed(cseed)
    
    lg = log( cfg, cseed, gcfg( ) )
    best = False
    for i in range( int(cfg[MAIN][TOTAL_RUNS]) ):
        puz=graph(conf=cfg, quiet=True)        
        if i == 0:
            renderHead(cfg)
        nbest = runner.manSeq( puz, cfg, lg, i )
        if best == False or nbest.fit > best.fit:
            lg.newBest( nbest )
            best = nbest
    print( "" )
    
    lg.best(best)
    lg.wrapUp(best)

if __name__ == '__main__':
    main()
