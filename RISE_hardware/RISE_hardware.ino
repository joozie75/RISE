


//#include <PixySPI_SS.h>
#include <PixyI2C.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Preferences.h>

String webhtml = "<html><body><h1>Hello, this is your ESP32!</h1><div id=\"log\"></div><script>var source = new EventSource('/events');"
"source.onmessage = function(event) {document.getElementById('log').innerHTML += event.data + '<br>';};</script></body></html>";

int SSPin= D13;
int ledPin = D9;
const char* ssid = "Ooi Circle";
const char* password = "Welcome, NSA!";

const char* prefdict = "ParticiPatron";
double secondscounter = 0.0;
Preferences prefs;
int msdelay = 1000;
int msdaddr = 0;
IPAddress localIP(192, 168, 10, 42);  // Desired static IP address
IPAddress gateway(192, 168, 10, 1);  // IP address of the network gateway
IPAddress subnet(255, 255, 255, 0); 

//PixySPI_SS pixy(SSPin);
PixyI2C pixy;
AsyncWebServer server(80);
AsyncEventSource events("/events");
// struct Student {
//   int signature;
//   int angle_lower;
//   int angle_upper;
//   int times_seen;
// };

// struct Student allstudents[2];
  
void message_out(String msg) {
  Serial.println(msg);
  events.send(msg.c_str());
}

void setup() {
  // put your setup code here, to run once:
  char buf[50];
  pinMode(ledPin, OUTPUT);

  Serial.begin(115200);

  prefs.begin(prefdict,false);
  msdelay = prefs.getInt("msdelay", msdelay);
  prefs.end();

  sprintf(buf, "msdelay initialized to %d from preferences",msdelay);
  Serial.println(buf);
  Serial.println("Attempting Wifi connetion...");
  if (1==1) {
    WiFi.config(localIP, gateway, subnet);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected.");
    Serial.println(WiFi.localIP());

    server.addHandler(&events);
    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
      String html = "<!DOCTYPE html><html><style>body {font-family: Arial, sans-serif;}</style><body><h1>RISE Device Portal</h1><div id='log'></div><script>var source = new EventSource('/events');source.onmessage = function(event) {var timestamp = new Date().toLocaleString();document.getElementById('log').innerHTML += timestamp + ': ' + event.data + '<br>';}</script></body></html>";
      request->send(200, "text/html", html);
    });
    server.on("/control", HTTP_GET, [](AsyncWebServerRequest *request){
      String html = "<html><style>body {font-family: Arial, sans-serif;}</style><body><h1>Delay in ms: " + String(msdelay) + "</h1>"
                  "<form method='POST' action='/update'>"
                  "New Value: <input type='number' name='newvalue'>"
                  "<input type='submit' value='Update'>"
                  "</form></body></html>";
      request->send(200, "text/html", html);
    });

    server.on("/update", HTTP_POST, [](AsyncWebServerRequest *request){
      if (request->hasArg("newvalue")) {
        int newValue = request->arg("newvalue").toInt();
        msdelay = newValue;
        prefs.begin(prefdict,false);
        prefs.putInt("msdelay",msdelay);
        prefs.end();
        Serial.println("Variable updated and saved: " + String(msdelay));
      }
      else {
        Serial.println("Variable not updated: " + String(msdelay));
      }
      request->redirect("/");
    });
    server.begin();
    
  }

  pixy.init();
  // allstudents[0].signature=12;
  // allstudents[0].angle_lower=-45;
  // allstudents[0].angle_upper=45;
  // allstudents[0].times_seen=0;

  // allstudents[1].signature=13;
  // allstudents[1].angle_lower=-45;
  // allstudents[1].angle_upper=45;
  // allstudents[1].times_seen=0;
  

}

void loop2(){

  message_out("Testing");
  delay(1000);
}

void loop() {
  // put your main code here, to run repeatedly:
  static int i = 0;
  int j;
  uint16_t numblocks;
  char buf[50]; 
  
  // grab blocks!
  numblocks = pixy.getBlocks();
  secondscounter = secondscounter + msdelay/1000.0;
  
  // If there are detect blocks, print them!
  if (numblocks)
  {
    Serial.println("some blocks");
    for (j=0;j<numblocks;j++) {
      //pixy.blocks[j].print();
      forwardblock(pixy.blocks[j], secondscounter);

    }
  } 
  else {
    sprintf(buf,"signature:-1,angle:0,seconds:%f",secondscounter);
    message_out(buf);
  }
  delay(msdelay);
}

int decimal_to_octal(int decimal) {
  int quotient;
  int octal=0;
  int i=1;

  quotient = decimal;

  while (quotient != 0) {
        octal += (quotient % 8) * i;
        quotient /= 8;
        i *= 10;
  }
  return octal;
}

void forwardblock(Block blk, double secondscounter) {
  int j;
  int16_t realangle, realsig;
  char buf[50];
  String output="";
  realangle = int16_t(blk.angle);
  realsig = decimal_to_octal(blk.signature);
  sprintf(buf, "signature:%d,angle:%d,seconds:%f\n", realsig, realangle,secondscounter);
  output = output+(String)buf;
  // for (j=0;j<numstudents;j++) {
  //   if (studentinfo[j].signature==realsig) {
  //     if ((studentinfo[j].angle_lower<realangle) && (studentinfo[j].angle_upper>realangle)) {
  //       studentinfo[j].times_seen++;
  //       sprintf(buf, "Have seen student %d %d times\n", j, studentinfo[j].times_seen);
  //       output = output+(String)buf;
  //       break;
  //     }
  //   }
  // }
  message_out(output);
}