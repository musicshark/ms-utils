import os
import sys
import sqlite3
from datetime import datetime, date, time, timezone
from dataclasses import dataclass
import time
import random

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


# Check to see if file exists, if so create the filepath, if not: create the dir and return the filepath
def db_create_filepath(version, db_file_name):
    if not os.path.exists("./db"):
        os.system("mkdir db")

    if not os.path.exists(f"db/{db_file_name}.db"):
        try:
            fp = str(f"db/{db_file_name}.db")
            #os.system(f'touch {fp}')
            #print(f"DB Filepath Created: {fp}")
            return fp
        except OSError as error:
            print(error)

    elif os.path.exists(f"db/{db_file_name}.db"):
        fp = str(f"./db/{db_file_name}.db")
        print(f"Existing DB Filepath: ./db/{db_file_name}.db")
        return fp

def init_db(db):
    db["total_notes"] = note_dict_init()
    db["total_notes_played"] = 0
    db["note_time_played"] = 0.0
    db["session_dict"] = dict()

    if debug == True: 
        print(f"DB INIT: {db}")


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

def initalize_day_table_to_db(db_day_filepath):
    global debug 

    try: 
        conn = sqlite3.connect(db_day_filepath)
        print(f"Connected to {db_day_filepath} for initalize_day_table_to_db()")
        cursor = conn.cursor()

        #db_file_day = datetime.now().strftime("%Y%m%d")
        db_file_day = datetime.now().strftime("%Y%m%M")
        
        day_name = db_file_day
        day_total_notes_played = 0
        day_total_note_time_played = 0.0
        day_start = time.time()
        day_end = 0.0
        day_runtime = 0.0

        create_table_day_totals = f"""CREATE TABLE IF NOT EXISTS day_totals (
                name INTEGER, 
                total_notes_played INTEGER, 
                total_note_time_played FLOAT, 
                start FLOAT, 
                end FLOAT, 
                runtime FLOAT,
                note_name TEXT,
                note_times_played INTEGER,
                note_time_total FLOAT);"""
        cursor.execute(create_table_day_totals)
        print(f"day_totals table created")

        day_data = (day_name, day_total_notes_played, day_total_note_time_played, day_start, day_end, day_runtime)
        init_day_db = f"""INSERT INTO day_totals
                        (name, total_notes_played, total_note_time_played, start, end, runtime)
                        VALUES (?, ?, ?, ?, ?, ?);"""                        
        cursor.execute(init_day_db, day_data)
        conn.commit()

        notes_dict = note_dict_init()
        initalize_session_notes_to_db(notes_dict, "day_totals", conn)
        conn.commit()

        if debug == True:
            print(f'\n\nday_totals:')
            cursor.execute(f"SELECT * FROM day_totals")
            print(cursor.fetchall())

    except sqlite3.Error as error:
        print(f"Failed to initalize {day_name} table", error)
    finally:
        if conn:
            conn.close()
            print(f"Connection to {db_day_filepath} is closed")

def initalize_session_stats_to_db(current_session_dict, db_cursor):
    try: 
        session_name = current_session_dict["session_name"]
        session_total_notes_played = current_session_dict["total_notes_played"]
        session_total_note_time_played = current_session_dict["note_time_played"]
        session_start = current_session_dict["session_start"]
        session_end = current_session_dict["session_end"]
        session_runtime = current_session_dict["total_session_runtime"]

        current_session_table = str(f"session_{session_name}")

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

        notes_dict = current_session_dict["total_notes"]
        initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor)

        if debug == True:
            db_cursor.execute(f"SELECT * FROM {current_session_table}")
            print(db_cursor.fetchall())

            print(f'\n\nday_totals:')
            db_cursor.execute(f"SELECT * FROM day_totals")
            print(db_cursor.fetchall())

    except sqlite3.Error as error:
        print(f"Failed to initalize {current_session_table} table", error)                       

def initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor):
    try:    
        sqlite_insert_query = f"""INSERT INTO {current_session_table}
                          (note_name, note_times_played, note_time_total) 
                          VALUES (?, ?, ?);""" 

        for n in notes_dict.keys():
            note_name = n
            note_times_played = notes_dict[n].times_played
            note_time_total = notes_dict[n].total_time 

            note_record = (note_name, note_times_played, note_time_total)  
            if debug:
                print(f"note_name: {note_name}\nnote_times_played: {note_times_played}\nnote_time_total: {note_time_total}")
        
            db_cursor.execute(sqlite_insert_query, note_record)
        
        print(f"Initalized Note stats in {db_day_filepath} for {current_session_table}")            
    except sqlite3.Error as error:
        print(f"Failed to insert session_notes into {current_session_table} of db_day", error)


def initalize_db_LIFETIME(db_LIFETIME_filepath):
    global debug 

    try: 
        conn = sqlite3.connect(db_LIFETIME_filepath)
        print(f"Connected to {db_LIFETIME_filepath}")
        cursor = conn.cursor()
        
        LIFETIME_name = "LIFETIME"
        current_session_table = "LIFETIME"
        LIFETIME_notes_played = 0
        LIFETIME_note_time_played = 0.0
        LIFETIME_runtime = 0.0

        LIFETIME_data = (LIFETIME_name, LIFETIME_notes_played, LIFETIME_note_time_played,LIFETIME_runtime)
        
        create_LIFETIME_table = f"""CREATE TABLE IF NOT EXISTS {LIFETIME_name} (
                        name TEXT, 
                        total_notes_played INTEGER, 
                        total_note_time_played REAL, 
                        runtime REAL,
                        date_list INTEGER,
                        note_name TEXT,
                        note_times_played INTEGER,
                        note_time_total REAL);""" 
        cursor.execute(create_LIFETIME_table)
        
        init_LIFETIME_db = f"""INSERT INTO {LIFETIME_name}
                        (name, total_notes_played, total_note_time_played, runtime)
                        VALUES (?, ?, ?, ?);"""
        cursor.execute(init_LIFETIME_db, LIFETIME_data)

        notes_dict = note_dict_init()
        initalize_session_notes_to_db(notes_dict, LIFETIME_name, conn)
        initalize_LIFETIME_current_session_table(cursor, 0, notes_dict, conn)

        conn.commit()

        if debug == True:
            cursor.execute(f"SELECT * FROM {LIFETIME_name}")
            print(cursor.fetchall())

    except sqlite3.Error as error:
        print(f"Failed to initalize {LIFETIME_name} table", error)
    finally:
        if conn:
            conn.close()
            print(f"Connection to {db_LIFETIME_filepath} is closed")

def initalize_LIFETIME_current_session_table(cursor, name, notes_dict, conn): 
    session_name = name
    session_notes_played = 0
    session_note_time_played = 0
    session_runtime = 0
    session_data = (session_name, session_notes_played, session_note_time_played, session_runtime)
       
    create_current_session_table = f"""CREATE TABLE IF NOT EXISTS current_session (
                    name INTEGER, 
                    total_notes_played INTEGER, 
                    total_note_time_played REAL, 
                    runtime REAL,
                    note_name TEXT,
                    note_times_played INTEGER,
                    note_time_total REAL);"""
    cursor.execute(create_current_session_table)

    init_session_db = f"""INSERT INTO current_session
                    (name, total_notes_played, total_note_time_played, runtime)
                    VALUES (?, ?, ?, ?);"""
    cursor.execute(init_session_db, session_data)

    initalize_session_notes_to_db(notes_dict, "current_session", conn)


