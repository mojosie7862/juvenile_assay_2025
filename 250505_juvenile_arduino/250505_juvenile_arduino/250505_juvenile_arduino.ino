//Zebra Fish 2x7 lane

//version 0.2
//Added timeout for the wire mesh control
//timeout defined as TIMEOUT, in millisecond, defined 2000 = 2000ms = 2 sec


//History
//version 0.1
//Initial project for fish lane control
//Serial setting - 9600bps
//Control code design
//lane, pdlc1, pdlc2, pdlc3, pdlc4, mesh1, mesh2
//example
//1,1,0,0,1,1,0 (lane 1, pdlc1/pdlc4/mesh1 ON, pdlc2/pdlc3/mesh2 OFF)


//#include <Adafruit_MCP23X08.h>
#include <Adafruit_MCP23X17.h>

#define LED_PIN 8     // MCP23XXX pin LED is attached to
#define BUTTON_PIN 1  // MCP23XXX pin button is attached to

#define L1_PDLC1  8
#define L1_PDLC2  9
#define L1_PDLC3  10
#define L1_PDLC4  11
#define L1_M1     12
#define L1_M2     13

#define L2_PDLC1  14
#define L2_PDLC2  15
#define L2_PDLC3  0
#define L2_PDLC4  1
#define L2_M1     2
#define L2_M2     3

#define L3_PDLC1  4
#define L3_PDLC2  5
#define L3_PDLC3  6
#define L3_PDLC4  7
#define L3_M1     8  // 21
#define L3_M2     9

#define L4_PDLC1  10
#define L4_PDLC2  11
#define L4_PDLC3  12
#define L4_PDLC4  13
#define L4_M1     14
#define L4_M2     15

#define L5_PDLC1  0
#define L5_PDLC2  1
#define L5_PDLC3  2
#define L5_PDLC4  3
#define L5_M1     4
#define L5_M2     5

#define L6_PDLC1  6
#define L6_PDLC2  7
#define L6_PDLC3  8   //22
#define L6_PDLC4  9
#define L6_M1     10
#define L6_M2     11

#define L7_PDLC1  12
#define L7_PDLC2  13
#define L7_PDLC3  14
#define L7_PDLC4  15
#define L7_M1     7
#define L7_M2     6

// only used for SPI
#define CS_PIN 6
#define ULONG_MAX 4294967295
#define TIMEOUT 10 //in ms

//For Serial Communication
String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

int lane, P1, P2, P3, P4, M1, M2;
char dtm[100];

unsigned long lane1_m1 = 0;
unsigned long lane1_m2 = 0;
unsigned long lane2_m1 = 0;
unsigned long lane2_m2 = 0;
unsigned long lane3_m1 = 0;
unsigned long lane3_m2 = 0;
unsigned long lane4_m1 = 0;
unsigned long lane4_m2 = 0;
unsigned long lane5_m1 = 0;
unsigned long lane5_m2 = 0;
unsigned long lane6_m1 = 0;
unsigned long lane6_m2 = 0;
unsigned long lane7_m1 = 0;
unsigned long lane7_m2 = 0;
// uncomment appropriate line
Adafruit_MCP23X17 mcp;
Adafruit_MCP23X17 mcp_21;
Adafruit_MCP23X17 mcp_22;

