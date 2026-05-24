import os
import time
from datetime import datetime, date, time, timezone
import shelve

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
    def __init__(self, name, times_played, note_pressed_on, time_stats, current_note_time, total_time):
        self.name = name
        self.times_played = 0
        self.total_times_pressed = 0
        self.note_pressed_on = False
        self.time_stats = Timer()
        self.current_note_time = 0.0
        self.total_time = 0.0
        global note_tracker_dict

#midishark = "MidiShark_v0.6.2"
#import midishark

def paginated_print(text, lines_per_page=20):
    lines = text.splitlines()
    total_lines = len(lines)
    start_index = 0

    while start_index < total_lines:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
        end_index = min(start_index + lines_per_page, total_lines)
        for i in range(start_index, end_index):
            print(lines[i])
        
        if end_index < total_lines:
            input("Press Enter for more, q to quit: ")
            user_input = input()
            if user_input.lower() == 'q':
                break
        start_index = end_index

def print_day(db_day_name):
    # Get current day info
    if db_day_name == "current":
        with open("db/db_day.info") as f:
            db_day_name = f.read()

    db_day_filepath = f"db/{db_day_name}"
    db_day = shelve.open(db_day_filepath, writeback=True)

    os.system('clear')
    print("\t\t\tDAY STATS")

#            print(f"DAY: {datetime.fromtimestamp(db_day['name'])}")
    print(f"\n\n+-------------- Total Notes Played Today: {db_day['total_notes_played']} --------------+\
    \n+-------------- Total Time Pressed Today: {db_day['total_time_pressed']} --------------+\n\n")

            # Find and print total note stats
    print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
    for k, v in db_day["total_notes"].items():
        print(f"{k}\t\t\t{v.times_played}\t\t\t\t{v.total_time}")

    db_day.close()
    print_totals()

def print_totals():
    print("Please choose an option")
    print("1) Previous Session")
    print("2) Day Totals")
    print("3) Lifetime Totals")
    print("4) Show Days Between Date Range (YYYYMMDD - YYYYMMDD)")
    print("5) Show Sessions On Date (YYYYMMDD - YYYYMMDD)")
    print("6) Show Sessions Between Date Range (YYYYMMDD - YYYYMMDD)")
    print("7) Browse Days")
    stat_type = input()

    # Get previous session info
    with open("db/current_session.info") as f:
        previous_session_name = f.read()

    previous_session_fp = f"db/{previous_session_name}"
    
    match stat_type:
        case "1":
            db_day = shelve.open(db_day_filepath, writeback=True)
            os.system('clear')
            print("\t\t\tPREVIOUS SESSION STATS")
            
            last_session = list(db_day["session_dict"])[-1]
            if not "session_end" in db_day["session_dict"][last_session]:
                last_session = list(db_day["session_dict"])[-2]
            
            print(f'SESSION START: {datetime.fromtimestamp(db_day["session_dict"][last_session]["session_start"])}')
            print(f'SESSION END: {datetime.fromtimestamp(db_day["session_dict"][last_session]["session_end"])}')
            print(f'\n\n\nSESSION NAME: {db_day["session_dict"][last_session]["session_name"]}')
            print(f'Total Session Runtime: {db_day["session_dict"][last_session]["total_session_runtime"]}')

            print(f"\n+-------------- Total Notes Played: {db_day['session_dict'][last_session]['total_notes_played']} --------------+\
            \n+-------------- Total Time Pressed: {db_day['session_dict'][last_session]['total_time_pressed']} --------------+\n\n")

            # Find and print total note stats
            print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
            for note, val in db_day["session_dict"][last_session]["total_notes"].items():
                print(f"{note}\t\t\t{val.times_played}\t\t\t\t{val.total_time}")

            db_day.close()

            print_totals()

            
    # Current Day totals
        case "2":
            print_day("current")

    # Lifetime totals
        case "3": 
            db_LIFETIME_filepath = f'db/LIFETIME'
            db_LIFETIME = shelve.open(db_LIFETIME_filepath, writeback=True)
            print("\t\t\LIFETIME STATS")
            os.system('clear')
            print(f'Total Session Runtime: {db_LIFETIME["total_session_runtime"]}')

            print(f"\n+-------------- Total Notes Played: {db_LIFETIME['total_notes_played']} --------------+\
            \n+-------------- Total Time Pressed: {db_LIFETIME['total_time_pressed']} --------------+\n\n")

            # Find and print total note stats
            print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
            for note, val in db_LIFETIME["total_notes"].items():
                print(f"{note}\t\t\t{val.times_played}\t\t\t\t{val.total_time}")

            db_LIFETIME.close()
            print_totals()

        case "4":
            start_date = input("START DATE:  ")
            if len(start_date) != 8:
                print("Must be in format 'YYYYMMDD'")
            
            end_date = input("END DATE:  ")
            if len(start_date) != 8:
                print("Must be in format 'YYYYMMDD'")

            date_list = list()

            db_lifetime = shelve.open("db/LIFETIME")
            os.system('clear')
            i = 0
            date_total = len(db_lifetime["date_list"])
            
            for date in db_lifetime["date_list"]:
                if date >= start_date and date <= end_date:
                    print(date)
                    i += 1
                    if i > 20:
                        cont_prompt = input("Press ENTER To Continue OR type date (YYYYMMDD) for more info")
                        if cont_prompt == '':
                            i = 0
                            os.system('clear')

                        elif len(cont_prompt) != 8 or cont_prompt not in date_list:
                            cont_prompt = input("Please enter a valid date (YYYYMMDD)")
                        
                        else:
                            print_day(cont_prompt)
                        
                    date_list.append(date)

            view_day = input("Type date (YYYYMMDD) for more info, otherwise press ENTER to exit")
            if view_day == '':
                print_totals()
            elif len(view_day) != 8 or view_day not in date_list:
                view_day = input("Please enter a valid date (YYYYMMDD)")
            else:
                print_day(view_day)
#            enum_date = enumerate(date_list)
#            date_dict = dict((k, v) for k, v in enum_date)
#            print(date_dict)

    # Custom totals
        case _:
            print("\nPlease select an option by inputing a number\n")

            print_totals()

def print_current_session(current_session):
    os.system('clear')
    print("\t\t\tCURRENT SESSION STATS")
    #print(f'SESSION START: {db_day["session_dict"][current_session]["session_start"]}')
    print(f'\nSESSION NAME: {current_session["session_name"]}')
#          print(f'Total Session Runtime: {db_day["session_dict"][current_session]["session_runtime"]}')
    print(f'SESSION TIME ELAPSED: {time.time() - current_session["session_start"]}')

    print(f"\n+-------------- Total Notes Played: {current_session['total_notes_played']} --------------+\
    \n+-------------- Total Time Pressed: {current_session['total_time_pressed']} --------------+\n\n")

    # Find and print total note stats
    print(f"Note\t\tTotal Times Played\t\tTotal Time Pressed")
    for note, val in current_session["total_notes"].items():
        print(f"{note}\t\t\t{val.times_played}\t\t\t\t{val.total_time}")        

if __name__ == "__main__":
    os.system('clear')
    
    print_totals()