import RPi.GPIO as GPIO
import time
import os
import subprocess
import logging

gpio_warnings=False

DISKID="sda1" # safe bet for default
MOUNTPOINT= "/media/pi/BASEBAND"

#you can find the drive model with lsblk -o NAME,MODEL
#DRIVE_MODEL= "SanDisk_SD9SN8W1T00"
DRIVE_MODEL="My_Book_25ED"


def lprint(logfile=None,*args,**kwargs):
    mystr=''
    for arg in args:
        if len(mystr)>0:
            mystr=mystr+' '
        if isinstance(arg,str):
            mystr=mystr+arg
        else:
            mystr=mystr+repr(arg)
    print(mystr)
    if not(logfile is None):
        logfile.write(mystr+'\n')
        logfile.flush()


def init_mux():
    '''
    GPIO pin assignments for mux
    '''

    GPIO.setwarnings(gpio_warnings)

    A0 = 6
    A1 = 13
    A2 = 19
    A3 = 26
    MUXEN = 12
    PWREN = 16

    # use Broadcom pinout
    GPIO.setmode(GPIO.BCM)

    # set all pins for digital out
    GPIO.setup(A0, GPIO.OUT)
    GPIO.setup(A1, GPIO.OUT)
    GPIO.setup(A2, GPIO.OUT)
    GPIO.setup(A3, GPIO.OUT)
    GPIO.setup(MUXEN, GPIO.OUT)
    GPIO.setup(PWREN, GPIO.OUT)

def select_drive(drive):
    '''
    Select the drive using the mux via RPi GPIO pins. 
    The drive argument must be 0-15.
    '''

    # Otherwise, we get warnings when we run it again, on setmode and setup
    GPIO.setwarnings(gpio_warnings)

    # GPIO pin assignments for mux
    A0 = 6
    A1 = 13
    A2 = 19
    A3 = 26
    MUXEN = 12
    PWREN = 16

    # GPIO values
    gv = (GPIO.LOW, GPIO.HIGH)

    #select the appropriate drive.
    GPIO.output(A0, gv[(drive >> 0) & 1])
    GPIO.output(A1, gv[(drive >> 1) & 1])
    GPIO.output(A2, gv[(drive >> 2) & 1])
    GPIO.output(A3, gv[(drive >> 3) & 1])

def poweren(state):
    '''
    Set the power enable status of the mux using RPi GPIO pins
    State argument must be 0 (off) or 1 (on)
    '''

    # Otherwise, we get warnings when we run it again, on setmode and setup
    GPIO.setwarnings(gpio_warnings)

    # GPIO pin assignments for mux
    A0 = 6
    A1 = 13
    A2 = 19
    A3 = 26
    MUXEN = 12
    PWREN = 16

    # GPIO values
    gv = (GPIO.LOW, GPIO.HIGH)

    #set the power state
    GPIO.output(PWREN, gv[state])

def muxen(state):
    '''
    Set the mux enable (data path) status of the mux using RPi GPIO pins
    State argument must be 0 (off) or 1 (on)
    '''

    # Otherwise, we get warnings when we run it again, on setmode and setup
    GPIO.setwarnings(gpio_warnings)

    # GPIO pin assignments for mux
    A0 = 6
    A1 = 13
    A2 = 19
    A3 = 26
    MUXEN = 12
    PWREN = 16

    # GPIO values
    gv = (GPIO.LOW, GPIO.HIGH)

    #set the mux state
    GPIO.output(MUXEN, gv[state])

def get_diskid(drive_model):
    '''
    Given the model of the drive you are trying to mount, finds
    where it is (i.e. sda1, sdb1, etc)

    NOTE: cannot deal with subpartitions in drive (e.g. if drive for
    some reason has partitions in sda1 and sda2
    '''

    lsblk_out=subprocess.check_output(['lsblk','-o', 'MODEL,NAME']).decode('utf-8')
    lines=lsblk_out.split('\n')
    for line in lines:
        if drive_model in line:
            loc= line.split(" ")[1] # will be sda or sdb
            drive_name = "/dev/" + str(loc)
            for i in range(1,4): # trying sda1, sda2, sda3
                try:
                    tmp = drive_name + str(i)
                    subprocess.check_output(['lsblk',tmp]).decode('utf-8')
                    return tmp
                except:
                    print "Could not find drive"