void setup() {
  Serial.begin(9600);
  //while (!Serial);
  // uncomment appropriate mcp.begin
  if (!mcp.begin_I2C(0x20)) {
  //if (!mcp.begin_SPI(CS_PIN)) {
    Serial.println("GPIO Board 1 Error.");
    while (1);
  }

  if (!mcp_21.begin_I2C(0x21)) {
  //if (!mcp.begin_SPI(CS_PIN)) {
    Serial.println("GPIO Board 2 Error.");
    while (1);
  }

  if (!mcp_22.begin_I2C(0x22)) {
  //if (!mcp.begin_SPI(CS_PIN)) {
    Serial.println("GPIO Board 3 Error.");
    while (1);
  }

  // configure pins for output
  mcp.pinMode(L1_PDLC1, OUTPUT);
  mcp.pinMode(L1_PDLC2, OUTPUT);
  mcp.pinMode(L1_PDLC3, OUTPUT);
  mcp.pinMode(L1_PDLC4, OUTPUT);
  mcp.pinMode(L1_M1, OUTPUT);
  mcp.pinMode(L1_M2, OUTPUT);

  mcp.pinMode(L2_PDLC1, OUTPUT);
  mcp.pinMode(L2_PDLC2, OUTPUT);
  mcp.pinMode(L2_PDLC3, OUTPUT);
  mcp.pinMode(L2_PDLC4, OUTPUT);
  mcp.pinMode(L2_M1, OUTPUT);
  mcp.pinMode(L2_M2, OUTPUT);

  mcp.pinMode(L3_PDLC1, OUTPUT);
  mcp.pinMode(L3_PDLC2, OUTPUT);
  mcp.pinMode(L3_PDLC3, OUTPUT);
  mcp.pinMode(L3_PDLC4, OUTPUT);
  mcp_21.pinMode(L3_M1, OUTPUT);
  mcp_21.pinMode(L3_M2, OUTPUT);

  mcp_21.pinMode(L4_PDLC1, OUTPUT);
  mcp_21.pinMode(L4_PDLC2, OUTPUT);
  mcp_21.pinMode(L4_PDLC3, OUTPUT);
  mcp_21.pinMode(L4_PDLC4, OUTPUT);
  mcp_21.pinMode(L4_M1, OUTPUT);
  mcp_21.pinMode(L4_M2, OUTPUT);

  mcp_21.pinMode(L5_PDLC1, OUTPUT);
  mcp_21.pinMode(L5_PDLC2, OUTPUT);
  mcp_21.pinMode(L5_PDLC3, OUTPUT);
  mcp_21.pinMode(L5_PDLC4, OUTPUT);
  mcp_21.pinMode(L5_M1, OUTPUT);
  mcp_21.pinMode(L5_M2, OUTPUT);

  mcp_21.pinMode(L6_PDLC1, OUTPUT);
  mcp_21.pinMode(L6_PDLC2, OUTPUT);
  mcp_22.pinMode(L6_PDLC3, OUTPUT);
  mcp_22.pinMode(L6_PDLC4, OUTPUT);
  mcp_22.pinMode(L6_M1, OUTPUT);
  mcp_22.pinMode(L6_M2, OUTPUT);

  mcp_22.pinMode(L7_PDLC1, OUTPUT);
  mcp_22.pinMode(L7_PDLC2, OUTPUT);
  mcp_22.pinMode(L7_PDLC3, OUTPUT);
  mcp_22.pinMode(L7_PDLC4, OUTPUT);
  mcp_22.pinMode(L7_M1, OUTPUT);
  mcp_22.pinMode(L7_M2, OUTPUT);

  // // configure button pin for input with pull up
  // mcp.pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println("Start...");

  all_off();

  unsigned long time_millis = millis();
  //prints time since program started\
  printLine("millis = ", time_millis);

}

void loop()
{
  // test_pattern_films();
  // test_pattern_films_shocks();
  process();
}

void processString(String str)
{
  strcpy( dtm, str.c_str());
  sscanf( dtm, "%d,%d,%d,%d,%d,%d,%d,%d", &lane, &P1, &P2, &P3, &P4, &M1, &M2 );
  printLine(lane, P1, P2, P3, P4, M1, M2 );
}

void process()
{
  if (stringComplete) {
      Serial.println(inputString);
      processString(inputString);
      output_control();
      // clear the string:
      inputString = "";
      stringComplete = false;
  }
  timeout_process();
}

