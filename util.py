#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Utility Functions
#  This file houses most of the functions that don't belong anywhere else or are used in several classes

import random, datetime, time, configparser, fileinput, argparse, re, sys, math
from const import gt, ci, opp

######################################
# RNG-related functions
######################################

# Generates a random (!= 0) id for a graph.
def id( ):
    start = seed( )
    start *= 1+random.random( )
    return start

# Generates a seed for the rng.
def seed( ):
    dt = datetime.datetime.now( )
    return time.mktime(dt.timetuple())+float("0.%s"%dt.microsecond)

# "Roll" a 100 sided die and compares it to chance%.
def roll( chance ):
    if( random.uniform(0, 100) <= chance*100 ):
        return True
        
    return False
# "Flip" a coin uniformly. Since Python's random is uniform this works.
def flip( ):
    prob = random.uniform(0, 1)
    return prob >= 0.5 #in [a,b], b is often not included due to floating point rounding, so >=

# Returns a chance between 1 - 1M
def chance( ):
    return random.randint( 1, 1000000 )

######################################
# Config-parsing functions / logging functions
######################################
# Reads in a config from a file handle and returns a dictionary.
def readConfig( fn ):
    config = configparser.ConfigParser()
    config.read(fn)
    return config._sections

# Called before readConfig to parse command line options or return the default.
def gcfg( ):
    parser = argparse.ArgumentParser(description='CS348 FS2013 Assignment 1a')
    parser.add_argument('-c', type=str,
                        help='Specifies a configuration file (default: cfgs/default.cfg)',
    default="cfgs/default.cfg")
    
    args = parser.parse_args()
    return args.c

class log:        
    def __init__( self, fcfg, gseed, cfgf):
        cfg = fcfg[ci.LOG]
        self.res = open( cfg[ci.RESULT_LOG_FILE], 'w' )
        self.sol = open( cfg[ci.SOLUTION_LOG_FILE], 'w' )
        res = self.res
        sol = self.sol
        
        #FIXME: ALL THIS BORKED
        #res.write( ''.join(["Result Log\n", "Config File: ", cfgf, "\n"]) )
        #if( fcfg['graph']['gen'] != 'True' ):
            #res.write( ''.join(["Puzzle File: ", fcfg['graph']['gen'], "\n" ]) )
        #else:
            #res.write( ''.join(["Randomly Generating Graph(s)\n"]) )
            
        #res.write( ''.join(['Seed: ', str(gseed), '\n' ]) )
        
        ##Fancy git output
        #if cfg['logh'] != '0':
            #output = subprocess.check_output("git log -n1 --pretty=\"Git Hash: %H\n  Commit Date: %ad (%ar)\n  Author: %an <%ae>\n  Change Message: %s\"", shell=True)
            #output = str( output )
            #output = re.sub( r'\\n', '\n', output )
            #output = re.sub( r'(b\'|\'$)', '', output )
            #resLogh.write( output )
        
        ##Map generation parameters
        #if fcfg['graph']['gen'] == 'True':
            #self.cfgStr( fcfg['graph'], res, "Map generation parameters:", ['gen'] )
        
        ##Population Section
        #self.cfgStr( fcfg['pop'], res, "Population Parameters:" )
            
        ##General Information
        #res.write( ''.join(["Overall Parameters:\n", 
            #"  Runs: ", fcfg[ci.MAIN]['runs']]) )
        #if fcfg[ci.MAIN]['gens'] != '0':
            #res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.MAIN]['gens'], " generations"]) )
        #elif fcfg[ci.MAIN]['fitevals'] != '0':
            #res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.MAIN]['fitevals'], " fitness evaluations"]) )
        #elif fcfg[ci.MAIN]['homogenity'] != '0':
            #res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.MAIN]['homogenity'], " turns without a new, better, best fitness in a solution"]) )
        
        #res.write( ''.join([ "\n  ignoreblack: ", fcfg[ci.MAIN]['ignoreblack']]) )

        #sol.write( ''.join(["Solution Log", '\n', 'Seed: ', str(gseed), '\n']) )
        
    def flush( self ):
        self.sol.flush( )
        self.res.flush( )
        
    def cfgStr( self, cfg, log, title, skip=[] ):
        params = ''
        params += title
        for param in cfg:
            if param in skip:
                next
            params += ''.join(["\n  ", param, ": ", cfg[param]])
        params += '\n'
        log.write( params )

    # Seperates our result log file with pretty run numbers.
    def sep( self, run ):
        self.res.flush( )
        self.res.write( ''.join( [ "\n", "Run ", str(run+1), "\n" ] ) )
    
    # Logs the result to a file handle. Used for result-log.txt
    def gen( self, tgen, evals=0 ):
        if evals == 0:
            evals = tgen.fitEvals
        else:
            evals = tgen.mu
        self.res.write( ''.join( [ str(evals), '\t', str(round(tgen.hAverage( ), 5)), '\t', str(round(tgen.best( ).getFit(),5)), '\n'] ) )
        
    # Serializes and logs the soulution to solution-log.txt
    def best( self, solu ):
        self.sol.write( ''.join( [ str(solu.graph.litsq( )), '\n', solu.graph.serialize( ) ] ) )
        self.sol.flush( )
    
    # Our generational best
    def genBest( self, solu, thisgen ):
        self.res.write( ''.join([ "Run best: \n", str(solu.graph), "Fitness: ", str(solu.getFit( )), " (", str(solu.fit),
                                 "/", str(thisgen.fitDenom), ") ", " Birth Gen: ", str(solu.birth), "/", str(thisgen.num), "\n"]) )
        self.res.write( ''.join([ "Bulbs: ", str(solu.graph.lights( )), " Satisified Black Tiles: ", str(solu.graph.blackSats( )), "\n"]) )
        
    def newBest( self, solu ):
        self.res.write( ''.join([ "This is our new global best!\n"]) )

    def finish( self ):
        self.res.close( )
        self.sol.close( )

