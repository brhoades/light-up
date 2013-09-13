#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Solver Functions
#  This file does a bulk of the large scale logic operations and generation operations / output.

from const import gt, lh
import gen
import random
import util
import math

# The main sequence for our solver. Will eventually call all of
#   the generation handling, breeding, mutating, etc.
def manSeq( puz, cfg, plh, run ):
    evals = int(cfg['main']['fitevals'])
    chance = float(cfg['main']['chance'])
    
    slh = plh[lh.SOL]
    rlh = plh[lh.RES]
    
    i = 0
    lastline=""
    
    logSeperate( rlh, run )
    util.delprn( ''.join([str(run+1), "/", cfg['main']['runs'], " \t", \
        util.perStr( (run+1)/int(cfg['main']['runs']), False), "\t"]), 0 )
    prnBase( cfg, i, evals, False )
    thisgen = gen.gen( conf=cfg, genNum=run, puz=puz )        
    
    while runCriteria(cfg, i):
        prnBase( cfg, i, evals, thisgen )
        thisgen.reproduce( )
        thisgen.mutate( )
        thisgen.natSelection( ) #FIXME: Make this a negative tournament
        if int(cfg['main']['gens']) != 0:
            i += 1
        else:
            i = thisgen.fitEvals
  
    prnBase( cfg, i, evals, thisgen )
  
    print( "" )
    print( thisgen.best( ).graph )
    
def runCriteria( cfg, i ):
    if int(cfg['main']['gens']) != 0:
        return i < int(cfg['main']['gens'])
    elif int(cfg['main']['fitevals']) != 0:
        return i < int(cfg['main']['fitevals'])
   
# Seperates our result log file with pretty run numbers.
#FIXME: This really needs to be somewhere else
def logSeperate( rlf, run ):
    rlf.flush( )
    rlf.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )

# Prints our basic string
def prnBase( cfg, i, evals, gen ):
    if gen == False:
        avg = 0
    else:
        avg = round( gen.average( ), 4 )
    if cfg['main']['gens'] != 0:
        util.delprn( ''.join([str(i), '\t'*(math.ceil(int(cfg['main']['gens'])/100000)-math.floor(i/10000)), '\t\t', util.perStr(i/evals, False), "\t", str(avg), "\t" ]), 1 )
    else:
        util.delprn( ''.join([str(i), '\t'*(math.ceil(int(cfg['main']['fitevals'])/100000)-math.floor(i/10000)), '\t\t',  util.perStr(i/evals, False), "\t", str(avg), "\t" ]), 1 )
                    
