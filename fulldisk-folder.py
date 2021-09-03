
from datetime import datetime
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import metpy  # noqa: F401
import numpy as np
import xarray
import os
import subprocess
from pathlib import Path
import sys

outputFolder = sys.argv[1]

def fullDisc(i, fileName):
    print('')
    print('Processing ' + str(i) + ' of ' +
          str(totalFiles) + " files: " + str(fileName) + ' ...')

    # FILE = (
    #     'files/OR_ABI-L2-MCMIPF-M6_G17_s20202311430321_e20202311439393_c20202311439479.nc')
    FILE = Path(os.path.join(dir, fileName))
    F = xarray.open_dataset(FILE)

    scan_start = datetime.strptime(
        F.time_coverage_start, '%Y-%m-%dT%H:%M:%S.%fZ')

    # # Load the RGB arrays
    R = F['CMI_C02'][:].data
    G = F['CMI_C03'][:].data
    B = F['CMI_C01'][:].data

    # Apply range limits for each channel. RGB values must be between 0 and 1
    R = np.clip(R, 0, 1)
    G = np.clip(G, 0, 1)
    B = np.clip(B, 0, 1)

    # # Apply the gamma correction
    gamma = 2.2
    R = np.power(R, 1/gamma)
    G = np.power(G, 1/gamma)
    B = np.power(B, 1/gamma)

    # # Calculate the "True" Green
    G_true = 0.48358168 * R + 0.45706946 * B + 0.06038137 * G
    G_true = np.clip(G_true, 0, 1)

    # # The final RGB array :)
    RGB = np.dstack([R, G_true, B])

    # # We'll use the `CMI_C02` variable as a 'hook' to get the CF metadata.
    dat = F.metpy.parse_cf('CMI_C02')

    x = dat.x
    y = dat.y

    # night
    cleanIR = F['CMI_C13'].data

    # Normalize the channel between a range.
    #       cleanIR = (cleanIR-minimumValue)/(maximumValue-minimumValue)
    cleanIR = (cleanIR-90)/(313-90)

    # Apply range limits to make sure values are between 0 and 1
    cleanIR = np.clip(cleanIR, 0, 1)

    # Invert colors so that cold clouds are white
    cleanIR = 1 - cleanIR

    # Lessen the brightness of the coldest clouds so they don't appear so bright
    # when we overlay it on the true color image.
    cleanIR = cleanIR/1.4

    # Yes, we still need 3 channels as RGB values. This will be a grey image.
    # RGB_cleanIR = np.dstack([cleanIR, cleanIR, cleanIR])

    # Maximize the RGB values between the True Color Image and Clean IR image
    RGB_ColorIR = np.dstack([np.maximum(R, cleanIR), np.maximum(G_true, cleanIR),
                             np.maximum(B, cleanIR)])

    fig = plt.figure(figsize=(10, 8))

    geos = dat.metpy.cartopy_crs

    ax = fig.add_subplot(1, 1, 1, projection=geos)

    ax.imshow(RGB_ColorIR, origin='upper',
              extent=(x.min(), x.max(), y.min(), y.max()),
              transform=geos)

    ax.coastlines(resolution='50m', color='black', linewidth=0.4)
    ax.add_feature(ccrs.cartopy.feature.BORDERS, linewidth=0.4, color='black')

    # plt.title('GOES-16 True Color', fontweight='bold', fontsize=15, loc='left')
    plt.title('{}'.format(scan_start.strftime('%H:%M UTC %d %B %Y')),
              loc='right')
    noExtension = os.path.splitext(fileName)[0]
    outputFileName = os.path.join(
        'output', outputFolder, str(noExtension) + '.png')
    print('processing ' + outputFileName)
    plt.savefig(outputFileName, bbox_inches='tight', dpi=300)
    plt.close()


dir = os.path.join(
    '/Users/portatil/Documents/projects/goes-16-downloading/files', outputFolder)
totalFiles = len([name for name in os.listdir(
    dir) if os.path.isfile(os.path.join(dir, name))])

print(str(totalFiles) + ' files in folder')

for idx, file in enumerate(os.listdir(dir)):

    noExtension = os.path.splitext(file)[0]
    outputFileName = os.path.join(
        'output', outputFolder, str(noExtension) + '.png')
    FILE = Path(os.path.join(outputFileName))
    if FILE.is_file():
        print(str(noExtension) + '.png exists in folder')
        continue

    fullDisc(idx, file)
