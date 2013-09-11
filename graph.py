#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1B
#Graph Class File
#  This file houses the container for graphs in which all tiles reside.

from const import gt
from sq import sq
import util
import random, time, datetime, solve, fileinput, configparser

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
    
    # Copies another graph over to us
    def copy(self, other):
        # Same test speeds up functions that copy graphs 30 or 40 times
        #   by not copying optimized info that never changes
        same = (self.id == other.id)
        if not same:
            self.x = other.x
            self.y = other.y
            self.seed=other.seed
            self.id=other.id
            self.ignoreBlacks=other.ignoreBlacks
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
                        self.data[i][j].addLight( )    
                        
        # This shit isn't static, it always needs to be copied
        self.bad=other.bad
        self.invalid=other.invalid
        self.fit=other.fit
        self.blackSats=other.blackSats

    ######################################
    # Incrementors or Bool Changers
    ######################################
    
    # Increments our "satisfied black tiles counter"
    def incBlackSats( self ):
        self.blackSats += 1
        
    # Decrements our "satisfied black tiles counter"
    def decBlackSats( self ):
        self.blackSats -= 1
    
    # Flips us to bad when we have a bad solution, not to be confused with
    #   invalid which is for the graph (and deprecated)
    def setBad( self ):
        self.bad = True
        
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

        print( "Generating random, solveable graph: " )
        for i in range(0, self.x):
            for j in range(0, self.y):
                self.genRandBlack( self.data[i][j], bprobs )

        self.optimize( )

    # Destroys a graph, clears its cache, and reinitilizes it with unlit tiles
    #   Optimization is lost and must be done after again.
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
    
    # Clears a graph of all bulbs, quicker for graphs that don't need to be
    #   actually reinitilized as it allows optimization to stay and reuses squares.
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
        
        #FIXME: Put me in a function, baby
        sqr.newType(b)
        if sqr.type == gt.BLACK0:
            for n in sqr.neighbors:
                if not sqr.isBlack( ):
                    n.bad.add( sqr )
        sqr.black = True
    
    # Anymore, this is nothing more than a wrapper function. This is mostly
    #   deprecated as we no longer need to be careful.
    def addLight( self, sqr, careful=False ):
        #Check surrounding spots for validation
        if not self.ignoreBlacks and sqr.isBad( ):
            if careful:
                return False
            self.setBad( )
                
        return sqr.addLight( )

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
                    
    def optimize( self ):
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
    
    # Our quick and lame fitness function.
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
    
    # A wrapper to determine if we're a valid solution.
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
                
    ######################################
    # Reporters
    ######################################
    
    # Number of unlit squares
    def unLitsq( self ):
        return len(self.sqgt[gt.UNLIT])
    
    # Number of lit squares
    def litsq( self ):
        return len(self.sqgt[gt.LIT])

    # Number of possible lit squares
    # FIXME: Tauritz wants bulbs to count as lit squares
    def posLitsq( self ):
        return self.litsq( ) + self.unLitsq( )
    
    # Number of black tiles
    def blacks( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])+len(self.sqgt[gt.BLACK0])+len(self.sqgt[gt.BLACK])
    
    # Number of satisfied black tiles
    def blacksSb( self ):
        return len(self.sqgt[gt.BLACK1])+len(self.sqgt[gt.BLACK2])+len(self.sqgt[gt.BLACK3])+len(self.sqgt[gt.BLACK4])
        
    # Number of bulbs
    def lights( self ):
        return len(self.sqgt[gt.BULBS])

    ######################################
    # Logging Functions 
    ######################################
    # FIXME: This should be in util as a class

    # Logs the result to a file handle. Used for result-log.txt
    def logResult( self, i, fh ):
        fh.write( ''.join( [ str(i), '\t', str(round(self.fit, 4)), '\n'] ) )
    
    # Serializes and logs the soulution to solution-log.txt
    def logSolution( self, fh ):
        fh.write( ''.join( [ str(self.litsq( )), '\n', self.serialize( ) ] ) )
    
    # Serializes our graph into Dr. Taurtiz's format. Since we rotated 90 degrees
    #   ccw on input, we've now gotta go 90 degrees cw.
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
    
    # Wraps sq.rmLight( ) by allowing you to pass arguments
    def rmLight( self, x, y ):
        self.data[x][y].rmLight( )
    
    # Calculates fitness
    def setFitness( self ):
        self.fit = self.fitness( )
