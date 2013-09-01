#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
from graph import graph
import random
import solve
import sys
import argparse
from subprocess import call
from const import lh

def readConfig( fn ):
    config = configparser.ConfigParser()
    config.read(fn)
    return config

def main():
    cfg = readConfig(gcfg( ))
    plh = initLogs( cfg['log'] )
    puz = graph(cfg['graph'])
    print( puz )
    
    best = graph( True, puz )
    for i in range( 0, int(cfg['solve']['runs']) ):
        npuz = solve.manSeq( puz, cfg, plh, i )
        if npuz.fit > best.fit:
            best = graph( True, npuz )
    
    best.logSolution( plh[lh.SOL] )
    
    for elh in plh:
        elh.close( )
    return 0

def gcfg( ):
    parser = argparse.ArgumentParser(description='S348 FS2013 Assignment 1a')
    parser.add_argument('-c', type=str,
                       help='Specifies a configuration file (default: default.cfg)',
                       default="default.cfg")

    args = parser.parse_args()
    return args.c
    
def initLogs( cfg ):
    resLogh = open( cfg['result'], 'w' )
    solLogh = open( cfg['solution'], 'w' )
    
    resLogh.write( ''.join(["Result Log", '\n']) )
    #if cfg['logh']:
    #    resLogh.write( 
    solLogh.write( ''.join(["Solution Log", '\n']) )
    
    handles = [resLogh, solLogh]
    return handles

if __name__ == '__main__':
    main()
