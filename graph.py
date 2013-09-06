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
        for typ in range(0, gt.lookup[len(gt.lookup)-1]+1):
            self.sqgt.append([])
            self.sqgt[typ] = set( )
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
                self.seed = time.mktime(dt.timetuple())+float("0.%s"%dt.microsecond)
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
            self.bbsq = []
            self.data = []
            self.blank( )
            for [x,y] in other.bbsq:
                self.bbsq.append([x,y])

        for i in range(0,other.x):
            for j in range(0,other.y):
                self.data[i][j].copy(other.data[i][j], same)

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
    # Graph Modifiers
    ######################################
    
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
                    
                    #print("Transposed (", (x+1), ",", (y+1), ",", b, ") as (", x, ",", y, ", ", b+gt.TRANSFORM,")" ) 
                    self.addBlack( x, y, b )

            fh.close()
            
    def genGraph( self, conf ):
        made = False
        self.x = int(conf['x'])
        self.y = int(conf['y'])
        
        print( "Generating random, solveable graph: " )
        if max(self.x, self.y) > 10:
            print( "  Due to large graph size, this may take some time" )
        
        timeout = 1
        if conf['timeout'] == "auto":
                #long enough to solve a hard graph but
                #not too short to kill the hard ones
                timeout = ceil(max(self.x, self.y)/2)
        else:
            timeout = int( conf['timeout'] )
        
        while made == False or solve.ideal( self, timeout ) == False:
            self.blank()
            for i in range(0, self.x):
                if self.genCoinFlip( float(conf['noblackx']) ):
                    next
                for j in range(0, self.y):
                    if self.genCoinFlip( float(conf['placeblack']) ):
                        self.genRandBlack( i, j, float(conf['blackmod']) )
            made = True

    def blank( self ):        
        self.invalid=False
        self.bad=False
        self.blackSats = 0
        self.fit=0
        self.solu=None
        del self.bbsq
        self.bbsq = []

        if len(self.data) != 0:
            del self.data
            self.data = []
        for i in range(0,self.x):
            self.data.append([])
            for j in range(0,self.y):
                self.data[i].append( sq( self, i, j, gt.UNLIT ) )
        return

    ######################################
    ### Graph Generator Sub Functions
    ######################################
    
    def addBlack( self, x, y, b ):
        self.data[x][y] = sq( self, x, y, b+gt.TRANSFORM )
        ourType = b+gt.TRANSFORM
        if x > 0:
            self.data[x-1][y].blackN.add( self.data[x][y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x-1, y] in self.bbsq ):
                self.bbsq.append( [x-1, y] )
            if ourType == gt.BLACK0:
                self.data[x-1][y].bad = True
        if x < self.x-1:
            self.data[x+1][y].blackN.add( self.data[x][y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x+1, y] in self.bbsq ):
                self.bbsq.append( [x+1, y] )
            if ourType == gt.BLACK0:
                self.data[x+1][y].bad = True                    
        if y > 0:
            self.data[x][y-1].blackN.add( self.data[x][y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x, y-1] in self.bbsq ):
                self.bbsq.append( [x, y-1] )
            if ourType == gt.BLACK0:
                self.data[x][y-1].bad = True
        if y < self.y-1:
            self.data[x][y+1].blackN.add( self.data[x][y] )
            if not( ourType == gt.BLACK0 or ourType == gt.BLACK ) \
                and not( [x, y+1] in self.bbsq ):
                self.bbsq.append( [x, y+1] )
            if ourType == gt.BLACK0:
                self.data[x][y+1].bad = True

    def addLight( self, x, y, careful=False ):
        #Check surrounding spots for validation
        if self.badBulbSpot( x, y ):
            if careful:
                return False
            self.setBad( )
                
        self.data[x][y].type = gt.BULB
        
        self.data[x][y].addNeighbors( self )
        
        #Light up a line vertically and horizontally
        self.lightUpPlus( x, y )

        return True
        
    def lightUpPlus( self, x, y ):
        if x > 0:
            for i in range(x-1, -1, -1):
                ret = self.data[i][y].light( self.data[x][y] )
                if ret == lprets.STOPPED:
                    break
        if x < self.x-1:
            for i in range(x+1, self.x ):
                ret = self.data[i][y].light( self.data[x][y] )
                if ret == lprets.STOPPED:
                    break
        if y > 0:
            for i in range(y-1, -1, -1):
                ret = self.data[x][i].light( self.data[x][y] )
                if ret == lprets.STOPPED:
                    break
        if y < self.y-1:
            for i in range(y+1, self.y):
                ret = self.data[x][i].light( self.data[x][y] )
                if ret == lprets.STOPPED:
                    break
        return lprets.LIT

    
    def genRandBlack( self, x, y, bprob ):
        if self.hasNeighbor( x, y, gt.BLACK4 ):
            return
            
        #weighted towards non-requring blacks
        if self.genCoinFlip( bprob/1.5 ):
            self.addBlack( x, y, gt.BLACK-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/1.75 ):
            self.addBlack( x, y, gt.BLACK1-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2 ):
            self.addBlack( x, y, gt.BLACK2-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2.25 ):
            if ( x == 0 or y == 0 ) and ( x == self.x-1 or y == self.y-1 ):
                self.genRandBlack( x, y, bprob )
            self.addBlack( x, y, gt.BLACK3-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2 ):   #Hard to place, higher,chance
            if x == self.x-1 or x == 0 or y == self.y-1 or y == 0 or \
                ( x > 0 and self.data[x-1][y].type != gt.UNLIT ) or \
                ( y > 0 and self.data[x][y-1].type != gt.UNLIT ) or \
                ( y < self.y and self.data[x][y+1].type != gt.UNLIT ) or \
                ( x < self.x and self.data[x+1][y].type != gt.UNLIT ):
                self.genRandBlack( x, y, bprob )
                return
                
            self.addBlack( x, y, gt.BLACK4-gt.TRANSFORM )
        elif self.genCoinFlip( bprob/2.75 ):
            if( x > 0 and self.data[x-1][y].type == gt.BLACK4 ) or \
                ( y > 0 and self.data[x][y-1].type == gt.BLACK4 ):
                self.genRandBlack( x, y, bprob )
                return
            
            self.addBlack( x, y, gt.BLACK0-gt.TRANSFORM )
        else:
            self.genRandBlack( x, y, bprob )

    def genCoinFlip( self, prob ):
        if prob*100 >= random.randint( 0, 100 ):
            return True
        return False

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
            
    def hitTopLim( self ):
        return ( self.hitTop > self.hitTopLimit )
    
    def hasNeighbor( self, x, y, type=gt.NOTHING ):
        n = []
        if x < self.x-1 and self.data[x+1][y].type != gt.UNLIT:
            n.append( self.data[x+1][y].type )
        if x > 0 and self.data[x-1][y].type != gt.UNLIT:
            n.append( self.data[x-1][y].type )
        if y < self.y-1 and self.data[x][y+1].type != gt.UNLIT:
            n.append( self.data[x][y+1].type )
        if y > 0 and self.data[x][y-1].type != gt.UNLIT:
            n.append( self.data[x][y-1].type )
        
        for t in n:
            if t == type or type == gt.NOTHING:
                return True
        return False
        
    
    def badBulbSpot( self, x, y ):
        if self.data[x][y].type != gt.UNLIT:
            return True
        if self.fullNeighbors( x, y ) and not self.ignoreBlacks:
            return True
    
    def fullNeighbors( self, x, y ):
        if len(self.data[x][y].blackN) == 0:
            return False
        
        for sqr in self.data[x][y].blackN:
            if sqr.atCapacity( ):
                return True
                
    def unLitsq( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.UNLIT:
                    count += 1
        return count
        
    def posLitsq( self ):
        return self.litsq( ) + self.unLitsq( )
        
    def litsq( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.LIT:
                    count += 1
        return count
        
    def blacks( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type > gt.BLACK_THRESHOLD:
                    count += 1
        return count
        
    def blacksSb( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                mytype = self.data[i][j].type
                if mytype >= gt.BLACK1 and mytype <= gt.BLACK4:
                    count += 1
        return count
        
    def lights( self ):
        count = 0
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                if self.data[i][j].type == gt.BULB:
                    count += 1
        return count

    #Bordered by a black cell that isn't full
    def bbRange( self ):
        ret = []
        for [i, j] in self.bbsq:
            for sqr in self.data[i][j].blackN:
                if not sqr.atCapacity( ) and \
                    not( [i, j] in ret ):
                    ret.append( [i, j] )
        return ret

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
        return
        
    def setFitness( self ):
        self.fit = self.fitness( )
