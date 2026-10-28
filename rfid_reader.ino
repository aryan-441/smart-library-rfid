#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10  // Slave Select pin
#define RST_PIN 9  // Reset pin

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(9600);  // Initialize serial communications
  SPI.begin();         // Init SPI bus
  rfid.PCD_Init();     // Init MFRC522
  Serial.println(" Starting");
}

void loop() {
  // Look for a new RFID card
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
    //Serial.print("No card");

  }

  // Select one of the cards
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Show UID on serial monitor
  //Serial.print("UID tag: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Halt PICC
  rfid.PICC_HaltA();
}
