#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Graph Class File
#  This file houses the container for graphs in which all tiles reside.

from const import gt
from sq import sq
import util
import random, time, datetime, fileinput, configparser

class graph:
    ######################################
    # Stock Methods
    ######################################
    def __init__( self, **args ):
        self.data=[]

        #Is this an invalid graph?
        self.invalid=False
        
        #Possible squares to light
        self.possq = 0
        
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
                
        # Our unique id, used for comparisons between two graphs
        self.id=util.id( )
         
        conf=None

        # Custom file loading argument, used for testing
        if 'file' in args:
            config = configparser.ConfigParser()
            config.read(args['file'])
            conf=config
        
        # Used for when conf is passed in or to string along the above
        if 'conf' in args or conf != None:
            if conf == None:
                conf=args['conf']
            if 'x' in args:
                conf['graph']['x'] = str(args['x'])
            if 'y' in args:
                conf['graph']['y'] = str(args['y'])
           
            self.ignoreBlacks = conf['main']['ignoreblack'] == 'True'
            
            if conf['graph']['gen'] != 'True':
                self.readGraph(conf['graph']['gen'])
                if not 'quiet' in args:
                    print("Loaded graph from:", conf['graph']['gen'])
            else:
                self.genGraph(conf['graph'])    
                if not 'quiet' in args:
                    print("Randomly generated graph: ")
                    print( self )
    # Fancily prints us out in a bordered graph when print(graph)
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
    
    # Remove references recursively so the garbage collector will take care of the rest
    def delete( self ):
        for i in range(0,len(self.data)):
            for j in range(0,len(self.data[i])):
                self.data[i][j].delete( )
        self.data = []
        self.bbsq = []
        self.sqgt = []
    
    # Copies another graph over to us
    def copy(self, other):
        # Same test speeds up functions that copy graphs 30 or 40 times
        #   by not copying optimized info that never changes
        same = (self.id == other.id)
        if not same:
            self.x = other.x
            self.y = other.y
            self.id=other.id
            self.ignoreBlacks=other.ignoreBlacks
            self.possq = other.possq
            self.blank( )
            # Calls copy function per square
            for i in range(0,self.x):
                for j in range(0,self.y):
                    self.data[i][j].copy( other.data[i][j] )
        else:
            # If the graphs are known to be the same we just remove anything
            #   that's not a black tile and then add bulbs. Drastically faster
            #   than the constant calling.
            self.clear( )
            for i in range(0,other.x):
                for j in range(0,other.y):
                    if other.data[i][j].type == gt.BULB:
                        self.addLight( i, j )    
                        
        # This shit isn't static, it always needs to be copied
        self.invalid=other.invalid
        self.fit=other.fit
        
    ######################################
    ### Graph Generators
    ######################################

    # This reads in Tauritz's funny-ass graph format, and beats it into submission,
    #  and, subsequently, creates a graph from it.
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
    
    # Generates a random and inherently valid graph by checking neighbors
    def genGraph( self, conf ):
        self.x = int(conf['x'])
        self.y = int(conf['y'])
        bprobs = self.readBlacks( conf )
        self.blank()

        for i in range(0, self.x):
            for j in range(0, self.y):
                self.genRandBlack( self.data[i][j], bprobs )

        self.optimize( )

    # Destroys a graph, clears its cache, and reinitilizes it with unlit tiles
    #   Optimization is lost and must be done after again.
    def blank( self ):        
        self.invalid=False
        self.fit=-1
        self.delete( )
        
        for typ in range(0,gt.MAX):
            self.sqgt.insert(typ, set( ))
            
        for i in range(0,self.x):
            self.data.append([])
            for j in range(0,self.y):
                self.data[i].insert( j, sq( self, i, j, gt.UNLIT ) )
        
        self.procNeighbors( )
    
    # Clears a graph of all bulbs, quicker for graphs that don't need to be
    #   actually reinitilized as it allows optimization to stay and reuses squares.
    def clear( self ):
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
    
    # A much improved addBlack function. This is used by all graph
    #   generators in order to properly place black tiles and mark 
    #   a graph as invalid if an improper black tile is actually placed.
    # Magic happens here as we never make an invalid placement if check
    #   is true. This is the brains of the graph generator.
    def addBlack( self, sqr, b, check=False ):
        x = sqr.x
        y = sqr.y
        canLight = 0
        
        if check:
            #Black (no req) tiles, due to constant schemes put in place by Dr. Tauritz,
            # appear to need 5 tiles around them. This is a caveat for those
            # and a quick return false for anything that needs more than what's available.
            if len(sqr.neighbors) < b-gt.TRANSFORM and b != gt.BLACK:
                return False
            #We're looking at all of our neighbors that are black tiles
            for n in sqr.neighbors:
                if n.isBlack( ):
                    #If it's black0 or black it won't care
                    if n.type == gt.BLACK0 or n.type == gt.BLACK:
                        continue
                    #Check to see if we're going to make an invalid board by blocking this square
                    # We're essentially checking to see if he can be satisifed here.
                    hisLight = 0
                    for hn in n.neighbors:
                        if hn.x != x and hn.y != y and not hn.isBlack( ):
                            hisLight += 1
                    if hisLight < n.type-gt.TRANSFORM:
                        return False
                else:
                    canLight += 1
            
            #If we can't light more than our requirement and we aren't a nonrequiring black 
            # tile or 0 (no bulbs down at graph gen so who cares) then return false.
            if canLight < b-gt.TRANSFORM and b != gt.BLACK and b != gt.BLACK0:
                return False                
        
        #FIXME: Put me in a function
        sqr.newType(b)
        if sqr.type == gt.BLACK0:
            for n in sqr.neighbors:
                if not sqr.isBlack( ):
                    n.bad.add( sqr )
        sqr.black = True
    
    # Anymore, this is nothing more than a wrapper function. This is mostly
    #   deprecated as we no longer need to be careful.
    def addLight( self, x, y, careful=False ):
        #Check surrounding spots for validation
        if not self.ignoreBlacks and self.data[x][y].isBad( ) and careful:
            return False
        elif self.data[x][y].type != gt.UNLIT and careful:
            return False
                
        return self.data[x][y].addLight( )

    # This function reads in black tile probabilities from our .cfg
    #   for later use by genRandomBlack
    def readBlacks( self, conf ):
        bprobs = []
        bprobs.append([gt.BLACK, int(conf['black'])])
        bprobs.append([gt.BLACK1, int(conf['black1'])])
        bprobs.append([gt.BLACK2, int(conf['black2'])])
        bprobs.append([gt.BLACK3, int(conf['black3'])])
        bprobs.append([gt.BLACK4, int(conf['black4'])])
        bprobs.append([gt.BLACK0, int(conf['black0'])])
        return bprobs
    
    # This gerates a random black tile by looping through a list of lists
    #   prepared by readBlacks. Each second argument is the 1 in # prob
    #   supporting up to 1M.
    def genRandBlack( self, sqr, bprobs ):
        prob = util.chance( )
        
        #If we don't shuffle here we're predisposed to get the ones at the
        #  top more often because of the ordered list.
        random.shuffle(bprobs)
        for probs in bprobs:
            typ = probs[0]
            tprob = probs[1] 
            #We're doing # % # == 0 here so we don't get 1-n/n and get 1/n...
            #   It'll make sense, think about it.
            if prob % tprob == 0:
                if self.addBlack( sqr, typ, True ):
                    return
    
    #Process Neighbors function. This is called at opimization 
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
    
    # This function later pays itself off lightsPlaced/"self.unLitsq( )"-fold by automatically
    #   storing the squares to light up instead of constantly searching every time we place
    def optimize( self ):
        # Set our possible # of lit squares
        self.possq = self.litsq( ) + self.unLitsq( ) + self.lights( )
        
        for i in range( 0, self.x ):
            for j in range( 0, self.y ):
                sqr = self.data[i][j]
                x = sqr.x
                y = sqr.y
                
                # Add us to the appropriate counter, for all square types
                self.sqgt[sqr.type].add( sqr )
                
                # For unlit squares we are going to store where they would "shine" 
                #   instead of doing this on the fly.
                if sqr.type == gt.UNLIT:
                    # Run lines down y=sqr.x, y=-sqr.x, x=sqr.y, x=-sqr.y from our location and add these.
                    #   If a bulb is placed, it'll light these squares.
                    if x > 0:
                        for k in range(x-1, -1, -1):
                            tsqr = self.data[k][y]
                            # Black tiles block lights, so we finish here
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
                            
                    #A quick and nasty caveat for black tiles that require 0.
                    for tsqr in sqr.neighbors:
                        if tsqr.type == gt.BLACK0:
                            sqr.bad.add( tsqr ) 
                    
    ######################################
    # Checkers
    ######################################
    
    # A wrapper to determine if we're a valid solution.
    def isValid( self ):
        if not self.ignoreBlacks and self.blackSats( ) < self.blacksSb( ):
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
                
    ######################################
    # Reporters
    ######################################
    
    # Number of unlit squares
    def unLitsq( self ):
        return len(self.sqgt[gt.UNLIT])
    
    # Number of lit squares
    def litsq( self ):
        return len(self.sqgt[gt.LIT]) + len(self.sqgt[gt.BULB])

    # Number of possible lit squares
    def posLitsq( self ):
        return self.possq
    
    # Number of black tiles
    def blacks( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])+len(self.sqgt[gt.BLACK0])+len(self.sqgt[gt.BLACK])
    
    # Number of satisfiable black tiles
    #   We count zero as being satisifiable since 1C as it can now be unsatisfied (bulbs around it)
    def blacksSb( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])+len(self.sqgt[gt.BLACK0])
        
    # Number of bulbs
    def lights( self ):
        return len(self.sqgt[gt.BULB])
    
    # Number of satisfied black tiles
    def blackSats( self ):
        sat = 0
        for sqr in self.sqgt[gt.TRANSFORM]:
            if sqr.type == gt.BLACK:
                continue
            if util.maxLights(sqr.type) == len(sqr.lights):
                sat += 1
                
        return sat 
            
    ######################################
    # Loggers
    ######################################
    
    # Serializes our graph into Dr. Taurtiz's format. Since we rotated 90 degrees
    #   ccw on input, we've now gotta go 90 degrees cw.
    def serialize( self ):
        ret = ""
        for sqr in self.sqgt[gt.BULB]:
            #90 degree cw rotation about origin
            ni = sqr.x
            nj = (self.y-1)-sqr.y               
            ret += ''.join([str(ni+1), " ", str(nj+1), '\n'])
        return ret

    ######################################
    # Wrapper Functions
    ######################################
    
    # Wraps sq.rmLight( ) by allowing you to pass coordinates
    def rmLight( self, x, y ):
        self.data[x][y].rmLight( )
