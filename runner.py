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
    runs = int(cfg['main']['fitevals'])
    chance = float(cfg['main']['chance'])
    
    slh = plh[lh.SOL]
    rlh = plh[lh.RES]
    
    i = 0
    lastline=""
    count = run*int(cfg['main']['fitevals'])
    
    logSeperate( rlh, run )
    util.delprn( ''.join(["Run #", str(run+1).zfill(len(cfg['main']['runs'])), "/", cfg['main']['runs'], ": "]), 0 )

    gen.gen( conf=cfg, genNum=i, puz=puz )
    
    print( "" )
    
    #while i < runs:

    #if i % 3 > 0:
    #    print('\b'*len(lastline), end='')
    #    lastline = status(cfg['main'], i, count)
    #    print(lastline, end='')
    #print( "" )

# Prints our status out in a sexy format. Shouldn't be called often as it
#   does do some calculation and a bunch of backspaces beforehand.
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

# Seperates our result log file with pretty run numbers.
#FIXME: This really needs to be somewhere else
def logSeperate( rlf, run ):
    rlf.flush( )
    rlf.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )
