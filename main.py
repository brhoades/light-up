#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
import random
from graph import graph
from solve import solve

def readConfig():
    config = configparser.ConfigParser()
    config.read('default.cfg')
    if config['graph']['seed'] == 'random':
        config['graph']['seed'] = str(random.SystemRandom())
    return config
    
def main():
    cfg = readConfig()
    random.seed(cfg['graph']['seed'])
    
    puz = graph(cfg['graph'])
    print( puz )
    
    sol = solve(cfg['solve']['method'])
    sol.ideal(puz)
    #sol.solve(puz)
    print( sol );
    
    return 0
    
if __name__ == '__main__':
    main()
