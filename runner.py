#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Solver Functions
#  This file does a bulk of the large scale logic operations and generation operations / output.

from const import gt, lh
import gen
import random
import util

# The main sequence for our solver. Will eventually call all of
#   the generation handling, breeding, mutating, etc.
def manSeq( puz, cfg, plh, run ):
    evals = int(cfg['main']['fitevals'])
    chance = float(cfg['main']['chance'])
    
    slh = plh[lh.SOL]
    rlh = plh[lh.RES]
    
    i = 0
    lastline=""
    count = run*int(cfg['main']['fitevals'])
    
    logSeperate( rlh, run )
    util.delprn( ''.join([str(run+1), "/", cfg['main']['runs'], " \t", \
        util.perStr( (run+1)/int(cfg['main']['runs']), False), "\t"]), 0 )
    util.delprn( ''.join([str(i), "/", str(evals), "\t", util.perStr(i/evals, False), "\t" ]), 1 )
    thisgen = gen.gen( conf=cfg, genNum=run, puz=puz )        
    
    while i < evals:
        util.delprn( ''.join([str(i), "/", str(evals), "\t", util.perStr(i/evals, False), "\t" ]), 1 )
        thisgen.reproduce( )
        thisgen.mutate( )
        thisgen.natSelection( )

        i += 1
        
    print( "" )
    
# Seperates our result log file with pretty run numbers.
#FIXME: This really needs to be somewhere else
def logSeperate( rlf, run ):
    rlf.flush( )
    rlf.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )
