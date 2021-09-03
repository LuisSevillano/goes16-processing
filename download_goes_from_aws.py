import s3fs

import numpy as np
import os
import shutil
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool
import sys
import time
import urllib.request
from julianDay import daytoJulian


date = sys.argv[1]
outputFolder = sys.argv[2]

format = "%Y-%m-%d"
splitted = date.split('-')

year = [splitted[0]]
month = [splitted[1]]
day = [splitted[2]]
yearToDownload = splitted[0]



dayToDownload = daytoJulian(year, month, day)

# Use the anonymous credentials to access public data
fs = s3fs.S3FileSystem(anon=True)

# List contents of GOES-16 bucket.
fs.ls('s3://noaa-goes16/')

if not os.path.exists(outputFolder):
    print("Output folder doesn't exists. Creating it...");
    try:
        os.makedirs(outputFolder);
        print('Done')
    except:
        print("An exception occurred")
        raise


def downloadHour(element):
    file = element.get('file')
    hour = element.get('hour')
    fileName = file.split('/')[-1]
    # fs.get(file, fileName)
    url = 'https://noaa-goes16.s3.amazonaws.com/ABI-L2-MCMIPF/' + \
        yearToDownload + '/' + \
        dayToDownload[0] + '/' + hour + '/'
    # https://noaa-goes16.s3.amazonaws.com/ABI-L2-MCMIPF/2020/232/00/OR_ABI-L2-MCMIPF-M6_G16_s20202320010209_e20202320019523_c20202320020031.nc

    try:
        print('')
        print('Downloading ' + fileName)
        urllib.request.urlretrieve(url+fileName, fileName)
        shutil.move(fileName, Path(
            os.path.join(outputFolder, fileName)))
    except:
        print("An exception occurred")
        raise



print('Checking for files. Please wait...')

filesAvailable = []
filesInSystem = []
allFiles = []
for i in range(0, 23):
    hour = str(i).zfill(2)
    folder = 'noaa-goes16/ABI-L2-MCMIPF/' + yearToDownload + '/' + \
        str(dayToDownload[0]) + '/' + hour + '/'
    files = np.array(
        fs.ls(folder))
    for j in range(0, len(files)):
        fileName = files[j].split('/')[-1]
        filesAvailable.append(fileName)
        FILE = Path(os.path.join(outputFolder, fileName))
        if FILE.is_file():
            filesInSystem.append(fileName)
            continue

        allFiles.append({"file": fileName, "hour": hour})

print('* ' + str(len(filesAvailable)) +
      ' files are available for the date ' + date)
print('* ' + str(len(filesInSystem)) + ' files are alreay in folder')
print('* ' + str(len(allFiles)) + ' files will be downloaded')
print('')

# Make the Pool of workers
pool = ThreadPool(4)
pool.map(downloadHour, allFiles)
pool.close()
pool.join()
