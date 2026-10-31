# SAGIP electronics list, pin map and open design points

Matches `kicad/SAGIP.kicad_sch` (open it in KiCad 7 or later) and `SAGIP_Simplified_Diagram.png`. References (U1, M1 and so on) are the same in all three. All values are planning values to confirm against the parts you buy. "Sheet" means the Materials Tracker sheet in Drive.

## 1. Boards (4 ESP32 boards in total)

| Ref | Part | Qty | Job | Sheet |
|---|---|---|---|---|
| U5 | ESP32-CAM Type C, OV2640, 4 MB PSRAM (Makerlab) | 1 | Bow camera: runs the object detector, sends plastic position by UART | Yes |
| U10 | ESP32-S3 N16R8 CAM board (OV2640, 8 MB PSRAM, microSD slot) | 1 | Belt camera: CNN, gate servo, hood LED, microSD log, phone Wi-Fi page | Yes |
| U4 | ESP32 DevKit, 30-pin | 1 | **Boat controller**: motors, safety, sensors, ESP-NOW to the bank | **No (new)** |
| U22 | ESP32 DevKit, 30-pin | 1 | Flood node controller | Yes (the one DevKit row) |

## 2. Boat power

| Ref | Part | Qty | Job | Sheet |
|---|---|---|---|---|
| PV1 | 30 W solar panel, 350 x 600 mm | 1 | Charging | Yes |
| U1 | 20 A charge controller (bought with the panel) | 1 | Charges the battery | Yes (in the panel row) |
| BT1 | 12 V 12 Ah sealed lead-acid battery | 1 | Boat power | Yes |
| F0 | 15 A blade fuse and holder | 1 | Main fuse | **No** |
| F1, F2, F3 | 5 A blade fuse and holder | 3 | Left thruster, right thruster, belt motor | Yes ("3 to 4 fuses") |
| F4 | 3 A blade fuse and holder | 1 | Electronics, bucks and hood LED | Yes (same row) |
| SW1 | Master switch rated 15 A or more | 1 | Cuts everything | **No** |
| U2 | 5 V 3 A buck converter (LM2596 or XL4015) | 1 | Logic rail: all boards, drivers, sensors | Yes |
| U3 | 5 V 3 A buck converter | 1 | Servo rail only | Yes (qty 2 in that row) |

## 3. Motion and actuators

| Ref | Part | Qty | Job | Sheet |
|---|---|---|---|---|
| DRV1, DRV2 | BTS7960-class motor driver module (current sense output) | 2 | One per thruster | **Changed**: sheet has one "dual driver" |
| DRV3 | BTS7960-class motor driver module | 1 | Belt motor, forward and reverse | **No** (belt driver missing from the sheet) |
| M1, M2 | 12 V underwater thruster | 2 | Differential steering | Yes (price may be per piece) |
| M3 | 12 V DC gear motor, low rpm | 1 | Conveyor belt | Yes |
| M4 | MG996R metal-gear servo | 1 | Sorting gate | Yes |
| LED1 | 12 V white LED strip, about 20 cm | 1 | Hood light | Yes |
| Q1 | Logic-level N-MOSFET (IRLZ44N or similar) | 1 | Switches the hood LED | **No** |

## 4. Sensors and inputs

| Ref | Part | Qty | Job | Sheet |
|---|---|---|---|---|
| U6 | MPU6050 module | 1 | Tilt cut-off (no heading) | Yes |
| U7 | QMC5883L or HMC5883L compass | 1 | Heading, **to decide** | Yes (row marked "to decide") |
| U8, U9 | JSN-SR04T waterproof ultrasonic sensor | 2 | Left and right bank distance | Yes (qty 2) |
| SW2, SW3 | Micro switch with roller | 2 | Bow bump, wired in parallel to one input | Yes ("2 to 4") |
| U11 | DS3231 RTC module | 1 | Timestamps, optional | **No** |
| (on U10) | microSD card | 1 | Append-only log | **No** |

## 5. Flood node

| Ref | Part | Qty | Job | Sheet |
|---|---|---|---|---|
| PV2 | 5 V 2 W solar panel | 1 | Charging | Yes |
| U20 | TP4056 charger **with protection chip** | 1 | Charges and protects the cell | Yes (check the protected version) |
| BT2 | Protected 18650 cell and holder | 1 | Storage | Yes |
| U21 | MT3608 boost converter | 1 | Cell voltage to 5 V | **No** |
| SW4, SW5, SW6 | Float switch | 3 | Watch, alert, danger levels | Yes |
| BZ1 | Active buzzer, 5 V | 1 | Local alarm | Yes |
| Q2 | NPN transistor (S8050 or 2N2222) | 1 | Drives the buzzer | **No** |
| LED2 | Small LED | 1 | Status | Yes |
| (box) | IP67 waterproof box | 1 | Holds the cell and board | Yes |

