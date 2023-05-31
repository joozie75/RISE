# RISE
Code for RISE: Recording Individual Student Engagement

RISE_hardware/RISE_hardware.ino is the code that must be loaded into the Arduino IDE for upload into your FireBeetle ESP32 microcontroller. Note you should adjust the IP address from the hardcoded value of 192.168.10.42 on line 23 to something that will work with your local network. Similarly, adjust the Wifi SSID and password on lines 15 and 16 to work with your Wifi setup.

RISE/ contains the python code: from this directory, run "python server.py --dbname my_school.db"

Once server is running, turn on your RISE device, and go to the url "http://127.0.0.1:5000/" on a web browser.

From here, you can add students and color signatures to your classes, delete them, etc. 

Once a class has begun, click the "Start Monitor" button and then click "Class Monitor Tab" to move to a new tab showing the students in your class with a table of a record of their handraises for the day.

