from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import sys
from io import StringIO
from RISE_server import participationater as pp
import argparse
import threading
import datetime

listening_thread = None

def _parse_args():
    parser = argparse.ArgumentParser(description="RISE with multiple modes of operation")
    parser.add_argument("--dbname", help="Name of the database", default="test0.db")
    args = parser.parse_args()
    return args

app = Flask(__name__)

# Connect to the SQLite database
#conn = sqlite3.connect('test0.db', check_same_thread=False)  # We add check_same_thread=False because Flask runs on multiple threads

# Redirect stdout to a string buffer
sys.stdout = mystdout = StringIO()

@app.route('/', methods=['GET', 'POST'])
def home():
    global dbname, c, listening_thread
    class_name=""
    if request.method == 'POST':
        if 'add_student' in request.form:
            assert pp.conn is not None
            student_name = request.form.get('student_name')
            class_name = request.form.get('class_name')
            signature = request.form.get('signature')
            pp.add_student(c, student_name,class_name,signature)
            print(f"Added student: {student_name} in class: {class_name} with signature: {signature}")
        elif 'delete_student' in request.form:
            assert pp.conn is not None
            student_name = request.form.get('student_name')
            class_name = request.form.get('class_name')
            pp.delete_student(c, student_name,class_name)
            print(f"Deleted student: {student_name} from class: {class_name}")
        elif 'show_class' in request.form:
            assert pp.conn is not None
            class_name = request.form.get('class_name')
            pp.classlist(c,class_name=class_name)
        elif 'show_student' in request.form:
            assert pp.conn is not None
            student_name = request.form.get('student_name')
            class_name = request.form.get('class_name')
            c.execute("SELECT * FROM class_student WHERE student_name = ?", (student_name,))
            info = c.fetchall()
            print(f"Student information for {student_name}: {info}")
            print(f"Student information for {student_name}: {info}")
        elif 'show_raises' in request.form:
            assert pp.conn is not None
            class_name = request.form.get('class_name')
            pp.raiseslist(c,class_name=class_name)
        elif 'startmonitor' in request.form:
            class_name = request.form.get('class_name')
            pp.stop_listen = False
            def bgtask():
                pp.listen_to_events(f"http://{pp.ipaddr}:{pp.port}/events", class_name)
            listening_thread = threading.Thread(target=bgtask)
            listening_thread.start()
            print(f"Listening to http://{pp.ipaddr}:{pp.port}/events for events in class {class_name}")
            #pp.listen_to_events(f"http://{pp.ipaddr}:{pp.port}/events",class_name)
        elif 'stopmonitor' in request.form:
            class_name = request.form.get('class_name')
            print(f"Stop listening to http://{pp.ipaddr}:{pp.port}/events for events in class {class_name}")
            pp.stop_listen=True
            if listening_thread is not None:
                listening_thread.join()
                listening_thread = None
        elif 'refresh' in request.form:
            class_name = request.form.get('class_name')
            pass

    # Get the stdout string
    stdout_string = mystdout.getvalue()
    return render_template('index.html', stdout_string=stdout_string, dbname=dbname, class_name=class_name, hardwareip=f"{pp.ipaddr}:{pp.port}")

@app.route('/class/<class_name>', methods=['GET'])
def class_handraises(class_name):
    global c
    date=datetime.datetime.now()
    datestr = f'{date:%Y-%m-%d}'
    c.execute('''
        SELECT class_student.student_name, COUNT(handRaises.signature)
        FROM class_student
        LEFT JOIN handRaises ON class_student.signature = handRaises.signature
        AND DATE(handRaises.raise_time) = DATE(?) and class_student.class_name=handRaises.class_name
        WHERE class_student.class_name = ? 
        GROUP BY class_student.student_name
        ORDER BY COUNT(handRaises.signature) ASC
    ''', (date,class_name))
    students = c.fetchall()
    return render_template('classtable.html', students=students, class_name=class_name, datestr=datestr, listening_status=f"Listening is {'on' if not pp.stop_listen else 'off'}")

if __name__ == '__main__':
    args = _parse_args()
    c, pp.conn = pp.dbcc(args.dbname)
    dbname = args.dbname
    pp.stop_listen=True
    app.run(debug=True)