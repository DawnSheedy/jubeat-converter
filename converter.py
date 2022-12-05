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

with open('.\\resources\\song_registry.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    songs = [song for song in reader]


typeMap = { 'PLAY': 0, 'LONG': 1, 'HAKU': 2, 'MEASURE': 3, 'END': 4 }
difficultyFileNames = ['bsc.json', 'adv.json', 'ext.json']

# assign directory
inputDirectory = '.\\input\\'
imageDirectory = '.\\imageout\\'
tmpDirectory = '.\\tmp\\'
tmpDirectory2 = '.\\temp\\'
outputDirectory = '.\\output\\'

paths = [inputDirectory, tmpDirectory, outputDirectory]
for path in paths:
    if not os.path.exists(path):
        os.mkdir(path)

def truncate_fraction(f: Fraction, places: int) -> Fraction:
    """Truncates a fraction to the given number of decimal places"""
    exponent = Fraction(10) ** places
    return Fraction(math.floor(f * exponent), exponent)


def iter_truncated(f: Fraction) -> Iterator[Fraction]:
    for places in count():
        yield truncate_fraction(f, places)


def value_to_bpm(value: int) -> Fraction:
    return 6 * 10**7 / Fraction(value)


def bpm_to_value(bpm: Fraction) -> Fraction:
    return 6 * 10**7 / bpm


def value_to_truncated_bpm(value: int) -> Fraction:
    """Only keeps enough significant digits to allow recovering the original
    TEMPO line value from the bpm"""
    exact_bpm = value_to_bpm(value)
    truncated_bpms = iter_truncated(exact_bpm)
    bpms_preserving_value = filter(
        lambda b: bpm_to_value(b) < value + 1, truncated_bpms
    )
    return next(bpms_preserving_value)

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

def cleanup(directories):
    for directory in directories:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

def extract_ifs_dir_to_tmp(path):
    process = subprocess.Popen('.\\resources\\ifstools.exe ' +path+ ' -e -o '+tmpDirectory)
    process.wait()
    print(process.returncode)

def retrieve_song_info(filename):
    return next((item for item in songs if item["songId"] == filename), None)

def generate_song_chart(note_path):
    difficulty = 0
    if (note_path.endswith('adv.eve')):
        difficulty = 1
    if (note_path.endswith('ext.eve')):
        difficulty = 2

    tempo = 0
    length = 0
    noteCount = 0
    events = []
    with open(note_path, newline='', encoding='utf-8') as note_file:
        reader = csv.DictReader(note_file, ['tick', 'event', 'meta'])
        for line in reader:
            eventTick = line['tick'].strip()
            eventType = line['event'].strip()
            eventMeta = line['meta'].strip()

            if (eventType == 'TEMPO'):
                tempo = convert_to_float(value_to_bpm(int(eventMeta, base=10)))
                continue
            if (eventType == 'END'):
                length = int(eventTick, base=10)
            if (eventType in ['PLAY', 'LONG']):
                noteCount+=1

            event = { 'type': typeMap[eventType], 'detail': int(eventMeta), 'tick': int(eventTick) }

            events.append(event)

    return { 'tempo': tempo, 'length': length, 'difficulty': difficulty, 'events': events, 'noteCount': noteCount }

def generate_song_meta(title, artist, outputDir, note_paths):
    charts = [generate_song_chart(chart) for chart in note_paths]
    baseChart = charts[0]

    songMeta = { 'title': title, 'artist': artist if artist else 'N/A', 'tempo': baseChart['tempo'], 'length': baseChart['length'], 'versions': [{ 'difficulty': chart['difficulty'], 'noteCount': chart['noteCount']} for chart in charts] }
    with open(os.path.join(outputDir, 'meta.json'), "w", encoding='utf-8') as metaFile:
        json.dump(songMeta, metaFile, ensure_ascii=False)

    endTime = charts[0]['length']
    for chart in charts:
        if endTime != chart['length']:
            print("AHHHHHHHHHH")
        final_chart = {'events': chart['events']}
        with open(os.path.join(outputDir, difficultyFileNames[chart['difficulty']]), "w", encoding='utf-8') as diffFile:
            json.dump(final_chart, diffFile, ensure_ascii=False)

def process_song(filename, path):
    songId = filename.split('_')[0]
    song = retrieve_song_info(songId)
    if not song:
        print("[ERROR] Song ID: "+filename+" not found!")
        return
    print("Processing song: "+song['title']+" (Artist:"+song["artist"]+")")
    
    songOutputDirectory = os.path.join(outputDirectory, "".join(i for i in song['title'] if i not in "\/:*?<>|"))
    songPath = os.path.join(path, 'bgm.bin')
    indexPath = os.path.join(path, 'idx.bin')
    basicPath = os.path.join(path, 'bsc.eve')
    advancedPath = os.path.join(path, 'adv.eve')
    expertPath = os.path.join(path, 'ext.eve')

    if (not os.path.exists(songPath) or not os.path.exists(indexPath)):
        print("Skipping song! No music found.")
        return
    
    if (not os.path.exists(basicPath) and not os.path.exists(advancedPath) and not os.path.exists(expertPath)):
        print("Skipping song! No maps found!.")
        return

    if os.path.exists(songOutputDirectory):
        return

    imagePath = os.path.join(imageDirectory, "BNR_BIG_ID"+songId+".png")

    os.mkdir(songOutputDirectory)
    parse_bin(songPath, os.path.join(songOutputDirectory, 'song.wav'))
    parse_bin(indexPath, os.path.join(songOutputDirectory, 'index.wav'))
    if (os.path.exists(imagePath) and os.path.isfile(imagePath)):
        os.rename(imagePath, os.path.join(songOutputDirectory, 'bnr.png'))

    note_paths = [basicPath, advancedPath, expertPath]
    generate_song_meta(song["title"], song["artist"], songOutputDirectory, note_paths)

def run_song_processing():
    for filename in os.listdir(tmpDirectory):
        f = os.path.join(tmpDirectory, filename)
        if not os.path.isdir(f):
            continue
        process_song(filename, f)

def extract_all_data():
    # iterate over files in
    # that directory
    for filename in os.listdir(inputDirectory):
        f = os.path.join(inputDirectory, filename)
        # checking if it is a file
        if os.path.isdir(f):
            extract_ifs_dir_to_tmp(f)

# start by cleaning up tmp and output
cleanup([tmpDirectory, tmpDirectory2, outputDirectory])
 
extract_all_data()
run_song_processing()

# cleanup at end
cleanup([tmpDirectory, tmpDirectory2])
