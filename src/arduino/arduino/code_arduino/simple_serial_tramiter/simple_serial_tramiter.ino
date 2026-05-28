// Code Arduino : envoie périodiquement des messages sur Serial
// Vitesse : 115200 bauds (à adapter si besoin)

unsigned long lastSend = 0;
const unsigned long interval = 1000; // envoi toutes les secondes
int counter = 0;

void setup() {
  Serial.begin(115200);
  // Optionnel : petite LED pour signaler le démarrage
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (millis() - lastSend >= interval) {
    lastSend = millis();
    
    // Construit un message avec un compteur
    Serial.print("Message depuis Arduino #");
    Serial.println(counter); // println ajoute un '\n' à la fin
    
    counter++;
    
    // Pour bien visualiser l'envoi (facultatif)
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
}
