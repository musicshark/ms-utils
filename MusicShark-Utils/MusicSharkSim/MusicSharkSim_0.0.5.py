import os
import sys
import sqlite3
from datetime import datetime, date, time, timezone
from dataclasses import dataclass
import time
import random
import hashlib
from MSS_Utils import *

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

#def initalize_session_stats_to_db(current_session_dict, db_cursor):
#    try: 
#        session_name = current_session_dict["session_name"]
#        session_total_notes_played = current_session_dict["total_notes_played"]
#        session_total_note_time_played = current_session_dict["note_time_played"]
#        session_start = current_session_dict["session_start"]
#        session_end = current_session_dict["session_end"]
#        session_runtime = current_session_dict["total_session_runtime"]
#
#        current_session_table = str(f"session_{session_name}")
#
#        session_data = (session_name, session_total_notes_played, session_total_note_time_played, session_start, session_end, session_runtime)
#        create_table_session_totals = f"""CREATE TABLE IF NOT EXISTS {current_session_table} (
#                        name INTEGER, 
#                        total_notes_played INTEGER, 
#                        total_note_time_played FLOAT, 
#                        start FLOAT, 
#                        end FLOAT, 
#                        runtime FLOAT,
#                        note_name TEXT,
#                        note_times_played INTEGER,
#                        note_time_total FLOAT);"""
#        db_cursor.execute(create_table_session_totals)
#        print(f"session_table {current_session_table} created")
#
#        init_session_db = f"""INSERT INTO {current_session_table}
#                        (name, total_notes_played, total_note_time_played, start, end, runtime)
#                        VALUES (?, ?, ?, ?, ?, ?);"""                        
#        db_cursor.execute(init_session_db, session_data)
#
#        notes_dict = current_session_dict["total_notes"]
#        initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor)
#
#        if debug == True:
#            db_cursor.execute(f"SELECT * FROM {current_session_table}")
#            print(db_cursor.fetchall())
#
#            print(f'\n\nday_totals:')
#            db_cursor.execute(f"SELECT * FROM day_totals")
#            print(db_cursor.fetchall())
#
#    except sqlite3.Error as error:
#        print(f"Failed to initalize {current_session_table} table", error)                       
#
#def initalize_session_notes_to_db(notes_dict, current_session_table, db_cursor):
#    try:    
#        sqlite_insert_query = f"""INSERT INTO {current_session_table}
#                          (note_name, note_times_played, note_time_total) 
#                          VALUES (?, ?, ?);""" 
#
#        for n in notes_dict.keys():
#            note_name = n
#            note_times_played = notes_dict[n].times_played
#            note_time_total = notes_dict[n].total_time 
#
#            note_record = (note_name, note_times_played, note_time_total)  
#            if debug:
#                print(f"note_name: {note_name}\nnote_times_played: {note_times_played}\nnote_time_total: {note_time_total}")
#        
#            db_cursor.execute(sqlite_insert_query, note_record)
#        
#        print(f"Initalized Note stats in {db_day_filepath} for {current_session_table}")            
#    except sqlite3.Error as error:
#        print(f"Failed to insert session_notes into {current_session_table} of db_day", error)


