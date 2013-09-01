#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
from graph import graph
import random
import solve
import sys
import argparse

def readConfig( fn ):
    config = configparser.ConfigParser()
    config.read(fn)
    return config

def main():
    cfg = readConfig(gcfg( ))
    puz = graph(cfg['graph'])
    print( puz )
    quit
    lastline=""
    count = 0
    runs = int(cfg['solve']['runs'])
    chance = float(cfg['solve']['chance'])
    countBlack = bool(cfg['solve']['ignoreblack'])
    i = 0
    while i < runs:
        sol = graph( True, puz )
        solve.rng( sol, chance )
        
        count += 1
        if sol.isValid( countBlack ):
            i += 1
        
        if count % 50:
            for j in range(0, len(lastline)):
                print('\b', end='')
                
            lastline = status(cfg['solve'], i, count)
            print(lastline, end='')
    print( "" )
    return 0

def status( cfg, i, count ):
    #(numgoodruns/totalruns) (%done)
    line = str(i)
    line +="/"
    line += cfg['runs']
    line += " ("
    line += str(round(i/int(cfg['runs'])*100, 1))
    line +="%)"
    #Spacer
    line +=" "*4
    #numoftotalpossibleruns/max (%done)
    line +=str(count)
    line +="/"
    line +=cfg['maxruns']
    line +=" ("
    line +=str(round(count/int(cfg['maxruns'])*100, 3))
    line +="%)"
    return line

def gcfg( ):
    parser = argparse.ArgumentParser(description='CS348 AS1-1')
    parser.add_argument('-c', type=str,
                       help='Specifies a configuration file (default: default.cfg)',
                       default="default.cfg")

    args = parser.parse_args()
    return args.c

if __name__ == '__main__':
    main()