def update_session_stats_to_db(current_session_dict, db_day_filepath):
    try: 
        conn = sqlite3.connect(db_day_filepath)
        #print(f"Connected to {db_day_filepath}")
        cursor = conn.cursor()
        
        session_name = current_session_dict["session_name"]
        session_total_notes_played = current_session_dict["total_notes_played"]
        session_total_note_time_played = current_session_dict["note_time_played"]
        session_end = current_session_dict["session_end"]
        session_runtime = current_session_dict["total_session_runtime"]
        current_session_table = str(f'session_{session_name}')
        if debug:
            print(type(current_session_dict["total_session_runtime"]))

        values = (session_total_notes_played, session_total_note_time_played, session_end, session_runtime)
        
        cursor.execute(f"""UPDATE {current_session_table}
                          SET (total_notes_played, total_note_time_played, end, runtime) = (?, ?, ?, ?)""", (values))

        conn.commit()
        #print(f"Updated Session {session_name} Stats")   

        notes_dict = current_session_dict["total_notes"]
        update_session_note_values_to_db(notes_dict, current_session_table, conn)
    
    except sqlite3.Error as error:
        print(f"Failed to update Session {current_session_table} Stats", error)
    finally:
        if conn:
            conn.close()
            #print(f"Connection to {db_day_filepath} is closed")

def update_session_note_values_to_db(notes_dict, current_session_table, conn):
    try:
        cursor = conn.cursor()
        #print(f"Connected to {db_day_filepath}")

        for n in notes_dict.keys():
            note_name = n
            note_times_played = notes_dict[n].times_played
            note_time_total = notes_dict[n].total_time 

            # Update times_played/note
            cursor.execute(f"""UPDATE {current_session_table}
                              SET note_times_played = ? WHERE note_name = ?""", (note_times_played, note_name))

            # Update note_time_total/note
            cursor.execute(f"""UPDATE {current_session_table}
                              SET note_time_total = ? WHERE note_name = ?""", (note_time_total, note_name))
        
        conn.commit()
        #print(f"Updated Note stats in {db_day_filepath} for {current_session_table}")  

    except sqlite3.Error as error:
        print(f"Failed to update session {current_session_table} note values", error)

def increment_note_stats_to_table(current_session_note_dict, current_note, db_cursor, col, db_name):
    if db_name == "db_day":
        table_name = "day_totals"
    elif db_name == "db_LIFETIME":
        table_name = "LIFETIME"

    #print(f"current_note: {current_note}")
    res1 = db_cursor.execute(f'''SELECT {col} FROM {table_name} WHERE note_name = ?;''', (current_note,))
    res1_list = res1.fetchall()
    #print(f"res1_list[0]: {res1_list[0]} - {table_name} - {db_name}")
    res1_tuple = res1_list[0]
    #print(f"res1_tuple[0]: {res1_tuple[0]} - {table_name} - {db_name}")

    new_total = 0

    if col == "note_times_played":
        new_total = current_session_note_dict["total_notes"][current_note].times_played

    elif col == "note_time_total":
        new_total = float(res1_tuple[0]) + current_session_note_dict["total_notes"][current_note].total_time
 
    
    db_cursor.execute(f"""UPDATE {table_name}
                        SET {col} = ?
                        WHERE note_name = ?;""", (new_total, current_note))
        
    #if db_name == "db_day":
    #    db_cursor.execute(f"""UPDATE day_totals
    #                SET {col} = ?
    #                WHERE note_name = ?;""", (new_total, current_note))
        
    #print(f"new_total: {new_total} - {table_name} - {db_name} - {col}")

def increment_total_stats_to_table(current_session_note_dict, db_cursor, col, db_name):
    if db_name == "db_day":
        table_name = "day_totals"
    elif db_name == "db_LIFETIME":
        table_name = "LIFETIME"

    res1 = db_cursor.execute(f'''SELECT {col} FROM {table_name};''')# WHERE name = ?;''', (table_name, ))
    res1_list = res1.fetchall()
    #print(f"res1_list[0]: {res1_list[0]} - {table_name} - {db_name} - {col}")
    res1_tuple = res1_list[0]
    #print(f"res1_tuple[0]: {res1_tuple[0]} - {table_name} - {db_name} - {col}")

    new_total = 0
    
    if col == "total_notes_played":
        new_total = current_session_note_dict["total_notes_played"]
    
    elif col == "total_note_time_played":
        new_total = current_session_note_dict["note_time_played"]

    db_cursor.execute(f"""UPDATE {table_name}
                        SET {col} = ?;""", (new_total, ))
    
    #print(f"new_total: {new_total} - {table_name} - {db_name} - {col}")

