import sqlite3
import os
import time
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



def get_db_values(db_filepath, table):
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    conn.close()

    final_data = [dict(row) for row in rows]

    print(f"{final_data}")

    return retrieve_json(final_data)

def retrieve_json(db_data):
    db_data_list = list()

    name = db_data[0]['name']
    db_data_list.append(name)

    total_notes_played = db_data[0]['total_notes_played']
    db_data_list.append(int(total_notes_played))

    total_note_time_played = db_data[0]['total_note_time_played']
    db_data_list.append(float(total_note_time_played))

    start = db_data[0]['start']
    db_data_list.append(float(start))

    end = db_data[0]['end']
    db_data_list.append(float(end))

    runtime = db_data[0]['runtime']
    db_data_list.append(float(runtime))

#    note_name = db_data[0]['note_name']
#    notes.append(note_name)
#
#    note_times_played = db_data[0]'note_times_played')
#    notes.append(int(note_times_played))
#
#    note_time_total = db_data.get('note_time_total')
#    notes.append(note_time_total)

    # I think I need an 2d array for [[note_name], [note_times_played],[note_total_time]] 
    # The notes list will start at db_data_list[6][0]
    note_dict = note_dict_init()

    for n in range(1, 13):
        #print(f"N: {n}")
        note_dict[db_data[n]['note_name']].name = db_data[n]['note_name']
        #print(f"NAME: {note_dict[db_data[n]['note_name']].name}")
        note_dict[db_data[n]['note_name']].times_played = db_data[n]['note_times_played']
        #print(f"NP: {note_dict[db_data[n]['note_name']].times_played}")
        note_dict[db_data[n]['note_name']].total_time = db_data[n]['note_time_total']
        #print(f"TP: {note_dict[db_data[n]['note_name']].time_total}")

    return db_data_list, note_dict
    #return print(f"DB_DATA_LIST: {db_data_list}\n\n NOTE_DICT: {note_dict}")


# Check to see if file exists, if so create the filepath, if not: create the dir and return the filepath
def db_create_filepath(db_dir_path, db_name):
    
    # Create a directory leading up the the db's name, but not for the db_name. If only db name is supplied, and 'db' dir isn't present - make the 'db' dir
    if not os.path.exists(f"./db/{db_dir_path}"):
        subprocess(f"mkdir", "-p", f"./db/{db_dir_path}") 

    # Create full db_filepath
    if not os.path.exists(f"./db/{db_dir_path}/{db_name}.db"):
        try:
            fp = str(f"./db/{db_dir_path}/{db_name}.db")
            #print(f"DB Filepath Created: {fp}")
            return fp
        except OSError as error:
            print(error)

    elif os.path.exists(f"./db/{db_dir_path}/{db_name}.db"):
        fp = str(f"./db/{db_dir_path}/{db_name}.db")
        print(f"Existing DB Filepath: ./db/{db_dir_path}/{db_name}.db")
        return fp

# Get DB connection
def get_db_connection(db_filepath):
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn



def initalize_day_table_to_db(db_day_filepath, day_id, conn):
    #global debug 

    try: 
        #conn = sqlite3.connect(db_day_filepath)
        #print(f"Connected to {db_day_filepath} for initalize_day_table_to_db()")
        cursor = conn.cursor()

        #db_file_day = datetime.now().strftime("%Y%m%d")
        #db_file_day = datetime.now().strftime("%Y%m%M")
        
        day_name = day_id
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

#        if debug == True:
#            print(f'\n\nday_totals:')
#            cursor.execute(f"SELECT * FROM day_totals")
#            print(cursor.fetchall())

    except sqlite3.Error as error:
        print(f"Failed to initalize {day_name} table", error)
#    finally:
#        if conn:
#            conn.close()
#            print(f"Connection to {db_day_filepath} is closed")

