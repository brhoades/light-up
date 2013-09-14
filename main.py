#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B

from const import lh
from graph import graph
from util import *
import runner

def main():
    cfg = readConfig(gcfg( ))
    
    if cfg['graph']['seed'] == 'random':
        dt = datetime.datetime.now( )
        cseed = seed( )
    else:
        cseed = float(cfg['graph']['seed'])
    
    random.seed(cseed)
    
    lg = log( cfg, cseed, gcfg( ) )
    best = False
    for i in range( int(cfg['main']['runs']) ):
        puz=graph(conf=cfg, quiet=True)        
        if i == 0:
            renderHead(cfg['main'])
        nbest = runner.manSeq( puz, cfg, lg, i )
        if best == False or nbest.fitness( ) > best.fitness( ):
            best = nbest
    print( "" )
    
    lg.best(best)
    lg.finish( )

if __name__ == '__main__':
    main()
