#!/usr/bin/python
import muxtools
import supertools
import time
import subprocess
import argparse
import sys
import logging
import datetime

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument("-s","--sleep",type=float,default=0.0,help="Time to sleep after each initialization command.")
    parser.add_argument("-r","--retries",type=int,default=3,help="Number of retry attempts before giving up.")

    args=parser.parse_args()
    dt=args.sleep

    ################ Logger things #################
    logger=logging.getLogger("albatros_mount_drive")
    logger.setLevel(logging.INFO)
    file_logger=logging.FileHandler("/home/pi/logs/albatros_mount_drive/albatros_mount_drive_"+datetime.datetime.now().strftime("%d%m%Y_%H%M%S")+".log")
    file_format=logging.Formatter("%(asctime)s %(name)s %(message)s", "%d-%m-%Y %H:%M:%S")
    file_logger.setFormatter(file_format)
    file_logger.setLevel(logging.INFO)
    logger.addHandler(file_logger)

    # also prints log messages as stdout
    stdout_logger=logging.StreamHandler(sys.stdout)
    stdout_logger.setLevel(logging.INFO)
    logger.addHandler(stdout_logger)

    logger.info("##########################################################")
    logger.info("Selecting next drive")
    # diskid is the label of the next drive (int ranging from 0 to ndrive-1)
    diskid=supertools.select_next_drive()
    logger.info("Will mount drive "+ str(diskid))
    if diskid is None:
        logger.info('Error - diskid not returned by select_next_drive')
        assert(1==0)

    muxtools.init_mux()
    time.sleep(dt)
    muxtools.poweren(0)
    time.sleep(dt)
    muxtools.muxen(0)
    time.sleep(dt)

    mp=muxtools.mount_drive(diskid, logger)
    
    if mp is not None:
        logger.info("Drive mounted")
    else:
        logger.info("Drive did not mount successfully.")
