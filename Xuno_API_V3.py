import requests
import os
from html2image import Html2Image
from datetime import datetime, timedelta

hti = Html2Image()


id_num = 0       #https://pmsc.xuno.com.au/index.php/timetable/33/2025-07-04 /33/ is the id number for me
Username = ''    #username email
Password = ''    #password 


target_date = datetime.now().strftime("%Y-%m-%d")

# Start a session to maintain cookies
session = requests.Session()

# Login request
login_url = 'https://pmsc.xuno.com.au/index.php?do=login'
login_data = {
    'username': Username,
    'password': Password,
    'do': 'login',
    'redirect': f"/index.php/timetable/{id_num}/"
}
session.post(login_url, data=login_data)

# Get the timetable JSON from the API
api_url = f"https://pmsc.xuno.com.au/api/v1/index.php/students/{id_num}/timetable?date={target_date}"
response = session.get(api_url)
data = response.json()

# --- Find the week (Monday to Friday) containing target_date ---
target_dt = datetime.strptime(target_date, "%Y-%m-%d")
monday = target_dt - timedelta(days=target_dt.weekday())
week_dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]  # Only Mon-Fri

# --- Build a mapping: date -> periods ---
date_to_periods = {d['date']: d.get('periods', []) for d in data['data']['dates'] if d['date'] in week_dates}

# --- Find all unique period numbers and their times ---
period_times = {}
for periods in date_to_periods.values():
    for period in periods:
        pnum = period.get('period', '')
        timetable_obj = period['timetables'][0]['timetable']
        start = timetable_obj.get('starttime', '')
        end = timetable_obj.get('endtime', '')
        if pnum and (pnum not in period_times):
            period_times[pnum] = (start, end)
# Sort periods by period number (as int if possible)
sorted_periods = sorted(period_times.keys(), key=lambda x: int(x) if str(x).isdigit() else x)

# --- HTML Table ---
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

# Table header: days (Mon-Fri only)
for i, d in enumerate(week_dates):
    dayname = (monday + timedelta(days=i)).strftime("%a %d %b %Y")
    html += f'<th class="day-col">{dayname}</th>'
html += '</tr>\n'

# Table body: periods as rows, days as columns
for pnum in sorted_periods:
    start, end = period_times[pnum]
    html += f'<tr><td class="period-col">{pnum}<br><span class="period-time">{start}–{end}</span></td>'
    for d in week_dates:
        cell = ""
        periods = date_to_periods.get(d, [])
        period = next((p for p in periods if str(p.get('period', '')) == str(pnum)), None)
        # --- Event/Program logic ---
        event_display = ""
        # Check for events/programs in sessions_by_date
        sessions = data['data'].get('sessions_by_date', {}).get(d, [])
        for session in sessions:
            # Match session_time to period start time
            session_time = session.get('session_time', '')
            session_name = session.get('name', '')
            room_name = session.get('room_name', '')
            session_start = session.get('session_start_time', '')
            session_end = session.get('session_end_time', '')
            # If the session time matches the period start time, display it
            if session_time == start:
                event_display += (
                    f"<div class='replacement' style='background:#ffe6b3;color:#23272a;'>"
                    f"• {session_name}<br>"
                    f"{session_start} - {session_end} {room_name}"
                    f"</div>"
                )
        if period:
            timetable_obj = period['timetables'][-1]['timetable']
            class_info = timetable_obj['class']
            teachers = class_info.get('teachers', [])
            teacher_display = []
            replacement_found = False
            room_change_found = False
            room = timetable_obj.get('roomlist', '')
            # Check for teacher and room replacements
            for t in teachers:
                # Teacher replacement
                if t.get("replacement_staff"):
                    replacement_found = True
                    rep_first = t.get("replacement_firstname", "")
                    rep_surname = t.get("replacement_surname", "")
                    rep_full = f"{rep_first} {rep_surname}".strip()
                    rep_display = t.get("replacement_staff")
                    teacher_display.append(rep_display if rep_display else rep_full)
                else:
                    teacher_display.append(t.get("displayname", ""))
                # Room replacement (if present in teacher object)
                if t.get("replacement_room"):
                    room_change_found = True
                    room = t.get("replacement_room")
            teacher_names = "<br>".join(teacher_display)
            class_name = period.get('className', '')
            cancelled = timetable_obj.get('cancelled', False)
            cell += f"{class_name}<br>"
            if teacher_names:
                cell += f"<span style='font-style:italic;color:#666'>{teacher_names}</span><br>"
            if room:
                cell += f"{room}<br>"
            if replacement_found:
                cell += f"<span class='replacement'>{teacher_names}</span>"
            if room_change_found:
                cell += f"<span class='replacement'>Room Change: {room}</span>"
            if cancelled:
                cell += "<span class='cancelled'>CANCELLED</span>"
        # Add event/program display at the end of the cell
        cell += event_display
        html += f"<td>{cell}</td>"
    html += "</tr>\n"

html += """
</table>
</div>
</body>
</html>
"""

# Save HTML to file
html_path = os.path.abspath('timetable.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# Set output path for images and save as image
hti.output_path = os.path.dirname(html_path)
hti.screenshot(html_file=html_path, save_as='timetable.png', size=(1920, 1080))

print(f"Timetable saved as {html_path} and {os.path.join(hti.output_path, 'timetable.png')}")