def get_drivestates_path():
    home=os.getenv("HOME")
    if home is None:
        print('HOME environment variable not found.  Falling back to hardwired.')
    return home+'/.drivestates.txt'

def isthere(diskid=DISKID):
    stuff=subprocess.check_output(['lsblk'])
    stuff=stuff.decode('utf-8')
    if diskid in stuff:
        return True
    else:
        return False

def ismounted(diskid=DISKID):
    '''
    running df to check whether the drive is there
    '''
    df=subprocess.check_output(['df','-h']).decode('utf-8')
    lines=df.split('\n')
    for line in lines:
        if diskid in line:
            tags=line.split()
            if  diskid in tags[0]:
                ind=line.find(diskid)
                tmp=line[ind+len(diskid):]
                ind2=tmp.find('/')
                mount_point=tmp[ind2:]
                return mount_point
    return None #if disk is not mounted

def lsblk():
    mybytes=subprocess.check_output(['lsblk'])
    return mybytes.decode('utf-8')

def mount_drive(id,logger,drive_model=DRIVE_MODEL,timeout=120,dt=2,mount_point=MOUNTPOINT):
    '''
    Mounts a drive. 

    Parameters:
    -----------
    id: int
        the id of the drive (ranging from 0 to ndrive -1)

    timeout: int
        amount of time (in seconds) to wait before giving up

    dt: int
        downtime between querying lsblk and doing mux stuff
    '''

    select_drive(id)
    time.sleep(0.5)
    print 'enabling power'
    poweren(1)
    time.sleep(0.5)
    print 'enabling mux'
    muxen(1)
    time.sleep(10.5)

    logger.info("Starting lsblk search")

    t1=time.time()
    while True:
        try:
            if (time.time())-t1>timeout:
                logger.error('Timed out looking for drive in lsblk.')
                success=False
                return None
            diskid=get_diskid(drive_model)
            if diskid is not None:
                logger.info('Found drive in '+repr(diskid)+' after '+ str(round(time.time()-t1,4)) + ' seconds')
                success=True
                break
        except:
            #if time.time()-t1>timeout:
            #    logger.info('Timeout recognizing drive in lsblk.')
            #    success=False
            #    break
            logger.error('Error finding drive in lsblk.')
            return None
        time.sleep(dt)


    logger.info('Starting to mount drive')

    time.sleep(0.5)
    mp=ismounted(diskid)

    if mp is not None:
        logger.info('Drive seemed to automount')
        return mp  #get here if the drive is now mounted

    os.system('sudo mount '+ diskid +" " +mount_point)
    t1=time.time()
    while True:
        mp=ismounted(diskid)
        print mp
        #assert(1==0)
        if mp is not None:
            return mp
        if time.time()-t1>timeout:
            logger.info('Timeout mounting disk')
            return None
        time.sleep(dt)


def free_drive(dev='/dev/sda1'):
    mp=ismounted(dev)
    if not(mp is None):
        os.system('sudo umount '+dev)
        dd=dev[:-1]
        os.system('sudo udisksctl power-off -b '+dd)
    #dd=dev[:-1]
    #os.system('sudo udisksctl power-off -b '+dd)
    time.sleep(0.5)
    muxen(0)
    time.sleep(0.5)
    poweren(0)

def scan_drives_jls(diskid=DISKID,outf=None):
    t1=time.time()
    for id in range(16):
        lprint(outf,'mounting drive ',id)
        mp=mount_drive(id)
        if mp is None:
            lprint(outf,'failure in mounting drive, going to try again.')
            mp=mount_drive(id)
            if mp is None:
                lprint(outf,'double failure  in mounting.')
        lprint(outf,'drive ',id,' mounted at ',mp,' after ',time.time()-t1,' seconds.')
        time.sleep(1)
        lprint(outf,'calling df')
        os.system('df -kh | grep ' + diskid)
        time.sleep(1)
        myout=subprocess.check_output(['df']).decode('utf-8')
        if diskid in myout:
            lines=myout.split('\n')
            for ll in lines:
                if diskid in ll:
                    lprint(outf,ll)
        else:
            lprint(outf,'Sadness - drive does not appear in df')
        lprint(outf,'freeing drive')
        free_drive()
        lprint(outf,'freed')
        time.sleep(1)

