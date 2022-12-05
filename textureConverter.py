from fractions import Fraction
from itertools import count
import math
import shutil
from typing import Iterator
from resources.wavbintool import *

import os
import subprocess
import csv
import json

songs = []


typeMap = { 'PLAY': 0, 'LONG': 1, 'HAKU': 2, 'MEASURE': 3, 'END': 4 }
difficultyFileNames = ['bsc.json', 'adv.json', 'ext.json']

# assign directory
inputDirectory = '.\\imagein\\'
outputDirectory = '.\\imageout\\'

paths = [inputDirectory, outputDirectory]
for path in paths:
    if not os.path.exists(path):
        os.mkdir(path)

def extract_ifs_dir_to_tmp(path):
    process = subprocess.Popen('.\\resources\\texbintool.exe ' +path)
    process.wait()
    print(process.returncode)

def extract_all_data():
    # iterate over files in
    # that directory
    for filename in os.listdir(inputDirectory):
        f = os.path.join(inputDirectory, filename)
        # checking if it is a file
        if os.path.isfile(f) and 'bnr_big_id' in f:
            extract_ifs_dir_to_tmp(f)

def move_dir_contents_to_output(path):
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        o = os.path.join(outputDirectory, filename)
        if os.path.isfile(f):
            os.rename(f, o)


def aggregate_all_data():
    # iterate over files in
    # that directory
    for filename in os.listdir(inputDirectory):
        f = os.path.join(inputDirectory, filename)
        # checking if it is a file
        if os.path.isdir(f):
            move_dir_contents_to_output(f)
 
#extract_all_data()
aggregate_all_data()