def initalize_session_stats_to_db(current_session_dict, db_cursor):
    try: 
        session_name = current_session_dict["session_name"]
        session_total_notes_played = current_session_dict["total_notes_played"]
        session_total_note_time_played = current_session_dict["note_time_played"]
        session_start = current_session_dict["session_start"]
        session_end = current_session_dict["session_end"]
        session_runtime = current_session_dict["total_session_runtime"]

        if session_name == 'LIFETIME':
            current_session_table = "LIFETIME"
        else:
            current_session_table = current_session_dict["current_session_table"]

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

#        if debug == True:
#            db_cursor.execute(f"SELECT * FROM {current_session_table}")
#            print(db_cursor.fetchall())
#
#            print(f'\n\nday_totals:')
#            db_cursor.execute(f"SELECT * FROM day_totals")
#            print(db_cursor.fetchall())

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

def initalize_db_LIFETIME(db_LIFETIME_filepath):
#    global debug 

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
        initalize_LIFETIME_current_session_table(cursor, "LIFETIME", notes_dict, conn)

        conn.commit()

#        if debug == True:
#            cursor.execute(f"SELECT * FROM {LIFETIME_name}")
#            print(cursor.fetchall())

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

def init_current_session_dict(session_name):
    current_session_dict = dict()
    current_session_dict["total_notes"] = note_dict_init()
    current_session_dict["total_notes_played"] = 0
    current_session_dict["note_time_played"] = 0.0
    current_session_dict["session_dict"] = dict()
    current_session_dict["session_name"] = session_name
    current_session_dict["session_start"] = 0.0
    current_session_dict["session_end"] = 0
    current_session_dict["total_session_runtime"] = 0
    current_session_dict["total_session_notes_played"] = dict()

    return current_session_dict

def update_current_session_dict(db_data_list, note_dict):
    current_session_dict = dict()
    current_session_dict["total_notes"] = note_dict.copy()
    current_session_dict["total_notes_played"] = db_data_list[1]
    current_session_dict["note_time_played"] = db_data_list[2]
    current_session_dict["session_dict"] = dict()
    current_session_dict["session_name"] = f"{db_data_list[0]}"
    current_session_dict["session_start"] = db_data_list[3]
    current_session_dict["session_end"] = db_data_list[4]
    current_session_dict["total_session_runtime"] = db_data_list[5]
    current_session_dict["total_session_notes_played"] = dict()

    return current_session_dict


def update_session_stats_to_db(current_session_dict, db_day_cursor):
    try: 
        #conn = sqlite3.connect(db_day_filepath)
        #print(f"Connected to {db_day_filepath}")
        cursor = db_day_cursor
        
        session_name = current_session_dict["session_name"]
        session_total_notes_played = current_session_dict["total_notes_played"]
        session_total_note_time_played = current_session_dict["note_time_played"]
        session_start = current_session_dict["session_start"]
        session_end = current_session_dict["session_end"]
        session_runtime = current_session_dict["total_session_runtime"]
        current_session_table = current_session_dict["table_name"]

#        if debug:
#            print(type(current_session_dict["total_session_runtime"]))

        values = (session_total_notes_played, session_total_note_time_played, session_end, session_runtime)
        
        cursor.execute(f"""UPDATE {current_session_table}
                          SET (total_notes_played, total_note_time_played, end, runtime) = (?, ?, ?, ?)""", (values))

        
        notes_dict = current_session_dict["total_notes"]
        update_session_note_values_to_db(notes_dict, current_session_table, db_day_cursor)
    
    except sqlite3.Error as error:
        print(f"Failed to update Session {current_session_table} Stats", error)

