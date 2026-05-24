import os
import sys
import sqlite3
from datetime import datetime, date, time, timezone
from dataclasses import dataclass
import time
import random
import hashlib

import sqlite3
import subprocess

# times played, note pressed, how long note was pressed, 
class Timer:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0

    def start_timer(self):
        self.start_time = time.time()

    def stop_timer(self):
        self.end_time = time.time()

    def check_timer(self):
        return time.time() - self.start_time

    def reset_timer(self):
        start_time = 0

class Note:
    def __init__(self, name):
        self.name = name
        self.times_played = 0
        self.total_times_pressed = 0
        self.note_pressed_on = False
        self.time_stats = Timer()
        self.current_note_time = 0.0
        self.total_time = 0.0
        global note_tracker_dict



def note_dict_init():
    c = Note("C")
    c_sharp = Note("C#")
    d = Note("D")
    d_sharp = Note("D#")
    e = Note("E")
    f = Note("F")
    f_sharp = Note("F#")
    g = Note("G")
    g_sharp = Note("G#")
    a = Note("A")
    a_sharp = Note("A#")
    b = Note("B")

    note_dict = {
        'A': a,
        'A#': a_sharp,
        'B': b,    
        'C': c,
        'C#': c_sharp,
        'D': d,
        'D#': d_sharp,
        'E': e,
        'F': f,
        'F#': f_sharp,
        'G': g,
        'G#': g_sharp
    }

    return note_dict



# Check to see if file exists, if so create the filepath, if not: create the dir and return the filepath
def db_create_filepath(db_file_name):
    if not os.path.exists("./db"):
        subprocess.run(["mkdir", "-p", f"./db/"])

    # Create full db_filepath
    if not os.path.exists(f"./db/{db_file_name}.db"):
        try:
            fp = str(f"./db/{db_file_name}.db")
            db_conn = get_db_connection(fp)
            db_cursor = db_conn.cursor()
            initalize_totals_db(db_file_name, db_cursor)
            
            db_conn.commit()
            db_conn.close()
            #print(f"DB Filepath Created: {fp}")
            return fp
        except OSError as error:
            print(error)
    



# Get DB connection
def get_db_connection(db_filepath):
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn


def db_create_filepath(db_name):
    # Create a directory leading up the the db's name, but not for the db_name. If only db name is supplied, and 'db' dir isn't present - make the 'db' dir
    if not os.path.exists(f"./db"):
        subprocess.run(["mkdir", "-p", f"./db/"])

    fp = str(f"./db/{db_name}.db")

    # Create full db_filepath
    if not os.path.exists(f"./db/{db_name}.db"):
        try:
            db_conn = get_db_connection(fp)
            db_cursor = db_conn.cursor()
            initalize_totals_db(db_name, db_cursor)
            
            db_conn.commit()
            db_conn.close()
            #print(f"DB Filepath Created: {fp}")
            return fp
        except OSError as error:
            print(error)
    else:
        return fp

def initalize_totals_db(session_name, db_cursor):
    try: 
        if session_name != 'LIFETIME':
            current_session_table = "day_totals"
        else:
            current_session_table = session_name

        create_table_session_totals = f"""CREATE TABLE IF NOT EXISTS {current_session_table} (
                        name TEXT, 
                        total_notes_played INTEGER, 
                        total_note_time_played FLOAT, 
                        runtime FLOAT,
                        note_name TEXT,
                        note_times_played INTEGER,
                        note_time_total FLOAT);"""
        db_cursor.execute(create_table_session_totals)
        print(f"session_table {current_session_table} created")

        db_cursor.execute(f'''INSERT INTO {current_session_table} DEFAULT VALUES;''')


        notes_dict = note_dict_init()
        initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor)

    except sqlite3.Error as error:

        print(f"Failed to initalize {current_session_table} table", error)                       

def initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor):
    try:    
        sqlite_insert_query = f"""INSERT INTO {current_session_table}
                          (note_name, note_times_played, note_time_total) 
                          VALUES (?, ?, ?);""" 

        for note_name in notes_dict.keys():
            #note_name = n
            note_times_played = notes_dict[note_name].times_played
            note_time_total = notes_dict[note_name].total_time 

            note_record = (note_name, note_times_played, note_time_total)  
#            if debug:
#                print(f"note_name: {note_name}\nnote_times_played: {note_times_played}\nnote_time_total: {note_time_total}")
        
            db_cursor.execute(sqlite_insert_query, note_record)
        
#        print(f"Initalized Note stats in {db_day_filepath} for {current_session_table}")            
    except sqlite3.Error as error:
        print(f"Failed to insert session_notes into {current_session_table} of db_day", error)










