#!/usr/bin/python
import serial
import time
import serial.tools.list_ports
import datetime

def open_efoy():
    """
    Finds the efoy comport using the usb vid/pid of the usb-serial adaptor.
    Opens the comport.
    Returns a Serial port object of the opened comport.
    Returns False if there's a problem along the way.
    """
    ports = None
    comport = None    
    try:
        ports = serial.tools.list_ports.comports() #get all the comports in use
        if not ports:
            print("could not find comports")
            return False
    except:
        print("error listing comports")
        return False       
    try:        
        for port in ports:
            if port.pid == 0x6001 and port.vid == 0x0403: #USB vid and pid of the Prolific usb-serial adapter, should work regardless of OS.
                comport = port.device #if it found the Prolific adapter, then that's our comport
        if comport is None:
            print("could not find USB-Serial adapter")
            return False
    except:
        print("error finding comport")
        return False
    try:
        ser = serial.Serial(comport) #open the port
    except:
        print("error opening comport")
        return False
    return ser
    
def read_efoy(ser):
    """
    Argument is a Serial port object.
    Writes the 'SFC' status command to the argument port (hopefully the efoy comport) and gets the output.
    Returns a UTC datetime object of the current time and the efoy status output as a split string list.
    Returns False if there's a problem along the way.
    """     
    try:
        ser.write('SFC') #write the command
        ser.write('\r') #efoy is unhappy if it gets SFC and carriage return on the same write...dunno why
    except:
        print("error writing to comport")
        return False
    time.sleep(.5) #let the efoy answer
    try:
        output = ser.read(ser.in_waiting) #get the output - this does not check for a number of bytes in the buffer it just reads however many are there after 0.5sec
    except:
        print("error reading comport buffer")
        return False    
    if not output: #if efoy doesn't answer and the output is just ''
        print("no response from efoy - is it connected?")
        return False
    else:
        output = output.split('\r') #split by carriage returns    
    tstamp = datetime.datetime.utcnow()    
    return tstamp, output

def close_efoy(ser):
    """
    Argument is a Serial port object.
    Closes the argument port (hopefully the efoy comport).
    Returns True if successful, False if there's a problem.
    """
    try:
        ser.close()
    except: 
        print("error closing comport")
        return False   
    return True

def log_data(efoydata, filepath):
    """
    Arguments are the output of the above read_efoy() function, and the logfile directory.
    read_efoy() above outputs a utc datetime object plus a list of strings of the split efoy status.
    Returns True if the logfile is written to, False if there is a problem doing so.
    """
    tstamp = efoydata[0].strftime('%Y%m%d') #convert the tstamp returned by read_efoy into a yyyymmdd format, used for naming the logfiles
    ctime = int((efoydata[0]-datetime.datetime(1970,1,1)).total_seconds()) #convert the tstamp returned by read_efoy to a ctime which is logged in the logfile
    filedata = str(ctime)+' '+str(efoydata[0])+' '+str(efoydata[1])+'\n' #data to write to logfile        
    filename = tstamp+'.txt' #will create a new logfile every new calendar day
    try:
        file = open(filepath+filename, 'a+')
        file.write(filedata)
        file.close() #here and above lines open the logfile, write data to it and close it
        print('wrote to ' + filename)
    except:
        print("logfile error")
        return False
    return True

if __name__ == "__main__":
    ### a routine to open the efoy and then read from it every 60sec, logging the output, forever ###
    filepath = '/home/pi/logs/efoy/' #logfile location
    ser = open_efoy() #open the port, could put some logging stuff here for if there is trouble finding/opening the efoy port.
#    testfile = filepath+'test.txt'
#    i=0
    while(True): 
#        testf = open(testfile, 'a+')
#        dummydata = 'testing supervisor, iteration: '+str(i)+'\n'
#        testf.write(dummydata)
#        testf.close()
#        i+=1 
        efoydata = read_efoy(ser) #read the data, like open_efoy above could put some logging info here if there is trouble.
        if efoydata is not False:
            log_data(efoydata, filepath)
        time.sleep(60)

    close_efoy(ser) #need to alter above code or it'll never get here..   


