#!/usr/bin/env python3

import asyncio
import numpy as np
import os
import time

import pymodbus.client as ModbusClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)

async def holding(comm, host, port, mbus):
    """Run async client."""
    # activate debugging
    # pymodbus_apply_logging_config("DEBUG")

    framer=Framer.SOCKET

    # print("get client")
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host,
            port=port,
            framer=framer,
            timeout=10,
            retries=3,
            # retry_on_empty=False,
            # source_address=("localhost", 502),
        )
    else:
        print(f"Unknown client {comm} selected")
        return

    # print("connect to server")
    await client.connect()
    # test client is connected
    assert client.connected

    #print("get and verify data")

    try:
        rr = await client.read_holding_registers(mbus, 2, slave=1)
    except ModbusException as exc:
        print(f"Received ModbusException({exc}) from library")
        client.close()
    if rr.isError():
        print(f"Received Modbus library error({rr})")
        # client.close()
    elif isinstance(rr, ExceptionResponse):
        print(f"Received Modbus library exception ({rr})")
        # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        # client.close()
    else:
        read1 = rr.registers[0]
        read2 = rr.registers[1]
        hex_read1 = format(read1, '04x')
        hex_read2 = format(read2, '04x')
        concatenated_hex = str(hex_read1) + str(hex_read2)

        concatenated = int(concatenated_hex, 16)
        float_value = np.frombuffer(np.uint32(concatenated).tobytes(), dtype=np.float32)[0]
        # print(f"Current value of register: {float_value}")
        client.close()
        return float_value
        
    print("close connection")
    client.close()

if __name__ == "__main__":

    powys = [{'name': 'Gerilim', 'num': 0},
             {'name': 'Akim', 'num': 2},
             {'name': 'Frekans', 'num': 4},
             {'name': 'Cos_fi', 'num': 6},
             {'name': 'Guc_Faktoru', 'num': 8},
             {'name': 'Aktif_Guc', 'num': 10},
             {'name': 'Reaktif_Guc', 'num': 12},
             {'name': 'Gorunur_Guc', 'num': 14},
             {'name': 'THDV', 'num': 16},
             {'name': 'THDI', 'num': 18}
             ]

    ipaddr = input("Enter an IP address (xx.xx.xx.xx): ")

    parts = ipaddr.split(".")

    if len(parts) == 4:
        valid = True
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                valid = False
                break

        if valid:
            print("Valid IP address")
        else:
            print("Invalid IP address")
    else:
        print("Invalid IP address")

    # register number , not port
    mbus = 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear command prompt
        for item in powys:
            mbus = item['num']
            cur_value = asyncio.run(
                holding("tcp", ipaddr, 502, mbus), debug=True
            )
            print(f"{item['name']} : {cur_value}")
        time.sleep(1)