def add_session_to_db_day(current_session_dict, db_cursor):
    try: 
        session_name = current_session_dict["session_name"]
        session_total_notes_played = current_session_dict["total_notes_played"]
        session_total_note_time_played = current_session_dict["note_time_played"]
        session_start = current_session_dict["session_start"]
        session_end = current_session_dict["session_end"]
        session_runtime = current_session_dict["total_session_runtime"]
        current_session_table = current_session_dict["table_name"]

        session_data = (session_name, session_total_notes_played, session_total_note_time_played, session_start, session_end, session_runtime)
        create_table_session_totals = f"""CREATE TABLE IF NOT EXISTS {current_session_table} (
                        name INTEGER, 
                        total_notes_played INTEGER, 
                        total_note_time_played FLOAT, 
                        start FLOAT, 
                        end FLOAT, 
                        runtime FLOAT,
                        note_name TEXT,
                        note_times_played INTEGER,
                        note_time_total FLOAT);"""
        db_cursor.execute(create_table_session_totals)
        print(f"session_table {current_session_table} created")

        init_session_db = f"""INSERT INTO {current_session_table}
                        (name, total_notes_played, total_note_time_played, start, end, runtime)
                        VALUES (?, ?, ?, ?, ?, ?);"""                        
        db_cursor.execute(init_session_db, session_data)

        add_session_notes_to_db(current_session_dict["total_notes"], current_session_table, db_cursor)

    except sqlite3.Error as error:
        print(f"Failed to initalize {current_session_table} table", error)                       

 

def add_session_notes_to_db(notes_dict, current_session_table, db_cursor):
    try:    
        sqlite_insert_query = f"""INSERT INTO {current_session_table}
                          (note_name, note_times_played, note_time_total) 
                          VALUES (?, ?, ?);""" 

        for note_name in notes_dict.keys():

            note_times_played = notes_dict[note_name].times_played
            note_time_total = notes_dict[note_name].total_time 

            note_record = (note_name, note_times_played, note_time_total)  
    
            db_cursor.execute(sqlite_insert_query, note_record)
        
    except sqlite3.Error as error:
        print(f"Failed to insert session_notes into {current_session_table} of db_day", error)





def update_db_day_and_db_lifetime(current_session_dict, db_day_cursor, db_LIFETIME_cursor):
    columns = ("total_notes_played", "total_note_time_played", "runtime")
    totals_cursors = (db_day_cursor, db_LIFETIME_cursor)
    current_session_table = current_session_dict["table_name"]
    
    
    for rowid in range(1, 14):
        if rowid > 1:
            columns = ("note_times_played", "note_time_total")
        sum_session_db_and_totals_db(totals_cursors, current_session_table, columns, rowid)

def sum_session_db_and_totals_db(totals_cursors, current_session_table, cols, rowid):
    db_day_cursor = totals_cursors[0]

    totals_table_index = 0
    totals_table_tuple = ("day_totals", "LIFETIME")

    for totals_cursor in totals_cursors:    
        totals_table = totals_table_tuple[totals_table_index]

        session_value_query = f'''SELECT * FROM {current_session_table} WHERE rowid = {rowid}'''
        session_query_results_list = db_day_cursor.execute(session_value_query).fetchall()
        session_query_results_row = session_query_results_list[0]

        totals_value_query = f'''SELECT * FROM {totals_table} WHERE rowid = {rowid}'''
        totals_query_results_list = totals_cursor.execute(totals_value_query).fetchall()
        totals_query_results_row = totals_query_results_list[0]
        print(type(totals_query_results_row))

        for col in cols:
            totals_value = totals_query_results_row[col]
            session_value = session_query_results_row[col]

            print(totals_value)
            print(session_value)
            if totals_value == None:
                totals_value = 0

                new_total = session_value + totals_value

            elif type(totals_value) is str:
                new_total = session_value
            
            else:
                new_total = session_value + totals_value

            
            
            print(new_total)

    #        totals_cursor.execute(f'''INSERT OR REPLACE INTO {totals_table} ({col}) VALUES ({new_total}) WHERE rowid = {rowid};''')
            totals_cursor.execute(f"UPDATE {totals_table} SET {col} = ? WHERE rowid = ?;", (new_total, rowid))    
        
        totals_table_index += 1



# This is for the automated sleep program -- Wait for runtime to expire before running program again to increase realism
def update_runtime_info_file(previous_session_name, runtime, fp="session_info.py"):
    with open(f'./{fp}', "w") as file:
        file.write(f'previous_session_name = {previous_session_name}\n')
        file.write(f'previous_session_runtime = {runtime}\n')
    file.close()



def print_current_session(current_session):
    os.system('clear')
    print("\t\t\tCURRENT SESSION STATS")
    print(f'\nSESSION NAME: {current_session["session_name"]}')
#          print(f'Total Session Runtime: {db_day["session_dict"][current_session]["session_runtime"]}')
    print(f'SESSION TIME ELAPSED: {current_session["total_session_runtime"]}')

    print(f"\n+-------------- Total Notes Played: {current_session['total_notes_played']} --------------+\
    \n+-------------- Total Time Pressed: {current_session['note_time_played']} --------------+\n\n")

    # Find and print total note stats
    print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
    for note, val in current_session["total_notes"].items():
        print(f"{note}\t\t\t{val.times_played}\t\t\t\t{val.total_time}")  

    print('\n\n\nend')