def update_table_with_runtime_and_session_end(db_cursor, session_end, runtime, table_name):
    global db_LIFETIME_filepath
    previous_session_name = get_previous_session_name(db_LIFETIME_filepath)

    print(f"session_end: {session_end}\truntime: {runtime}")
    runtime_total = 0
    
    res1 = db_cursor.execute(f'''SELECT runtime FROM {table_name}''')
    res1_list = res1.fetchall()
    res1_tuple = res1_list[0]
    runtime_total = res1_tuple[0] + runtime
    db_cursor.execute(f'''UPDATE {table_name} SET runtime = ?;''', (runtime_total, ))

    if table_name == 'day_totals' or table_name == previous_session_name:
        db_cursor.execute(f'''UPDATE {table_name} SET end = ?;''', (session_end, ))

def update_current_session_table_name(db_cursor, session_name):
    db_cursor.execute(f'''UPDATE current_session
                        SET name = ?''', (session_name,))

def init_current_session_dict():
    current_session_dict = dict()
    current_session_dict["total_notes"] = note_dict_init()
    current_session_dict["total_notes_played"] = 0
    current_session_dict["note_time_played"] = 0.0
    current_session_dict["session_dict"] = dict()
    current_session_dict["session_name"] = str(f"{datetime.now().strftime('%H%M%S')}")
    current_session_dict["session_start"] = 0.0
    current_session_dict["session_end"] = 0
    current_session_dict["total_session_runtime"] = 0
    current_session_dict["total_session_notes_played"] = dict()
    
    print(f"NEW current_session_dict CREATED")
    print(f'current_session_dict["session_name"]: {current_session_dict["session_name"]}')

    return current_session_dict

# Generate total session notes
def generate_session_total_notes(session_type):
    match session_type:
        case "short":
            MIN_NOTES = 126
            MAX_NOTES = 2500

        case "medium":
            MIN_NOTES = 2430
            MAX_NOTES = 3600

        case "long":
            MIN_NOTES = 3560
            MAX_NOTES = 5125

        case "test":
            MIN_NOTES = 10
            MAX_NOTES = 20

        case _:
            print(f"ERROR: session_total_notes case statement")

    return random.randint(MIN_NOTES, MAX_NOTES)

# Generate random session playtime
def generate_total_session_playtime(session_type):
    match session_type:
        case "short":
            MIN_TIME = 186.9
            MAX_TIME = 1243.3

        case "medium":
            MIN_TIME = 1134.2
            MAX_TIME = 2293.7

        case "long":
            MIN_TIME = 2148.4
            MAX_TIME = 7322.8

        case "test":
            MIN_TIME = 10.0
            MAX_TIME = 15.0

        case _:
            print(f"ERROR: find_total_session_playtime case statement")

    #print(f"{random.uniform(MIN_TIME, MAX_TIME)}")
    return random.uniform(MIN_TIME, MAX_TIME)
        

def add_notes_to_session_dict(current_session_dict, total_session_notes):
    # Split total notes in session between each note in dict
    print(f"total_session_notes = {total_session_notes}")
    random_number_array = []
    for n in range(12):
        random_number = random.randint(0, int(total_session_notes * .8))

        if random_number < 1 and random_number > 0:
            random_number_array.append(1)
            total_session_notes -= random_number
            continue

        if random_number == 0:
            random_number_array.append(0)
            continue 

        random_number_array.append(random_number)
        total_session_notes -= random_number

    for note, val in current_session_dict["total_notes"].items():
        val.times_played = random.choice(random_number_array)
        random_number_array.remove(val.times_played)

# Assign random playtimes to each note - derived from session total playtime
def add_note_playtime_to_dict(current_session_dict, total_session_playtime):
    #print(f"total_session_playtime = {total_session_playtime}")

    random_number_array = []
    for note, val in current_session_dict["total_notes"].items():
        #if total_session_playtime < .5:
        #    random_number_array.append(total_session_playtime)
        #    total_session_playtime = 0
        if val.times_played > 0:
            rand_number = total_session_playtime * random.uniform(.2, .4)
            random_number_array.append(rand_number)
            total_session_playtime -= rand_number
        else:
            random_number_array.append(0)
    total = 0.0
    #print(f"rand_array len: {len(random_number_array)}")
    for note, val in current_session_dict["total_notes"].items():
        val.total_time = random.choice(random_number_array)
        #print(f"{note}.total_time = {val.total_time}")
        random_number_array.remove(val.total_time)
        total += val.total_time

    print(total)

