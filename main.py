#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
import graph

def readConfig():
    config = configparser.RawConfigParser()
    config.read('default.cfg')
    return config

def main():
    cfg = readConfig()
    puz = graph(cfg['graph'])
    
    return 0
    
if __name__ == '__main__':
    main()
