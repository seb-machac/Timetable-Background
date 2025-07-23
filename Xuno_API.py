#---- Imports ----

import requests                                                                                             # https://requests.readthedocs.io/en/latest/
import os                                                                                                   # https://docs.python.org/3/library/os.html
from html2image import Html2Image                                                                           # https://github.com/vgalin/html2image
from datetime import datetime, timedelta                                                                    # https://docs.python.org/3/library/datetime.html

#-------------------------------------------------------------------------------------------------------

                                                                                                            #---- Variables ----

hti = Html2Image()                                                                                          # Sets hti to be Html2Image


id_num = 00                                                                                                 # Student ID (found at https://pmsc.xuno.com.au/index.php/timetable/33/2025-07-04, where 33 is the id number)
Username = 'First.LastName@portmelbournesc.vic.edu.au'                                                      # Email (firstname.lastname@portmelbournesc.vic.edu.au)
Password = 'Pass'                                                                                           # Password (Usually DD/MM/YY format unless manually changed)

#-------------------------------------------------------------------------------------------------------

                                                                                                            #---- Check if Details are entered correctly ----

if id_num == "" or Username == '' or Password == '':                                                        # If any fields are empty:
    print("One or more fields are empty.\nPlease update them to your details before running.")              # Print error
    os._exit(0)                                                                                             # Exit code

#-------------------------------------------------------------------------------------------------------

target_date = datetime.now().strftime("%Y-%m-%d")                                                           # Sets current time

#-------------------------------------------------------------------------------------------------------

session = requests.Session()                                                                                # Start a session to maintain cookies

#-------------------------------------------------------------------------------------------------------

                                                                                                            #---- Send HTTPS Request ----

login_url = 'https://pmsc.xuno.com.au/index.php?do=login'                                                   # Login request
login_data = {
    'username': Username,
    'password': Password,
    'do': 'login',
    'redirect': f"/index.php/timetable/{int(id_num)}/"
}
session.post(login_url, data=login_data)                                                                    # Sends post command to current session

#-------------------------------------------------------------------------------------------------------

                                                                                                            #---- JSON Handling ----

api_url = f"https://pmsc.xuno.com.au/api/v1/index.php/students/{int(id_num)}/timetable?date={target_date}"  # URL for the timetable.json file
response = session.get(api_url)                                                                             # Get the timetable JSON from the API
data = response.json()                                                                                      # Save JSON as a variable


target_dt = datetime.strptime(target_date, "%Y-%m-%d")                                                      # Find the week (Monday to Friday) containing target_date
monday = target_dt - timedelta(days=target_dt.weekday())                                                    # Sets Mondays date
week_dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]                          # Sets the week dates (only Mon-Fri)

date_to_periods = {                                                                                         # Build a map for date to periods
    d['date']: d.get('periods', []) for d in data['data']['dates'] if d['date'] in week_dates               # Connect dates to periods
    }

                                                                                                            #---- Find all unique period numbers and their times----
period_times = {}                                                                                           # Create empty array for period times
for periods in date_to_periods.values():                                                                    # Loops for periods per day
    for period in periods:                                                                                  # Loops for each period in periods group
        pnum = period.get('period', '')                                                                     # Sets pnum to current period
        timetable_obj = period['timetables'][0]['timetable']                                                # Creates an timetable object for each period
        start = timetable_obj.get('starttime', '')                                                          # Finds start time for current period
        end = timetable_obj.get('endtime', '')                                                              # Finds end time for current period
        if pnum and (pnum not in period_times):                                                             # If current period number isn't in period_times:
            period_times[pnum] = (start, end)                                                               # Adds start and end times to current period in period_times array

sorted_periods = sorted(period_times.keys(), key=lambda x: int(x) if str(x).isdigit() else x)               # Sort periods by period number (as int if possible)

#-------------------------------------------------------------------------------------------------------

#HTML Table
html = f"""
<html>
<head>
    <title>Timetable for week of {datetime.now().strftime('%d %b %Y %H:%M:%S')}</title>
    <meta charset="utf-8">
    <style>
        body {{
            background: #181a1b;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 95vw;
            height: 95vh;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        table {{
            width: 100%;
            max-width: 1800px;
            table-layout: fixed;
            border-collapse: collapse;
            background: #23272a;
            font-size: 1.1vw;
            box-shadow: 0 0 16px #111;
        }}
        th, td {{
            border: 1px solid #333;
            padding: 0.5em;
            vertical-align: top;
            word-break: break-word;
        }}
        th {{
            background: #2c2f34;
            font-weight: bold;
            text-align: center;
            color: #fff;
        }}
        .period-time {{
            color: #b0b0b0;
            font-size: 0.95em;
            font-style: italic;
            margin-bottom: 0.2em;
        }}
        .replacement {{
            background: #ffb84d;
            font-weight: bold;
            color: #23272a;
            border-radius: 4px;
            padding: 0.2em 0.3em;
            display: block;
        }}
        .cancelled {{
            background: #444;
            color: #bbb;
            font-weight: bold;
            border-radius: 4px;
            padding: 0.2em 0.3em;
            display: inline-block;
        }}
        .period-col {{
            width: 6vw;
            background: #202225;
            text-align: center;
            font-weight: bold;
            color: #fff;
        }}
        .day-col {{
            width: 16vw;
        }}
    </style>
</head>
<body>
<div class="container">
<h2>Timetable for week of {datetime.now().strftime('%d %b %Y %H %M %S')}</h2>                               
<table>
    <tr>
        <th class="period-col"></th>
"""

                                                                                                            #---- Table header: days (Mon-Fri only) ----