def start_session(db_day_filepath, db_LIFETIME):
    global midi_list 
    global note_input
    global note_time 
    global note_tracker_dict
    global db_synced
    global note_pressed
    global new_session_dict
    global note_idle_timer
    global db_day_date
    
    midi_list, note_input, note_time, note_tracker_dict = program_init()

    current_session_dict = init_current_session_dict() 
    #session_type = random.choice(["short", "medium", "long"])
    session_type = "test"

    db_day_conn = sqlite3.connect(db_day_filepath)
    db_day_cursor = db_day_conn.cursor()

    db_LIFETIME_conn = sqlite3.connect(db_LIFETIME_filepath)
    db_LIFETIME_cursor = db_LIFETIME_conn.cursor()


    try:
        # Add current_session_dict to the day_db file here
        initalize_session_stats_to_db(current_session_dict, db_day_cursor)
        db_day_conn.commit()

        update_current_session_table_name(db_LIFETIME_cursor, current_session_dict["session_name"])
        db_LIFETIME_conn.commit()

    except Exception as e:
        print(f'\nEXCEPTION CAUGHT DURING NEW SESSION DB CREATION: {e}')
        print("\nDAY_DB FILE CORRUPTED!!!!!!\n")
        dispatcher["menu"](db_day_filepath, db_LIFETIME_filepath)

        
#    total_notes_played = current_session_dict["total_notes_played"]
#    total_note_time = current_session_dict["note_time_played"]
#
#    for note, val in current_session_dict["total_notes"].items():
#        notes_played = random.randint(15, 2516)
#        val.times_played = notes_played
#        current_session_dict["total_notes_played"] += notes_played
#        #print(total_notes_played)
#
#        note_time_min = float(notes_played * .2)
#        note_time_max = float(notes_played * 1.5)
#        
#        val.total_time = random.uniform(note_time_min, note_time_max)
#        current_session_dict["note_time_played"] += val.total_time
#
#    update_session_stats_to_db(current_session_dict, db_day_filepath)
#

    print(f"Session Type: {session_type}")
    current_session_dict["total_notes_played"] = generate_session_total_notes(session_type)
    print(f"current_session_dict TNP: {current_session_dict["total_notes_played"]}")

    current_session_dict["note_time_played"] = generate_total_session_playtime(session_type)
    #print(f"current_session_dict NTP: {current_session_dict['note_time_played']}")

    add_notes_to_session_dict(current_session_dict, current_session_dict["total_notes_played"])
    add_note_playtime_to_dict(current_session_dict, current_session_dict["note_time_played"])

    for note, val in current_session_dict["total_notes"].items():        
        increment_note_stats_to_table(current_session_dict, val.name, db_day_cursor, "note_times_played", "db_day")
        increment_note_stats_to_table(current_session_dict, val.name, db_LIFETIME_cursor, "note_times_played", "db_LIFETIME")

        increment_note_stats_to_table(current_session_dict, val.name, db_day_cursor, "note_time_total", "db_day")
        increment_note_stats_to_table(current_session_dict, val.name, db_LIFETIME_cursor, "note_time_total", "db_LIFETIME")
                   
    #update_session_stats_to_db(current_session_dict, db_day_filepath)

    increment_total_stats_to_table(current_session_dict, db_day_cursor, "total_notes_played", "db_day")
    increment_total_stats_to_table(current_session_dict, db_LIFETIME_cursor, "total_notes_played", "db_LIFETIME")

    increment_total_stats_to_table(current_session_dict, db_day_cursor, "total_note_time_played", "db_day")
    increment_total_stats_to_table(current_session_dict, db_LIFETIME_cursor, "total_note_time_played", "db_LIFETIME")
    
    current_session_dict["session_end"] = current_session_dict["note_time_played"] + random.uniform(2.1, 4400.8)
    session_end = current_session_dict["session_end"]

    current_session_dict["total_session_runtime"] = session_end
    session_runtime = current_session_dict["total_session_runtime"]

    db_day_conn.commit()
    db_LIFETIME_conn.commit()
                
    update_table_with_runtime_and_session_end(db_LIFETIME_cursor, session_end, session_runtime, 'LIFETIME')
    update_table_with_runtime_and_session_end(db_day_cursor, session_end, session_runtime, 'day_totals')
    update_table_with_runtime_and_session_end(db_day_cursor, session_end, session_runtime, f'session_{current_session_dict["session_name"]}')
            
    db_day_conn.commit()
    db_LIFETIME_conn.commit()

    print_current_session(current_session_dict)

    #print(datetime.fromtimestamp(current_session_dict["session_end"]))
    print('\n\n\nend')

    db_day_conn.close()
    db_LIFETIME_conn.close()   

    #dispatcher['menu'](db_day_filepath, db_LIFETIME_filepath)

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

