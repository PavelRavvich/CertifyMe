# CertifyMe
Quiz certification helper for pass exams hidden using OpenAI to generate answers

We need:
1. `ESP32 C3` - Core CPU Module with built-in WiFi and Bluetooth
2. `TZT LIS3DSH LIS3DH` - accelerometer module using as interface
3. `PWM Vibration Motor Module DC Motor Phone Vibrator` - answer receiver
4. `CR2450` - Power Battery 3V
5. `CR2450 Coin Cell holder` - battery holder
6. `Reusable Hook` - as an all-hardware holder `30mm` width is enough
7. Superglue for sticking all hardware pieces to a Reusable Hook
8. `DIY Kit 5050 SMD RGB LED Diodes module` or OLED display `0.96 Inch OLED Display Module SSD1306 I2C IIC SPI Serial 128X64 LCD` for sys indication like Power, WiFi and server connection.

## How does the system work?
Sending commands and responses go through the DIY gadget. 

#### Receiving Response with vibration motor
After three shakes were applied all screenshots were sent to the OpenAI and the response will be represented as a Morse A-Z:

`* - - - -`: Var. 1

`* * - - -`: Var. 2

`* * * - -`: Var. 3

`* * * * -`: Var. 4

`* * * * *`: Var. 5

Where: 

`*`: short vibro call

`-`: long vibro call


## Under the hood:
1. DIY Hardware - ``
2. Web server - `server.py`
3. Screenshot bot - `bot.py`


#### Send Command with an accelerometer:
1. Two shakes - create a screenshot. (Immediately successful command confirmation `* *`)
2. Three shakes - send saved screenshots to OpenAI. (Immediately successful command confirmation `* * *`)
3. Four shakes - clear the screenshots queue and start from scratch. (Immediately successful command confirmation `* -`)
4. Error recognize command `* - * -`
