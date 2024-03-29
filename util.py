#!/usr/bin/env python
#Author: Billy J Rhoades <bjrq48@mst.edu>
#Class: CS348 Assignment 1D
#Utility Functions
#  This file houses most of the functions that don't belong anywhere else or are used in several classes

import random, datetime, time, configparser, fileinput, argparse, re, sys, math, subprocess, shutil, os
from const import *

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
        cfg = fcfg[LOG]
        self.cfgf = cfgf
        self.rfn = cfg[RESULT_LOG_FILE].rsplit('/')
        self.sfn = cfg[SOLUTION_LOG_FILE].rsplit('/')
        
        self.processDirs( )
                
        self.fullRes = self.rfn
        self.fullSol = self.sfn
        
        self.res = open( self.rfn, 'w' )
        self.sol = open( self.sfn, 'w' )
        res = self.res
        sol = self.sol
        
        res.write( ''.join(["Result Log\n", "Config File: ", cfgf, "\n"]) )
        if( fcfg[GRAPH][GENERATE] != 'True' ):
            res.write( ''.join(["Puzzle File: ", fcfg[GRAPH][GENERATE], "\n" ]) )
        else:
            res.write( ''.join(["Randomly Generating Graph(s)\n"]) )
            
        res.write( ''.join(['Seed: ', str(gseed), '\n' ]) )
        
        #Fancy git output
        if cfg[GIT_LOG_HEADERS] != '0':
            output = subprocess.check_output("git log -n1 --pretty=\"Git Hash: %H\n  Commit Date: %ad (%ar)\n  Author: %an <%ae>\n  Change Message: %s\"", shell=True)
            output = str( output )
            output = re.sub( r'\\n', '\n', output )
            output = re.sub( r'(b\'|\'$)', '', output )
            self.res.write( output )
        
        #Map generation parameters
        if fcfg[GRAPH][GENERATE] == 'True':
            self.cfgStr( fcfg[GRAPH], "Map generation parameters:", [GRAPH] )
            
        self.cfgStr( fcfg[POP], "Population Parameters:" )
        
        self.cfgStr( fcfg[INIT], "Initilization Parameters:" )
                
        self.cfgStr( fcfg[PARENT_SEL], "Parent Selection Parameters:" )
                
        self.cfgStr( fcfg[MUTATE], "Mutate Parameters:" )

        self.cfgStr( fcfg[MAIN], "Main Parameters:" )

        #Termination Parameters
        res.write( ''.join(["Termination Parameters:"]) )
        if fcfg[TERMINATION][TYPE] == GENERATIONAL_LIMIT:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[TERMINATION][GENERATION_LIMIT], " generations"]) )
        elif fcfg[TERMINATION][TYPE] == FITNESS_EVALUATION_LIMIT:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[TERMINATION][EVALUATION_LIMIT], " fitness evaluations"]) )
        elif fcfg[TERMINATION][TYPE] == CONVERGENCE:
            res.write( ''.join (["\n  Termination criteria: ", fcfg[TERMINATION][TURNS_NO_CHANGE], " turns without a new, better, best fitness in a solution"]) )
        
        self.cfgStr( fcfg[TERMINATION], "", [TYPE] )
        
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
                    
        #<evals><tab><average first objective subfitness><tab><best first objective subfitness><average second
        #objective subfitness><best second objective fitness><average third objective subfitness><best third objec-
        #tive fitness> (not including the < and > symbols) with <evals> indicating the number of evals executed so
        out = [evals, tgen.average("LitSq"), tgen.max("LitSq"), tgen.average("BulbConflict"), tgen.max("BulbConflict"),
               tgen.average("BlackSat"), tgen.max("BlackSat")]
        newstr = ""
        for num in out:
            newstr += str(num)
            newstr += "\t"
        newstr += "\n"
            
        self.res.write( newstr )
    
    # Serializes and logs the soulution to solution-log.txt
    def best( self, gen ):
        
        pfront = gen.fitTable.data[0]
        
        for sol in pfront:
            out = [sol.getFit(LITSQ), sol.getFit(BULBCONFLICT), sol.getFit(BLACKVIO), len(pfront)]
            newstr = ""
            for num in out:
                newstr += str(num)
                newstr += "\t"
            newstr += "\n"        
            self.sol.write( newstr )
            
            self.sol.write( sol.graph.serialize( ) )
            
        self.sol.flush( )
    
    # Our generational best
    def spacer( self ):
        self.res.write( "=SPACER=\n\n" )
        
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
            dir = re.sub(r'\%bf', str(round(best.fitTable.data[0][0].oldFitness(),3)), dir )
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
    print(''.join(["Run #/",cfg[MAIN][TOTAL_RUNS]]), end='')
    if int(cfg[MAIN][TOTAL_RUNS]) < 100:
        print('\t', end='') 
    if cfg[TERMINATION][TYPE] == GENERATIONAL_LIMIT:
        print(''.join(["Gen #/", cfg[TERMINATION][GENERATION_LIMIT], '\t', "Fit"]), end='')
    elif cfg[TERMINATION][TYPE] == FITNESS_EVALUATION_LIMIT:
        print(''.join(["Gen", '\t', "Fit #/", cfg[TERMINATION][EVALUATION_LIMIT]]), end='')
    else:
        print(''.join(["Gen", '\t', "Fit"]), end='')
    print("\tAvg Fit\tSkew\tStdDiv\tBest\tLevels\tStatus\t", end='' )
    if cfg[TERMINATION][TYPE] == GENERATIONAL_LIMIT or \
            cfg[TERMINATION][TYPE] == FITNESS_EVALUATION_LIMIT:
        print("\t", end='')
    print("\tStatus %")
    
def pad(num, pad):
    if pad == '0':
        return str(num)
    inum = str(num)
    return inum.rjust(math.floor(math.log(int(pad), 10)+1), '0')

#Find our cumulative fitness. Next compare a random number to all of our generation's fitness.
#We use a sort of inverse fitness function to get the "correct" fitness numbers
def probSel( ogen, num, adj, neg=False, prn=False ):
    gen = []
    cumfit = 0
    for solu in ogen:
        gen.append(solu)
        if not neg:
            cumfit += solu.fit+1
        else:
            cumfit += adj-solu.fit+1
        
    rets = []
    while len(rets) < num:
        if prn:
            delprn(''.join(perStr(len(rets)/num)), 3)
        pnt = random.randint( 0, cumfit )
        
        tfit = 0
        for solu in gen:
            if pnt < tfit:
                gen.remove(solu)
                rets.append(solu)
                if not neg:
                    cumfit -= solu.fit+1
                else:
                    cumfit -= adj-solu.fit+1
                break
            if not neg:
                tfit += solu.fit+1
            else:
                tfit -= adj-solu.fit+1
        else:
            rets.append(solu)
            gen.remove(solu)
            if not neg:
                cumfit -= solu.fit+1
            else:
                cumfit -= adj-solu.fit+1
    return rets
    
def nsgabetter( tnsga, cmp2 ):
    p1 = tnsga.fitTable.data[0]
    p2 = cmp2.fitTable.data[0]
    wedom = 0
    tdom = 0
    for sol in p1:
        for scmp2 in p2:
            if tnsga.fitTable.dominates(sol, scmp2):
                wedom += 1
                break
    for sol in p2:
        for scmp2 in p1:
            if tnsga.fitTable.dominates(sol, scmp2):
                tdom += 1
                break
    
    if wedom >= tdom:
        return True
    else:
        return False
                