void timeout_process()
{
    unsigned long time = millis();
      
    if (time >= lane1_m1 && lane1_m1 != 0){
        M1 = 0;
        lane1_m1 = 0;
        mcp.digitalWrite(L1_M1, M1);
        printLine("lane 1 M1 timeout - OFF");
    }

    if (time >= lane1_m2 && lane1_m2 != 0){
        M2 = 0;
        lane1_m2 = 0;
        mcp.digitalWrite(L1_M2, M2);
        printLine("lane 1 M2 timeout - OFF");
    }

    if (time >= lane2_m1 && lane2_m1 != 0){
        M1 = 0;
        lane2_m1 = 0;
        mcp.digitalWrite(L2_M1, M1);
        printLine("lane 2 M1 timeout - OFF");
    }
    if (time >= lane2_m2 && lane2_m2 != 0){
        M2 = 0;
        lane2_m2 = 0;
        mcp.digitalWrite(L2_M2, M2);
        printLine("lane 2 M2 timeout - OFF");
    }
    if (time >= lane3_m1 && lane3_m1 != 0){
        M1 = 0;
        lane3_m1 = 0;
        mcp_21.digitalWrite(L3_M1, M1);
        printLine("lane 3 M1 timeout - OFF");
    }
    if (time >= lane3_m2 && lane3_m2 != 0){
        M2 = 0;
        lane3_m2 = 0;
        mcp_21.digitalWrite(L3_M2, M2);
        printLine("lane 3 M2 timeout - OFF");
    }
    if (time >= lane4_m1 && lane4_m1 != 0){
        M1 = 0;
        lane4_m1 = 0;
        mcp_21.digitalWrite(L4_M1, M1);
        printLine("lane 4 M1 timeout - OFF");
    }
    if (time >= lane4_m2 && lane4_m2 != 0){
        M2 = 0;
        lane4_m2 = 0;
        mcp_21.digitalWrite(L4_M2, M2);
        printLine("lane 4 M2 timeout - OFF");
    }
    if (time >= lane5_m1 && lane5_m1 != 0){
        M1 = 0;
        lane5_m1 = 0;
        mcp_21.digitalWrite(L5_M1, M1);
        printLine("lane 5 M1 timeout - OFF");
    }
    if (time >= lane5_m2 && lane5_m2 != 0){
        M2 = 0;
        lane5_m2 = 0;
        mcp_21.digitalWrite(L5_M2, M2);
        printLine("lane 5 M2 timeout - OFF");
    }
    if (time >= lane6_m1 && lane6_m1 != 0){
        M1 = 0;
        lane6_m1 = 0;
        mcp_22.digitalWrite(L6_M1, M1);
        printLine("lane 6 M1 timeout - OFF");
    }
    if (time >= lane6_m2 && lane6_m2 != 0){
        M2 = 0;
        lane6_m2 = 0;
        mcp_22.digitalWrite(L6_M2, M2);
        printLine("lane 6 M2 timeout - OFF");
    }
    if (time >= lane7_m1 && lane7_m1 != 0){
        M1 = 0;
        lane7_m1 = 0;
        mcp_22.digitalWrite(L7_M1, M1);
        printLine("lane 7 M1 timeout - OFF");
    }
    if (time >= lane7_m2 && lane7_m2 != 0){
        M2 = 0;
        lane7_m2 = 0;
        mcp_22.digitalWrite(L7_M2, M2);
        printLine("lane 7 M2 timeout - OFF");
    }
}


