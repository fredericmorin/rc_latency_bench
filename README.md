# End to end remote control lantency mesurement

This tool allows you to mesure what the reaction time is from stick movement to motor esc command change.

This then allows you to change any component, firmware or settings and mesure the impact of that change. For example:
- Crossfire vs FrSky vs FlySky
- OpenTX vs ersky9x
- SBUS vs FPort
- Taranis vs Horus vs X-Lite
- Internal Taranis Module vs external XJT
- RC filtering options


## Results

Find my latest results here:
https://docs.google.com/spreadsheets/d/14F0HHDNYIdGpTDLeHvXrCeLH8-vC3-hRIDzbgOypfuk/edit?usp=sharing


## General Strategy

Use an arduino to control a pot value on a taranis and
then use a logic analyzer to determine time between pot value change
and dshot motor command change.


## Credit

Original idea by Bryce Johnson
https://redpinelabs.com/reduce-your-frsky-taranis-latency-by-almost-1-2/
(He did not publish his code so I had to write a new program to do
the data acquisition)


## Preparation

### Taranis

1. Solder GND-SIG-3V wires to one of the POT of the taranis
2. Assign pot to the throttle channel
3. Move pot and see throttle value change in betaflight.
4. Set taranis pot to slightly past mid-position (voltage should read ~1.8v)
   (required for the logic analyser to detect edge change correctly)

### Arduino

1. Program an arduino to alternate a pin between pull-down and floating
   See `e2e_latency_bench.ino` file for arduino code.
2. Confirm with a multimeter that no voltage is coming out of the
   alternating pin. If 5v come out, you may fry your taranis...
3. Connect taranis pot ground to arduino ground
4. Connect taranis pot middle pin to arduino pull-down pin
5. See throttle value alternate between 0% and 70%

### Saleae Logic Analyser

1. Connect flight controller ground to analyzer ground
2. Connect flight controller motor output 1 to analyzer pin 1
3. Enable Dshot analyser on pin 1 and set to dshot600
4. Do a reading and confirm you see motor output
5. Connect taranis pot middle pin to analyzer pin 2
6. Setup trigger on rising edge on pin 2
7. Enable glitch filter on pin 2 and set to 1ms
8. Do another reading to confirm the trigger worked

### Ready to Mesure Latency
At this point you should be able to run `aquire.py` and see results
show up in the console as well as be appended to `result.txt`
