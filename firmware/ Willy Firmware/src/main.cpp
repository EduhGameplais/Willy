#include <WiFi.h>

const char* ssid = "hugo"; //TODO: Criar uma forma de alterar isso por exemplo via bluetooth
const char* password = "Hug0R3d35";

// Porta que o servidor vai escutar
const int serverPort = 5000;

WiFiServer server(serverPort);

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado!");
  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());

  // Inicia o servidor
  server.begin();
  Serial.println("Servidor iniciado.");
}

void loop() {
  WiFiClient client = server.available(); // Verifica se alguém conectou

  if (client) {
    Serial.println("Cliente conectado!");
    while (client.connected()) {
      if (client.available()) {
        String data = client.readStringUntil('\n');
        Serial.print("Recebido: ");
        Serial.println(data);

        // Resposta para o cliente
        client.println("Mensagem recebida: " + data);
      }
    }
    client.stop();
    Serial.println("Cliente desconectado.");
  }
}
