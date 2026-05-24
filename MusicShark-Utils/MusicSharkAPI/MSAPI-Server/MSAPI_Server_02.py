from flask import Flask, request, jsonify
import sqlite3
import os
from MSAPI_Utils import *

app = Flask(__name__)

# Init db and create a table
def init_db():
    pass

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

    for n in range(6, 12):
        notes = list()

        note_dict[db_data[n]['note_name']].name = db_data[n]['note_name']
        note_dict[db_data[n]['note_name']].times_played = db_data[n]['note_times_played']
        note_dict[db_data[n]['note_name']].time_total = db_data[n]['note_time_total']

    return db_data_list, note_dict
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

    
@app.route('/test', methods=['GET'])
def test():
    day_id = 20260505
    table = 'session_000246'

    db_day_filepath = f"/home/miles/MusicShark-dev/MusicSharkSim/db/20260505.db"
    #db_day_filepath = db_create_filepath(db_day_filename)

    #return get_db_values(db_day_filepath, table, 'db_day')
    #return return_list

    conn = sqlite3.connect(db_day_filepath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()

    final_data = [dict(row) for row in rows]

    db_data_list, notes_dict = retrieve_json(final_data)

    return final_data


if __name__ == "__main__":
    app.run()



"""
Possible endpoint ideas:

/<user_id>/list/<days> | /<user_id>/list/<days>/<sessions> -- GET
|
+-> This would list db_day names and the sessions in those days 

/
"""