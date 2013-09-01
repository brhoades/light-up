#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
from graph import graph
import random
import solve

def readConfig():
    config = configparser.ConfigParser()
    config.read('default.cfg')
    return config
    
def main():
    cfg = readConfig()
    puz = graph(cfg['graph'])
    print( puz )
    
    sol = solve.ideal(puz)
    print( sol );
    
    return 0
    
if __name__ == '__main__':
    main()
