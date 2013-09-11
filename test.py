#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#
#  This program is called to test the assignment before submission.

import os, unittest, io, cProfile, timeit, time, datetime, sys
import main
import graph
    
rstd=sys.stdout
    
class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.puzzles=[]
        self.times=[]

    def test_randomGen(self):
        count = 50
        size = 10
        
        print( ''.join(["Square board generation tests (", str(count)," ea), ignoring black tiles: "]), file=rstd)
        
        for size in range(2,size+1):
            print( ''.join(["  ", str(size), "x", str(size), ": "]), file=rstd, end='')
            times = []

            for i in range(0,count):
                st = datetime.datetime.now()
                graph.graph( file="cfgs/test-1.cfg", x=size, y=size )
                t = datetime.datetime.now( ) - st            
                times.append(t.microseconds)
            
            avg = 0
            for t in times:
              avg += t
            avg /= count
            
            
            print( avg, " µs", file=rstd )
            
        print( ''.join(["Square board generation tests (", str(count)," ea), counting black tiles: "]), file=rstd)
        
        for size in range(2,size+1):
            print( ''.join(["  ", str(size), "x", str(size), ": "]), file=rstd, end='')
            times = []
            
            for i in range(0,count):
                st = datetime.datetime.now()
                test = graph.graph( file="cfgs/test-2.cfg", x=size, y=size )
                t = datetime.datetime.now( ) - st            
                times.append(t.microseconds)
            
            avg = 0
            for t in times:
              avg += t
            avg /= count
            
            
            print( avg, " µs", file=rstd )
         
if __name__ == '__main__':
    unittest.main(buffer=True)
#pr = cProfile.Profile()
#pr.enable()
#main.main( )
#pr.disable()
#s = io.StringIO()
#sortby = 'cumulative'
#ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
#ps.print_stats()
#print(s.getvalue())
