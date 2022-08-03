import os
import subprocess
import numpy as np

DAQDIR="/home/pi/albatros2_daq/new_daq"

def get_pids(procname='supervisord'):
    try:
        #if this fails, I believe it means there is no matching process
        txt=subprocess.check_output(['ps','-C',procname,'-o','pid=']).decode('utf-8')
    except:
        return None
    txt=txt.strip()
    if len(txt)>0:
        lines=txt.split('\n')
        if len(lines)>1:
            lines=[ll.strip() for ll in lines]
        return lines
    else:
        return None


def get_dir(env='DAQDIR',default='/home/pi/albatros2_daq/new_daq/'):
    '''
    Gets the directory where the drive status file will be saved and read.
    '''

    '''
    dr=os.getenv(env)
    if dr is None:
        print("warning - " + env+" not found in environment in get_dir")
        return default
    else:
        return dr
    '''

    return DAQDIR

def read_status(fname='drive_status.npz'):
    try:
        fname=get_dir()+'/'+fname
        tmp=np.load(fname)
        isfull=tmp['isfull']
        nfail=tmp['nfail']
        current_drive=tmp['current_drive']
    except:
        print('failed in reading drive status from ',fname)
        isfull=None
        nfail=None
        current_drive=None
    return isfull,nfail,current_drive

def write_status(fname,isfull,nfail,current_drive):
    fname=get_dir()+'/'+fname
    try:
        np.savez(fname,isfull=isfull,nfail=nfail,current_drive=current_drive)
    except:
        print('unable to save drive status to ',fname)

def init_drive_file(ndrive=16,fname='drive_status.npz',force=False):
    '''
    This creates the drive_status.npz file, which keeps track of which
    drives are full, and which drive is currently being written to.

    Parameters:
    ----------
    ndrive: int
        the number of drives that are hooked up to the MUX.

    fname: str
        the name of the drive status file

    force: Bool
        if set to True, it will overwrite the existing drive status file.
    '''
    
    ff=get_dir()+'/'+fname
    if os.path.isfile(ff):
        print("found pre-existing status file ",ff)
        if force==False:
            print("Force is false, so not overwriting.")
            return None
        else:
            print("force is true, so overwriting pre-existing status.")
    
    # initializing all drives to empty, selecting drive 0 to start
    isfull=np.zeros(ndrive,dtype='bool')
    nfail=np.zeros(ndrive,dtype='int')
    current_drive=0

    write_status(fname,isfull,nfail,current_drive)

def mark_drive_full(id=None,fname='drive_status.npz'):
    isfull,nfail,current_drive=read_status(fname)
    if id is None:
        id=current_drive
    isfull[id]=True
    write_status(fname,isfull,nfail,current_drive)


def select_next_drive(fname='drive_status.npz',use_current=True):
    '''
    Searches for the next drive to mount.

    Parameters:
    -----------
    fname: str
        Path to the drive status file. 

    use_current: Bool
        Whether to use the drive that is currently selected in the npz file.
    '''
    
    isfull,nfail,current_drive=read_status(fname)
    
    if use_current: #checking whether current drive is full
        if isfull[current_drive]==False:
            return current_drive

    if np.all(isfull==True):
        print('all drives are marked full.')
        return None

    # finding next empty drive
    id=np.min(np.where(isfull==False)[0])
    current_drive=id

    # updating the drive logger file
    write_status(fname,isfull,nfail,current_drive)
    return current_drive

def flag_failure(id=None,fname='drive_status.npz',max_fails=10):
    isfull,nfail,current_drive=read_status(fname)
    if id is None:
        id=current_drive
    nfail[id]=nfail[id]+1
    if nfail[id]>=max_fails:
        isfull[id]=True
    write_status(fname,isfull,nfail,current_drive)

    

    
