# Smart Plant Monitoring & Remote Web Dashboard

This project implements a complete IoT‑based plant‑monitoring system using a Raspberry Pi, Sense HAT, Raspberry Pi Camera, MQTT messaging, a Flask web dashboard, and a Blynk mobile dashboard. The system collects real environmental data, publishes it to an MQTT broker, and displays it on a web interface.

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
- Optional SMS/email integration (In Progress)  
- LED control on the Sense HAT  

## Alert & Event Logic

### Temperature/Humidity Threshold Detection
The system continuously checks sensor values against predefined thresholds.

When a threshold is exceeded:

1. **An alert is sent**  
   - Blynk push notification  
   - Dashboard alert message  
   - Optional SMS/email (depending on configuration) (In Progress)

2. **A picture is taken**  
   - Saved as `data/latest.jpg`
   - Saved as a timestamped image in images folder  
   - latest.jpg is displayed on the dashboard  

3. **Sense HAT LEDs flash red**  
   - 3 seconds ON  
   - 3 seconds OFF  
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
- Libraries:  
  - `sense-hat`  
  - `picamera2`  
  - `paho-mqtt`  
  - `flask`  
  - `blynk-library`  
  - `opencv-python` (for motion detection)  

---

## Repository Structure
```text
IOT-Assignment/
|
|——— requirements.txt
|——— README.MD
|——— clear.sh
|
|——— sensor/
|    |——— sensor_reader.py
|    |——— camera_capture.py
|    |——— mqtt_publisher.py
|    |___ motion_detector.py
|
|——— dashboard/
|    |——— app.py
|    |——— static/
|    |    |——— css/
|    |    |    |___styles.css
|    |    |
|    |    |___ images/
|    |         |___ background.png
|    |
|    |___ templates/
|         |___ index.html
|___ data/
     |——— sensor_log.csv
     |——— latest.jpg
     |___ images/
```

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
These must be installed globally on your Raspberry Pi OS **before** setting up the virtual environment to ensure the physical hardware sensors and camera can be accessed.

```bash
sudo apt update
sudo apt install python3-opencv python3-picamera2 python3-rtimulib pkg-config
```

This installs:
- **python3-rtimulib**: Pre-compiled hardware drivers for the Sense Hat IMU chip (required for Python 3.13+).
- **python3-picamera2**: Official Raspberry Pi camera interaction framework.
- **python3-opencv**: ARM‑optimized computer vision modules for background motion detection processing.
- **pkg-config**: Package compilation tools required for modern Python wheels.

### 2. Create and activate a virtual environment
You **must** use the `--system-site-packages` flag when creating your virtual environment. This allows the isolated sandbox environment to link directly with the global hardware drivers (`Picamera2` and `RTIMU`) installed via `apt`:

```bash
# Create the environment with explicit hardware permissions
python3 -m venv --system-site-packages .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 3. Install Python dependencies inside the venv
With your virtual environment active, run the module installer tool:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuration Check
Before launching the services, open `sensor/sensor_reader.py` and ensure:
1. Your unique **Blynk Auth Token** is pasted into the `BLYNK_TOKEN` configuration field.
2. The Blynk instance is explicitly targeted to the modern cloud architecture: 
   `blynk = BlynkLib.Blynk(BLYNK_TOKEN, server="blynk.cloud", port=80)`

### 5. Start the Services

#### 5.1 Start the local MQTT broker
```bash
sudo systemctl start mosquitto
```
*(Only required if your system broker does not launch automatically on boot)*

#### 5.2 Run the sensor gateway pipeline
```bash
python3 sensor/sensor_reader.py
```

#### 5.3 Start the Flask web application
Open a **new terminal window or tab**, activate the virtual environment (`source .venv/bin/activate`), and run:
```bash
python3 dashboard/app.py
```

### 6. Access the System Dashboard
Open any web browser on your local network and visit:
`http://<YOUR_PI_IP_ADDRESS>:5000`

---

### Normal Operations After Setup
To boot up your environment on subsequent runs after completing the initial installations, execute your commands in this exact order:
1. **Activate Environment**: `source .venv/bin/activate`
2. **Start Gateway Pipeline**: `python3 sensor/sensor_reader.py`
3. **Start Web Interface** (In separate shell): `python3 dashboard/app.py`
4. **Clear images and cache** run  `./clear.sh` from the main project folder or the alias `clean`

---

## License & Usage

© [2026] [Kevlar501]. All rights reserved.

This repository is public for viewing and educational purposes only.  
You may not copy, distribute, modify, or use this code in any project  
(commercial or non-commercial) without explicit written permission  
from the author.

If you would like to request permission to use this code, please  
contact me at: [kcaseysawyer@yahoo.com].
