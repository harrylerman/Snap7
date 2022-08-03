#!/bin/bash

# the following code mounts /dev/sda1 to /media/pi/BASEBAND
# nice in case you are running with no mux and ssd plugged directly into pi
# to do: integrate this into code better

#strcheck="sda1"
#tries=5
#i=0
#while [ $i -lt $tries ];
#do
#    sleep 5
#    t="$(lsblk | grep sda1)"
#    a=${t:2:4}
#    if [ "$a" == "$strcheck" ];
#    then
#        sudo mount /dev/sda1 /media/pi/BASEBAND
#	echo "found drive"
#        break
#    else
#	echo "drive not found"
#    fi
#    i=$(( $i + 1 ))
#done

sleep 10
daqdir="/home/pi/albatros2_daq/new_daq"
config="$daqdir/config.ini"

# Initialize config_fpga and mount_next_drive sequentially, then run dump_spectra and dump_baseband simultaneously.
python "$daqdir/albaboss.py" --retries 1 --init "$daqdir/config_fpga.py -c $config" "$daqdir/mount_next_drive.py" --commands "$daqdir/dump_spectra.py -c $config" "$daqdir/dump_baseband.py -c $config"

# config_fpga then dump_spectra
#python "$daqdir/albaboss.py" --retries 1 --init "$daqdir/config_fpga.py -c $config" --commands "$daqdir/dump_spectra.py -c $config"