def menu(db_day_filepath, db_LIFETIME_filepath):

    try:
        print('Please choose from the following options: \n')
        print('1) Start: Start the program')
        print('2) Run program "n" times')
        print('3) Show Stats')
        print('4) Help: Show help')
        #print('36) Update MidiShark')
#        print('4) Exit')
    
        user_input = input()
        match user_input:
            case '1':
                dispatcher['start'](db_day_filepath, db_LIFETIME_filepath)
            case '2':
                times_to_run = input("How many times to run the program")
                for _ in range(0, times_to_run):
                    dispatcher['start'](db_day_filepath, db_LIFETIME_filepath)
            case '3':
                os.system("clear")
                print("Please choose an option")
                print("1) Previous Session")
                print("2) Day Totals")
                print("3) Lifetime Totals")
                stat_type = input()
                dispatcher['print_totals'](stat_type, db_day_filepath, db_LIFETIME_filepath)
            case '4':
                dispatcher['help']()
            case '5':
                dispatcher['troubleshooting'](db_day_filepath, db_LIFETIME_filepath)
            case '36':
                dispatcher['update-midishark']
            case '251':
                dispatcher['exit']()
            case _: 
                print("\nPlease select an option by inputing a number\n")
                dispatcher['menu'](db_day_filepath, db_LIFETIME_filepath)

    except KeyboardInterrupt:
        menu(db_day_filepath, db_LIFETIME_filepath)


def get_previous_session_name(db_LIFETIME_filepath) -> str:
    conn = sqlite3.connect(db_LIFETIME_filepath)
    cursor = conn.cursor()

    res = cursor.execute(f"""SELECT name FROM current_session""")
    session_name_list = res.fetchall()

    session_name = session_name_list[0]
    if int(session_name[0]) < 9999:
        return str(f"session_00{session_name[0]}")
    elif int(session_name[0]) < 99999:
        return str(f"session_0{session_name[0]}")
    elif int(session_name[0]) < 999999:
        return str(f"session_{session_name[0]}")
    else:
        print(f"INVALID SESSION NAME: {session_name}")

    conn.close()
 
