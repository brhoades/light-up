#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import lh
from graph import graph
import solve

import random, sys, argparse, configparser, subprocess, re

def readConfig( fn ):
    config = configparser.ConfigParser()
    config.read(fn)
    return config._sections

def main():
    cfg = readConfig(gcfg( ))
    puz = graph(conf=cfg)
    print( puz )
    plh = initLogs( cfg, puz, gcfg( ) )
    best = graph()
    best.copy(puz)
    for i in range( 0, int(cfg['solve']['runs']) ):
        tester = graph( )
        tester.copy(puz)
        solve.manSeq( tester, cfg, plh, i )
        if tester.fit > best.fit:
            best.copy(tester)
    
    best.logSolution( plh[lh.SOL] )
    print( "Best found: " )
    print( best )
    
    for elh in plh:
        elh.close( )
    return 0

def gcfg( ):
    parser = argparse.ArgumentParser(description='CS348 FS2013 Assignment 1a')
    parser.add_argument('-c', type=str,
                       help='Specifies a configuration file (default: cfgs/default.cfg)',
                       default="cfgs/default.cfg")

    args = parser.parse_args()
    return args.c
    
def initLogs( fcfg, puz, fname ):
    cfg = fcfg['log']
    resLogh = open( cfg['result'], 'w' )
    solLogh = open( cfg['solution'], 'w' )
    
    resLogh.write( ''.join(["Result Log\n", "Config File: ", fname, "\n"]) )
    if( fcfg['graph']['gen'] != 'True' ):
        resLogh.write( ''.join(["Puzzle File: ", fcfg['graph']['gen'], "\n" ]) )
    else:
        resLogh.write( ''.join(["Randomly Generated Graph\n"]) )
        
    resLogh.write( ''.join(['Seed: ', str(puz.seed), '\n' ]) )
    
    if cfg['logh'] != '0':
        output = subprocess.check_output("git log -n1 --pretty=\"Git Hash: %H\n  Commit Date: %ad (%ar)\n  Author: %an <%ae>\n  Change Message: %s\"", shell=True)
        output = str( output )
        output = re.sub( r'\\n', '\n', output )
        output = re.sub( r'(b\'|\'$)', '', output )
        resLogh.write( output )

    if fcfg['graph']['gen'] == 'True':
        #graph parameters
        resLogh.write( ''.join(["Map generation parameters:\n", 
            "  noblackx: ", fcfg['graph']['noblackx'], 
            "\n  seed: ", fcfg['graph']['placeblack'], 
            "\n  placeblack: ", fcfg['graph']['placeblack'], 
            "\n  blackmod: ", fcfg['graph']['blackmod'], 
            "\n  x: ", fcfg['graph']['x'], 
            "\n  y: ", fcfg['graph']['y'],
            "\n  timeout: ", fcfg['graph']['timeout'], "\n" ] ) )
        
    #rng parameters
    resLogh.write( ''.join(["RNG solution parameters:\n", 
        "  runs: ", fcfg['solve']['runs'], 
        "\n  fitevals: ", fcfg['solve']['fitevals'], 
        "\n  ignoreblack: ", fcfg['solve']['ignoreblack'], 
        "\n  chance: ", fcfg['solve']['chance'], "\n" ] ) )

    resLogh.write( "".join(['Graph:\n', str(puz)]) )

    #solLogh.write( ''.join(["Solution Log", '\n', 'Seed: ', str(puz.seed), '\n']) )
    
    handles = [resLogh, solLogh]
    return handles

if __name__ == '__main__':
    main()