######################################
# Miscellaneous functions
######################################

# Returns the maximum nuber of lights for this given square. Returns bad
#   stuff on gt.BLACK
def maxLights( btype ):
    return btype-gt.TRANSFORM

# Backspaces over previous stuff and padds the end of our line to cover it up
def delprn( new, level=2, overwrite=True ):
    if not hasattr(delprn, "old"):
         delprn.old = []
         for i in range(0,5):
            delprn.old.append("")
    if new == delprn.old[level]:
        return
        
    cnt = 0
    for i in range(level, len(delprn.old)):
        cnt += len(delprn.old[i])
        delprn.old[i] = ""
    print('\r', end='')
    sys.stdout.write("\033[K")
    for i in range(0, level):
        print(delprn.old[i], end='')
    print(new, end='')
    sys.stdout.flush( )
    delprn.old[level] = new
    
# Rounds a number off and gives a string
def perStr( dec, ceil=True, round=True ):
    rnd = 100
    if not round:
        rnd = 1
    if ceil:
        return str(math.ceil(dec*rnd))
    else:
        return str(math.floor(dec*rnd))

# Mutates a square if this returns >= 1  
def mutateSq( prob ):
    return math.floor(random.paretovariate(prob) - 1)

# Renders a header depending on options
def renderHead( cfg ):
    print(''.join(["Run #/",cfg[ci.MAIN][ci.TOTAL_RUNS]]), end='')
    if int(cfg[ci.MAIN][ci.TOTAL_RUNS]) < 100:
        print('\t', end='') 
    if cfg[ci.TERMINATION][ci.TYPE] == opp.GENERATIONAL_LIMIT:
        print(''.join(["Gen #/", cfg[ci.TERMINATION][ci.GENERATION_LIMIT], '\t', "Fit"]), end='')
    elif cfg[ci.TERMINATION][ci.TYPE] == opp.FITNESS_EVALUATION_LIMIT:
        print(''.join(["Gen", '\t', "Fit #/", cfg[ci.TERMINATION][ci.EVALUATION_LIMIT]]), end='')
    else:
        print(''.join(["Gen", '\t', "Fit"]), end='')
    print("\tAvg Fit\tStatus\t", end='' )
    if cfg[ci.TERMINATION][ci.TYPE] == opp.GENERATIONAL_LIMIT or \
            cfg[ci.TERMINATION][ci.TYPE] == opp.FITNESS_EVALUATION_LIMIT:
        print("\t", end='')
    print("\tStatus %")
    
def pad(num, pad):
    if pad == '0':
        return str(num)
    inum = str(num)
    return inum.rjust(math.floor(math.log(int(pad), 10)+1), '0')

# Distribution of probabilities. Uses arrays to simulate a number line, where we then
#   play something like roulette. If an element is removed we have to rebuild this.
class probDist:
    def __init__( self, ind, remove=True, prn=False ):
        delprn("Initilizing", 3)
        self.cumFit = 0
        self.prn = prn
        self.sols = ind.copy( )
        self.remove = remove
        self.line = []
        self.lookup = []
        
        self.reDistribute( )
    
    #What we're going to do is create a cumulative fitness and add points on the line along the way.
    # Pretty simple, just adding an index as we scoot alone and append references to ourself
    def reDistribute( self ):
        self.cumFit = 0
        self.line = []
        
        for sol in self.sols:
            self.line.append([self.cumFit, sol])
            if sol.fit > 0:
                self.cumFit += sol.fit

    def rm( self, strt ):
        amt = self.line[strt][1].fit
        self.line.remove(self.line[strt])
        for i in range(strt,len(self.line)):
            self.line[i][0] -= amt
        self.cumFit -= amt
    
    #Got to get, from our line a random element, throw it into a list, remove it from our probDist,
    #  reDistribute, then grab the next, etc, then at the end throw them all back on and redistribute again
    def get( self, num ):
        rets = []
        while len(rets) < num:
            if self.prn:
                delprn(''.join(perStr(len(rets)/num)), 3)
            pnt = random.randint( 0, self.cumFit )
            #print("NEW")
            i = self.binSearch( pnt, 0, len(self.line)-1 )
            #print(i,"!")
            sol = self.line[i][1]
            if not self.remove:
                if sol in rets:
                    continue
                else:
                    rets.append(sol)
            else:
                rets.append(sol)
                self.rm(i)
        
        if self.remove:
            for sol in rets:
                if not sol in self.sols:
                    self.sols.add(sol)
            self.reDistribute( )
        return rets
    
    #points [0, @sol.fit=2], [2, @sol.fit=6], [8, @sol.fit=3], [11, @sol.fit=4]
    #[0, 2), [2, 8), [8, 11), [11, 15]
    #Their respective ranges are below. If a point falls on that range, they get
    #  chosen.
    def binSearch( self, i, imin, imax ):
        mp = math.floor((imin+imax)/2)
        #print( mp, "[", imin, ",", imax, "]" )
        thispoint = self.line[mp]

        if mp == imax and mp == imin:
            return mp
            
        if i > self.line[mp][0]:
            return self.binSearch( i, mp+1, imax )
        elif i < self.line[mp][0]:
            if mp == 0:
                return mp
            if i > self.line[mp-1][0]:
                return mp-1
            else:
                return self.binSearch( i, imin, mp-1 )
        else:
            if mp < len(self.line):
                return mp+1
            else:
                return mp