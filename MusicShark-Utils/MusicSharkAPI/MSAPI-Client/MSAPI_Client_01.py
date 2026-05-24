import sqlite3
import requests
import json
import time
import random
import subprocess
import os 
import asyncio

# Program that takes session tables and adds them to the external server.

def get_db_connection(db_filepath):
    conn = sqlite3.connect(db_filepath)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def obtain_previous_session_info():
    db_filepath = SESSION_UPLOAD_TRACKER_PATH
    session_info_conn = get_db_connection(db_filepath)
    session_info_cursor = session_info_conn.cursor()

    try:
        session_info_results_list = session_info_cursor.execute("SELECT * FROM session_upload_tracker WHERE db_day_hash IS NOT NULL LIMIT 1;").fetchall()
        session_info_results = session_info_results_list[0]
#        print(f"session_info_results: {type(session_info_results)}")

        
        return session_info_results["db_day_hash"], session_info_results["db_day_name"], session_info_results["session_name"]


    except sqlite3.OperationalError as e:
        db_locked_handler(5, 0.5, e)
        
    finally:
        if session_info_conn:
            session_info_conn.close()
            print(f"Connection to {db_filepath} is closed")

#def g


def db_locked_handler(max_retries, base_delay, err):
    last_exc = err
    msg = str(err).lower()
    is_busy = "database is locked" in msg or "database table is locked" in msg
    is_locked = "database table is locked" in msg or "database is locked" in msg
        
    if is_busy or is_locked:
        for attempt in range(0, max_retries + 1):
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
            time.sleep(delay)
            #continue    


async def send_data_to_server(db_filepath, db_day_name, session_number, session_name, db_day_hash):
    await update_session_tracker_entry(db_day_hash)

    session_db_conn = get_db_connection(db_filepath)
    session_db_conn.row_factory = sqlite3.Row
    session_db_cursor = session_db_conn.cursor()

    session_db_rows = session_db_cursor.execute(f"""SELECT * FROM {session_name};""").fetchall()

    session_db_data = [dict(row) for row in session_db_rows]
    ms_username = os.getenv("MUSICSHARK_USERNAME")
    print(ms_username)

    ms_api_server_url = MS_API_SERVER + f"/update_dbs/{ms_username}/{db_day_name}/{session_number}/{db_day_hash}"
    print(ms_api_server_url)

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(ms_api_server_url, data=json.dumps(session_db_data), headers=headers)

        if response.status_code == 200:
            print("Success")
        else:
            print(f"Failed with status code: {response.status_code}")
    except Exception as e:
        db_locked_handler(5, 0.5, e)
        print(f"send_data_to_server: {e}")
        
    finally:
        if session_db_conn:
            session_db_conn.close()
            print(f"Connection to {db_filepath} is closed")

async def update_session_tracker_entry(db_day_hash):
    try:
        session_info_conn = get_db_connection(SESSION_UPLOAD_TRACKER_PATH)
        session_info_cursor = session_info_conn.cursor()
        print(f"Updated {db_day_hash} in {SESSION_UPLOAD_TRACKER_PATH}")

        session_info_cursor.execute(f"UPDATE session_upload_tracker SET status = ? WHERE db_day_hash = ?;", ("pending", db_day_hash))
        session_info_conn.commit()
        return

    except sqlite3.OperationalError as e:
        db_locked_handler(5, 0.5, e)
        print(f"update_session_tracker_entry: {e}")
        
    finally:
#        if session_info_conn:
#            session_info_conn.close()
            print(f"Connection to {db_filepath} is closed")

def delete_session_tracker_entry(db_day_hash):
    try:
        session_info_conn = get_db_connection(SESSION_UPLOAD_TRACKER_PATH)
        session_info_cursor = session_info_conn.cursor()

        session_info_cursor.execute(f"DELETE FROM session_upload_tracker WHERE status = 'pending';")
        session_info_conn.commit()

    except sqlite3.OperationalError as e:
        db_locked_handler(5, 0.5, e)
        print(f"delete_session_tracker_entry: {e}")
        
    finally:
        if session_info_conn:
            session_info_conn.close()
            print(f"delete_session_tracker_entry: Connection to {db_filepath} is closed")    

if __name__ == "__main__":

    MS_API_SERVER = "http://127.0.0.1:5000"
    SESSION_UPLOAD_TRACKER_PATH = "../../MusicSharkSim/db/session_upload_tracker.db"

    db_day_hash, db_day_name, session_number = obtain_previous_session_info()
    session_name = "session_" + str(session_number).zfill(6)
    print(db_day_hash)
    print(db_day_name)
    print(session_name)

    db_filepath = f"../../MusicSharkSim/db/{db_day_name}.db"
    asyncio.run(send_data_to_server(db_filepath, db_day_name, session_number, session_name, db_day_hash))
    delete_session_tracker_entry(db_day_hash)