#def initalize_db_LIFETIME(db_LIFETIME_filepath):
#    global debug 
#
#    try: 
#        conn = sqlite3.connect(db_LIFETIME_filepath)
#        print(f"Connected to {db_LIFETIME_filepath}")
#        cursor = conn.cursor()
#        
#        LIFETIME_name = "LIFETIME"
#        current_session_table = "LIFETIME"
#        LIFETIME_notes_played = 0
#        LIFETIME_note_time_played = 0.0
#        LIFETIME_runtime = 0.0
#
#        LIFETIME_data = (LIFETIME_name, LIFETIME_notes_played, LIFETIME_note_time_played,LIFETIME_runtime)
#        
#        create_LIFETIME_table = f"""CREATE TABLE IF NOT EXISTS {LIFETIME_name} (
#                        name TEXT, 
#                        total_notes_played INTEGER, 
#                        total_note_time_played REAL, 
#                        runtime REAL,
#                        date_list INTEGER,
#                        note_name TEXT,
#                        note_times_played INTEGER,
#                        note_time_total REAL);""" 
#        cursor.execute(create_LIFETIME_table)
#        
#        init_LIFETIME_db = f"""INSERT INTO {LIFETIME_name}
#                        (name, total_notes_played, total_note_time_played, runtime)
#                        VALUES (?, ?, ?, ?);"""
#        cursor.execute(init_LIFETIME_db, LIFETIME_data)
#
#        notes_dict = note_dict_init()
#        initalize_session_notes_to_db(notes_dict, LIFETIME_name, conn)
#        initalize_LIFETIME_current_session_table(cursor, 0, notes_dict, conn)
#
#        conn.commit()
#
#        if debug == True:
#            cursor.execute(f"SELECT * FROM {LIFETIME_name}")
#            print(cursor.fetchall())
#
#    except sqlite3.Error as error:
#        print(f"Failed to initalize {LIFETIME_name} table", error)
#    finally:
#        if conn:
#            conn.close()
#            print(f"Connection to {db_LIFETIME_filepath} is closed")


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
def generate_total_notes_played(session_type):
    match session_type:
        case "short":
            MIN_NOTES = 0
            MAX_NOTES = 123

        case "medium":
            MIN_NOTES = 110
            MAX_NOTES = 439

        case "long":
            MIN_NOTES = 428
            MAX_NOTES = 744

        case "test":
            MIN_NOTES = 1
            MAX_NOTES = 10

        case _:
            print(f"ERROR: session_total_notes case statement")

    return random.randint(MIN_NOTES, MAX_NOTES)

def generate_session_totals(current_session_dict, session_type):
    total = 0 
    print(session_type)
    for note, val in current_session_dict["total_notes"].items():
        val.times_played = generate_total_notes_played(session_type)
        print(f"{note}.times_played: {val.times_played}")
        current_session_dict["total_notes_played"] += val.times_played
        total += val.times_played

        val.total_time = val.times_played * random.random()
        current_session_dict["note_time_played"] += val.total_time

    print(f"total_notes_played: {current_session_dict['total_notes_played']}")
    print(total)

#def update_os_env(session_name):
#    os.environ["TEST"] = session_name

def start_session(db_day_filepath, db_LIFETIME_filepath):
    global db_day_date
    
    current_session_dict = init_current_session_dict() 
    session_type = random.choice(["short", "medium", "long"])
    #session_type = "test"

    db_day_conn = get_db_connection(db_day_filepath)
    db_day_cursor = db_day_conn.cursor()
    #initalize_day_table_to_db(db_day_filepath, day_id, db_day_conn)

    db_LIFETIME_conn = get_db_connection(db_LIFETIME_filepath)
    db_LIFETIME_cursor = db_LIFETIME_conn.cursor()
    #initalize_session_stats_to_db(init_current_session_dict("LIFETIME"), db_LIFETIME_cursor)
    
    current_session_dict["session_start"] = time.time()
    current_session_dict["session_name"] = str(datetime.now().strftime('%H%M%S'))
    current_session_dict["table_name"] = "session_" + str(current_session_dict["session_name"]).zfill(6)



    generate_session_totals(current_session_dict, session_type)
    current_session_dict["total_session_runtime"] = current_session_dict["note_time_played"] + random.uniform(2.1, 32.8)
    current_session_dict["session_end"] = current_session_dict["session_start"] + current_session_dict["total_session_runtime"]

    add_session_to_db_day(current_session_dict, db_day_cursor)

    db_day_conn.commit()
    #db_LIFETIME_conn.commit()

    update_db_day_and_db_lifetime(current_session_dict, db_day_cursor, db_LIFETIME_cursor)
    print(db_file_day)
    db_day_cursor.execute(f"UPDATE day_totals SET name = {db_file_day} WHERE rowid = 1;")
    db_LIFETIME_cursor.execute(f"UPDATE LIFETIME SET name = 'LIFETIME' WHERE rowid = 1;")


    db_day_conn.commit()
    db_LIFETIME_conn.commit()

    update_runtime_info_file(current_session_dict["session_name"], current_session_dict["total_session_runtime"])

    print_current_session(current_session_dict)

    db_day_conn.close()
    db_LIFETIME_conn.close()   


    update_session_tracker_db(db_day_filepath, db_file_day, current_session_dict["session_name"])

