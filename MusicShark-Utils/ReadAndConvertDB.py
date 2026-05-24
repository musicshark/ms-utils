import os
import sys
import shelve
import dbm
#import gdbm
from datetime import datetime, date, time, timezone
import json

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

class LCD_Screen:
    def __init__(self):
        self.session_name = " "
        self.tnp = 0
        self.ttp = 0

    def update(self, s_start, tnp, ttp):
        self.session_name = s_start
        self.tnp = tnp
        self.ttp = ttp

    def new_session(self, s_start):
        self.session_name = s_start
        self.tnp = 0
        self.ttp = 0


    def print_stats(self, midi_input):
        if (midi_input[0] == '80'):
            print(f"{datetime.now()}: {midi_input}\t\tNote: {self.name}   \t\tTotal Input: {self.times_played}     \t\tTotal Time Pressed: {self.current_note_time}")
            self.current_note_time = 0
        else:
            print(f"{datetime.now()}: {midi_input}\t\tNote: {self.name}   \t\tTotal Input: {self.times_played}") #     \t\tTotal Time Pressed: {self.total_time}")
            
# USAGE: ReadAndConvertDB.py <db_path> 
if len(sys.argv) < 2:
    print(f"USAGE: ReadAndConvertDB.py <db_path>")
    sys.exit(1)

db_path = sys.argv[1]
db = shelve.open(db_path)

os.system('clear')
print(list(db.keys()))
print(f'DAY NAME: {db["name"]}')
print(f"\n\n+-------------- Total Notes Played Today: {db['total_notes_played']} --------------+\
\n+-------------- Total Time Pressed Today: {db['total_time_pressed']} --------------+\n\n")

# Find and print total note stats
print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
for k, v in db["total_notes"].items():
    print(f"{k}\t\t\t{v.times_played}\t\t\t\t{v.total_time}")
input("Press ENTER to continue")

for n in db["session_dict"]:
    os.system('clear')
    current_session = db['session_dict'][n]
    print(f"Session Name: {current_session['session_name']}")
    print(f"\n\n+-------------- Total Notes Played Today: {current_session['total_notes_played']} --------------+\
    \n+-------------- Total Time Pressed Today: {current_session['total_time_pressed']} --------------+\n\n")
    #print(db["session_dict"][n].items())
    print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
    for k, v in current_session["total_notes"].items():
        print(f"{k}\t\t\t{v.times_played}\t\t\t\t{v.total_time}")
    input("Press ENTER to continue")


#for k, v in db["session_dict"].items():
#    print(f"{k}\t\t\t{v.times_played}\t\t\t\t{v.total_time}")

db.close()
