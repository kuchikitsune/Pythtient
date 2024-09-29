import os
import asyncio
import configparser
import sys
import json
import random

from random import randint

from iotc.models import Property, Command

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "samples.ini"))

if config["DEFAULT"].getboolean("Local"):
    sys.path.insert(0, "src")

from iotc import (
    IOTCConnectType,
    IOTCLogLevel,
    IOTCEvents,
    Command,
    CredentialsCache,
    Storage,
)
from iotc.aio import IoTCClient

# Update the following details with your Azure IoT Central credentials
device_id = ""
scope_id = ""
key = ""

class MemStorage(Storage):
    def retrieve(self):
        return None

    def persist(self, credentials):
        # a further option would be updating config file with latest hub name
        return None

# optional model Id for auto-provisioning
model_id = None

async def on_props(prop: Property):
    print(f"Received {prop.name}:{prop.value}")
    return True

async def on_commands(command: Command):
    print("Received command {} with value {}".format(command.name, command.value))
    await command.reply()

async def on_enqueued_commands(command: Command):
    print("Received offline command {} with value {}".format(command.name, command.value))

client = IoTCClient(
    device_id,
    scope_id,
    IOTCConnectType.IOTC_CONNECT_DEVICE_KEY,
    key,
    storage=MemStorage(),
)
if model_id != None:
    client.set_model_id(model_id)

client.set_log_level(IOTCLogLevel.IOTC_LOGGING_ALL)
client.on(IOTCEvents.IOTC_PROPERTIES, on_props)
client.on(IOTCEvents.IOTC_COMMAND, on_commands)
client.on(IOTCEvents.IOTC_ENQUEUED_COMMAND, on_enqueued_commands)

async def main():
    await client.connect()
    await client.send_property({"writeableProp": 50})

    while not client.terminated():
        if client.is_connected():
            await client.send_telemetry(
                {
                    "HeartRate": random.randint(60, 160),
                    "Temperature": random.randint(34, 39),
                    "SPO2": random.randint(89, 99),
                    "BreathRate": random.randint(14, 24),
                    "Glucose": random.randint(80, 140)
                },
                
            )
        await asyncio.sleep(25)

    await client.disconnect()  # Disconnect upon termination


if __name__ == "__main__":
    asyncio.run(main())
