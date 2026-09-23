/*
  XIAO nRF52840 solder-bridge tester

  Checks the 11 header pins D0-D10 for:
    1. a pin shorted to GND                 (reads LOW with its pull-up on)
    2. a pin shorted to 3V3 or 5V           (reads HIGH with its pull-down on)
    3. two pins shorted to each other       (driving one pin moves the other)
  then stays in a "touch test" mode for checking that each header pin is actually
  soldered (catches cold joints / open circuits, which a bridge test cannot see).

  HOW TO RUN
    - Take the XIAO OUT of the breadboard (or make sure nothing else is plugged into
      its rows). Anything wired to a pin -- the button to GND, the AD8232 outputs --
      would show up as a false "bridge".
    - Board: Tools > Board > "Seeed XIAO BLE Sense - nRF52840" (mbed-enabled core).
    - Upload, open Serial Monitor at 115200 baud. Send any character to re-run.

  WHAT IT CANNOT TEST
    - 3V3-to-GND or 5V-to-GND bridges: those stop the board from powering up at all
      (no USB port appears, board gets warm). Check those with a multimeter in
      continuity/resistance mode with USB unplugged.
    - Very high-resistance leakage (e.g. dirty flux) above ~100 kOhm.
    - The pads on the underside (BAT+, BAT-, NFC, SWD) -- inspect those by eye.

  Every pin is only ever driven through a check that proved it is not shorted to a
  supply first, so running this on a bridged board cannot make the short worse.
*/

#include <Arduino.h>

struct PinInfo {
  int pin;
  const char* name;
};

// Header order as seen from the top, USB-C at the top:
//   left side  top->bottom: D0 D1 D2 D3 D4 D5 D6
//   right side top->bottom: 5V GND 3V3 D10 D9 D8 D7
static const PinInfo PINS[] = {
  {D0, "D0/A0"}, {D1, "D1/A1"}, {D2, "D2/A2"}, {D3, "D3/A3"},
  {D4, "D4/SDA"}, {D5, "D5/SCL"}, {D6, "D6/TX"}, {D7, "D7/RX"},
  {D8, "D8/SCK"}, {D9, "D9/MISO"}, {D10, "D10/MOSI"},
};
static const int N = sizeof(PINS) / sizeof(PINS[0]);

// Physically neighbouring header pads (index pairs into PINS), where bridges happen.
static bool neighbours(int a, int b) {
  if (a > b) { int t = a; a = b; b = t; }
  if (b == a + 1 && b <= 6) return true;   // left side D0..D6
  if (b == a + 1 && a >= 7) return true;   // right side D7..D10
  return false;
}

static const uint32_t SETTLE_US = 200;     // internal pulls are ~13 kOhm; this is plenty

#if defined(LEDR) && defined(LEDG)
static void leds(bool red, bool green) {   // XIAO RGB LED is active-low
  digitalWrite(LEDR, red ? LOW : HIGH);
  digitalWrite(LEDG, green ? LOW : HIGH);
}
#else
static void leds(bool, bool) {}
#endif

static void allPull(int mode) {
  for (int i = 0; i < N; i++) pinMode(PINS[i].pin, mode);
  delayMicroseconds(SETTLE_US);
}

