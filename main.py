#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

import configparser
import fileinput
import graph

def readConfig():
    config = configparser.RawConfigParser()
    config.read('default.cfg')
    if config['file']['gen'] != "gen":
        config['graph'] = readGraphFile(config['file']['gen'])
    return config

def readGraphFile(filename)
    for line in fileinput.input(filename)
        
    return 0
    
#This reads in, from filename, and build a graph
def graphHandle(cfg):
    
    return 

def main():
    cfg = readConfig()
    return 0
    
if __name__ == '__main__':
    main()
