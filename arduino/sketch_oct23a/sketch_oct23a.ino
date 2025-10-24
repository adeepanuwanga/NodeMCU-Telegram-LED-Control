#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// WiFi credentials - UPDATE THESE!
const char* ssid = "YourWiFiSSID";        // Your iPhone hotspot name
const char* password = "YourWiFiPassword";      // Your iPhone hotspot password

// LED pin - Built-in LED has INVERSE logic!
const int LED_PIN = D4;  // GPIO2 (built-in LED)
bool ledState = false;

ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // Start with LED OFF (HIGH = OFF for built-in LED)
  
  Serial.println();
  Serial.println("🚀 Starting NodeMCU...");
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("📡 Connecting to ");
  Serial.print(ssid);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("📱 IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📶 Signal Strength: ");
    Serial.println(WiFi.RSSI());
  } else {
    Serial.println("\n❌ WiFi Connection Failed!");
    return;
  }
  
  // Setup server routes
  server.on("/", handleRoot);
  server.on("/led/on", handleLedOn);
  server.on("/led/off", handleLedOff);
  server.on("/led/toggle", handleLedToggle);
  server.on("/led/status", handleLedStatus);
  
  server.begin();
  Serial.println("🌐 HTTP Server Started!");
  Serial.println("📍 Use this IP in your Python code: " + WiFi.localIP().toString());
}

void loop() {
  server.handleClient();
  delay(10);
}

void handleRoot() {
  String html = "<html><head><title>NodeMCU LED Control</title></head>";
  html += "<body style='font-family: Arial; text-align: center;'>";
  html += "<h1>NodeMCU LED Control</h1>";
  html += "<p>LED is currently: <strong>" + String(ledState ? "ON" : "OFF") + "</strong></p>";
  html += "<button onclick=\"location.href='/led/on'\">Turn ON</button>";
  html += " <button onclick=\"location.href='/led/off'\">Turn OFF</button>";
  html += " <button onclick=\"location.href='/led/toggle'\">Toggle</button>";
  html += "<br><br><p>Also controllable via Telegram bot!</p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleLedOn() {
  digitalWrite(LED_PIN, LOW);   // LOW turns ON the built-in LED
  ledState = true;
  Serial.println("💡 LED turned ON via web request");
  server.send(200, "application/json", "{\"status\":\"LED ON\", \"ip\":\"" + WiFi.localIP().toString() + "\"}");
}

void handleLedOff() {
  digitalWrite(LED_PIN, HIGH);  // HIGH turns OFF the built-in LED
  ledState = false;
  Serial.println("🔌 LED turned OFF via web request");
  server.send(200, "application/json", "{\"status\":\"LED OFF\", \"ip\":\"" + WiFi.localIP().toString() + "\"}");
}

void handleLedToggle() {
  ledState = !ledState;
  digitalWrite(LED_PIN, ledState ? LOW : HIGH);  // Inverse logic for toggle
  Serial.println("🔄 LED toggled via web request");
  server.send(200, "application/json", "{\"status\":\"LED TOGGLED\", \"new_state\":\"" + String(ledState ? "ON" : "OFF") + "\"}");
}

void handleLedStatus() {
  String json = "{\"led_state\":\"" + String(ledState ? "on" : "off") + "\", \"ip\":\"" + WiFi.localIP().toString() + "\"}";
  server.send(200, "application/json", json);
}
