# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import sqlite3
import argparse
import requests
import sys
import datetime
import os

#ipaddr = '192.168.10.42'
#port = '80'

silentperiod = True

n_seen = 0
n_notseen = 0
nsperiodlen = 0
stop_listen = False


def _parse_args():
    parser = argparse.ArgumentParser(description="RISE with multiple modes of operation")

    parser.add_argument("mode", choices=["init", "add-students", "delete-students", "main", "class-list"], help="Operation mode")
    parser.add_argument("--dbname", help="Name of the database", default="test0.db")
    parser.add_argument("--classname", help="Name of class", required=False)
    parser.add_argument("--device_ip", help="IP addr of RISE device", default="192.168.10.42", required=False)
    parser.add_argument("--device_port", help="PORT of RISE device", default="80", required=False)

    args = parser.parse_args()
    return args


def dbcc(name):
    if os.path.exists(name):
        conn = sqlite3.connect(name,check_same_thread=False)
        c=conn.cursor()
    else:
        c,conn = dbinit(name)
    return c,conn


# Create table for students and handraises
def dbinit(name):
    if os.path.exists(name):
        os.remove(name)

    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute('''CREATE TABLE class_student
             (class_name TEXT,
             student_name TEXT,
             signature INTEGER PRIMARY KEY,
             UNIQUE (student_name, class_name))''')

    # Create table for handRaises
    c.execute('''CREATE TABLE handRaises
             (raise_id INTEGER PRIMARY KEY AUTOINCREMENT,
             signature INTEGER,
             raise_time TIMESTAMP,
             class_name TEXT,
             FOREIGN KEY(signature, class_name) REFERENCES class_student(signature, class_name))''')

    # Commit the changes
    conn.commit()
    return c, conn

def delete_student(c, student_name = None, class_name=None):
    global conn
    """
    Deletes a student from the class_student table.

    Args:
        c: db cursor.
        student_name Optional(str): The class name.
        class_name Optional(str): The class name.

    Returns:
        None.
    """
    if student_name is None:
        student_name = input("Enter the student's name (or 'EXIT' to exit, or 'ALL' for all students): ")
    if student_name == 'EXIT':
        return False
    if class_name is None:
        class_name = input("Enter the class name: ")
    # Delete the student from the class_student table
    if student_name=='ALL':
        c.execute("DELETE FROM class_student WHERE class_name = ?", (class_name,))
    else:
        c.execute("DELETE FROM class_student WHERE student_name = ? AND class_name = ?", (student_name, class_name))

    # Commit the changes
    conn.commit()
    return True

def add_student(c, student_name = None, class_name = None, signature=None):
    """
    Adds student to database. Prompts the user to input a student's name, class name, and signature as necessary.

    Args:
        c: db cursor.
        student_name Optional(str): The class name.
        class_name Optional(str): The class name.

    """
    # Prompt the user to input the student's information if necessary
    global conn
    if student_name is None:
        student_name = input("Enter the student's name (or 'EXIT' to exit): ")
    if student_name=='EXIT':
        return False
    if class_name is None:
        class_name = input("Enter the class name: ")
    if signature is None:
        signature = int(input("Enter the student's signature (a 3-digit number): "))
    c.execute("SELECT 1 FROM class_student WHERE signature = ? AND class_name = ? and student_name != ?",
              (signature, class_name, student_name))
    if c.fetchone() is not None:
        print(f"Signature {signature} is already in use by another student in {class_name}.")
        return True

    # Insert the student into the class_student table or update their signature if they already exist
    c.execute("INSERT OR REPLACE INTO class_student (student_name, class_name, signature) VALUES (?, ?, ?)",
              (student_name, class_name, signature))

    # Commit the changes
    conn.commit()
    return True

def handleblock(c, signature, ang, secs, class_name, minmsgs=4, reset=False):
    # takes a (signature, ang, secs) tuple, determines whether it is a hand-raising period (eg teacher asked question)
    # and if, determines who raised their hand during the period and saves it into the database
    global silentperiod, n_seen, n_notseen, nsperiodlen
    if not hasattr(handleblock, 'cd'):
        handleblock.cd = {}
    if reset:
        handleblock.cd = {}
        return
    if silentperiod:
        if signature > 0:
            n_seen = n_seen + 1
        if n_seen > minmsgs:
            silentperiod = False
            print(f"silentperiod ended: {datetime.datetime.now(): %H:%M:%S}")
            handleblock.cd = {}
            nsperiodlen = minmsgs
            n_seen = 0
    if not silentperiod:
        if signature < 0:
            n_notseen = n_notseen + 1
        else:
            nsperiodlen = nsperiodlen + 1
            if signature in handleblock.cd:
                handleblock.cd[signature] = handleblock.cd[signature] + 1
            else:
                handleblock.cd[signature] = 1

        if n_notseen > minmsgs:
            n_notseen = 0
            silentperiod = True
            print(f"silentperiod begin: {datetime.datetime.now(): %H:%M:%S}")
            who_raised(c, handleblock.cd, nsperiodlen, class_name)
            report_stats(c, class_name)

    #print("is a silentperiod?", silentperiod)



