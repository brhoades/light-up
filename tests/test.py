#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Test Unit Functions
#  This program is called to test the assignment before submission.

import os, unittest, io, cProfile, timeit, time, datetime, sys, pstats
sys.path.append('../')
import main
import graph
from const import gt
    
rstd=sys.stdout
    
    
def test_sqrOfType( gph, typ ):
    count = 0
    for i in range(0,gph.x):
        for j in range(0,gph.y):
            if gph.data[i][j].type == typ:
                count += 1
    return count
    
class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.puzzles=[]
        self.times=[]
        
    def checkIntegrity(self, test):
        for i in range(0,test.x):
            for j in range(0,test.y):
                sqr = test.data[i][j]
                x = sqr.x
                y = sqr.y
                
                #Check our parent
                self.assertEqual(sqr.parent, test)
                
                #Check our type
                self.assertGreater(sqr.type, gt.NOTHING)
                self.assertLess(sqr.type, gt.MAX)
                if sqr.type > gt.BLACK_THRESHOLD:
                    self.assertTrue(sqr.isBlack( ))
                    self.assertTrue(sqr.black)
                if sqr.type == gt.LIT:
                    self.assertFalse(sqr.isBad())
                
                #Check bad squares
                for neigh in sqr.bad:
                    self.assertIn(neigh, sqr.neighbors)
                    
                #Check more of our parent
                if sqr.isBlack( ):
                    self.assertIn(sqr, test.sqgt[gt.BLACK_THRESHOLD])
                self.assertIn(sqr, test.sqgt[sqr.type])
                
                #Check neighbors for validity
                neighs = []
                if x > 0:
                    neighs.append(test.data[x-1][y])
                if x < test.x-1:
                    neighs.append(test.data[x+1][y])
                if y > 0:
                    neighs.append(test.data[x][y-1])
                if y < test.y-1:
                    neighs.append(test.data[x][y+1])
                
                for neigh in neighs:
                    self.assertIn(neigh, sqr.neighbors)
                    self.assertIn(sqr, neigh.neighbors)
                    if neigh.isBlack( ) and not sqr.isBad( ) \
                        and not sqr.isBlack:
                        self.assertIn(sqr, test.bbsq)
               
    #def checkSolvable( self ):
        
    
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
            for i in range(0,count):
                test = graph.graph(file="cfgs/test-1.cfg", x=x, y=y)
                
                print(x,"x",y)
                self.checkIntegrity(test)
                self.assertEqual(test.lights( ), 0)
                
        print("Done", file=rstd)
            
    def test_manSolve(self):
        print("Manually solving a graph", file=rstd)
        test = graph.graph( file="cfgs/test-2.cfg" )
        
        test.addLight(1, 0)
        test.addLight(3, 0)
        test.addLight(0, 1)
        test.addLight(4, 2)
        test.addLight(1, 2)
        test.addLight(2, 4)
        test.addLight(0, 4)
        test.addLight(1, 6)
        test.addLight(5, 3)
        test.addLight(6, 6)
        test.addLight(6, 4)
        
        print("  Checking internals of graph: ", file=rstd, end='')
        #Check lights placed counter function, then a manual check to check the counter function
        self.assertEqual(test.lights( ), 11)
        self.assertEqual(test_sqrOfType(test, gt.BULB), test.lights( ))
        
        #Same as above, but with black squares
        self.assertEqual(test.blacks( ), 12)
        self.assertEqual( (test_sqrOfType(test, gt.BLACK0)+test_sqrOfType(test, gt.BLACK1)+test_sqrOfType(test, gt.BLACK2)+test_sqrOfType(test, gt.BLACK3)+test_sqrOfType(test, gt.BLACK4)+test_sqrOfType(test, gt.BLACK)), test.blacks( ) )
        
        #Lit squares. As designed by the problem description, these count bulbs
        self.assertEqual(test.litsq( ), (7*7-12))
        self.assertEqual(test.posLitsq( ), (7*7-12))
        self.assertEqual( test_sqrOfType(test, gt.LIT) + test_sqrOfType(test, gt.BULB), test.litsq( ) )
        
        #Satisifiable / satisifed, aslo make sure that the internal satisfiable counter is set
        self.assertEqual(test.blacksSb( ), 5)
        self.assertEqual(test.blacksSb( ), test.blackSats)
        
        #Is satisfied
        self.assertTrue(test.isValid( ))
        
        #Integrity (square's references, counter references, etc)
        self.checkIntegrity(test)
        print("Valid!", file=rstd)
        
        
       
        
        
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
