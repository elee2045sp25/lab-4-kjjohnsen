from bleak import BleakClient, BleakScanner # get button state from the m5stickc
import threading
import asyncio
import struct

class M5StickGameController:
    def __init__(self, ble_name):
        self.ble_name = ble_name
        self.t = threading.Thread(target=self.__run_controller) 
        self.connected = False
        self.acc = (0,0,0)
        self.battery = 0
        self.t.start() 
        self.running = True

    def close(self):
        self.running = False
        self.t.join()

    def __run_controller(self):
        # attempt a connection to the bluetooth device
        def callback(sender,data:bytearray):
            res=struct.unpack("<fffh",data)
            self.acc = res[0:3]
            self.battery = res[3]

        async def run():
            while self.running: # we'll keep doing this until the program ends
                devices = await BleakScanner.discover(5) # short discovery time so it starts quickly
                print("Devices: ",devices)
                try:
                    for d in devices:
                        if d.name == self.ble_name: # this approach should work on windows or mac
                            async with BleakClient(d, timeout=10) as client:
                                print("connected")
                                self.connected = True
                                await client.start_notify("82a7e967-7504-4f75-a68e-57c2803d8f41",callback)
                                while self.running:
                                    if not client.is_connected: break
                                    await asyncio.sleep(.01)
                except Exception as e:
                    self.connected = False
                    print(e)
                    pass
        asyncio.run(run())