def update_session_note_values_to_db(notes_dict, current_session_table, db_day_cursor):
    try:
        #cursor = conn.cursor()
        #print(f"Connected to {db_day_filepath}")

        for note_name in notes_dict.keys():
            note_times_played = notes_dict[note_name].times_played
            note_time_total = notes_dict[note_name].total_time 

            # Update times_played/note
            db_day_cursor.execute(f"""UPDATE {current_session_table}
                              SET note_times_played = ? WHERE note_name = ?""", (note_times_played, note_name))

            # Update note_time_total/note
            db_day_cursor.execute(f"""UPDATE {current_session_table}
                              SET note_time_total = ? WHERE note_name = ?""", (note_time_total, note_name))
        
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
        new_total = res1_tuple[0] + current_session_note_dict["total_notes"][current_note].times_played

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
    old_value = res1_tuple[0]
    new_total = 0
    
    if col == "total_notes_played":
        new_total = old_value + current_session_note_dict["total_notes_played"]
    
    elif col == "total_note_time_played":
        new_total = old_value + current_session_note_dict["note_time_played"]

    db_cursor.execute(f"""UPDATE {table_name}
                        SET {col} = ?;""", (new_total, ))
    
    #print(f"new_total: {new_total} - {table_name} - {db_name} - {col}")


def update_table_with_runtime_and_session_end(db_cursor, session_end, runtime, table_name, db_LIFETIME_filepath):
    #previous_session_name = get_previous_session_name(db_LIFETIME_filepath)

    print(f"session_end: {session_end}\truntime: {runtime}")
    runtime_total = 0
    
    res1 = db_cursor.execute(f'''SELECT runtime FROM {table_name}''')
    res1_list = res1.fetchall()
    res1_tuple = res1_list[0]
    runtime_total = res1_tuple[0] + runtime
    db_cursor.execute(f'''UPDATE {table_name} SET runtime = ?;''', (runtime_total, ))

    if table_name == 'day_totals': #or table_name == previous_session_name:
        db_cursor.execute(f'''UPDATE {table_name} SET end = ?;''', (session_end, ))


def update_db_day_and_db_lifetime(current_session_dict, db_day_cursor, db_LIFETIME_cursor, db_LIFETIME_filepath):
    for note, val in current_session_dict["total_notes"].items():        
        increment_note_stats_to_table(current_session_dict, note, db_day_cursor, "note_times_played", "db_day")
        increment_note_stats_to_table(current_session_dict, note, db_LIFETIME_cursor, "note_times_played", "db_LIFETIME")

        increment_note_stats_to_table(current_session_dict, note, db_day_cursor, "note_time_total", "db_day")
        increment_note_stats_to_table(current_session_dict, note, db_LIFETIME_cursor, "note_time_total", "db_LIFETIME")
                   
    update_session_stats_to_db(current_session_dict, db_day_cursor)

    increment_total_stats_to_table(current_session_dict, db_day_cursor, "total_notes_played", "db_day")
    increment_total_stats_to_table(current_session_dict, db_LIFETIME_cursor, "total_notes_played", "db_LIFETIME")

    increment_total_stats_to_table(current_session_dict, db_day_cursor, "total_note_time_played", "db_day")
    increment_total_stats_to_table(current_session_dict, db_LIFETIME_cursor, "total_note_time_played", "db_LIFETIME")
    
    session_end = current_session_dict["session_end"]
    session_runtime = current_session_dict["total_session_runtime"]

    update_table_with_runtime_and_session_end(db_LIFETIME_cursor, session_end, session_runtime, 'LIFETIME', db_LIFETIME_filepath)
    update_table_with_runtime_and_session_end(db_day_cursor, session_end, session_runtime, 'day_totals', db_LIFETIME_filepath)
    update_table_with_runtime_and_session_end(db_day_cursor, session_end, session_runtime, current_session_dict["session_name"], db_LIFETIME_filepath)
            
#def get_previous_session_name(db_LIFETIME_filepath) -> str:
#    conn = sqlite3.connect(db_LIFETIME_filepath)
#    cursor = conn.cursor()
#
#    res = cursor.execute(f"""SELECT name FROM current_session""")
#    session_name_list = res.fetchall()
#
#    session_name = session_name_list[0]
#    if int(session_name[0]) < 9999:
#        return str(f"session_00{session_name[0]}")
#    elif int(session_name[0]) < 99999:
#        return str(f"session_0{session_name[0]}")
#    elif int(session_name[0]) < 999999:
#        return str(f"session_{session_name[0]}")
#    else:
#        print(f"INVALID SESSION NAME: {session_name}")
#
#    conn.close()