import machine      # Access to the Pico's hardware: pins, I2C, PWM
import ssd1306      # OLED display driver (ssd1306.py must already be saved on the Pico)
import time         # For delays and sleeping between loops

# --- Hardware Initialization ---

# 1. Initialize the shared I2C bus for the OLED and Sensor
i2c_bus = machine.I2C(0, sda=machine.Pin(12), scl=machine.Pin(13), freq=400000)  # I2C0 on GP0 (SDA) / GP1 (SCL), 400kHz

# 2. Initialize the OLED display (Address 0x3c)
oled = ssd1306.SSD1306_I2C(128, 64, i2c_bus, addr=0x3c)  # 128x64 pixel OLED, using the I2C bus above

# 3. Initialize the MD13S Motor Driver logic pins
dir_pin = machine.Pin(7, machine.Pin.OUT)    # GP7 controls pump direction (HIGH = forward, LOW = reverse)
pwm_pin = machine.PWM(machine.Pin(8))        # GP8 controls pump speed via PWM
pwm_pin.freq(1000)                            # Set the PWM switching frequency to 1kHz

# 4. Initialize the two control buttons
btn_setpoint = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)  # GP5: press to increase setpoint by 10%
btn_pump = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)      # GP4: press to start/stop the pump
btn_speed = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)     # GP3: press to increase pump speed by 10%

# PULL_UP means each pin reads 1 (HIGH) normally, and drops to 0 (LOW) the instant the button is pressed to GND

# --- Sensor Settings ---
ADDR_LOW = 0x77       # I2C address for the lower half of the level sensor
ADDR_HIGH = 0x78      # I2C address for the upper half of the level sensor
THRESHOLD = 100       # A raw reading above this counts as "wet" for that section

# Level Sensor Syntax (AI)

def read_water_level(i2c_bus):
    touch_val = 0
    trig_section = 0
    try:
        low_data = i2c_bus.readfrom(0x77, 8)
        for i in range(8):
            if low_data[i] > 100:
                touch_val |= (1 << i)
    except OSError:
        pass

    try:
        high_data = i2c_bus.readfrom(0x78, 12)
        for i in range(12):
            if high_data[i] > 100:
                touch_val |= (1 << (8 + i))
    except OSError:
        pass

    while touch_val & 0x01:
        trig_section += 1
        touch_val >>= 1

    level_percent = trig_section * 5
    level_mm = trig_section * 5
    return level_percent, level_mm

# Pump Syntax

def pump_parameters(speed_percent, forward=True):
    # Pump Direction
    if forward == True:
        dir_pin.value(1)
    else:
        dir_pin.value(0)
    
    # Convert Percentage into 16-bit Number
    duty = int((speed_percent / 100) * 65535)
    
    #Sending 16-Bit Number to PWM Pin
    pwm_pin.duty_u16(duty)
    
# --- Setup Variables ---
pump_running = False
btn_pump_prev = 1

# Set Point button
setpoint = 50
btn_setpoint_prev = 1

# Pump Speed
speed_percent = 50
btn_speed_prev = 1

# --- Control Loop ---
while True:
    # 1. Read Hardwarer
    btn_pump_now = btn_pump.value()
    percent, mm = read_water_level(i2c_bus)
    btn_setpoint_now = btn_setpoint.value()
    btn_speed_now = btn_speed.value()
    
    # 2. The Latch: Check for a fresh button press to flip the memory state
    if btn_pump_now == 0 and btn_pump_prev == 1:
        pump_running = not pump_running
        
    btn_pump_prev = btn_pump_now
    
    # 3. Setpoint Latch (Tap GP16 to increase target by 10%)
    if btn_setpoint_now == 0 and btn_setpoint_prev == 1:
        setpoint += 10
        if setpoint > 100:
            setpoint = 0  # Loop back to 0 if it goes over 100%
    btn_setpoint_prev = btn_setpoint_now
    
    #
    if btn_speed_now == 0 and btn_speed_prev ==1:
        speed_percent += 10
        if speed_percent > 100:
            speed_percent = 0  # Loop back to 0 if it goes over 100%
    btn_speed_prev = btn_speed_now
        
    
    # Print telemetry to the console
    print("Water Level:", percent, "% |", mm, "mm | System Active:", pump_running, "Pump Speed:", speed_percent, "%")
    
    # --- Update OLED Display ---
    oled.fill(0) # 1. Wipe the previous screen clear
    
    oled.text("Fluid Level:", 0, 0)
    oled.text(str(percent) + " %", 0, 16)
    oled.text(str(mm) + " mm", 50, 16)
    oled.text("Setpoint: "+ str(setpoint) + "mm", 0, 32)
    oled.text("Pump Speed: " + str(speed_percent) + "%", 0, 48)
    oled.show()
    
    # 4. Route power based on the memory state (No PID)
    if pump_running: 
        pump_parameters(80, forward=True) # System is latched ON at a static 80%
    else:
        pump_parameters(0) # System is latched OFF
    
    #5. Setpoint Logic
    if pump_running:
        if percent < setpoint:
            pump_parameters(speed_percent, forward = True)
        elif setpoint < percent:
            pump_parameters(speed_percent, forward = False)
        else:
            pump_parameters(0)
    else:
        pump_parameters(0)
   
    # 6. Pace the loop (keep at 0.1 for responsive button taps)
    time.sleep(0.1)
    