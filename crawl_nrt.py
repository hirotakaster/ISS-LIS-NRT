#!/usr/bin/env python

import codecs
import sys
import urllib2
import numpy as np
import glob
import os
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import csv
import traceback
from itertools import izip
from bs4 import BeautifulSoup

COOKIE = ""
TARGET_URL = "https://ghrc.nsstc.nasa.gov/pub/lis/iss/data/science/nrt/nc/2018/1016/"
SAVE_DIR = "./data/"
CSV_FILE = "./flashloc_test.csv"


def getncdata(file):
    files = glob.glob(SAVE_DIR + file)

    flash_lat = np.array([]) #latitude
    flash_lon = np.array([]) #longitude

    try:
        # save data to csv file
        for i in files:
            datafile = Dataset(i)

            flash_lat = np.concatenate([flash_lat,datafile.variables['lightning_flash_lat'][:]]) #add to array
            flash_lon = np.concatenate([flash_lon,datafile.variables['lightning_flash_lon'][:]]) #add to array

        with open(CSV_FILE, 'ab') as myfile:
            writer = csv.writer(myfile)
            writer.writerows(izip(flash_lat,flash_lon)) #Define data rows (izip creates columns)

        # send to MQTT server

    except:
        traceback.print_exc()


def crawlnc(file):
    if os.path.exists(SAVE_DIR + file) == False:
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', COOKIE))
        r = opener.open(TARGET_URL + file)
        f = open(SAVE_DIR + file, "wb")
        f.write(r.read())
        f.close()

        # check NC data
        getncdata(file)
    
def main():
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', COOKIE))
    f = opener.open(TARGET_URL)
    html = f.read().decode('utf-8', 'ignore')

    soup = BeautifulSoup(html, "html.parser")
    links = [a.get("href") for a in soup.find_all("a")]

    for l in links:
        if l.startswith("ISS_LIS_SC_P0"):
            # crawl data to files
            crawlnc(l)

if __name__ == "__main__":
    main()