def scan_drives(drivesafety=0.95):
#### Makes or updates a statetable with 5 columns: drive number, bytes used, bytes free, percent used, active flag
#### Will take ~8 mins to run as each drive can take ~30sec to be recognized by the Pi.
#### The drivesafety argument is the drive safety parameter from the config file.
#### Uses the mountpoint /media/pi/ALBATROS for all drives.
#### No drives will be mounted after this. Running the following function get_active_drive should mount one if available.

    mountpoint = '/media/pi/ALBATROS'
    #sudopassword = 'raspberry'
    sudopassword = 'M@ri0n!'
    mountcmd = 'mount /dev/sda1 ' + mountpoint         ####put an lsblk command here for more robustness, this is ok for now
    umountcmd = 'umount ' + mountpoint
    poweroffcmd = 'udisksctl power-off -b /dev/sda'

    #unmount and power-off a drive if one is mounted:
    if os.path.ismount(mountpoint):
        os.system('echo %s|sudo -S %s' % (sudopassword, umountcmd))
        os.system('echo %s|sudo -S %s' % (sudopassword, poweroffcmd))
        time.sleep(5) #let the drive spin down before killing power
    #also set the mux to an off state
    muxen(0)
    poweren(0)

    #filepath = '/home/pi/Documents/mux_testing/' #'statetable-filepath-goes-here'
    #filename = filepath+'drivestates.txt'
    filename=get_drivestates_path()

    #Open or create the statetable file and read it
    try:
        file = open(filename, "a+")
        filelines = file.readlines()
        file.close()
    except:
        filelines=[]

    #scanning through 16 drives
    drivelist = range(16)

    #make a default empty list to write the lines to, if the statetable wasn't already present
    if len(filelines) <= 0:
        filelines = [str(drive) + ' 0 0 0 False' for drive in drivelist]

    #now go through all the drives.
    for drive in drivelist:
        #s/p/m/mount drive:
        select_drive(drive)
        poweren(1)
        muxen(1)  
        #can take ~30 sec for the Pi to detect the drive
        time.sleep(30)
        #mount the drive:
        os.system('echo %s|sudo -S %s' % (sudopassword, mountcmd))
        #check the drive's free space and get ready to update the table
        time.sleep(5) #let the mounting finish
        mystr = subprocess.check_output(['df','-k',mountpoint])
        if isinstance(mystr,bytes):
            mystr=mystr.decode('utf-8')
        info = mystr.split('\n') #driveinfo
        tags = info[1].split()
        usedbytes = tags[2]
        freebytes = tags[3]
        usedprct = tags[4].replace('%','') #remove the % symbol from the output of df     
        
        #update the elements of the table
        split = filelines[drive].split()
        split[1] = usedbytes
        split[2] = freebytes
        split[3] = usedprct
        line = ' '.join(split) + '\n'
        filelines[drive] = line

        #unmount and power-off the drive
        time.sleep(5) #let anything from the df command finish
        os.system('echo %s|sudo -S %s' % (sudopassword, umountcmd))
        os.system('echo %s|sudo -S %s' % (sudopassword, poweroffcmd))
        time.sleep(5) #let the drive spin down before killing power
        muxen(0)
        poweren(0)
        
    #after going through all the drives, write the updated table.
    file = open(filename, "w")
    file.writelines(filelines)
    file.close()
    print("Finished updating table!")
    return True