for i, d in enumerate(week_dates):                                                                          # For i and d in week_dates:
    dayname = (monday + timedelta(days=i)).strftime("%a %d %b %Y")                                          # Set dayname correctly
    html += f'<th class="day-col">{dayname}</th>'                                                           # Add to the HTML
html += '</tr>\n'                                                                                           # Finish with a new table row and line


                                                                                                            #---- Creating Table ----
for pnum in sorted_periods:                                                                                 # For each period number:
    html += f'<tr><td class="period-col">{pnum}<br><span class="period-time">{start}–{end}</span></td>'     # Add each period number and times into table rows
    for d in week_dates:                                                                                    # For each day in the week:
        cell = ""                                                                                           # Creates empty cell variable
        periods = date_to_periods.get(d, [])                                                                # Map periods to period dates
        period = next((p for p in periods if str(p.get('period', '')) == str(pnum)), None)                  # Set next period

                                                                                                            # --- Event/Program logic ---
        event_display = ""                                                                                  # Create empty event variable
        sessions = data['data'].get('sessions_by_date', {}).get(d, [])                                      # Check for events/programs in sessions_by_date
        for session in sessions:                                                                            # For each session:
            session_time = session.get('session_time', '')                                                  # Set session_time to period time
            session_name = session.get('name', '')                                                          # Set session name
            room_name = session.get('room_name', '')                                                        # Set session room name
            session_start = session.get('session_start_time', '')                                           # Set session start time
            session_end = session.get('session_end_time', '')                                               # Set session end time

            if session_time == start:                                                                       # If the session time matches the period start time:
                event_display += (                                                                          # Add data to event_display variable
                    f"<div class='replacement' style='background:#ffe6b3;color:#23272a;'>"                  # Create and open new div element
                    f"• {session_name}<br>"                                                                 # Add the session name
                    f"{session_start} - {session_end} {room_name}"                                          # Add the session times and room name
                    f"</div>"                                                                               # Close the div
                )

        if period:                                                                                          # If period:
            timetable_obj = period['timetables'][-1]['timetable']                                           # Set the timetable object
            class_info = timetable_obj['class']                                                             # Get the class information
            teachers = class_info.get('teachers', [])                                                       # Get the teacher information
            teacher_display = []                                                                            # Display the teachers
            replacement_found = False                                                                       # Set replacement_found to false
            room_change_found = False                                                                       # Set room_change_found to false
            room = timetable_obj.get('roomlist', '')                                                        # Get the room information
 
            for t in teachers:                                                                              # For every teacher:
                if t.get("replacement_staff"):                                                              # If there is a replacement teacher:
                    replacement_found = True                                                                # Set replacement_found to true
                    rep_first = t.get("replacement_firstname", "")                                          # Get the replacement teachers first name
                    rep_surname = t.get("replacement_surname", "")                                          # Get the replacement teachers last name
                    rep_full = f"{rep_first} {rep_surname}".strip()                                         # Join the first name and last name
                    rep_display = t.get("replacement_staff")                                                # Prepare to display this teacher
                    teacher_display.append(rep_display if rep_display else rep_full)                        # Add this teacher to the display object
                else:                                                                                       # Else:
                    teacher_display.append(t.get("displayname", ""))                                        # Get the default teachers name

                if t.get("replacement_room"):                                                               # If there is a replacement room:
                    room_change_found = True                                                                # Set room_change_found to true
                    room = t.get("replacement_room")                                                        # Get the room

            teacher_names = "<br>".join(teacher_display)                                                    # Get the teacher names
            class_name = period.get('className', '')                                                        # Get the class name
            cancelled = timetable_obj.get('cancelled', False)                                               # Set cancelled to true or false
            cell += f"{class_name}<br>"                                                                     # Create element for class name
            if teacher_names:                                                                               # If there is teacher data:
                cell += f"<span style='font-style:italic;color:#666'>{teacher_names}</span><br>"            # Create an element for the default teacher names
            if room:                                                                                        # If there is room data:
                cell += f"{room}<br>"                                                                       # Create an element for the default room data
            if replacement_found:                                                                           # If there is a replacement teacher:
                cell += f"<span class='replacement'>{teacher_names}</span>"                                 # Create an element for the replacement teacher names
            if room_change_found:                                                                           # If there is a room change:
                cell += f"<span class='replacement'>Room Change: {room}</span>"                             # Create an element for the room change data
            if cancelled:                                                                                   # If cancelled is true:
                cell += "<span class='cancelled'>CANCELLED</span>"                                          # Create an element saying "CANCELLED"

        cell += event_display                                                                               # Add all events/programs to the cell
        html += f"<td>{cell}</td>"                                                                          # Add the current cell to the table
    html += "</tr>\n"                                                                                       # Close the table element

                                                                                                            # Add closing statements to all html elements
html += """
</table>
</div>
</body>
</html>
"""

                                                                                                            #---- Save HTML to file ----
html_path = os.path.abspath('timetable.html')                                                               # Set file path
with open(html_path, 'w', encoding='utf-8') as f:                                                           # Open the file path
    f.write(html)                                                                                           # Write to the file

hti.output_path = os.path.dirname(html_path)                                                                # Set Html2Image output path
hti.screenshot(html_file=html_path, save_as='timetable.png', size=(1920, 1080))                             # Take a screenshot of the HTML file

print(f"Timetable saved as {html_path} and {os.path.join(hti.output_path, 'timetable.png')}")               # Print the html file path and image path
