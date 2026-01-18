# POWYS 1120 Reader

## Overview

This Python script reads electrical measurement values from a **POWYS 1120 power quality analyzer device** and displays them in the console every second. The script communicates with the device via **Modbus TCP protocol** through a **serial-to-Modbus TCP gateway**. POWYS 1120 power quality analyzer device manual can be reached from [here](https://web.archive.org/web/20250801000000*/https://res.poltechnik.pl/powys_1120.pdf), archived from [this source](https://res.poltechnik.pl/powys_1120.pdf).

## System Architecture

```
┌──────────────────────┐
│  POWYS 1120 Device   │  (Outputs via serial port)
│  (Power Analyzer)    │
└──────────┬───────────┘
           │ Serial Port
           │
┌──────────▼───────────────────────┐
│ Serial-to-Modbus TCP Gateway      │  (Converts serial to TCP)
│ (Modbus TCP Server)               │  Listens on port 502
└──────────┬───────────────────────┘
           │ Modbus TCP
           │
┌──────────▼──────────────────────────────────────┐
│  This Python Script                              │
│  (Modbus TCP Client)                             │
│  Reads holding registers every second            │
└────────────────────────────────────────────────┘
```

## How It Works

### 1. **Connection Setup**
   - The script prompts you to enter the IP address of the serial-to-Modbus TCP gateway
   - Validates the IP address format (xx.xx.xx.xx)
   - Connects to the gateway via Modbus TCP on port 502

### 2. **Register Reading**
   - The POWYS 1120 device exposes its measurements as **holding registers** in the Modbus protocol
   - Each measurement (voltage, current, frequency, etc.) occupies 2 consecutive registers
   - Each register is 16-bit, so 2 registers = 32-bit float value

### 3. **Data Conversion**
   - Reads 2 consecutive 16-bit registers for each value
   - Combines them into a single 32-bit hexadecimal string
   - Converts the combined 32-bit value to a floating-point number (IEEE 754 format)

### 4. **Continuous Monitoring**
   - Loops through all 10 measurement types
   - Reads values from the device
   - Displays results in the console
   - Clears the screen and repeats every 1 second

## Measured Parameters

The script reads the following 10 electrical parameters from the POWYS 1120:

| Parameter | Turkish Name | Register | Unit |
|-----------|--------------|----------|------|
| Voltage | Gerilim | 0 | V |
| Current | Akim | 2 | A |
| Frequency | Frekans | 4 | Hz |
| Power Factor | Cos_fi / Guc_Faktoru | 6 / 8 | - |
| Active Power | Aktif_Guc | 10 | W |
| Reactive Power | Reaktif_Guc | 12 | VAR |
| Apparent Power | Gorunur_Guc | 14 | VA |
| Voltage THD | THDV | 16 | % |
| Current THD | THDI | 18 | % |

Those values can be reached from 35th page of the specified pdf file.

## Requirements

### Python Packages
```bash
pip install pymodbus numpy
```

- **pymodbus**: Modbus TCP client library for async communication
- **numpy**: For IEEE 754 float conversion

### Hardware
- POWYS 1120 power quality analyzer device
- Serial-to-Modbus TCP gateway (configured to listen on port 502)
- Network connection between your PC and the gateway

## Usage

Run the script:
```bash
python powys_1120_reader.py
```

When prompted:
```
Enter an IP address (xx.xx.xx.xx): 192.168.1.100
```

The script will then display:
```
Gerilim : 230.5
Akim : 15.2
Frekans : 50.0
...
```

The values will refresh every second.

## Code Explanation

### `holding()` Function
- **Async function** that establishes a Modbus TCP connection
- Parameters:
  - `comm`: Communication protocol (currently only "tcp" is supported)
  - `host`: IP address of the Modbus TCP gateway
  - `port`: Port number (502 for Modbus TCP)
  - `mbus`: Register address to read (starting address)
- Reads 2 holding registers starting from the specified address
- Converts the raw register data to a 32-bit float value
- Returns the calculated float value

### Main Loop
- Validates the entered IP address
- Continuously loops through all 10 measurement parameters
- For each parameter, calls the `holding()` function asynchronously
- Displays the retrieved value with its name
- Clears the screen and repeats every second

## Modbus Protocol Details

- **Protocol**: Modbus TCP (TCP/IP)
- **Port**: 502 (standard Modbus port)
- **Slave ID**: 1 (default device address)
- **Function**: Read Holding Registers (function code 03)
- **Data Format**: IEEE 754 32-bit floating-point (2 registers per value)

## Notes

- The timeout is set to 10 seconds for each connection
- Up to 3 retries are attempted if a request fails
- The gateway must be running and reachable at the specified IP address
- The script uses async I/O for non-blocking operations
- Press `Ctrl+C` to stop the script

## Troubleshooting

- **"Unknown client selected"**: Make sure to use "tcp" protocol (only option supported)
- **Connection timeout**: Verify the gateway IP address and that it's reachable
- **Modbus exception**: Check that the device is powered on and the gateway is properly configured
- **Invalid IP address**: Enter a valid IP in the format x.x.x.x
