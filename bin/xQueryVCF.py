#!/usr/bin/env python
# Programmer : zhuxp
# Date: 
# Last-modified: 09-25-2013, 08:59:54 EDT
VERSION="0.1"
import os,sys,argparse
from xplib.Annotation import Bed
from xplib import TableIO,Tools
from xplib.Tools import IO
import signal
signal.signal(signal.SIGPIPE,signal.SIG_DFL)
import time

def ParseArg():
    ''' This Function Parse the Argument '''
    p=argparse.ArgumentParser( description = 'Example: %(prog)s -h', epilog='Library dependency : xplib')
    p.add_argument('-v','--version',action='version',version='%(prog)s '+VERSION)
    p.add_argument('-i','--input',dest="input",default="stdin",type=str,help="input file DEFAULT: STDIN")
    p.add_argument('-o','--output',dest="output",type=str,default="stdout",help="output file DEFAULT: STDOUT")
    p.add_argument('-b','--bam', dest="bams",type=str,nargs="+",help="bam files")
    
    if len(sys.argv)==1:
        print >>sys.stderr,p.print_help()
        exit(0)
    return p.parse_args()
def Main():
    '''
    IO TEMPLATE
    '''
    global args,out
    args=ParseArg()
    fin=IO.fopen(args.input,"r")
    out=IO.fopen(args.output,"w")
    '''
    END OF IO TEMPLATE 
    '''
    print >>out,"# This data was generated by program ",sys.argv[0]," (version: %s)"%VERSION,
    print >>out,"in bam2x ( https://github.com/nimezhu/bam2x )"
    print >>out,"# Date: ",time.asctime()
    print >>out,"# The command line is :"
    print >>out,"#\t"," ".join(sys.argv)
    print >>out,args.bams
    
    dbi=[];
    for i,bam in enumerate(args.bams):
        print >>out,"# No."+str(i+1)+" BAM File:",bam
        dbi.append(DBI.init(bam,"bam"))
    for i in TableIO.parse(fin,"vcf"):
        print >>out,i,
        for d in dbi:
            print >>out,"\t",dbi.query(i)

def format(vcf,result,method=0):
    pass
    
if __name__=="__main__":
    Main()






