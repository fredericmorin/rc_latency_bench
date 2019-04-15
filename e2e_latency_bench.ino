void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(10, LOW);
  pinMode(10, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  pinMode(10, OUTPUT);  // pull-down
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  pinMode(10, INPUT);  // floating
  delay(500);
}
