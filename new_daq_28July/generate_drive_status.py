#!/usr/bin/python

import argparse
import supertools

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Generate drive status table for N drives")
    parser.add_argument("-n", "--ndrives", type=int, default=16, help="Number of drives in generated drive status table")
    args = parser.parse_args()

    supertools.init_drive_file(args.ndrives,force=True)