void output_control()
{
  switch (lane) {
  case 1:
    mcp.digitalWrite(L1_PDLC1, P1);
    mcp.digitalWrite(L1_PDLC2, P2);
    mcp.digitalWrite(L1_PDLC3, P3);
    mcp.digitalWrite(L1_PDLC4, P4);
    mcp.digitalWrite(L1_M1, M1); 
    mcp.digitalWrite(L1_M2, M2);   

    //set timeout
    if (M1 == 1){
        lane1_m1 = millis() + TIMEOUT;
        printLine("lane 1 M1 ON ", lane1_m1);
    }
    if (M2 == 1){
        lane1_m2 = millis() + TIMEOUT;
        printLine("lane 1 M2 ON ", lane1_m2);
    }
    break;
  case 2:
    mcp.digitalWrite(L2_PDLC1, P1);
    mcp.digitalWrite(L2_PDLC2, P2);
    mcp.digitalWrite(L2_PDLC3, P3);
    mcp.digitalWrite(L2_PDLC4, P4);
    mcp.digitalWrite(L2_M1, M1);
    mcp.digitalWrite(L2_M2, M2);
    //set timeout
    if (M1 == 1){
        lane2_m1 = millis() + TIMEOUT;
        printLine("lane 2 M1 ON ", lane2_m1);
    }
    if (M2 == 1){
        lane2_m2 = millis() + TIMEOUT;
        printLine("lane 2 M2 ON ", lane2_m2);
    }
    break;
  case 3:
    mcp.digitalWrite(L3_PDLC1, P1);
    mcp.digitalWrite(L3_PDLC2, P2);
    mcp.digitalWrite(L3_PDLC3, P3);
    mcp.digitalWrite(L3_PDLC4, P4);
    mcp_21.digitalWrite(L3_M1, M1);
    mcp_21.digitalWrite(L3_M2, M2);
    //set timeout
    if (M1 == 1){
        lane3_m1 = millis() + TIMEOUT;
        printLine("lane 3 M1 ON ", lane3_m1);
    }
    if (M2 == 1){
        lane3_m2 = millis() + TIMEOUT;
        printLine("lane 3 M2 ON ", lane3_m2);
    }
    break;
  case 4:
    mcp_21.digitalWrite(L4_PDLC1, P1);
    mcp_21.digitalWrite(L4_PDLC2, P2);
    mcp_21.digitalWrite(L4_PDLC3, P3);
    mcp_21.digitalWrite(L4_PDLC4, P4);
    mcp_21.digitalWrite(L4_M1, M1);
    mcp_21.digitalWrite(L4_M2, M2);
    //set timeout
    if (M1 == 1){
        lane4_m1 = millis() + TIMEOUT;
        printLine("lane 4 M1 ON ", lane4_m1);
    }
    if (M2 == 1){
        lane4_m2 = millis() + TIMEOUT;
        printLine("lane 4 M2 ON ", lane4_m2);
    }
    break;
  case 5:
    mcp_21.digitalWrite(L5_PDLC1, P1);
    mcp_21.digitalWrite(L5_PDLC2, P2);
    mcp_21.digitalWrite(L5_PDLC3, P3);
    mcp_21.digitalWrite(L5_PDLC4, P4);
    mcp_21.digitalWrite(L5_M1, M1);
    mcp_21.digitalWrite(L5_M2, M2);
    //set timeout
    if (M1 == 1){
        lane5_m1 = millis() + TIMEOUT;
        printLine("lane 5 M1 ON ", lane5_m1);
    }
    if (M2 == 1){
        lane5_m2 = millis() + TIMEOUT;
        printLine("lane 5 M2 ON ", lane5_m2);
    }
    break;
  case 6:
    mcp_21.digitalWrite(L6_PDLC1, P1);
    mcp_21.digitalWrite(L6_PDLC2, P2);
    mcp_22.digitalWrite(L6_PDLC3, P3);
    mcp_22.digitalWrite(L6_PDLC4, P4);
    mcp_22.digitalWrite(L6_M1, M1);
    mcp_22.digitalWrite(L6_M2, M2);
    //set timeout
    if (M1 == 1){
        lane6_m1 = millis() + TIMEOUT;
        printLine("lane 6 M1 ON ", lane6_m1);
    }
    if (M2 == 1){
        lane6_m2 = millis() + TIMEOUT;
        printLine("lane 6 M2 ON ", lane6_m2);
    }
    break;
  case 7:
    mcp_22.digitalWrite(L7_PDLC1, P1);
    mcp_22.digitalWrite(L7_PDLC2, P2);
    mcp_22.digitalWrite(L7_PDLC3, P3);
    mcp_22.digitalWrite(L7_PDLC4, P4);
    mcp_22.digitalWrite(L7_M1, M1);
    mcp_22.digitalWrite(L7_M2, M2);
    //set timeout
    if (M1 == 1){
        lane7_m1 = millis() + TIMEOUT;
        printLine("lane 7 M1 ON ", lane7_m1);
    }
    if (M2 == 1){
        lane7_m2 = millis() + TIMEOUT;
        printLine("lane 7 M2 ON ", lane7_m2);
    }
    break;
  default:

    break;
}
}

