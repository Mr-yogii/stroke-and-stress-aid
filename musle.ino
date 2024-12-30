#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi credentials
const char* ssid = "yogii";          // Wi-Fi credentials
const char* password = "yogesh1528";  // Wi-Fi credentials

// Raspberry Pi server URL
const String serverUrl = "http://192.168.137.130:5000/upload_data";

// Muscle signal and other variables
#define SAMPLE_RATE 500  // Increase sample rate to 1000 Hz for faster data
#define INPUT_PIN 34      // Change this to the correct pin for BioAmp EXG Pill
#define BUFFER_SIZE 128
int circular_buffer[BUFFER_SIZE];
int data_index = 0, sum = 0;

int muscleSignal = 0;

void setup() {
  Serial.begin(115200);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Read muscle signal (BioAmp EXG Pill)
  muscleSignal = analogRead(INPUT_PIN);  // Assuming you're reading the signal from the correct analog pin
  int emgSignal = EMGFilter(muscleSignal);
  int envelop = getEnvelop(abs(emgSignal));

  // Prepare JSON payload with muscle signal data
  String payload = "{\"muscleSignal\": " + String(envelop) + "}";

  // Send data to the Raspberry Pi server using HTTP POST
  HTTPClient http;
  http.begin(serverUrl);            // Raspberry Pi server endpoint
  http.addHeader("Content-Type", "application/json");  // Specify content type

  int httpResponseCode = http.POST(payload);  // Send POST request

  // Log the result of the HTTP request
  if (httpResponseCode > 0) {
    Serial.println("Data sent successfully");
    Serial.println(httpResponseCode); // Print response code
  } else {
    Serial.println("Error sending data");
    Serial.println(httpResponseCode); // Print error code
  }

  http.end();  // Close the HTTP connection

  // Reduce the delay between requests to speed up data sharing
  delay(100);  // Send data every 100ms (adjust this if needed)
}

// Envelop detection algorithm for EMG signal
int getEnvelop(int abs_emg) {
  sum -= circular_buffer[data_index];
  sum += abs_emg;
  circular_buffer[data_index] = abs_emg;
  data_index = (data_index + 1) % BUFFER_SIZE;
  return (sum / BUFFER_SIZE) * 2;
}

// EMG Filter to process the signal
float EMGFilter(float input) {
  float output = input;
  {
    static float z1, z2;  // filter section state
    float x = output - 0.05159732 * z1 - 0.36347401 * z2;
    output = 0.01856301 * x + 0.03712602 * z1 + 0.01856301 * z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2;  // filter section state
    float x = output - -0.53945795 * z1 - 0.39764934 * z2;
    output = 1.00000000 * x + -2.00000000 * z1 + 1.00000000 * z2;
    z2 = z1;
    z1 = x;
  }
  {   
    static float z1, z2;  // filter section state
    float x = output - 0.47319594 * z1 - 0.70744137 * z2;
    output = 1.00000000 * x + 2.00000000 * z1 + 1.00000000 * z2;
    z2 = z1;
    z1 = x;

  }
  {
    static float z1, z2;  // filter section state
    float x = output - -1.00211112 * z1 - 0.74520226 * z2;
    output = 1.00000000 * x + -2.00000000 * z1 + 1.00000000 * z2;
    z2 = z1;
    z1 = x;
  }
  return output;
} 
