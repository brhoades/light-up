#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Solver Functions
#  This file does a bulk of the large scale logic operations and generation operations / output.

from const import gt, ci, opp
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
    if int(cfg[ci.MAIN][ci.TOTAL_RUNS]) > 9:
        runs += '\t' 
    util.delprn( ''.join([str(run+1), "\t"]), 0 )
    prnBase( cfg, False )
    thisgen = gen.gen( conf=cfg, genNum=run, puz=puz )        
    lg.gen( thisgen )

    while runCriteria(cfg[ci.TERMINATION], thisgen):
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
  
# This is the logic behind the termination critera described in default.cfg under [main]
#   Takes our basic configuration and the generation to test.
def runCriteria( tcfg, gen ):
    
    if gen.best( ).getFit( ) == 1 and tcfg[ci.STOP_ON_BEST] == "True":
        return False
    if tcfg[ci.TYPE] == opp.GENERATIONAL_LIMIT:
        return gen.num < int(cfg[ci.GENERATION_LIMIT])
    elif tcfg[ci.TYPE] == opp.FITNESS_EVALUATION_LIMIT:
        return gen.fitEvals < int(tcfg[ci.EVALUATION_LIMIT])
    elif tcfg[ci.TYPE] == opp.CONVERGENCE:
        thisbest = gen.average( )
        if thisbest <= gen.lastBestAvg:
            gen.sameTurns += 1
            if gen.sameTurns >= int(tcfg[ci.TURNS_NO_CHANGE]):
                return False
        else:
            gen.lastBestAvg = thisbest
            gen.sameTurns = 0
        return True
        
# Prints our basic status string
def prnBase( cfg, gen=False ):
    evals=0
    avg=0
    genn=0
    if gen != False:
        avg = round( gen.hAverage( ), 4 )
        genn = gen.num
        evals = gen.fitEvals
    
    out = ""
    if int(cfg[ci.MAIN][ci.TOTAL_RUNS]) >= 10:
        out += "\t"
    out += util.pad(genn, cfg[ci.TERMINATION][ci.GENERATION_LIMIT])
    out += "\t"
    if cfg[ci.TERMINATION][ci.TYPE] == opp.GENERATIONAL_LIMIT:
        out += "\t"
        if math.log(int(cfg[ci.TERMINATION][ci.GENERATION_LIMIT]), 10) >= 12:
            out += "\t"
    out += util.pad(evals, cfg[ci.TERMINATION][ci.EVALUATION_LIMIT])
    if cfg[ci.TERMINATION][ci.TYPE] == opp.FITNESS_EVALUATION_LIMIT and math.log(int(cfg[ci.TERMINATION][ci.EVALUATION_LIMIT]), 10) >= 3:
        out += "\t"
    out += "\t"
    out += str(avg)
    out += "\t"
    
    util.delprn(out, 1)
