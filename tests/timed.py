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

pr = cProfile.Profile()
pr.enable()
main.main( )
pr.disable()
s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
