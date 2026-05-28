# Smart Plant Monitoring & Remote Web Dashboard

This project implements a complete IoT‑based plant‑monitoring system using a Raspberry Pi, Sense HAT, Raspberry Pi Camera, MQTT messaging, a Flask web dashboard, and a Blynk mobile dashboard. The system collects real environmental data, publishes it to an MQTT broker, displays it on a web interface, and supports simulated sensor data using Cisco Packet Tracer.

In addition to basic monitoring, the system includes **threshold‑based alerts**, **automatic image capture**, **Sense HAT LED warnings**, **event acknowledgement logic**, and **motion detection** to identify potential pests.

---

## Project Overview

The goal of this project is to build a real IoT system capable of monitoring plant health through:

- Environmental sensing (temperature, humidity, pressure)
- Threshold detection for abnormal conditions
- Automatic image capture during alert events
- Real‑time data transmission via MQTT
- Mobile monitoring through Blynk (including notifications)
- Web‑based monitoring through a Flask dashboard
- Motion detection to identify possible pests
- Simulated IoT data using Packet Tracer for testing and validation

The system supports both real hardware inputs and simulated sensor values, allowing full testing even when hardware is unavailable.

---

## System Architecture

### 1. Raspberry Pi (Real IoT Device)
- Reads Sense HAT sensor values  
- Detects temperature/humidity threshold violations  
- Captures plant images  
- Publishes data to MQTT topics  
- Sends live values and alerts to Blynk  
- Logs data locally  
- Detects motion using the Pi Camera  
- Controls Sense HAT LED alerts  
- Supports event acknowledgement via joystick button  

### 2. MQTT Broker
Handles lightweight publish/subscribe messaging for:

- Real sensor data  
- Simulated Packet Tracer data  
- Dashboard updates  
- Alert events  

### 3. Flask Web Dashboard
Displays:

- Live sensor readings  
- Latest plant image  
- Historical logs  
- Auto‑refreshing UI  
- Alert notifications (threshold events, motion detection)  

### 4. Blynk Mobile Dashboard
Provides:

- Live temperature, humidity, pressure  
- Push notifications for alerts  
- Optional SMS/email integration  
- LED control on the Sense HAT  

### 5. Packet Tracer Simulation
Used to:

- Generate fake sensor data  
- Test MQTT communication  
- Validate dashboard behaviour under extreme or offline conditions  

This ensures the system can be tested even when hardware is unavailable.

---

## Alert & Event Logic

### Temperature/Humidity Threshold Detection
The system continuously checks sensor values against predefined thresholds.

When a threshold is exceeded:

1. **An alert is sent**  
   - Blynk push notification  
   - Dashboard alert message  
   - Optional SMS/email (depending on configuration)

2. **A picture is taken**  
   - Saved as `data/latest.jpg`  
   - Displayed on the dashboard  

3. **Sense HAT LEDs flash red**  
   - 3 seconds ON  
   - 12 seconds OFF  
   - Repeats until condition resolves or event is acknowledged  

### Event Acknowledgement (Sense HAT Joystick)
Pressing the joystick button:

- Acknowledges the alert  
- Stops LED flashing  
- Suppresses all further threshold warnings for **3 hours**  
- Indicates that someone has physically checked the plant  

### Motion Detection (Pest Alerting)
The Pi Camera monitors for movement around the plant.

If motion is detected:

- An alert is sent to the dashboard
- A picture is captured  
- The event is logged  
- Optional LED indication can be enabled  

---

## Tools, Technologies & Equipment

### Hardware
- Raspberry Pi 5  
- Sense HAT  
- Raspberry Pi Camera Module  

### Software & Protocols
- Python 3  
- Flask  
- MQTT (Mosquitto)  
- Blynk  
- SSH  
- Cisco Packet Tracer  
- Libraries:  
  - `sense-hat`  
  - `picamera2`  
  - `paho-mqtt`  
  - `flask`  
  - `blynk-library`  
  - `opencv-python` (for motion detection)  

---

## Repository Structure
IOT-Assignment/
|
├── requirements.txt
│
├── sensor/
│   ├── sensor_reader.py
│   ├── camera_capture.py
│   ├── mqtt_publisher.py
│   └── motion_detector.py
│
├── dashboard/
│   ├── app.py
│   ├── static/
│   └── templates/
│       └── index.html
│
├── data/
│   ├── sensor_log.csv
│   └── latest.jpg
│
└── README.md

---

## Features

- Real‑time environmental monitoring  
- Threshold‑based alerts  
- Automatic image capture during alert events  
- Motion detection for pest identification  
- MQTT‑based data transport  
- Flask web dashboard  
- Blynk mobile dashboard with notifications  
- Packet Tracer simulation support  
- Local CSV logging  
- Event acknowledgement with 3‑hour suppression  
- Modular, extensible architecture  

---

## MQTT Topics

| Topic | Description |
|-------|-------------|
| `plant/temperature` | Temperature in °C |
| `plant/humidity` | Humidity in % |
| `plant/pressure` | Pressure in hPa |
| `plant/alert` | Threshold or motion alerts |
| `plant/image` | Image event notifications |

---

## Blynk Virtual Pins

| Virtual Pin | Data |
|-------------|------|
| V0 | Temperature |
| V1 | Humidity |
| V2 | Pressure |
| V3 | Alert status |
| V4 | Motion detection status |

---

## Packet Tracer Simulation

Packet Tracer is used to:

- Simulate IoT sensor nodes  
- Publish fake MQTT data  
- Test dashboard behaviour under controlled conditions  
- Validate system reliability  

This ensures the system can be tested even when hardware is unavailable.

---

## Image Capture

The Raspberry Pi Camera captures:

- A new image every X minutes  
- Additional images during alert events  
- Motion‑triggered images  

Saved to:

data/latest.jpg

The Flask dashboard displays the most recent image automatically.

---

## How to Run the System

### 1. Install system‑level dependencies (REQUIRED on Raspberry Pi)
These must be installed **before** creating or activating a virtual environment.

sudo apt update
sudo apt install python3-opencv python3-picamera2 libatlas-base-dev pkg-config

This installs:

- OpenCV (ARM‑optimized, no FFmpeg build required)
- PiCamera2 (official Raspberry Pi camera library)
- Linear algebra libraries required by OpenCV
- pkg-config (needed for various Python wheels)

### 2. Create and activate a virtual environment
#### It is recommended to run the project inside a Python virtual environment:
python3 -m venv .venv
source .venv/bin/activate

### 3. Install Python dependencies inside the venv
pip install -r requirements.txt

### 3. Start the MQTT broker
sudo systemctl start mosquitto

### 4. Run the sensor reader
python3 sensor/sensor_reader.py

### 5. Start the Flask dashboard
python3 dashboard/app.py

### 6. Open the dashboard
Visit: http://YOUR_PI_IP_HERE:5000


---

## License & Usage

© [2026] [Kevlar501]. All rights reserved.

This repository is public for viewing and educational purposes only.  
You may not copy, distribute, modify, or use this code in any project  
(commercial or non-commercial) without explicit written permission  
from the author.

If you would like to request permission to use this code, please  
contact me at: [Your Contact Email/Method].