void test_pattern_films()
{
  mcp.digitalWrite(L1_PDLC1, 0);
  mcp.digitalWrite(L1_PDLC2, 0);
  mcp.digitalWrite(L1_PDLC3, 0);
  mcp.digitalWrite(L1_PDLC4, 0);
  mcp.digitalWrite(L2_PDLC1, 0);
  mcp.digitalWrite(L2_PDLC2, 0);
  mcp.digitalWrite(L2_PDLC3, 0);
  mcp.digitalWrite(L2_PDLC4, 0);
  mcp.digitalWrite(L3_PDLC1, 0);
  mcp.digitalWrite(L3_PDLC2, 0);
  mcp.digitalWrite(L3_PDLC3, 0);
  mcp.digitalWrite(L3_PDLC4, 0);
  mcp_21.digitalWrite(L4_PDLC1, 0);
  mcp_21.digitalWrite(L4_PDLC2, 0);
  mcp_21.digitalWrite(L4_PDLC3, 0);
  mcp_21.digitalWrite(L4_PDLC4, 0);
  mcp_21.digitalWrite(L5_PDLC1, 0);
  mcp_21.digitalWrite(L5_PDLC2, 0);
  mcp_21.digitalWrite(L5_PDLC3, 0);
  mcp_21.digitalWrite(L5_PDLC4, 0);
  mcp_21.digitalWrite(L6_PDLC1, 0);
  mcp_21.digitalWrite(L6_PDLC2, 0);
  mcp_22.digitalWrite(L6_PDLC3, 0);
  mcp_22.digitalWrite(L6_PDLC4, 0);
  mcp_22.digitalWrite(L7_PDLC1, 0);
  mcp_22.digitalWrite(L7_PDLC2, 0);
  mcp_22.digitalWrite(L7_PDLC3, 0);
  mcp_22.digitalWrite(L7_PDLC4, 0);
  delay(200);
  mcp.digitalWrite(L1_PDLC1, 1);
  mcp.digitalWrite(L1_PDLC2, 1);
  mcp.digitalWrite(L1_PDLC3, 1);
  mcp.digitalWrite(L1_PDLC4, 1);
  mcp.digitalWrite(L2_PDLC1, 1);
  mcp.digitalWrite(L2_PDLC2, 1);
  mcp.digitalWrite(L2_PDLC3, 1);
  mcp.digitalWrite(L2_PDLC4, 1);
  mcp.digitalWrite(L3_PDLC1, 1);
  mcp.digitalWrite(L3_PDLC2, 1);
  mcp.digitalWrite(L3_PDLC3, 1);
  mcp.digitalWrite(L3_PDLC4, 1);
  mcp_21.digitalWrite(L4_PDLC1, 1);
  mcp_21.digitalWrite(L4_PDLC2, 1);
  mcp_21.digitalWrite(L4_PDLC3, 1);
  mcp_21.digitalWrite(L4_PDLC4, 1);
  mcp_21.digitalWrite(L5_PDLC1, 1);
  mcp_21.digitalWrite(L5_PDLC2, 1);
  mcp_21.digitalWrite(L5_PDLC3, 1);
  mcp_21.digitalWrite(L5_PDLC4, 1);
  mcp_21.digitalWrite(L6_PDLC1, 1);
  mcp_21.digitalWrite(L6_PDLC2, 1);
  mcp_22.digitalWrite(L6_PDLC3, 1);
  mcp_22.digitalWrite(L6_PDLC4, 1);
  mcp_22.digitalWrite(L7_PDLC1, 1);
  mcp_22.digitalWrite(L7_PDLC2, 1);
  mcp_22.digitalWrite(L7_PDLC3, 1);
  mcp_22.digitalWrite(L7_PDLC4, 1);
  delay(200);
}

