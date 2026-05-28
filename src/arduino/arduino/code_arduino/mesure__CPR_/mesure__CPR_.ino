// Mesure du CPR en faisant tourner le moteur lentement
// L'utilisateur observe la roue et envoie 's' (stop) quand un tour est fini

#define L298N_enA 10
#define L298N_in2 9
#define L298N_in1 8
#define ENC_A 3
#define ENC_B 5

volatile long pulseCount = 0;
bool motorRunning = false;

void setup() {
  pinMode(L298N_enA, OUTPUT);
  pinMode(L298N_in1, OUTPUT);
  pinMode(L298N_in2, OUTPUT);
  digitalWrite(L298N_in1, HIGH);
  digitalWrite(L298N_in2, LOW);
  
  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  
  Serial.begin(115200);
  Serial.println("Envoyez 'g' pour démarrer le moteur (faible vitesse).");
  Serial.println("Regardez la roue. Quand elle a fait EXACTEMENT 1 tour, envoyez 's'.");
  Serial.println("Le programme affichera le nombre d'impulsions comptées (CPR).");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'g') {
      // Démarrage moteur à faible vitesse (PWM 80)
      analogWrite(L298N_enA, 80);
      motorRunning = true;
      pulseCount = 0;
      attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);
      Serial.println("Moteur en marche. Comptage démarré. Attendez 1 tour puis envoyez 's'.");
    }
    else if (c == 's' && motorRunning) {
      detachInterrupt(digitalPinToInterrupt(ENC_A));
      analogWrite(L298N_enA, 0);
      motorRunning = false;
      Serial.print("Impulsions comptées pendant 1 tour : ");
      Serial.println(pulseCount);
      Serial.print("Votre CPR (Counts Per Revolution) = ");
      Serial.println(pulseCount);
      Serial.println("Utilisez cette valeur dans votre code principal (remplacez 385).");
    }
  }
}

void encoderISR() {
  pulseCount++;
}