def get_db_values(db_filepath, table, stat_name):
    # Get values from DB, return trimmed values
    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()
    return_list = list()

    # Name (If not previous session)
    if stat_name != "Previous Session Stats":
        name_res = cursor.execute(f"""SELECT name from {table}""")
        name_res_list = name_res.fetchall()
        name = name_res_list[0]
    else:
        name = table
    return_list.append(name[0])

        # Session Start
    if stat_name != "Lifetime Totals":
        start_res = cursor.execute(f"""SELECT start from {table}""")
        start_res_list = start_res.fetchall()
        start = start_res_list[0]    
        # Sesssion End  
        end_res = cursor.execute(f"""SELECT end from {table}""")
        end_res_list = end_res.fetchall()
        end = end_res_list[0]
    else:
        start = (0, )
        end = (0, )
    return_list.append(start[0])
    return_list.append(end[0])

    # Runtime
    runtime_res = cursor.execute(f"""SELECT runtime from {table}""")
    runtime_res_list = runtime_res.fetchall()
    runtime = runtime_res_list[0]
    
    return_list.append(runtime[0])

    # Total Notes Played
    total_notes_played_res = cursor.execute(f"""SELECT total_notes_played from {table}""")
    total_notes_played_res_list = total_notes_played_res.fetchall()
    total_notes_played = total_notes_played_res_list[0]
    
    return_list.append(total_notes_played[0])

    # Total Note Time Played
    total_note_time_played_res = cursor.execute(f"""SELECT total_note_time_played from {table}""")
    total_note_time_played_res_list = total_note_time_played_res.fetchall()
    total_note_time_played = total_note_time_played_res_list[0]
    
    return_list.append(total_note_time_played[0])

    # Note Times Played
    note_times_played_final_list = list()
    note_times_played_res = cursor.execute(f"""SELECT note_times_played from {table}""")
    note_times_played_res_list = note_times_played_res.fetchall()

    for n in range(1, 13):
        note_times_played_list = note_times_played_res_list[n]
        note_times_played = note_times_played_list[0]
        note_times_played_final_list.append(note_times_played)
    
    return_list.append(note_times_played_final_list)

    # Note Time Total
    note_time_total_final_list = list()
    note_time_total_res = cursor.execute(f"""SELECT note_time_total from {table}""")
    note_time_total_res_list = note_time_total_res.fetchall()

    for n in range(1, 13):
        note_time_total_list = note_time_total_res_list[n]
        note_time_total = note_time_total_list[0]
        note_time_total_final_list.append(note_time_total)
    
    return_list.append(note_time_total_final_list)

    conn.close()
    return return_list 


def print_totals(stat_type, db_day_filepath, db_LIFETIME_filepath):
    '''
    STAT_NAME
    only session_start/end if not LIFETIME -- if LIFETIME only use runtime
    '''
    stat_name = str()
    db_filepath = str()

    match stat_type:
        case "1":
            db_filepath = db_day_filepath
            table = get_previous_session_name(db_LIFETIME_filepath)
            stat_name = "Previous Session Stats"
            
    # Current Day totals
        case "2":
            db_filepath = db_day_filepath
            table = "day_totals"
            stat_name = "Day Totals"

    # Lifetime totals
        case "3": 
            db_filepath = db_LIFETIME_filepath
            table = "LIFETIME"
            stat_name = "Lifetime Totals"

    # Custom totals
        case _:
            print("\nPlease select an option by inputing a number\n")
            dispatcher['menu'](db_day_filepath, db_LIFETIME_filepath)

    values_list = get_db_values(db_filepath, table, stat_name)
    name = values_list[0]
    start = values_list[1]
    end = values_list[2]
    runtime = values_list[3]
    total_notes_played = values_list[4]
    total_note_time_played = values_list[5]
    note_times_played = values_list[6]
    note_time_toal = values_list[7]
    note_dict = note_dict_init()
    note_stats_index = 0
    
    os.system('clear')            
    print(f"\t\t{stat_name}")
    if stat_name != "Lifetime Totals":
        print(f'SESSION START: {datetime.fromtimestamp(start)}')
        print(f'SESSION END: {datetime.fromtimestamp(end)}')
    
    print(f'Runtime: {runtime}')

    print(f"\n+-------------- Total Notes Played: {total_notes_played} --------------+\
            \n+-------------- Total Note Time Played: {total_note_time_played} --------------+\n\n")

    # Find and print total note stats
    print(f"Note\t\tNote Times Played\t\tNote Time Total")
    for note, val in note_dict.items():
        print(f"{note}\t\t\t{note_times_played[note_stats_index]}\t\t\t\t{note_time_toal[note_stats_index]}")
        note_stats_index += 1

    dispatcher['menu'](db_day_filepath, db_LIFETIME_filepath)


def help():
    print("Feature not yet available\n")
    dispatcher["menu"](db_day_filepath, db_LIFETIME_filepath)

