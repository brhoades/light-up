#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Solver Functions
#  This file does a bulk of the large scale logic operations and generation operations / output.

from const import gt
import gen
import random
import util
import math

# The main sequence for our solver. Will eventually call all of
#   the generation handling, breeding, mutating, etc.
def manSeq( puz, cfg, lg, run ):
    i = 0
    lastline=""
    
    lg.sep( run )
    runs = ""
    runs += str(run+1)
    runs += '\t'
    if int(cfg['main']['runs']) > 9:
        runs += '\t' 
    util.delprn( ''.join([str(run+1), "\t"]), 0 )
    prnBase( cfg, False )
    thisgen = gen.gen( conf=cfg, genNum=run, puz=puz )        
    lg.gen( thisgen )

    while runCriteria(cfg, thisgen):
        if thisgen.num % 25:
            lg.flush( )
        prnBase( cfg, thisgen )
        thisgen.reproduce( )
        thisgen.natSelection( )
        thisgen.num += 1
        lg.gen( thisgen )
    prnBase( cfg, thisgen )
    best = thisgen.best( )
    lg.genBest( best, thisgen )
    # Clear best's reference so we can die when our other stuff is done and when best loses its reference.
    best.gen = None
    thisgen.ind.discard(best)
    thisgen.delete( )
    return best
  
# This is the logic behind the termination critera described in default.cfg under 'main'
#   Takes our basic configuration and the generation to test.
def runCriteria( cfg, gen ):
    if cfg['main']['gens'] != "0":
        return gen.num < int(cfg['main']['gens'])
    elif cfg['main']['fitevals'] != "0":
        return gen.fitEvals < int(cfg['main']['fitevals'])
    elif cfg['main']['homogenity'] != "0":
        thisavg = gen.average( )
        if cfg['main']['stoponsol'] and gen.best( ).fitness( ) == 1:
            return False
        if round(thisavg, int(cfg['main']['homoacc'])) == gen.lastFit:
            gen.sameTurns += 1
            if gen.sameTurns >= int(cfg['main']['homogenity']):
                return False
        else:
            gen.lastFit = round(thisavg, int(cfg['main']['homoacc']))
            gen.sameTurns = 0
        return True
        
# Prints our basic status string
def prnBase( cfg, gen=False ):
    evals=0
    avg=0
    genn=0
    if gen != False:
        avg = round( gen.average( ), 4 )
        genn = gen.num
        evals = gen.fitEvals
    
    out = ""
    #if cfg['main']['gens'] != "0":
    #    out = "\t"
    if int(cfg['main']['runs']) >= 10:
        out += "\t"
    out += util.pad(genn, cfg['main']['gens'])
    out += "\t"
    if int(cfg['main']['gens']) > 0:
        out += "\t"
        if math.log(int(cfg['main']['gens']), 10) >= 12:
            out += "\t"
    out += util.pad(evals, cfg['main']['fitevals'])
    if int(cfg['main']['fitevals']) > 0 and math.log(int(cfg['main']['fitevals']), 10) >= 3:
        out += "\t"
    out += "\t"
    out += str(avg)
    out += "\t"
    
    util.delprn(out, 1)
