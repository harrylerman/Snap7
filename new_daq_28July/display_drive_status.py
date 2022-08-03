import numpy as np

ds = np.load("drive_status.npz")
print "########### Contents of drive_status.npz ###########"
print "isfull: " + repr(ds['isfull'])
print "nfail: " + repr(ds['nfail'])
print "current drive: " + repr(ds['current_drive'])