void test_pattern_films_shocks()
{
  mcp.digitalWrite(L1_PDLC1, 0);
  mcp.digitalWrite(L1_PDLC2, 0);
  mcp.digitalWrite(L1_PDLC3, 0);
  mcp.digitalWrite(L1_PDLC4, 0);
  mcp.digitalWrite(L1_M1, 0);
  mcp.digitalWrite(L1_M2, 0);
  mcp.digitalWrite(L2_PDLC1, 0);
  mcp.digitalWrite(L2_PDLC2, 0);
  mcp.digitalWrite(L2_PDLC3, 0);
  mcp.digitalWrite(L2_PDLC4, 0);
  mcp.digitalWrite(L2_M1, 0);
  mcp.digitalWrite(L2_M2, 0);
  mcp.digitalWrite(L3_PDLC1, 0);
  mcp.digitalWrite(L3_PDLC2, 0);
  mcp.digitalWrite(L3_PDLC3, 0);
  mcp.digitalWrite(L3_PDLC4, 0);
  mcp_21.digitalWrite(L3_M1, 0);
  mcp_21.digitalWrite(L3_M2, 0);
  mcp_21.digitalWrite(L4_PDLC1, 0);
  mcp_21.digitalWrite(L4_PDLC2, 0);
  mcp_21.digitalWrite(L4_PDLC3, 0);
  mcp_21.digitalWrite(L4_PDLC4, 0);
  mcp_21.digitalWrite(L4_M1, 0);
  mcp_21.digitalWrite(L4_M2, 0);
  mcp_21.digitalWrite(L5_PDLC1, 0);
  mcp_21.digitalWrite(L5_PDLC2, 0);
  mcp_21.digitalWrite(L5_PDLC3, 0);
  mcp_21.digitalWrite(L5_PDLC4, 0);
  mcp_21.digitalWrite(L5_M1, 0);
  mcp_21.digitalWrite(L5_M2, 0);
  mcp_21.digitalWrite(L6_PDLC1, 0);
  mcp_21.digitalWrite(L6_PDLC2, 0);
  mcp_22.digitalWrite(L6_PDLC3, 0);
  mcp_22.digitalWrite(L6_PDLC4, 0);
  mcp_22.digitalWrite(L6_M1, 0);
  mcp_22.digitalWrite(L6_M2, 0);
  mcp_22.digitalWrite(L7_PDLC1, 0);
  mcp_22.digitalWrite(L7_PDLC2, 0);
  mcp_22.digitalWrite(L7_PDLC3, 0);
  mcp_22.digitalWrite(L7_PDLC4, 0);
  mcp_22.digitalWrite(L7_M1, 0);
  mcp_22.digitalWrite(L7_M2, 0);
  delay(200);
  mcp.digitalWrite(L1_PDLC1, 1);
  mcp.digitalWrite(L1_PDLC2, 1);
  mcp.digitalWrite(L1_PDLC3, 1);
  mcp.digitalWrite(L1_PDLC4, 1);
  mcp.digitalWrite(L1_M1, 1);
  mcp.digitalWrite(L1_M2, 1);
  mcp.digitalWrite(L2_PDLC1, 1);
  mcp.digitalWrite(L2_PDLC2, 1);
  mcp.digitalWrite(L2_PDLC3, 1);
  mcp.digitalWrite(L2_PDLC4, 1);
  mcp.digitalWrite(L2_M1, 1);
  mcp.digitalWrite(L2_M2, 1);
  mcp.digitalWrite(L3_PDLC1, 1);
  mcp.digitalWrite(L3_PDLC2, 1);
  mcp.digitalWrite(L3_PDLC3, 1);
  mcp.digitalWrite(L3_PDLC4, 1);
  mcp_21.digitalWrite(L3_M1, 1);
  mcp_21.digitalWrite(L3_M2, 1);
  mcp_21.digitalWrite(L4_PDLC1, 1);
  mcp_21.digitalWrite(L4_PDLC2, 1);
  mcp_21.digitalWrite(L4_PDLC3, 1);
  mcp_21.digitalWrite(L4_PDLC4, 1);
  mcp_21.digitalWrite(L4_M1, 1);
  mcp_21.digitalWrite(L4_M2, 1);
  mcp_21.digitalWrite(L5_PDLC1, 1);
  mcp_21.digitalWrite(L5_PDLC2, 1);
  mcp_21.digitalWrite(L5_PDLC3, 1);
  mcp_21.digitalWrite(L5_PDLC4, 1);
  mcp_21.digitalWrite(L5_M1, 1);
  mcp_21.digitalWrite(L5_M2, 1);
  mcp_21.digitalWrite(L6_PDLC1, 1);
  mcp_21.digitalWrite(L6_PDLC2, 1);
  mcp_22.digitalWrite(L6_PDLC3, 1);
  mcp_22.digitalWrite(L6_PDLC4, 1);
  mcp_22.digitalWrite(L6_M1, 1);
  mcp_22.digitalWrite(L6_M2, 1);
  mcp_22.digitalWrite(L7_PDLC1, 1);
  mcp_22.digitalWrite(L7_PDLC2, 1);
  mcp_22.digitalWrite(L7_PDLC3, 1);
  mcp_22.digitalWrite(L7_PDLC4, 1);
  mcp_22.digitalWrite(L7_M1, 1);
  mcp_22.digitalWrite(L7_M2, 1);
  delay(200);
}