## 6. Small parts (not in the sheet, buy as a resistor and capacitor kit)

| Ref | Value | Job |
|---|---|---|
| C1 | 1000 uF 25 V | Bulk capacitor on the 12 V rail |
| C2 | 470 uF 10 V | Servo rail |
| C3, C4 | 100 nF | Battery sense filter, bump debounce |
| R1, R2 | 100k and 33k | Battery voltage divider (12.9 V becomes 3.2 V) |
| R3 | 10k | Motor enable pull-down (drivers off by default) |
| R4, R5, R6 | 1k | Current-sense loads |
| R7, R9 and R8, R10 | 1k and 2k | JSN-SR04T echo dividers, 5 V to 3.3 V |
| R11 | 10k | Bump pull-up |
| R12, R13 | 220 and 10k | Hood LED MOSFET gate |
| R20, R21, R22 | 100k | Float switch pull-downs |
| R23, R24 | 1k and 330 | Buzzer base, LED |

Also: 16 AWG silicone wire, connectors, heat shrink (Yes in the sheet), and four enclosures (three IP65 on the boat, one IP67 on the bank, both in the sheet).

## 7. Boat controller pin map (U4, ESP32 DevKit)

| Pin | Net | To |
|---|---|---|
| IO4 | MOTOR_EN | Enable of all three drivers (10k pull-down) |
| IO13 | THR_L_PWM | Left thruster driver RPWM |
| IO14 | THR_R_PWM | Right thruster driver RPWM |
| IO18, IO19 | BELT_RPWM, BELT_LPWM | Belt driver (forward, reverse) |
| IO34, IO35, IO36 | IS_THR_L, IS_THR_R, IS_BELT | Driver current sense (input-only pins) |
| IO39 | VBAT | Battery divider (input-only pin) |
| IO21, IO22 | SDA, SCL | MPU6050, compass |
| IO23, IO5 | TRIG_L, TRIG_R | JSN-SR04T trigger |
| IO25, IO26 | ECHO_L, ECHO_R | JSN-SR04T echo through the divider |
| IO27 | BUMP | Bump switches |
| IO16, IO17 | RX2, TX2 | UART to the bow ESP32-CAM |
| IO32, IO33 | RX, TX | UART to the ESP32-S3 |

All 16 usable output pins are used, so there is no spare. Thrusters use RPWM only and steer by speed difference.
Other boards: **S3** uses TX, RX (to controller), SERVO_PWM, LED_GATE, SDA, SCL (RTC). **Bow ESP32-CAM** uses U0T and U0R only. **Flood node** uses IO32, IO33, IO25 (float switches, wake on any high), IO26 (buzzer), IO27 (LED).

## 8. Open design points (please decide or check)

1. **Boat controller board added.** The two camera boards use most of their pins for the camera and microSD, so one board cannot also run three motor drivers, two sonars, I2C sensors and two UART links. I assumed the S3 board leaves 6 free pins and the ESP32-CAM leaves its serial pins. I have not seen either pinout, so check them. This adds one ESP32 DevKit (about PHP 120 to 350 from the listings you showed).
2. **Motor drivers.** I drew three BTS7960-class modules because they give a current-sense output, which the entry relies on ("reads belt and thruster current"). The sheet has one dual driver. An L298N dual driver is cheaper but handles about 2 A per channel and has no easy current sense. Match the driver rating to the real thruster current, which is unknown until the thrusters arrive.
3. **Fuse values** (15 A main, 5 A branches, 3 A electronics) are guesses until you have the thruster and belt motor ratings.
4. **R_IS and L_IS tied together** on each driver, read through 1k. Check this against the module you buy.
5. **JSN-SR04T echo** is 5 V, so it goes through a 1k and 2k divider. Some versions of the module output 3.3 V. Check the one you buy.
6. **Flood node wake.** The classic ESP32 wakes from deep sleep on any HIGH input, so the float switches connect to 3.3 V with pull-down resistors. The 5 V boost converter and the DevKit's own regulator draw current in sleep, so the real sleep current is higher than the bare chip. Measure it.
7. **TP4056 module wiring** differs between suppliers. Wire to the silkscreen of the protected version you buy.
8. **Compass** and **RTC** are optional. The RTC can be replaced by setting the time from the phone when it connects.
9. **ERC was not run.** The schematic loads in KiCad 7.0.11 and its netlist matches the intended connections (62 nets), but module symbols are simple boxes without footprints, so it is a planning schematic, not a PCB design.
