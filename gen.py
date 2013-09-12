#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Generation class file
# This file houses the class for generations (gen).

import graph, sol
from util import *
import math

class gen:

    #argument is the previous generation's number
    def __init__( self, **args ):
        #Store all of our populace here
        self.ind = set( )
        
        #Store for the clean, master puzzle
        self.puz = args['puz']
        
        self.genNumber=args['genNum']+1
        
        self.generate(args['conf'])
        
        
        
    # Add a single individual to our pool
    def add( self, ind ):
        self.ind.add( ind )
    
    # Randomly generates a generation (hehe) from scratch
    def generate( self, cfg ):
        delprn( "generating init. pop. " )
        
        mu = int(cfg['pop']['mu'])
        forcevalid = (cfg['pop']['forcevalid'] == "True")
        for i in range(0,mu):
            delprn( ''.join([str(math.ceil(i/mu*100)), "%"]), 2 )
            
            citizen = sol.sol( self.puz )    
            citizen.rng( forcevalid )
            self.ind.add( citizen )
