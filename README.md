# RISE
Code for RISE: Recorder of Individual Student Engagement

RISE_hardware_arduino_ide/RISE_hardware.ino is the code that must be opened in the Arduino IDE for upload into your FireBeetle  2 ESP32-E microcontroller. Note you should adjust the IP address from the hardcoded value of 192.168.10.42 on line 23 to something that will work with your local network. Similarly, adjust the Wifi SSID and password on lines 15 and 16 to work with your Wifi setup. 

If you use the Arduino Cloud Web Editor then upload all the files in RISE_hardware_arduino_cloud/ to the web editor and then choose FireBeetle ESP32 as the device to upload to. Similarly, you will need to edit the Wifi SSID and password and IP address.

RISE_server/ contains the python code that runs the webserver that will parse the hardware messages into handraising events, associate them with students, and save to the database. To install, first install python 3.10. Then clone this repo into some directory, go to the "RISE/" directory; check that it contains "setup.py", and then run "pip install ."

After installation, from any directory, run "python -m RISE_server.server --dbname my_school.db --device_ip 192.168.10.42". If "my_school.db" does not already exist, it will be created in the current directory.

Once server is running, turn on your RISE device, and go to the url "http://127.0.0.1:5000/" on a web browser.

From here, you can add students and color signatures to your classes, delete them, etc. 

Once a class has begun, click the "Start Monitor" button and then click "Class Monitor Tab" to move to a new tab showing the students in your class with a table of a record of their handraises for the day.