def get_active_drive(drivesafety):
####  Verify that the current active drive, if there is one, isn't too full and keep using it if so.
####  It will also mount the active drive if it was unmounted after for example a power reset and 
####     did not automatically remount itself.
####  Assumes all drives use the mountpoint /media/pi/ALBATROS
####  If the current active drive gets too full, or if there was no active drive, move on to the next 
####     most free drive, set it as the active drive, select it via the mux and mount it.
####  If there is no next most free drive below the drive safety percentage parameter, then all drives are full.
#### The drivesafety argument is the drive safety parameter from the config file.
####  Returns the active drive number (0-15), or False if all drives full.

    #set up some initial parameters
    drives = []
    mountpoint = '/media/pi/ALBATROS'
    sudopassword = 'raspberry'
    mountcmd = 'mount /dev/sda1 ' + mountpoint ####put an lsblk command here for more robustness, this is ok for now
    umountcmd = 'umount ' + mountpoint
    poweroffcmd = 'udisksctl power-off -b /dev/sda'

    #read the state table
    #make a list of unfull drives    
    filepath = '/home/pi/Documents/mux_testing/' #'statetable-filepath-goes-here'
    filename = filepath+'drivestates.txt'
    file = open(filename, "r")
    filelines = file.readlines()
    file.close()
    for i in range(len(filelines)):
        split = filelines[i].split()
        usedprct = int(split[3])
        if usedprct <= drivesafety:
            drives.append(filelines[i])
            
    #look for the active drive
    activedrive = None
    for drive in drives:
        split = drive.split()
        if split[4] == 'True':
            activedrive = drive
            
    #if it finds an active drive: 
    if activedrive is not None:
        isfull = False
        split = activedrive.split()
        drive = int(split[0])
        #check if it's mounted. if it's not, mount it (this assumes if a drive was mounted it was the active drive):
        if os.path.ismount(mountpoint) is False:
        #set the mux state to off, then select the drive, power it on, wait 30sec, and mount it
            muxen(0)
            poweren(0)
            select_drive(drive)
            poweren(1)
            muxen(1)
            #takes ~30sec for the pi to recognize the drive:
            time.sleep(30)
            os.system('echo %s|sudo -S %s' % (sudopassword, mountcmd))
        #check the active drive's free space.  
        mystr = subprocess.check_output(['df','-k',mountpoint])
        info = mystr.split('\n') #driveinfo
        tags = info[1].split()
        usedbytes = tags[2]
        freebytes = tags[3]
        usedprct = int(tags[4].replace('%','')) #remove the % symbol from the output of df
        split[1] = usedbytes
        split[2] = freebytes
        split[3] = str(usedprct)
        #if it is too full, unmount it and set its status in the table
        if usedprct >= drivesafety:
            split[4] = 'False'
            #unmount and power-off the drive
            os.system('echo %s|sudo -S %s' % (sudopassword, umountcmd))
            os.system('echo %s|sudo -S %s' % (sudopassword, poweroffcmd))
            time.sleep(5) #let the drive spin down before killing power
            muxen(0)
            poweren(0)
            isfull = True
            drives.remove(activedrive)
            line = ' '.join(split)+'\n'
            filelines[drive] = line
        #if it's not too full update the table and we're done:
        else:
            line = ' '.join(split)+'\n'
            filelines[drive] = line
            file = open(filename, "w")
            file.writelines(filelines)
            file.close()
            return drive
            
    #if there is no active drive, or if the active drive was too full:
    if activedrive is None or isfull is True:
        #pick the next most free drive. if there is no next most free drive, then all drives are full.
        try:
            freespace = [int(row.split()[3]) for row in drives]
            minindex = freespace.index(min(freespace))
            activedrive = drives[minindex]
        except (ValueError):
            print("All drives are full!")
            #update the table:
            file = open(filename, "w")
            file.writelines(filelines)
            file.close()
            return False
        
        #mount it, and it should be good to go, only the active drive was in use so the table should be accurate for this drive.
        split = activedrive.split()
        drive = int(split[0])
        muxen(0)
        poweren(0)
        select_drive(drive)
        poweren(1)
        muxen(1)
        #can take ~30 sec for the pi to recognize the drive.
        time.sleep(30)
        os.system('echo %s|sudo -S %s' % (sudopassword, mountcmd))
        #update the table with this drive as the active drive, and that's it.
        split[4] = 'True'
        line = ' '.join(split)+'\n'
        filelines[drive] = line
        file = open(filename, "w")
        file.writelines(filelines)
        file.close()
        return drive