void all_off()
{
  mcp.digitalWrite(L1_PDLC1, 0);
  mcp.digitalWrite(L1_PDLC2, 0);
  mcp.digitalWrite(L1_PDLC3, 0);
  mcp.digitalWrite(L1_PDLC4, 0);
  mcp.digitalWrite(L1_M1, 0);
  mcp.digitalWrite(L1_M2, 0);
  mcp.digitalWrite(L2_PDLC1, 0);
  mcp.digitalWrite(L2_PDLC2, 0);
  mcp.digitalWrite(L2_PDLC3, 0);
  mcp.digitalWrite(L2_PDLC4, 0);
  mcp.digitalWrite(L2_M1, 0);
  mcp.digitalWrite(L2_M2, 0);
  mcp.digitalWrite(L3_PDLC1, 0);
  mcp.digitalWrite(L3_PDLC2, 0);
  mcp.digitalWrite(L3_PDLC3, 0);
  mcp.digitalWrite(L3_PDLC4, 0);
  mcp_21.digitalWrite(L3_M1, 0);
  mcp_21.digitalWrite(L3_M2, 0);
  mcp_21.digitalWrite(L4_PDLC1, 0);
  mcp_21.digitalWrite(L4_PDLC2, 0);
  mcp_21.digitalWrite(L4_PDLC3, 0);
  mcp_21.digitalWrite(L4_PDLC4, 0);
  mcp_21.digitalWrite(L4_M1, 0);
  mcp_21.digitalWrite(L4_M2, 0);
  mcp_21.digitalWrite(L5_PDLC1, 0);
  mcp_21.digitalWrite(L5_PDLC2, 0);
  mcp_21.digitalWrite(L5_PDLC3, 0);
  mcp_21.digitalWrite(L5_PDLC4, 0);
  mcp_21.digitalWrite(L5_M1, 0);
  mcp_21.digitalWrite(L5_M2, 0);
  mcp_21.digitalWrite(L6_PDLC1, 0);
  mcp_21.digitalWrite(L6_PDLC2, 0);
  mcp_22.digitalWrite(L6_PDLC3, 0);
  mcp_22.digitalWrite(L6_PDLC4, 0);
  mcp_22.digitalWrite(L6_M1, 0);
  mcp_22.digitalWrite(L6_M2, 0);
  mcp_22.digitalWrite(L7_PDLC1, 0);
  mcp_22.digitalWrite(L7_PDLC2, 0);
  mcp_22.digitalWrite(L7_PDLC3, 0);
  mcp_22.digitalWrite(L7_PDLC4, 0);
  mcp_22.digitalWrite(L7_M1, 0);
  mcp_22.digitalWrite(L7_M2, 0);
}


//For Serial Function
/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
    // printLine("serialEvent");
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

//For printLine
void printLine() {
    Serial.println();
}

template <typename T, typename... Types>
void printLine(T first, Types... other) {
    // Serial.print(first);
    // printLine(other...) ;
}
