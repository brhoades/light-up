#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (gt, lprets, sym)
import fileinput

#Graph class
class graph:
    def __init__( self, conf ):
        self.data=[]

        #Have we made a bad placement?
        self.bad=False
        #Is this an invalid graph?
        self.invalid=False
        #How many lights have been placed
        self.lights=0
        #How many squares are lit
        self.litsq=0
        #Fitness
        self.fit=-1

        if conf['gen'] != 'True':
            self.readGraph(conf['gen'])
        else:
            self.genGraph(conf)    

    def readGraph( self, filename ):
        with fileinput.input(files=(filename)) as fh:
            for line in fh:
                ln = fh.filelineno()
                if ln == 1:
                    self.x=int(line)
                if ln == 2:
                    self.y=int(line)
                    self.blank()
                if ln > 2:
                    rawLine = line.split(' ')
                    #1 10 5
                    #(x) (y) (black #)
                    x = int(rawLine[0])-1
                    y = int(rawLine[1])-1
                    b = int(rawLine[2])
                    
                    oldx = x
                    x = (self.y-1)-y
                    y = oldx
                    
                    #Skip this line if it's invalid and complain
                    if x > self.x or y > self.y or x < 0 or y < 0 or b > 5 or b < 0:
                        print("Line is invalid (", (x+1), ",", (y+1), ") w/ Black of: ", b)
                        next
                    print("Transposed (", (x+1), ",", (y+1), ",", b, ") as (", x, ",", y, ", ", b+gt.TRANSFORM,")" ) 
                    self.data[x][y] = b+gt.TRANSFORM
                    
            fh.close()
        return

    def genGraph( self, conf ):
        self.x = conf['x']
        self.y = conf['y']
        self.blank()
        return
    
    def blank( self ):        
        #Initilize "blank" graph
        for i in range(0,self.x):
            self.data.append([])
            for j in range(0,self.y):
                self.data[i].append(gt.UNLIT)
        return
        
    def addLight( self, x, y, b ):
        #Add the light to the data list
        #print( "x:", x, " y:", y, " self.x: ", self.x, " self.y", y )
        self.data[x][y] = gt.BULB
        self.lights += 1
        
        #Check surrounding spots for validation
        #FIXME
        
        #Light up a line vertically and horizontally
        self.lightUpPlus( x, y, "x" )
        self.lightUpPlus( x, y, "y" )

            
    def lightUpPlus( self, x, y, axis ):
        #Light up squares on y=$x from (x,self.x]
        if axis == "x":
            for i in range(x, 0):
                if self.lightSq( i, y ) == lprets.STOPPED:
                    break
            for i in range(x, self.x):
                if self.lightSq( i, y ) == lprets.STOPPED:
                    break
        else:
            for i in range(y, 0):
                if self.lightSq( x, i ) == lprets.STOPPED:
                    break
            for i in range(y, self.y):
                if self.lightSq( x, i ) == lprets.STOPPED:
                    break

    def lightSq( self, x, y ):
        #Unlit, light
        if self.data[x][y] == gt.UNLIT:
            self.litsq += 1
            self.data[x][y] = gt.LIT 
            return lprets.LIT
        #Do nothing if lit
        if self.data[x][y] == gt.LIT:
            return lprets.YALIT
        #Bulb == invalid
        if self.data[x][y] == gt.BULB:
            self.bad= True
            return lprets.BAD
        #Black space stopped us
        if self.data[x][y] == gt.BLACK0:
            return lprets.STOPPED
    
    def drawGraph( self ):
        print("┌",end='')
        for i in range( 0, self.x):
            print("─",end='')
        print("┐") #\n
        
        for i in range(0, self.x):
            print("│",end='')
            for j in range(0, self.y):
                print(sym.tb[self.data[i][j]],end='')
            print("│")#nl
            
        print("└",end='')
        for i in range( 0, self.x):
            print("─",end='')
        print("┘") #\n
