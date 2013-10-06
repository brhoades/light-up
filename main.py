#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C

from graph import graph
from util import *
from const import ci
import runner

def main():
    cfg = readConfig(gcfg( ))
    
    if cfg[ci.GRAPH][ci.SEED] == 'random':
        dt = datetime.datetime.now( )
        cseed = seed( )
    else:
        cseed = float(cfg[ci.GRAPH][ci.SEED])
    
    random.seed(cseed)
    
    lg = log( cfg, cseed, gcfg( ) )
    best = False
    for i in range( int(cfg[ci.MAIN][ci.TOTAL_RUNS]) ):
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
