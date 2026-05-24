from flask import Flask, request, jsonify
import sqlite3
import os
from MSAPI_Server_Utils_02 import *

app = Flask(__name__)

# Init db and create a table
def init_db():
    pass


#
#@app.route('/update_dbs/<username>/<day_id>/<UUID>/', methods=['POST'])
#def update_dbs(username, day_id, UUID):
#    db_data = request.get_json()
#    db_data_list = retrieve_json(db_data)
#
#    for n in range(0, len(db_data_list)):
#        if not n:
#            return jsonify({'error': f'Missing required field {n}'}), 400
#    
#
#    db_day_filename = f"/db/{username}/db_day/{day_id}"
#    db_day_filepath = db_create_filepath(db_filename)
#    
#    db_LIFETIME_filename = f"db/{username}/LIFETIME"
#    db_LIFETIME_filepath = db_create_filepath(db_LIFETIME_filename)
#
#    db_day_conn = get_db_connection(db_day_filepath)
#    initalize_day_table_to_db(db_day_filepath, db_day_conn)
#
#    db_LIFETIME_conn = get_db_connection(db_LIFETIME_filepath)
#    initalize_day_table_to_db(db_LIFETIME_filepath, db_LIFETIME_conn)
#
#    note_dict = note_dict_init()
#
#    for n in range(6, len(db_data_list)):
#        note_dict[db_data_list[n][0]].times_played = db_data_list[n][1]
#        note_dict[db_data_list[n][0]].total_time = db_data_list[n][2]

    
#@app.route('/test', methods=['GET'])
@app.route('/update_dbs/<username>/<day_id>/<session>/<UUID>', methods=['GET','POST'])
def test(username, day_id, session, UUID):
    incoming_data = request.get_json()

    try:
        db_day_dir_path = f"{username}/db_day/"
        db_day_filepath = db_create_filepath(db_day_dir_path, day_id)
        
        db_LIFETIME_dir_path = f"{username}/LIFETIME"
        db_LIFETIME_filepath = db_create_filepath(db_LIFETIME_dir_path, "LIFETIME")

    except OSError as e:
        return jsonify({'error': f'Unable to create DB Paths: {e}'}), 400
 
    #table = "session_" + str(session).zfill(6)
    db_data_list, note_dict =  retrieve_json(incoming_data)
    
    current_session_dict = update_current_session_dict(db_data_list, note_dict)
    current_session_dict["table_name"] = "session_" + str(session).zfill(6)

#    try:
    db_day_conn = get_db_connection(db_day_filepath)
    db_day_cursor = db_day_conn.cursor()
    #initalize_day_table_to_db(db_day_filepath, day_id, db_day_conn)

    db_LIFETIME_conn = get_db_connection(db_LIFETIME_filepath)
    db_LIFETIME_cursor = db_LIFETIME_conn.cursor()
    #initalize_session_stats_to_db(init_current_session_dict("LIFETIME"), db_LIFETIME_cursor)
    
    add_session_to_db_day(current_session_dict, db_day_cursor)
    db_day_conn.commit()

    update_db_day_and_db_lifetime(current_session_dict, db_day_cursor, db_LIFETIME_cursor)
    db_day_cursor.execute(f"UPDATE day_totals SET name = {str(day_id)} WHERE rowid = 1;")
    db_LIFETIME_cursor.execute(f"UPDATE LIFETIME SET name = 'LIFETIME' WHERE rowid = 1;")

    db_day_conn.commit()
    db_LIFETIME_conn.commit()

    db_day_conn.close()
    db_LIFETIME_conn.close()
 
    return jsonify({'success': 'Local DBs updated'})

#    except sqlite3.Error as e:
#        return jsonify({'error': f'sqlite3 - Obtain DB Error: {e}'}), 400   



if __name__ == "__main__":
    app.run()

"""
Possible endpoint ideas:

/<user_id>/list/<days> | /<user_id>/list/<days>/<sessions> -- GET
|
+-> This would list db_day names and the sessions in those days 

/
"""