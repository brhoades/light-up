#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1C
#Utility Functions
#  This file houses most of the functions that don't belong anywhere else or are used in several classes

import random, datetime, time, configparser, fileinput, argparse, re, sys, math, subprocess, shutil, os
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
        self.cfgf = cfgf
        self.rfn = cfg[ci.RESULT_LOG_FILE].rsplit('/')
        self.sfn = cfg[ci.SOLUTION_LOG_FILE].rsplit('/')
        
        self.processDirs( )
                
        self.fullRes = self.rfn
        self.fullSol = self.sfn
        
        self.res = open( self.rfn, 'w' )
        self.sol = open( self.sfn, 'w' )
        res = self.res
        sol = self.sol
        
        res.write( ''.join(["Result Log\n", "Config File: ", cfgf, "\n"]) )
        if( fcfg[ci.GRAPH][ci.GENERATE] != 'True' ):
            res.write( ''.join(["Puzzle File: ", fcfg[ci.GRAPH][ci.GENERATE], "\n" ]) )
        else:
            res.write( ''.join(["Randomly Generating Graph(s)\n"]) )
            
        res.write( ''.join(['Seed: ', str(gseed), '\n' ]) )
        
        #Fancy git output
        if cfg[ci.GIT_LOG_HEADERS] != '0':
            output = subprocess.check_output("git log -n1 --pretty=\"Git Hash: %H\n  Commit Date: %ad (%ar)\n  Author: %an <%ae>\n  Change Message: %s\"", shell=True)
            output = str( output )
            output = re.sub( r'\\n', '\n', output )
            output = re.sub( r'(b\'|\'$)', '', output )
            self.res.write( output )
        
        #Map generation parameters
        if fcfg[ci.GRAPH][ci.GENERATE] == 'True':
            self.cfgStr( fcfg[ci.GRAPH], "Map generation parameters:", [ci.GRAPH] )
            
        self.cfgStr( fcfg[ci.POP], "Population Parameters:" )
        
        self.cfgStr( fcfg[ci.INIT], "Initilization Parameters:" )
                
        self.cfgStr( fcfg[ci.PARENT_SEL], "Parent Selection Parameters:" )
                
        self.cfgStr( fcfg[ci.MUTATE], "Mutate Parameters:" )

        self.cfgStr( fcfg[ci.MAIN], "Main Parameters:" )

        #Termination Parameters
        res.write( ''.join(["Termination Parameters:"]) )
        if fcfg[ci.TERMINATION][ci.TYPE] == opp.GENERATIONAL_LIMIT:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.TERMINATION][ci.GENERATION_LIMIT], " generations"]) )
        elif fcfg[ci.TERMINATION][ci.TYPE] == opp.FITNESS_EVALUATION_LIMIT:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.TERMINATION][ci.EVALUATION_LIMIT], " fitness evaluations"]) )
        elif fcfg[ci.TERMINATION][ci.TYPE] == opp.CONVERGENCE:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[ci.TERMINATION][ci.TURNS_NO_CHANGE], " turns without a new, better, best fitness in a solution"]) )
        
        self.cfgStr( fcfg[ci.TERMINATION], "", [ci.TYPE] )
        
        sol.write( ''.join(["Solution Log", '\n', 'Seed: ', str(gseed), '\n']) )
        
    # Flushes our logs to a file
    def flush( self ):
        self.sol.flush( )
        self.res.flush( )
                
    # Prints parameters for a long config sequence, beautifully
    def cfgStr( self, cfg, title, skip=[] ):
        params = ''
        params += title
        for param in cfg:
            if param in skip:
                next
            params += ''.join(["\n  ", param, ": ", cfg[param]])
        params += '\n'
        self.res.write( params )

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
        self.res.write( ''.join([ "Bulbs: ", str(solu.graph.lights( )), " Sats Black Tiles: ", str(solu.graph.blackSats( )), "\n"]) )
        
    # Just prints this simple string to mark a new best
    def newBest( self, solu ):
        self.res.write( ''.join([ "This is our new global best!\n"]) )
    
    # Do our initial variable sub
    def processDirs( self ):
        for i in range(len(self.rfn)):
            self.rfn[i] = self.variableHand( self.rfn[i] )
        for i in range(len(self.sfn)):
            self.sfn[i] = self.variableHand( self.sfn[i] )
            
        self.createDirectories( self.rfn )
        self.createDirectories( self.sfn )
        
        self.rfn = '/'.join(self.rfn)
        self.sfn = '/'.join(self.sfn)    
        
    # Move any files with new names, organize everything properly
    def wrapUp( self, best ):
        self.res.close( )
        self.sol.close( )
        
        oldrfn = self.rfn
        oldsfn = self.sfn
        
        newrfn = self.variableHand( oldrfn, best )
        newsfn = self.variableHand( oldsfn, best )

        if newrfn != oldrfn:
            shutil.move( os.path.abspath(self.rfn), os.path.abspath(newrfn) )
            
        if newsfn != oldsfn:
            shutil.move( os.path.abspath(self.sfn), os.path.abspath(newsfn) )
            
    # Translate some variables over to something useful
    def variableHand( self, dir, best=None ):
        com = str(subprocess.check_output("git rev-parse --short HEAD", shell=True))
        com = re.sub( r'(b\'|\'$|\?|\\n)', '', com)
        dir = re.sub( r'\%cm', com, dir )
        #ccfg = re.sub( r'\.cfg', '', self.cfgf )
        #dir = re.sub( r'\%cfg', ccfg, dir )
        if best != None:
            dir = re.sub(r'\%bf', str(round(best.getFit( ),3)), dir )
        return dir
    
    # Create directories and do substutitions on variabes (currently only %c)
    def createDirectories( self, infn ):
        if len(infn) < 2:
            return
        
        fn = infn[0:len(infn)-1]
        for i in range(len(fn)):
            me = ""
            for pd in range(0,i):
                me += me.join([fn[pd], "/"])
            me += fn[i]
            
            d = os.path.abspath(me)
            if not os.path.exists(d):
                os.makedirs(d)   

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
def mutateSq( mu, sigma ):
    return( math.floor( math.fabs( random.gauss( mu, sigma ) ) ) )

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

#Find our cumulative fitness. Next compare a random number to all of our generation's fitness.
def probSel( ogen, num, prn=False ):
    gen = []
    cumfit = 0
    for solu in ogen:
        gen.append(solu)
        cumfit += solu.fit
        
    rets = []
    while len(rets) < num:
        if prn:
            delprn(''.join(perStr(len(rets)/num)), 3)
        pnt = random.randint( 0, cumfit )
        
        tfit = 0
        for sol in gen:
            if pnt < tfit:
                gen.remove(sol)
                rets.append(sol)
                cumfit -= sol.fit
                break
            tfit += sol.fit
    return rets
    