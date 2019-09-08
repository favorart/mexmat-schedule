# -*- coding: cp1251 -*-
#import matplotlib as mpl
#import matplotlib.pyplot as plt
#import numpy as np
import csv
import sys
import os
import io

INPUT_DIR = sys.argv[1]
FNAME_OUT = os.path.join(INPUT_DIR, 'comp_rooms_scedule.txt')

ROOMS = [ "13-07", "13-08", "13-15", "13-16", "13-05" ]
DAYS =  [ " ÏÍ", 
          " ÂÒ", 
          " ÑÐ", 
          " ×Ò", 
          " ÏÒ", 
          " ÑÁ" ] # " ÂÑ"
TIMES = [ " 09:00-10:35", 
          " 10:45-12:20", 
          " 12:30-14:05", 
          " 15:00-16:35", 
          " 16:45-18:20" ]


def parse_cells(file, row, col, lines):
    day, time, group, subject, teacher = 0, 0, "", "", ""
    #row += 1
    rows_in_day = 15
    rows_in_title = 3
    rows_in_time = 3
    try:
        day = (row - rows_in_title) / rows_in_day
        time = ((row - rows_in_title) % rows_in_day) / rows_in_time
        group = lines[1][col].strip()
        if (row % 3) != 2:
            #print "!{:d}".format(row)
            subject = lines[row][col].strip().replace("~", "") + " ~~~ "
            teacher = ""
        else:
            #print "={:d}".format(row)
            if '~' in lines[row-1][col] or '~' in lines[row][col]:
                subject = " ~~~ " + lines[row][col].strip()
                teacher = ""
            else:
                subject = lines[row-2][col].strip()
                teacher = lines[row-1][col].strip()
    except Exception as e:
        err = "{}   error:   day={} time={} col={} row={}".format(file, day, time, col, row)
        print err.decode('cp1251').encode('cp866')
        print str(e)
    return day, time, group, subject, teacher

def parse_scedule(fn, cr_scedule):
    file = os.path.split(fn)[1]
    content = []
    with open(fn, "rb") as fi:
        for record in csv.reader(fi):
            if any(record):
                content.append(tuple(s.replace("\n", " ").replace("\r", " ") for s in record))
    #if (content): # write csv with corrections (no empty lines and no new_lines in cells)
    #    with open(fn, "wb") as fo:
    #        w = csv.writer(fo)
    #        for record in content:
    #            w.writerow(tuple(s for s in record)) #unicode(s), encoding="cp1251"
    #else: print "free content: ", file
    for row, line in enumerate(content):
        for col, cell in enumerate(line):
            for room in ROOMS:
                if (room in cell and col > 1):
                    #print cell, row, col
                    day, time, group, subject, teacher = parse_cells(file, row, col, content)
                    more_lesson = " ãð.{:6s} {:s}  {:s}".format(group, subject, teacher)
                    if cr_scedule[room].has_key((day,time)):
                        have_lesson = cr_scedule[room][(day,time)].strip('"')
                        
                        err = "{:s} \t duplicate:   {:s} has key({:s},{:s})  {:55s} \t {:55s} ".format(
                            file, room, DAYS[day], TIMES[time], have_lesson, more_lesson)
                        print err.decode('cp1251').encode('cp866'), " \t row=", row
                        
                        cr_scedule[room][(day,time)] = '"' + have_lesson + more_lesson + '"'
                    else:
                        cr_scedule[room][(day,time)] = '"' + more_lesson + '"'


if __name__ == '__main__':
    cr_scedule = {} # free dict
    for room in ROOMS:
        cr_scedule[room] = {} # append room-keys
    
    for file in os.listdir(INPUT_DIR):
        if (file.endswith(".csv")):
            #try:
            parse_scedule(os.path.join(INPUT_DIR, file), cr_scedule)
            #except: print "error: ", os.path.join(INPUT_DIR, file)
    
    with io.open(FNAME_OUT, 'wt', encoding="utf-8-sig") as f_out:
        f_out.write(u" ,{:14s}".format(' '))
        for room in ROOMS:
            f_out.write(u", {:54s}".format(room))
        f_out.write(u"\n")
        
        for day in xrange(len(DAYS)):
            for time in xrange(len(TIMES)):
                sday = unicode(DAYS[day] if (time==0) else '   ', encoding="cp1251")
                time_period = unicode(TIMES[time], encoding="cp1251")
                f_out.write(u"{:s},{:s}".format(sday, time_period))
                for room in ROOMS:
                    key = (day,time)
                    lesson = cr_scedule[room][key] if cr_scedule[room].has_key(key) else " "
                    lesson = unicode(",{0:55s}".format(lesson), encoding="cp1251")
                    f_out.write(lesson)
                f_out.write(u"\n")
    
