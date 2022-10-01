import network, secrets, time, urequests, uping
from neopixel import Neopixel
import machine

# ------------ Variables ------------ #
program = "status print"

# GPIO Pins
ldrPin = 27
ledPanelPin = 28
 
# Servers to ping
servers = [["Printer", "..."], ["NAS", "..."], ["Windows", "..."]]

# LEDS Setup
numpix = 30
pixels = Neopixel(numpix, 0, ledPanelPin, "GRB")
ldr = machine.ADC(ldrPin)

# LEDS Animations
numbers = [[0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 13, 14],[0, 5, 6, 11, 12], [0, 1, 2, 3, 6, 7, 8, 11, 12, 13, 14], [0, 1, 2, 5, 6, 7, 8, 11, 12, 13, 14], [0, 5, 6, 7, 8, 9, 11, 12, 14], [0, 1, 2, 5, 6, 7, 8, 9, 12, 13, 14], [0, 1, 2,  3, 5, 6, 7, 8, 9, 12, 13, 14], [0, 5, 6, 11, 12, 13, 14], [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 14], [0, 1, 2, 5, 6, 7, 8, 9, 11, 12, 13, 14]]
loadingAnimation = [[21, 9, 8, 3, 7, 10, 4, 6], [8, 10, 7, 4, 6, 11, 5, 23], [7, 11, 6, 5, 23, 24, 18, 22], [6, 18, 23, 24, 22, 25, 19, 21], [23, 19, 22, 25, 21, 26, 20, 8], [22, 21, 26, 20, 8, 9, 3, 7]]
openingAnimation = [[22, 21, 26, 20, 8, 9, 3, 7], [14, 10, 6, 4, 2, 15, 19, 23, 25, 27], [16, 18, 24, 28, 13, 11, 5, 1]]
closingAnimation = [[17, 0, 12, 29], [16, 18, 24, 28, 13, 11, 5, 1], [14, 10, 6, 4, 2, 15, 19, 23, 25, 27], [9, 7, 3, 20, 22, 26], [21, 8]]
errorAnimation = [[29, 12, 0, 17], [25, 10, 4, 19], [21, 8]]

# LEDS Colors
yellow = (255, 100, 0)
orange = (255, 50, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
white = (255, 255, 255)
off = (0, 0, 0)

# Wifi setup
wlan = network.WLAN(network.STA_IF)

# ------------ Variables ------------ #
    
def services() :
    while True :
        while wlan.isconnected() :
            # If ligth is = day
            light = brightness()
            
            if light != 0 :
                # If printer is online
                if ping(servers[0][0], servers[0][1]):
                    printer(job)
                
                else :
                    # Gather and show weather data
                    weather()
                    
                status()
                
            # If brightness = 0 then sleep
            else :
                pixels.fill(off)
                pixels.show()
                    
            i=0
            while i<=24 :
                time.sleep(5)
                if light != brightness() :
                    i=24
                i+=1
    
        wifi()
    
# Wifi service
def wifi() :
    while wlan.isconnected() == False :
        print("[Wifi] Connecting to the wifi...")
        wlan.active(True)
        wlan.connect(secrets.SSID, secrets.PASSWORD)
        k=0
        while k<7 :
            animation(loadingAnimation, white, 0.4, True)
            if wlan.isconnected() :
                break
            k+=1
    print(f"[Wifi] Connected to {secrets.SSID}")
    animation(openingAnimation, white, 0.2, False)
        
    pixels.fill(white)
    pixels.show()
    time.sleep(0.4)
    animation(closingAnimation, off, 0.2, False)
    return

# Animation
def animation(name, color, sleep, remove) :
    brightness()
    for i in range(len(name)) :
        if remove == True :
            pixels.fill(off)
        for j in range(len(name[i])) :
            pixels.set_pixel(name[i][j], color)
            pixels.show()
        time.sleep(sleep)
    return
    
# Printer service
def printer(job) :
    # Store print job data
    try:
        r = urequests.get("...").json()
        print(f"[] Printer online")
        return r
    except:
        print(f"[{file}] Printer offline")
        return False

    state = job["state"]
    completion = job["progress"]["completion"]
    
    if state == "Operational" :
        # Make the lights green
        pixels.fill(blue)
    elif state == "Printing" :
        if completion < 0.1 :
            pixels.fill(orange)
        pixels.fill(green)
    elif state == "Canceling" :
        pixels.fill(red)
    elif state == "None" :
        pixels.fill(red)
    
    brightness()
    pixels.show()

# Ping server
def ping(name, ip) :
    try :
        uping.ping(ip)
        print(f"[Ping] {name} is up")
        return True

    except :
        print(f"[Ping] {name} is down")
        return False
    
# Weather service
def weather() :
    # Try getting weather data
    try :
        weatherData = urequests.get("...").json()
    except :
        # Return error
        print("[Weather] Error while gathering weather data")
        animation(errorAnimation, red, 0.4, True)
        return
    
    print("[Weather] Weather data successfully gathered")
    temperature = int(float(weatherData["current"]["temp"]) - 273.15)
    if temperature >= 0 :
        displayNumber(temperature, red)
    else :
        displayNumber(-1*temperature, blue)

# Ckeck servers status
def status() :
    for i in range(len(servers)) :
        ping(servers[i][0], servers[i][1])
        #if ping(servers[i][0], servers[i][1]) :
            # Turn on green LED
            
        #else :
            # Turn on red LED
        
        
# Display numbers
def displayNumber(value, color) :
    pixels.fill(off)
    brightness()
    
    value = str(value)
    # Check if number has 1 or 2 dijits
    if int(value) >= 10 :
        for i in range(len(numbers[int(value[0])])) :
            pixels.set_pixel(numbers[int(value[0])][i]+15, color)
        
        for i in range(len(numbers[int(value[1])])) :
            pixels.set_pixel(numbers[int(value[1])][i], color)
    elif int(value) < 10:
        for i in range(len(numbers[int(value[0])])) :
            pixels.set_pixel(numbers[int(value[0])][i], color)
    else :
        animation(errorAnimation, white, 0.4, True)
        
    pixels.show()
    
def brightness() :
    # Measure brightness
    light = ldr.read_u16()
    
    # High
    if light<200 :
        b = 100
    # Moderate - high
    elif light<400 :
        b = 70
    # Moderate - low
    elif light<700 :
        b = 30
    # Low
    elif light<1000 :
        b = 10
    # Night
    elif light>=1000 :
        b=0
        
    pixels.brightness(b)
    return b
    
if __name__ == "__main__":
    print(f"[Main] Starting {program}...")
    print("[Main] Starting services")
    services()
    