def classlist(c, class_name=None):
    # prints class list for class_name
    global conn
    if class_name is not None:
        c.execute('''
                SELECT student_name, class_name, signature
                FROM class_student 
                WHERE class_name = ?
                ''', (class_name,))
    else:
        c.execute('''SELECT student_name, class_name, signature
                        FROM class_student''')


    # Fetch the results and print the report
    rows = c.fetchall()
    if rows:
        print(f"Class list:")
        for student_name, classname, signature in rows:
            print(f"{student_name}, {classname}: {signature}")
    else:
        print("No students found.")

def raiseslist(c, class_name=None):
    # prints data in database for handraises that have been detected for class_name
    global conn
    if class_name is not None and len(class_name)>0:
        c.execute('''
                SELECT signature, raise_time, class_name
                FROM handRaises
                WHERE class_name = ?
                ''', (class_name,))
    else:
        c.execute('''
                SELECT signature, raise_time, class_name
                FROM handRaises''')


    # Fetch the results and print the report
    rows = c.fetchall()
    if rows:
        print(f"Handraises detected (signature, class, raise_time):")
        for signature,raise_time,classname in rows:
            if len(classname)>0:
                print(f"{signature}, {classname}, {raise_time}")
    else:
        print("No raises found.")

def report_stats(c, class_name):
    date = datetime.datetime.now()
    """
    Prints a report showing the number of hand raises each student in a class has on a day.

    Args:
        c: db cursor
        class_name (str): The class name

    Returns:
        None.
    """
    # Define the start and end times of the day
    # start_time = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    end_time = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)

    # Use a JOIN to count the hand raises on that day for each student in the class
    # c.execute('''
    #     SELECT class_student.student_name, COUNT(handRaises.raise_id)
    #     FROM handRaises
    #     JOIN class_student
    #     ON handRaises.signature = class_student.signature
    #     WHERE class_student.class_name = ?
    #     AND handRaises.raise_time BETWEEN ? AND ?
    #     GROUP BY class_student.student_name
    # ''', (class_name, start_time, end_time))

    c.execute('''
            SELECT class_student.student_name, COUNT(handRaises.signature)
            FROM class_student
            LEFT JOIN handRaises ON class_student.signature = handRaises.signature
            AND DATE(handRaises.raise_time) = DATE(?) and class_student.class_name=handRaises.class_name
            WHERE class_student.class_name = ? 
            GROUP BY class_student.student_name
            ORDER BY COUNT(handRaises.signature) ASC
        ''', (end_time,class_name))


    # Fetch the results and print the report
    rows = c.fetchall()
    if rows:
        print(f"Hand raise report for {class_name} on {date: %Y-%m-%d %H:%M:%S}:")
        for student_name, count in rows:
            print(f"{student_name}: {count} hand raises")
    else:
        print(f"No hand raises in {class_name} on {date: %Y-%m-%d %H:%M:%S}")


def who_raised(c, cd, tot, class_name, mul=5):
    # determines who in the count dictionary, cd, has enough time raising hand to be counted
    # use mul to say that a student is counted if his hand-raising detections is 1/mul of the total possible
    raise_time = datetime.datetime.now()
    for k in cd:
        if cd[k] * mul > tot:
            record_handraise(c, k, class_name, raise_time)


def record_handraise(c, signature, class_name, raise_time):
    # save handraise event to the database
    global conn
    c.execute("INSERT INTO handRaises (signature, raise_time, class_name) VALUES (?, ?, ?)", (signature, raise_time, class_name))
    conn.commit()


def process_event(c, event, class_name):
    #parses the event message coming from the hardware device over the ip address
    if len(event) == 1:
        return
    if len(event.split(',')) == 3:
        event = event[6:]
        sigstr, angstr, secstr = event.split(',')
        sig = int(float(sigstr.split(':')[1]))
        ang = int(float(angstr.split(':')[1]))
        secs = float(secstr.split(':')[1])
        handleblock(c, sig, ang, secs, class_name)
        #print(f"Received event {datetime.datetime.now():%H:%M:%S}: {sig},{ang},{secs}, {class_name}")
    else:
        pass
        #print(f"Received unparseable event {datetime.datetime.now():%H:%M:%S}: {event}, {len(event)}, {class_name}")


def listen_to_events(url, class_name):
    # Connect to the device output server at url
    c=conn.cursor()
    response = requests.get(url, stream=True)

    buffer = ""
    for chunk in response.iter_content(chunk_size=1):  # Read one byte at a time
        if chunk:  # skip keep-alive newlines
            decoded_chunk = chunk.decode('utf-8')
            if decoded_chunk == '\n':
                process_event(c, buffer, class_name)
                buffer = ""
            else:
                buffer += decoded_chunk
        if stop_listen:
            print('Stop signal detected')
            handleblock(c,-1,0,0,None, reset=True)
            break


#listen_to_events(f"http://{ipaddr}:{port}/events")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # could run this code from command line instead of the web interface
    args = _parse_args()

    if args.mode == "init":
        c,conn=dbinit(args.dbname)
        exit()

    conn = dbcc(args.dbname)
    c=conn.cursor()
    if args.mode == "add-students":
        while add_student(c,class_name = args.classname):
            pass
        classlist(args.classname)
    elif args.mode == "delete-students":
        while delete_student(c, class_name = args.classname):
            pass
    elif args.mode=="class-list":
        classlist(c, args.classname)
    elif args.mode == "main":
        assert args.classname is not None, "Must specify a class"
        listen_to_events(f"http://{args.device_ip}:{args.device_port}/events", args.classname)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
