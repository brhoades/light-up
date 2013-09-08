#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1A

from const import (gt, lprets, sym)
from copy import deepcopy
from sq import sq
from math import ceil
import random, time, datetime, solve, fileinput, configparser
import util

#Graph class
class graph:
    ######################################
    # Stock Methods
    ######################################
    def __init__( self, **args ):
        self.data=[]

        #Is this an invalid graph?
        self.invalid=False
        #Have we made a bad placement?
        self.bad=False
        #Satisfied Black Squares
        self.blackSats = 0
        #Fitness
        self.fit=-1
        
        ######################## Caches ###############################
        # Dyanmic references to all open squares bordering black tiles
        self.bbsq = set( )
        # Dynamic list of sets of references to squares of that type
        self.sqgt = []
        ###############################################################
        
        # Dimensions of the graph
        self.x = 0
        self.y = 0
        
        # Set during configuration--- do we ignore black squares?
        self.ignoreBlacks = False
        
        # Our seed, generated at initilization
        self.seed=0
                
        # Our unique id, used for comparisons between two graphs
        self.id=util.id( )
         
        conf=None

        if 'file' in args:
            config = configparser.ConfigParser()
            config.read(args['file'])
            conf=config
        
        if 'conf' in args or conf != None:
            if conf == None:
                conf=args['conf']
            if 'x' in args:
                conf['graph']['x'] = str(args['x'])
            if 'y' in args:
                conf['graph']['y'] = str(args['y'])
            if 'seed' in args:
                self.seed = args['seed']
            elif conf['graph']['seed'] == 'random':
                dt = datetime.datetime.now( )
                self.seed = util.seed( )
            else:
                self.seed = float(conf['graph']['seed'])
           
            self.ignoreBlacks = conf['solve']['ignoreblack'] == 'True'

            random.seed(self.seed)
            print( "Seeded RNG off ", self.seed )
            
            if conf['graph']['gen'] != 'True':
                self.readGraph(conf['graph']['gen'])
                print("Loaded graph from:", conf['graph']['gen'])
            else:
                self.genGraph(conf['graph'])    
                print("Randomly generated graph")
                

    def __str__(self):
        ret = ""
        ret += "┌"
        for i in range( 0, self.x):
            ret += "─"
        ret += "┐\n" #\n

        for j in range(0, self.y):
            ret += "│"
            for i in range(0, self.x):
                ret += self.data[i][j].__str__( )
            ret += "│\n"#\n
            
        ret += "└"
        for i in range( 0, self.x):
            ret += "─"
        ret +="┘\n" #\n
        
        return ret

    def copy(self, other):
        same = (self.id == other.id)
        if not same:
            self.x = other.x
            self.y = other.y
            self.seed=other.seed
            self.id=other.id
            self.ignoreBlacks=other.ignoreBlacks
            self.blank( )
            for i in range(0,self.x):
                for j in range(0,self.y):
                    self.data[i][j].copy( other.data[i][j] )
        else:
            self.clear( )
            for i in range(0,other.x):
                for j in range(0,other.y):
                    if other.data[i][j].type == gt.BULB:
                        self.data[i][j].addLight( )    
        self.bad=other.bad
        self.invalid=other.invalid
        self.fit=other.fit
        self.blackSats=other.blackSats

    ######################################
    # Incrementors or Bool Changers
    ######################################
    def incBlackSats( self ):
        self.blackSats += 1
        
    def decBlackSats( self ):
        self.blackSats -= 1
    
    def setBad( self ):
        self.bad = True
        
    def hitTopinc( self, f=False ):
        if f:
            self.hitTopLimit = (self.x*self.y) #cache
            self.hitTop = 0
        else:
            self.hitTop += 1
    
    ######################################
    ### Graph Generators
    ######################################

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
                    
                    #90 degree ccw rotation about origin
                    x = x
                    y = (self.y-1)-y
                    
                    #Skip this line if it's invalid and complain
                    if x > self.x or y > self.y or x < 0 or y < 0 or b > 5 or b < 0:
                        print("Line is invalid (", (x+1), ",", (y+1), ") w/ Black of: ", b)
                        next
                    
                    self.addBlack( self.data[x][y], b+gt.TRANSFORM )

            fh.close()
        self.optimize( )
            
    def genGraph( self, conf ):
        made = False
        self.x = int(conf['x'])
        self.y = int(conf['y'])
        bprobs = self.readBlacks( conf )
        
        print( "Generating random, solveable graph: " )
        if max(self.x, self.y) > 10:
            print( "  Due to large graph size, this may take some time" )
        
        self.blank()
        for i in range(0, self.x):
            for j in range(0, self.y):
                self.genRandBlack( self.data[i][j], bprobs )
        made = True
        self.optimize( )

    def blank( self ):        
        self.invalid=False
        self.bad=False
        self.blackSats = 0
        self.fit=-1
        self.data.clear( )
        self.bbsq.clear( )
        self.sqgt.clear( )
        
        for typ in range(0,gt.MAX):
            self.sqgt.insert(typ, set( ))
            
        for i in range(0,self.x):
            self.data.append([])
            for j in range(0,self.y):
                self.data[i].insert( j, sq( self, i, j, gt.UNLIT ) )
        
        self.procNeighbors( )
        
    def clear( self ):
        self.bad=False
        self.fit=-1
                
        if len(self.sqgt) == 0:
            raise OSError("Clear called before graph initilized.")
        
        if len(self.sqgt[gt.BULB]) == 0:
            return
        
        while len(self.sqgt[gt.BULB]) != 0:
            for sqr in self.sqgt[gt.BULB]:
                sqr.rmLight( )
                break
            
    ######################################
    ### Graph Generator Sub Functions
    ######################################
    
    def addBlack( self, sqr, b, check=False ):
        x = sqr.x
        y = sqr.y
        canLight = 0
        
        if check:
            if len(sqr.neighbors) < b-gt.TRANSFORM and b != gt.BLACK:
                return False
            for n in sqr.neighbors:
                if n.isBlack( ):
                    #If he's black0 or black he won't care
                    if n.type == gt.BLACK0 or n.type == gt.BLACK:
                        continue
                    #Check to see if we're going to make an invalid board by blocking this square
                    hisLight = 0
                    for hn in n.neighbors:
                        if hn.x != x and hn.y != y and not hn.isBlack( ):
                            hisLight += 1
                    if hisLight < n.type-gt.TRANSFORM:
                        return False
                else:
                    canLight += 1
            
            if canLight < b-gt.TRANSFORM and b != gt.BLACK and b != gt.BLACK0:
                return False                
        
        sqr.newType(b)
        if sqr.type == gt.BLACK0:
            for n in sqr.neighbors:
                if not sqr.isBlack( ):
                    n.bad.add( sqr )
        sqr.black = True
 
    def addLight( self, sqr, careful=False ):
        #Check surrounding spots for validation
        if not self.ignoreBlacks and sqr.isBad( ):
            if careful:
                return False
            self.setBad( )
                
        return sqr.addLight( )
    
    def genRandBlack( self, sqr, bprobs ):
        prob = util.chance( )
        
        random.shuffle(bprobs)
        for probs in bprobs:
            typ = probs[0]
            tprob = probs[1] 
            if prob % tprob == 0:
                if self.addBlack( sqr, typ, True ):
                    return
        
    def readBlacks( self, conf ):
        bprobs = []
        bprobs.append([gt.BLACK, int(conf['black'])])
        bprobs.append([gt.BLACK1, int(conf['black1'])])
        bprobs.append([gt.BLACK2, int(conf['black2'])])
        bprobs.append([gt.BLACK3, int(conf['black3'])])
        bprobs.append([gt.BLACK4, int(conf['black4'])])
        bprobs.append([gt.BLACK0, int(conf['black0'])])
        return bprobs
        
    def procNeighbors( self ):
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                sqr = self.data[i][j]
                x = sqr.x
                y = sqr.y
                if x > 0:
                    sqr.addNeighbor( self.data[x-1][y] )
                if x < self.x-1:
                    sqr.addNeighbor( self.data[x+1][y] )
                if y > 0:
                    sqr.addNeighbor( self.data[x][y-1] )
                if y < self.y-1:
                    sqr.addNeighbor( self.data[x][y+1] )
                    
    def optimize( self ):
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                sqr = self.data[i][j]
                x = sqr.x
                y = sqr.y
                
                # Add us to the appropriate counter
                self.sqgt[sqr.type].add( sqr )
                
                ################    UNLIT SQUARES   ################
                # For unlit squares we are going to store where they would "shine" instead of doing this
                #   on the fly. We are also going to store references to neighbors here of any type.
                if sqr.type == gt.UNLIT:
                    # Run lines down y=sqr.x, y=-sqr.x, x=sqr.y, x=-sqr.y from our location and add these.
                    #   If a bulb is placed, it'll light these squares.
                    if x > 0:
                        for k in range(x-1, -1, -1):
                            tsqr = self.data[k][y]
                            if tsqr.isBlack( ):
                                break
                            sqr.shine.add( tsqr )
                    if x < self.x-1:
                        for k in range(x+1, self.x ):
                            tsqr = self.data[k][y]
                            if tsqr.isBlack( ):
                                break
                            sqr.shine.add( tsqr )
                    if y > 0:
                        for k in range(y-1, -1, -1):
                            tsqr = self.data[x][k]
                            if tsqr.isBlack( ):
                                break
                            sqr.shine.add( tsqr )
                    if y < self.y-1:
                        for k in range(y+1, self.y):
                            tsqr = self.data[x][k]
                            if tsqr.isBlack( ):
                                break
                            sqr.shine.add( tsqr )
                    for tsqr in sqr.neighbors:
                        if tsqr.type == gt.BLACK0:
                            sqr.bad.add( tsqr ) 
                    
    ######################################
    # Checkers or Reporters
    ######################################

    def fitness( self ):
        fit = 0
        if self.bad:
            return fit
            
        # ( num of lit tiles / num of possible lit tiles )
        fit = self.litsq( )  / self.posLitsq( )
        # * ( num of satisfied black squares / number of (satisifiable) black squares )
        if not self.ignoreBlacks:
            fit *= self.blackSats / self.blacksSb( )
        return fit

    def isValid( self ):
        if not self.ignoreBlacks and self.blackSats < self.blacksSb( ):
            return False
        return True

    def hasNeighbor( self, sqr, type=gt.NOTHING ):
        n = []
        x = sqr.x
        y = sqr.y
        for sq in sqr.neighbors:
            if sq.type == type or type == gt.NOTHING:
                return True
        return False
                
    def unLitsq( self ):
        return len(self.sqgt[gt.UNLIT])

    def litsq( self ):
        return len(self.sqgt[gt.LIT])

    def posLitsq( self ):
        return self.litsq( ) + self.unLitsq( )
        
    def blacks( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])+len(self.sqgt[gt.BLACK0])+len(self.sqgt[gt.BLACK])
        
    def blacksSb( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])
        
    def lights( self ):
        return len(self.sqgt[gt.BULBS])

    def logResult( self, i, fh ):
        fh.write( ''.join( [ str(i), '\t', str(round(self.fit, 4)), '\n'] ) )
        
    def logSolution( self, fh ):
        fh.write( ''.join( [ str(self.litsq( )), '\n', self.serialize( ) ] ) )
    
    def serialize( self ):
        ret = ""
        for i in range(0,self.x):
            for j in range(0,self.y):
                if self.data[i][j].type == gt.BULB:
                    #90 degree cw rotation about origin
                    ni = i
                    nj = (self.y-1)-j                
                    ret += ''.join([str(ni+1), " ", str(nj+1), '\n'])
        return ret

    ######################################
    # Wrapper Functions
    ######################################
        
    def rmLight( self, x, y ):
        self.data[x][y].rmLight( )
        
    def setFitness( self ):
        self.fit = self.fitness( )
