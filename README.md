# Automated Level-Controlled Fluid Bath

This repository contains the MicroPython control logic for a fully automated fluid level control system. The project was built to apply skills learnt at university to a tangible, physical hardware system. 

The system continuously reads fluid levels via a capacitive sensor, processes the data through a custom PID loop on a Raspberry Pi Pico H, and drives a reversible peristaltic pump to maintain a precise, stable fluid level inside a custom-designed, watertight 3D-printed enclosure.

## 🛠️ Hardware & Components

* **Microcontroller:** Raspberry Pi Pico H
* **Sensor:** Seeed Studio Grove 10cm Capacitive Water Level Sensor
* **Actuator:** 12V DC Reversible Peristaltic Pump
* **Motor Control:** 13A 6V-30V DC Motor Driver
* **Interface:** Fermion: Monochrome 0.96" 128x64 I2C/SPI OLED Display and tactile switches for manual input
* **Power Supply:** 12V 2A Power Supply with 2.1mm Barrel Jack
* **Power Regulation:** 20W Adjustable DC-DC Buck Converter with Digital Display

## 💻 Software & Logic

* **Language:** MicroPython (developed in Thonny IDE)s.
* **Data Output:** Real-time system diagnostics and fluid levels are outputted to the OLED screen via I2C communication.

## ⚙️ Mechanical Design & Manufacturing

* **CAD Software:** SolidWorks 
* **Design Features:** Engineered with precise sliding tolerance gaps and custom compartments to house the fluid and electronics securely.
* **Manufacturing:** Sliced in Bambu Studio and printed on a Bambu Lab FDM 3D printer.
* **Materials & Post-Processing:** Printed using PLA and PETG filament for its watertight properties, followed by surface finishing using 400-grit silicon carbide wet/dry sandpaper to ensure optimal seal and aesthetics.

## 📂 Repository Contents

* `main.py`: The core MicroPython script containing the PID logic and hardware initialization.
* `lib/`: Required libraries for the SSD1306 OLED and capacitive sensor.
