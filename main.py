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
    print( "Seeded RNG off ", cseed )
    
    plh = initLogs( cfg, gcfg( ) )
    for i in range( int(cfg['main']['runs']) ):
        puz = graph(conf=cfg)        
        if i == 0:
            renderHead(cfg['main'])
        runner.manSeq( puz, cfg, plh, i )

    for elh in plh:
        elh.close( )
    return 0

if __name__ == '__main__':
    main()