static int runBridgeTest() {
  int problems = 0;
  bool stuck[N] = {false};

  Serial.println();
  Serial.println("=== XIAO nRF52840 solder-bridge test ===");

  // 1. Shorted to GND: with its pull-up on, an unconnected pin must read HIGH.
  Serial.println("\n[1] Pins shorted to GND");
  allPull(INPUT_PULLUP);
  for (int i = 0; i < N; i++) {
    if (digitalRead(PINS[i].pin) == LOW) {
      Serial.print("  FAIL  "); Serial.print(PINS[i].name);
      Serial.println(" is connected to GND");
      stuck[i] = true; problems++;
    }
  }
  if (!problems) Serial.println("  OK");

  // 2. Shorted to 3V3/5V: with its pull-down on, an unconnected pin must read LOW.
  Serial.println("\n[2] Pins shorted to 3V3 / 5V");
  int before = problems;
  allPull(INPUT_PULLDOWN);
  for (int i = 0; i < N; i++) {
    if (!stuck[i] && digitalRead(PINS[i].pin) == HIGH) {
      Serial.print("  FAIL  "); Serial.print(PINS[i].name);
      Serial.println(" is connected to 3V3 or 5V");
      stuck[i] = true; problems++;
    }
  }
  if (problems == before) Serial.println("  OK");

  // 3. Pin-to-pin: drive one pin, the rest held by pulls; a bridged partner follows it.
  //    Done both ways (drive LOW against pull-ups, drive HIGH against pull-downs) so a
  //    bridge is only reported when it shows up in both directions.
  Serial.println("\n[3] Pins shorted to each other");
  before = problems;
  bool lowHit[N][N] = {{false}};
  for (int pass = 0; pass < 2; pass++) {
    int pull = pass == 0 ? INPUT_PULLUP : INPUT_PULLDOWN;
    int drive = pass == 0 ? LOW : HIGH;
    for (int i = 0; i < N; i++) {
      if (stuck[i]) continue;                  // never drive a pin tied to a supply
      allPull(pull);
      pinMode(PINS[i].pin, OUTPUT);
      digitalWrite(PINS[i].pin, drive);
      delayMicroseconds(SETTLE_US);
      for (int j = 0; j < N; j++) {
        if (j == i || stuck[j]) continue;
        bool followed = digitalRead(PINS[j].pin) == drive;
        if (pass == 0) {
          lowHit[i][j] = followed;
        } else if (followed && lowHit[i][j] && i < j) {
          Serial.print("  FAIL  "); Serial.print(PINS[i].name);
          Serial.print(" <-> "); Serial.print(PINS[j].name);
          Serial.println(neighbours(i, j) ? "  (neighbouring pads - look for a solder blob)"
                                          : "  (not neighbours - a stray wire/whisker, or one blob spanning several pads)");
          problems++;
        }
      }
      pinMode(PINS[i].pin, pull);
    }
  }
  if (problems == before) Serial.println("  OK");

  allPull(INPUT);  // leave everything high-impedance

  Serial.println();
  if (problems == 0) {
    Serial.println("RESULT: PASS - no bridges found on D0-D10.");
  } else {
    Serial.print("RESULT: FAIL - "); Serial.print(problems);
    Serial.println(" problem(s). Unplug USB, remove the bridge with solder wick or a clean");
    Serial.println("        iron tip, then re-run. (If the board is in a breadboard, pull it");
    Serial.println("        out first - external wiring also shows up here.)");
  }
  leds(problems != 0, problems == 0);
  return problems;
}

static void printTouchHelp() {
  Serial.println();
  Serial.println("=== Touch test (checks every header pin is really soldered) ===");
  Serial.println("Put the XIAO in the breadboard with nothing else attached. Run a jumper");
  Serial.println("wire from the XIAO's GND row and touch it to each D-pin's row in turn.");
  Serial.println("Each touch should print that pin. If a pin never shows up, its joint is");
  Serial.println("cold/open - reheat it. (Showing up at all also proves the GND pin joint.)");
  Serial.println("Send any character to re-run the bridge test.");
}

static bool lastLow[N];

void setup() {
#if defined(LEDR) && defined(LEDG)
  pinMode(LEDR, OUTPUT); pinMode(LEDG, OUTPUT);
#endif
#if defined(LEDB)
  pinMode(LEDB, OUTPUT); digitalWrite(LEDB, HIGH);
#endif
  leds(false, false);
  Serial.begin(115200);
  while (!Serial) {}          // wait for Serial Monitor so the results are not missed
  delay(300);
  runBridgeTest();
  printTouchHelp();
  allPull(INPUT_PULLUP);
  for (int i = 0; i < N; i++) lastLow[i] = false;
}

void loop() {
  if (Serial.available()) {
    while (Serial.available()) Serial.read();
    runBridgeTest();
    printTouchHelp();
    allPull(INPUT_PULLUP);
  }

  // Touch test: pins held HIGH by pull-ups; touching one to GND pulls it LOW.
  for (int i = 0; i < N; i++) {
    bool low = digitalRead(PINS[i].pin) == LOW;
    if (low && !lastLow[i]) {
      Serial.print("  touched "); Serial.println(PINS[i].name);
    }
    lastLow[i] = low;
  }
  delay(20);  // also debounces the wire contact
}