def create_session_upload_tracker_db(SESSION_UPLOAD_TRACKER_DB_PATH):
    upload_tracker_conn = sqlite3.connect(SESSION_UPLOAD_TRACKER_DB_PATH)
    upload_tracker_cursor = upload_tracker_conn.cursor()

    # db_day_hash will be the key for idempotency
    create_session_upload_tracker_table = f"""CREATE TABLE IF NOT EXISTS session_upload_tracker(
            db_day_hash TEXT PRIMARY KEY,
            db_day_name INTEGER,
            session_name TEXT,
            status TEXT);"""
    try:
        upload_tracker_cursor.execute(create_session_upload_tracker_table)

    except sqlite3.Error as error:
        print(f"Failed to initalize session_upload_tracker table", error)

    finally:
        if upload_tracker_conn:
            upload_tracker_conn.close()
            print(f"Connection to {SESSION_UPLOAD_TRACKER_DB_PATH} is closed")


def update_session_tracker_db(db_day_filepath, db_day_name, current_session_id, max_retries=5, base_delay=0.05):
    global SESSION_UPLOAD_TRACKER_DB_PATH
    sql_insert_statment = ("INSERT INTO session_upload_tracker (db_day_hash, db_day_name, session_name, status) VALUES (?, ?, ?, ?);")


    # db_day file hash
    with open(db_day_filepath, "rb") as f:
        digest = hashlib.file_digest(f, "sha256")
    db_day_hash = digest.hexdigest()
    
    upload_tracker_conn = sqlite3.connect(SESSION_UPLOAD_TRACKER_DB_PATH)
    print(f"Connection to {SESSION_UPLOAD_TRACKER_DB_PATH} open")

    # Add info to session_upload_tracker_db with retries if db is locked
    
    try:
        upload_tracker_cursor = upload_tracker_conn.cursor()
        upload_tracker_cursor.execute(sql_insert_statment, (db_day_hash, db_day_name, current_session_id, "false"))
        upload_tracker_conn.commit()
        print(f"Committed to {SESSION_UPLOAD_TRACKER_DB_PATH}")

    except sqlite3.OperationalError as e:
        last_exc = e
        msg = str(e).lower()
        is_busy = "database is locked" in msg or "database table is locked" in msg
        is_locked = "database table is locked" in msg or "database is locked" in msg
            
        if is_busy or is_locked:
            for attempt in range(0, max_retries + 1):
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
                time.sleep(delay)
                #continue
        
    finally:
        if upload_tracker_conn:
            upload_tracker_conn.close()
            print(f"Connection to {SESSION_UPLOAD_TRACKER_DB_PATH} is closed")
    

      


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
    
    
   
    # Check len of args, if '-d' then debug = True
    arg_len = len(sys.argv)
    debug = False
    if "-d" in sys.argv:
        debug = True
    
    elif "-v" in sys.argv:
        print(version)
   
    os.system('clear')
    
    # Path for db to create hash of db_day for upload idempotency 
    SESSION_UPLOAD_TRACKER_DB_PATH = "./db/session_upload_tracker.db"

    # Check for or create db_day file
#    db_file_day = str(datetime.now().strftime("%Y%m%d"))
    db_file_day = str(datetime.now().strftime("%Y%m%M"))
    db_day_filepath = db_create_filepath(db_file_day)
#    db_day_date = str(f"{db_file_day}")
#    db_day_filepath = db_create_filepath(version, db_day_date)
#    if not os.path.exists(f"{db_day_filepath}"):
#        initalize_day_table_to_db(db_day_filepath)
    
    # Check for or create LIFETIME db file
    db_LIFETIME_filepath = db_create_filepath("LIFETIME")
#    if not os.path.exists(f"{db_LIFETIME_filepath}"):
#        initalize_db_LIFETIME(db_LIFETIME_filepath)
#
    # Create the db file and table if it doesn't exist
    if not os.path.exists(f"{SESSION_UPLOAD_TRACKER_DB_PATH}"):
#        subprocess.run(["mkdir", "-p", SESSION_UPLOAD_TRACKER_DB_PATH])
        create_session_upload_tracker_db(SESSION_UPLOAD_TRACKER_DB_PATH)

    start_session(db_day_filepath, db_LIFETIME_filepath)


""" 
Create a folder with DB day to store all sessions of that day
"""
