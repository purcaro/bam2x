# Programmer : zhuxp
# Date: 
# Last-modified: 09-11-2013, 15:30:06 EDT
import types
import pysam
from xplib.Annotation import Bed,Bed12,Fragment
from xplib import Tools

def BamIterator(filename,**kwargs):
    '''
    iterator for reading a bam file. 
    Usage:
        from xplib.TableIO.BamIO import BamIterator
        for read in BamIterator(filename):
            print read
    read is a alignment in pysam.AlignedRead format.
    Wrapper In TableIO.parse(filename,"bam")
    Usage:
        for i in TableIO.parse(filename,"bam"):
            print i
    '''
    if type(filename)==type("str"):
        f=pysam.Samfile(filename,"rb")

    else:
        f=filename
    for i in f:
        #print i #debug
        yield i
def SamIterator(filename,**kwargs):
    '''
    iterator for reading a sam file. 
    Usage:
        from xplib.TableIO.BamIO import SamIterator
        for read in SamIterator(filename):
            print read
    read is a alignment in pysam.AlignedRead format.
    Wrapper In TableIO.parse(filename,"sam")
    Usage:
        for i in TableIO.parse(filename,"sam"):
            print i
    '''
    if type(filename)==type("str"):
        f=pysam.Samfile(filename,"r")
    else:
        f=filename
    for i in f:
        yield i
def BamToBedIterator(filename,**kwargs):
    '''
    iterator for reading a bam file, yield Bed Object instead of pysam.AlignedRead Object 
    Usage:
        from xplib.TableIO.BamIO import BamToBedIterator
        for read in BamToBedIterator(filename):
            print read
    read is a alignment in pysam.AlignedRead format.
    Wrapper In TableIO.parse(filename,"bam2bed")
    Usage:
        for i in TableIO.parse(filename,"bam2bed"):
            print i

    A simple bam2bed.py which will read bam file and print aligned read in bed format:
        import sys
        from xplib import TableIO
        filename=sys.args[1]
        for i in TableIO.parse(filename,"bam2bed"):
            print i
    '''

    f=pysam.Samfile(filename,"rb")
    for i in f:
        if i.tid<0:continue
        strand="+"
        if i.is_reverse:
            strand="-"
        score=i.mapq
        bed=Bed([f.references[i.tid],i.pos,i.aend,i.qname,score,strand])
        yield bed
def BamToBed12Iterator(handle,**kwargs):
    '''
    handle is an bam iterator
    need references hash if handle is not filename.
    '''
    if type(handle)==type("string"):
        handle=pysam.Samfile(handle,"rb");
    for i in handle:
        #print i #debug
        if i.tid<0: continue
        strand="+"
        if i.is_reverse:
            strand="-"
        score=i.mapq
        
        '''
        test
        '''
        if kwargs.has_key("references"):
            chr=kwargs["references"][i.tid];
        else:
            try:
                 chr=handle.references[i.tid];
            except:
                 chr="chr"
        
        start=i.pos
        end=i.aend
        name=i.qname
        cds_start=start
        cds_end=start
        itemRgb="0,0,0"
        '''
        debug
        import sys
        if i.cigar is None:
            print >>sys.stderr,"why cigar is Nonetype?"
            print >>sys.stderr,i
            exit(0)
        end of debug
        '''
        if i.cigar==None: continue # IGNORE THIS READS?
        (block_starts,block_sizes)=Tools.cigar_to_coordinates(i.cigar);
        bed=Bed12([chr,start,end,name,score,strand,cds_start,cds_end,itemRgb,len(block_sizes),block_sizes,block_starts])
        yield bed




def BamToFragmentIterator(handle,**kwargs):
    '''
    handle is an bamfile or an iterator

    if it is an iterator , 
    a "bam" option could add to find the mate read which are not in the iterator.
    
    The strategy is:
        find all the pairs in iterator first and yield them 
        then
        try to find the rest reads' mate in bamfile.

    One problem is that :
        if too much read are clustered together
        it might be very cost memory if we read too much first read and the iterator still doesn't find their mates.
        TODO: FIX THIS PROBLEM!

    '''
    paired_reads={}
    if type(handle)==type("string"):
        handle=pysam.Samfile(handle,"rb");
    for read in handle:
        fragment_name=strip_mate_id(read.qname)
        if paired_reads.has_key(fragment_name):
            yield Fragment(paired_reads[fragment_name],read) #Paired End fragment
            del paired_reads[fragment_name]
        else:
            if read.is_qcfail or read.is_unmapped:
                continue 
            if  read.mate_is_unmapped or (not read.is_paired):
                yield Fragment(read) # Single end Fragment
            else:
                paired_reads[fragment_name]=read

    
    '''
    the rest of paired end read which haven't find mate yet 
    '''
    db=None
    if kwargs.has_key("bam"): 
        db=kwargs["bam"]
        if type(db)==type("string"):
            db=pysam.Samfile(db,"rb")
    elif isinstance(handle,pysam.Samfile): 
        db=handle
    if db is not None:
        pos=db.tell()
        for read in paired_reads.values():
            try: 
                mate=db.mate(read)
            except ValueError:
                mate=None
                continue
            finally: 
                db.seek(pos)
            yield Fragment(read,mate)
    else:
        for read in paired_reads.values():
            yield Fragment(read)
    del paired_reads




            

        


def strip_mate_id(read_name):
    '''
    this function was copied from http://pydoc.net/Python/misopy/0.4.7/misopy.sam_utils/ 
    
    Strip canonical mate IDs for paired end reads, e.g.
    #1, #2
    or:
    /1, /2
    '''
    if read_name.endswith("/1") or read_name.endswith("/2") or read_name.endswith("#1") or read_name.endswith("#2"):
        read_name = read_name[0:-3]
    return read_name

