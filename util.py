#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Utility Functions
#  This file houses most of the functions that don't belong anywhere else or are used in several classes

import random, datetime, time, configparser, fileinput, argparse, re, sys, math

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
        cfg = fcfg['log']
        self.res = open( cfg['result'], 'w' )
        self.sol = open( cfg['solution'], 'w' )
        res = self.res
        sol = self.sol
        
        res.write( ''.join(["Result Log\n", "Config File: ", cfgf, "\n"]) )
        if( fcfg['graph']['gen'] != 'True' ):
            res.write( ''.join(["Puzzle File: ", fcfg['graph']['gen'], "\n" ]) )
        else:
            res.write( ''.join(["Randomly Generating Graph(s)\n"]) )
            
        res.write( ''.join(['Seed: ', str(gseed), '\n' ]) )
        
        #Fancy git output
        if cfg['logh'] != '0':
            output = subprocess.check_output("git log -n1 --pretty=\"Git Hash: %H\n  Commit Date: %ad (%ar)\n  Author: %an <%ae>\n  Change Message: %s\"", shell=True)
            output = str( output )
            output = re.sub( r'\\n', '\n', output )
            output = re.sub( r'(b\'|\'$)', '', output )
            resLogh.write( output )
        
        #Map generation parameters
        if fcfg['graph']['gen'] == 'True':
            self.cfgStr( fcfg['graph'], res, "Map generation parameters:", ['gen'] )
        
        #Population Section
        self.cfgStr( fcfg['pop'], res, "Population Parameters:" )
            
        #General Information
        res.write( ''.join(["Overall Parameters:\n", 
            "  Runs: ", fcfg['main']['runs']]) )
        if fcfg['main']['gens'] != '0':
            res.write( ''.join (["\n  Termination criteria: ", fcfg['main']['gens'], " generations"]) )
        elif fcfg['main']['fitevals'] != '0':
            res.write( ''.join (["\n  Termination criteria: ", fcfg['main']['fitevals'], " fitness evaluations"]) )
        elif fcfg['main']['homogenity'] != '0':
            res.write( ''.join (["\n  Termination criteria: ", fcfg['main']['homogenity'], " turns without a 10^-", fcfg['main']['homoacc']," change in fitness"]) )
        
        res.write( ''.join([ "\n  ignoreblack: ", fcfg['main']['ignoreblack']]) )

        sol.write( ''.join(["Solution Log", '\n', 'Seed: ', str(gseed), '\n']) )
        
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
        self.res.write( ''.join( [ str(evals), '\t', str(round(tgen.hAverage( ), 5)), '\t', str(round(tgen.best( ).fit,5)), '\n'] ) )
        
    # Serializes and logs the soulution to solution-log.txt
    def best( self, solu ):
        self.sol.write( ''.join( [ str(solu.graph.litsq( )), '\n', solu.graph.serialize( ) ] ) )
        self.sol.flush( )
    
    # Our generational best
    def genBest( self, solu, thisgen ):
        self.res.write( ''.join([ "Generation best: \n", str(solu.graph), "Fitness: ", str(solu.fitness( )), " Birth Gen: ", str(solu.birth), "/", str(thisgen.num), "\n"]) )
        
    def newBest( self, solu ):
        self.res.write( ''.join([ "This is our new overall best!\n"]) )

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
    print(''.join(["Run #/",cfg['runs']]), end='')
    if int(cfg['runs']) < 100:
        print('\t', end='') 
    if cfg['gens'] != "0":
        print(''.join(["Gen #/", cfg['gens'], '\t', "Fit"]), end='')
    elif cfg['fitevals'] != "0":
        print(''.join(["Gen", '\t', "Fit #/", cfg['fitevals']]), end='')
    else:
        print(''.join(["Gen", '\t', "Fit"]), end='')
    print("\tAvg Fit\tStatus\t", end='' )
    if cfg['gens'] != "0" or cfg['fitevals'] != 0:
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
    def __init__( self, ind, remove=True ):
        delprn("Initilizing", 3)
        self.cumFit = 0
        self.sols = set( )
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
            thisfit = sol.fit
            for i in range(self.cumFit, self.cumFit+thisfit):
                self.line.append(sol)
            self.cumFit += thisfit
    
    #Got to get, from our line a random element, throw it into a list, remove it from our probDist,
    #  reDistribute, then grab the next, etc, then at the end throw them all back on and redistribute again
    def get( self, num ):
        rets = []
        while len(rets) < num:
            desPoint = math.floor(random.uniform(0,self.cumFit))
            rets.append(self.line[desPoint])
            if self.remove:
                self.sols.remove(self.line[desPoint])
                self.reDistribute( )
                
        if self.remove:
            for sol in rets:
                self.sols.add(sol)
            self.reDistribute( )
        
        return rets