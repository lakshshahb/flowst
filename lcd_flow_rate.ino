#include <LiquidCrystal.h>

const int Output_Pin = 2;  // Pin connected to the flow sensor
volatile int Pulse_Count = 0;
unsigned long Current_Time = 0;
unsigned long Loop_Time = 0;
float Liter_per_hour = 0;

// Initialize the LCD with RS, EN, D4, D5, D6, D7 pin connections
LiquidCrystal lcd(12,11,6,5,4,3);

void setup() {
  pinMode(Output_Pin, INPUT);
  Serial.begin(9600); // Start serial communication at 9600 bps
  lcd.begin(16, 2); // Initialize the 16x2 LCD
  attachInterrupt(digitalPinToInterrupt(Output_Pin), Detect_Rising_Edge, RISING);

  Current_Time = millis();
  Loop_Time = Current_Time;

  // Welcome message
  lcd.setCursor(0, 0);
  lcd.print("Flow Sensor Init");
  delay(2000);
  lcd.clear();
}

void loop() {
  Current_Time = millis();

  if (Current_Time >= (Loop_Time + 1000)) { // Every 1 second
    Loop_Time = Current_Time;

    // Calculate flow rate in liters per hour
    Liter_per_hour = (Pulse_Count * 60.0) / 7.5;
    Pulse_Count = 0; // Reset pulse count

    // Display the flow rate on the LCD
    lcd.setCursor(0, 0);
    lcd.print("Flow: ");
    lcd.print(Liter_per_hour);
    lcd.print(" L/h");

    // Send flow rate to the serial monitor (to be read by Python)
    Serial.print("Flow rate: ");
    Serial.print(Liter_per_hour);
    Serial.println(" L/h");

    // Display additional calculation (e.g., rotations per second on the second line)
    float RPS = Liter_per_hour / 60.0; // Example calculation, adjust as needed
    lcd.setCursor(0, 1);
    lcd.print("Rotations: ");
    lcd.print(RPS, 2);
    lcd.print(" RPS");
  }
}

void Detect_Rising_Edge() {
  Pulse_Count++;
}
