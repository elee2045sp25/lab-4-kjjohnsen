#include <M5Unified.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include "esp_gap_ble_api.h"
#define SERVICE_UUID        "82a7e967-7504-4f75-a68e-57c2803d8f40"
#define CHARACTERISTIC_UUID "82a7e967-7504-4f75-a68e-57c2803d8f41"

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool advertising = false;

#pragma pack(1)
typedef struct {
  float accx,accy,accz;
  uint16_t batt;
} Packet;

Packet p;
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) {
    Serial.println("Device connected");

    // --- Request Connection Parameter Update ---
    esp_ble_conn_update_params_t conn_params;
    conn_params.min_int = 6;
    conn_params.max_int = 12;
    conn_params.latency = 0;
    conn_params.timeout = 400;

    esp_err_t err = esp_ble_gap_update_conn_params(&conn_params);

    deviceConnected = true;
    advertising = false;
  }
  void onDisconnect(BLEServer* pServer) {
    Serial.println("Device disconnected");
    deviceConnected = false;
  }
};


void setup() {
  M5.begin();
  BLEDevice::init("M5StickCPlus-Kyle");
  
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  pCharacteristic->addDescriptor(new BLE2902());
  pService->start();
  BLEDevice::startAdvertising();
}


void loop() {
  M5.update();
  M5.Imu.update();
  M5.Imu.getAccelData(&p.accx, &p.accy, &p.accz);
  p.batt = M5.Power.getBatteryVoltage();
  if (deviceConnected) {
    pCharacteristic->setValue((uint8_t*)(&p), sizeof(Packet));
    pCharacteristic->notify();
    delay(10);
  }
  if (!deviceConnected && !advertising) {
    BLEDevice::startAdvertising();
    Serial.println("start advertising");
    advertising = true;
  }
}