def tutorial():
    print("Feature not yet available\n")
    dispatcher['menu'](db_day_filepath, db_LIFETIME_filepath)

def troubleshooting(db_day_filepath, db_LIFETIME_filepath):
    global debug
    os.system('clear')
    print(f'Please choose from the following:')
    print(f'1) Toggle Debug mode\n2) Delete db_day file\n3) Delete LIFETIME_db file')
    choice = input()
    match choice:

        # Toggle debug
        case '1':
            if debug == True:
                debug = False
            elif debug == False:
                debug = True
            
            dispatcher["menu"](db_day_filepath, db_LIFETIME_filepath)


        # Delete day_db file and create a new one
        case '2':
            os.system(f'rm -dfv {db_day_filepath}')

            db_file_day = datetime.now().strftime("%Y%m%d")
            db_day_date = str(f"{db_file_day}")
            db_day_filepath = db_create_filepath(version, db_day_date)
            if not os.path.exists(f"{db_day_filepath}"):
                initalize_day_table_to_db(db_day_filepath)

            print("DAY_DB_FILE created")
            dispatcher["menu"](db_day_filepath, db_LIFETIME_filepath)

        case '3':
            os.system(f'rm -dfv {db_LIFETIME_filepath}.db')
    
            db_LIFETIME_filepath = db_create_filepath(version, "LIFETIME")
            if not os.path.exists(f"{db_LIFETIME_filepath}"):
                initalize_db_LIFETIME(db_LIFETIME_filepath)

            #TODO For loop to add all day_db's into "date_list"

            print("LIFETIME_DB_FILE created")
            dispatcher["menu"](db_day_filepath, db_LIFETIME_filepath)

def quit_program():
    sys.exit()

def update_midishark():
    sys.exit()
    os.system("./update/update.sh")
    os.system(".MidiShark")


# Create a file to share info about sessions with StatViewer
# Create one file for current session data, and one for day info
def day_info_file_create(db_day, fp="db_day.info"):
    with open(f'db/{fp}', "w") as file:
        file.write(f'{db_day["name"]}')
    file.close()

def latest_session_info_file(current_session_dict, fp="current_session.info"):
    with open(f'db/{fp}', "w") as file:
        file.write(f'{current_session_dict["session_name"]}')
    file.close()

def program_init(*args, **kwargs):
    midi_list = []
    note_input = ""
    note_time = 0.0    
    note_tracker_dict = dict()

    return midi_list, note_input, note_time, note_tracker_dict

# TODO: Add stats() method
if __name__ == "__main__":
    version = "v0-0-8-4"
    
    
    dispatcher = {'start': start_session, 
        'menu': menu,
        'print_totals': print_totals,
        'tutorial': tutorial,
        'troubleshooting': troubleshooting,
        'help': help,
        'update-midishark': update_midishark,
        'exit': quit_program}
    
    # Check len of args, if '-d' then debug = True
    arg_len = len(sys.argv)
    debug = False
    if "-d" in sys.argv:
        debug = True
    
    elif "-v" in sys.argv:
        print(version)
        dispatcher['exit']()
    
    os.system('clear')
    
    # Check for or create db_day file

    db_file_day = datetime.now().strftime("%Y%m%d")
    #db_file_day = datetime.now().strftime("%Y%m%M")
    db_day_date = str(f"{db_file_day}")
    db_day_filepath = db_create_filepath(version, db_day_date)
    if not os.path.exists(f"{db_day_filepath}"):
        initalize_day_table_to_db(db_day_filepath)
    
    # Check for or create LIFETIME db file
    db_LIFETIME_filepath = db_create_filepath(version, "LIFETIME")
    if not os.path.exists(f"{db_LIFETIME_filepath}"):
        initalize_db_LIFETIME(db_LIFETIME_filepath)

    db_synced = False
    note_pressed = False
    new_session_dict = True
    note_idle_timer = Timer()

    start_session(db_day_filepath, db_LIFETIME_filepath)


""" 
Create a folder with DB day to store all sessions of that day
"""
