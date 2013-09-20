#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Test Unit Functions
#  This program is called to test the assignment before submission.

import os, unittest, io, cProfile, timeit, time, datetime, sys, pstats
import main
import graph
    
rstd=sys.stdout
    
class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.puzzles=[]
        self.times=[]

    def test_randomGenSq(self):
        count = 100
        size = 15
 
        print( ''.join(["Square board generation tests (", str(count)," ea): "]), file=rstd)
        
        for size in range(2,size+1):
            print(''.join(["  ", str(size), "x", str(size), ": "]), file=rstd, end='')
            times = []
            
            for i in range(0,count):
                st = datetime.datetime.now()
                test = graph.graph( file="cfgs/test-1.cfg", x=size, y=size )
                t = datetime.datetime.now( ) - st            
                times.append(t.microseconds)
                
                self.assertTrue(test.lights( ) == 0)
            
            avg = 0
            for t in times:
              avg += t
            avg /= count
            
            print(avg, " µs", file=rstd)

    def test_randomGenRect(self):
        count = 100
        upper = 15
        sizes = []
        
        print( ''.join(["Rectangular board generation tests (", str(count)," ea): "]), file=rstd)
        
        for i in range(2,upper):
            for j in range(2,upper):
                if i == j:
                    continue
                sizes.append([i,j])
        
        for [x,y] in sizes:
            if y == 2:
                print(''.join[x,":"], file=rstd)
            print(''.join([]), file=rstd, end='')
            times = []
            
            for i in range(0,count):
                st = datetime.datetime.now()
                test = graph.graph(file="cfgs/test-1.cfg", x=x, y=y)
                t = datetime.datetime.now( ) - st            
                times.append(t.microseconds)
                
                self.assertTrue(test.lights( ) == 0)
                
            avg = 0
            for t in times:
                avg += t
                avg /= count
            
            print( avg, " µs", file=rstd )
            
    def test_manSolve(self):
        print("Manually solving a graph", file=rstd)
        st = datetime.datetime.now()
        test = graph.graph( file="cfgs/test-1.cfg" )
        t = datetime.datetime.now( ) - st            
        
        test.addLight(0, 0)
        print( graph )
        
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
