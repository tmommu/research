/*
  TIBOK — real-time arrhythmia screening firmware
  Seeed XIAO nRF52840 Sense + AD8232 ECG front-end

  Runs the INT8 RR-fused 1D-CNN trained in TIBOK_Combined_COMPETITION_v3.ipynb on the
  device, beat by beat, with the SAME input pipeline the notebook trained on:

    - ECG sampled at 360 Hz (the notebook resamples INCART to 360 Hz; MIT-BIH is native)
    - one 1250-sample window centred on each R peak  (signal[r-625 : r+625])
    - per-window z-score:  (x - mean) / (std + 1e-8)          (normalize_batch)
    - 4 RR features, in seconds:                               (load_and_segment)
        pre_rr   = time since the previous beat
        post_rr  = time to the next beat
        local_rr = mean pre_rr of the previous (up to) 10 beats
        ratio    = pre_rr / (local_rr + 1e-6)
      standardised with the TRAINING-set rr_mean / rr_std
    - arrhythmia when probability > the precision_floor_90 deploy threshold, applied as
      the equivalent integer cutoff on the INT8 output (int8_threshold_grid)

  The notebook used cardiologist-annotated beat positions. The device has no annotations,
  so it finds R peaks itself with a real-time Pan-Tompkins style detector.

  ---------------------------------------------------------------------------------------
  SETUP (Arduino IDE)
  ---------------------------------------------------------------------------------------
  1. Boards Manager URL:
       https://files.seeedstudio.com/arduino/package_seeeduino_boards_index.json
     Install "Seeed nRF52 mbed-enabled Boards" and pick
       Tools > Board > "Seeed XIAO BLE Sense - nRF52840"
     (use the *mbed-enabled* core, NOT "Seeed nRF52 Boards": this sketch uses
      mbed::Ticker and ArduinoBLE, which need the mbed core.)
  2. Library Manager: install "ArduinoBLE" and "Chirale_TensorFlowLite".
  3. Copy the header the notebook downloaded into THIS sketch folder (next to this file):
       tibok_combined_rr_cnn_model_int8.h         (PTQ model, default)
       tibok_combined_rr_cnn_model_qat_int8.h     (QAT model, if USE_QAT_MODEL = 1)
  4. Fill in the four constants in "CONSTANTS FROM YOUR TRAINING RUN" below from
     tibok_combined_rr_cnn_summary.json, then set TIBOK_CONSTANTS_FILLED to 1.
  5. Check the pin assignments below match your PCB, then Upload.
     Open Serial Monitor at 115200 baud.

  Output: one CSV line per classified beat on Serial, plus a BLE notification (see the
  BLE section for the 16-byte packet layout) for the Flutter app.
*/

#include <Arduino.h>
#include <mbed.h>
#include <ArduinoBLE.h>

#include <Chirale_TensorFlowLite.h>
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include <math.h>
#include <string.h>

// =======================================================================================
// MODEL SELECTION
// =======================================================================================
// 0 = PTQ INT8 model (always produced by the notebook)
// 1 = QAT INT8 model (only if the notebook's QAT section succeeded and you chose it)
#define USE_QAT_MODEL 0

#if USE_QAT_MODEL
  #include "tibok_combined_rr_cnn_model_qat_int8.h"
  #define TIBOK_MODEL_DATA tibok_model_qat
#else
  #include "tibok_combined_rr_cnn_model_int8.h"
  #define TIBOK_MODEL_DATA tibok_model
#endif

// =======================================================================================
// CONSTANTS FROM YOUR TRAINING RUN   <-- EDIT THESE
// =======================================================================================
// They change every time the notebook is re-run, so they cannot be hard-coded here.
// Copy them from tibok_combined_rr_cnn_summary.json:
//
//   RR_MEAN          <- "rr_feature_norm" -> "mean"   (4 numbers)
//   RR_STD           <- "rr_feature_norm" -> "std"    (4 numbers)
//   DEPLOY_THRESHOLD <- PTQ: "thresholds" -> "precision_floor_90"
//                       QAT: "qat" -> "recommended_threshold"
//
// (The same values are also under "quantization" -> "firmware" as rr_feature_mean /
//  rr_feature_std / deploy_threshold_float.)
//
// The INT8 input/output scales and zero points are NOT needed here: the sketch reads
// them straight out of the model at start-up, so they can never go out of sync.
//
// The values below are placeholders (typical adult RR statistics) so the sketch compiles
// and runs for bench testing. Classifications made with them are NOT the validated model.
#define TIBOK_CONSTANTS_FILLED 0

static const float RR_MEAN[4] = {0.80f, 0.80f, 0.80f, 1.00f};  // pre, post, local, ratio
static const float RR_STD[4]  = {0.20f, 0.20f, 0.17f, 0.20f};
static const float DEPLOY_THRESHOLD = 0.50f;

#if !TIBOK_CONSTANTS_FILLED
  #warning "TIBOK: RR_MEAN / RR_STD / DEPLOY_THRESHOLD are placeholders - copy them from tibok_combined_rr_cnn_summary.json and set TIBOK_CONSTANTS_FILLED to 1"
#endif

// =======================================================================================
// PINS  (match these to your PCB)
// =======================================================================================
// AD8232 OUTPUT is read with the nRF52840 SAADC directly (not analogRead) so it can be
// sampled from a timer interrupt at exactly 360 Hz. Pick the AIN channel of the pin the
// AD8232 OUTPUT is wired to:
//   XIAO A0/D0 = P0.02 = AIN0    XIAO A1/D1 = P0.03 = AIN1
//   XIAO A2/D2 = P0.28 = AIN4    XIAO A3/D3 = P0.29 = AIN5
//   XIAO A4/D4 = P0.04 = AIN2    XIAO A5/D5 = P0.05 = AIN3   (A4/A5 are also I2C)
#define ECG_SAADC_PSELP  SAADC_CH_PSELP_PSELP_AnalogInput0   // A0

#define PIN_LO_PLUS   D1    // AD8232 LO+  (HIGH = electrode off). -1 if not wired
#define PIN_LO_MINUS  D2    // AD8232 LO-  (HIGH = electrode off). -1 if not wired
#define PIN_BUZZER    D3    // MLT buzzer driver transistor base.  -1 if not wired
#define PIN_BUTTON    D8    // event-marker button to GND.         -1 if not wired

#define BUZZER_FREQ_HZ   2700
#define BUZZER_MS        150

// =======================================================================================
// BEHAVIOUR
// =======================================================================================
// Mains notch: the Philippines grid is 60 Hz. Set 50 for 50 Hz countries, 0 to disable.
#define NOTCH_HZ            60
#define USE_HIGHPASS_0P5HZ  1   // removes electrode drift / baseline wander
#define USE_LOWPASS_40HZ    0   // off by default: the training data was NOT low-passed at
                                // 40 Hz (MIT-BIH is 0.1-100 Hz), so extra smoothing moves the
                                // device input further from what the model learned.

// Alert rule. The model classifies every beat; the buzzer sounds when at least
// ALERT_K of the last ALERT_N classified beats were flagged. Set both to 1 to beep
// on every flagged beat (the notebook's per-beat operating point, but noisy to wear).
#define ALERT_K  3
#define ALERT_N  10

// 1 = stream the filtered ECG as one number per line for Tools > Serial Plotter
//     (beat CSV lines are then suppressed).
#define SERIAL_PLOTTER_MODE 0

#define BLE_DEVICE_NAME "TIBOK"

// =======================================================================================
// FIXED BY THE TRAINED MODEL — do not change
// =======================================================================================
static const int   FS          = 360;   // Hz  (notebook FS)
static const int   WINDOW_SIZE = 1250;  // samples (notebook WINDOW_SIZE)
static const int   N_RR        = 4;

// ==== TIBOK_DSP_BEGIN ==================================================================
// Pure C++ (no Arduino calls) so this block can be unit-tested on a PC.

// Direct-form-II-transposed biquad. Double precision on purpose: the 0.5 Hz high-pass
// has poles at |z| ~ 0.994, where float32 state loses enough precision to drift.
// At 360 Hz the software-double cost is negligible.
struct Biquad {
  double b0, b1, b2, a1, a2, z1, z2;
  void set(double b0_, double b1_, double b2_, double a1_, double a2_) {
    b0 = b0_; b1 = b1_; b2 = b2_; a1 = a1_; a2 = a2_; z1 = z2 = 0.0;
  }
  void reset() { z1 = z2 = 0.0; }
  double step(double x) {
    double y = b0 * x + z1;
    z1 = b1 * x - a1 * y + z2;
    z2 = b2 * x - a2 * y;
    return y;
  }
};

// Coefficients designed for fs = 360 Hz with scipy.signal:
//   butter(2, 0.5, 'highpass'), iirnotch(60|50, Q=30), butter(2, 40)
// and, in QrsDetector, butter(2, [5, 15], 'bandpass') as two sections.
class EcgConditioner {
 public:
  void begin(bool highpass, int notchHz, bool lowpass) {
    useHp_ = highpass; useNotch_ = (notchHz == 50 || notchHz == 60); useLp_ = lowpass;
    hp_.set(0.993848328562, -1.987696657124, 0.993848328562, -1.987658813705, 0.987734500544);
    if (notchHz == 50)
      notch_.set(0.985663100363, -1.267144056477, 0.985663100363, -1.267144056477, 0.971326200726);
    else
      notch_.set(0.982844387404, -0.982844387404, 0.982844387404, -0.982844387404, 0.965688774807);
    lp_.set(0.080423658972, 0.160847317944, 0.080423658972, -1.053329920813, 0.375024556702);
    reset();
  }
  void reset() { hp_.reset(); notch_.reset(); lp_.reset(); haveOffset_ = false; }
  float step(float raw) {
    // Subtract the first sample so the high-pass does not start with a full-scale step
    // (the AD8232 output idles around mid-rail, ~1.65 V).
    if (!haveOffset_) { offset_ = raw; haveOffset_ = true; }
    double x = (double)raw - offset_;
    if (useHp_) x = hp_.step(x);
    if (useNotch_) x = notch_.step(x);
    if (useLp_) x = lp_.step(x);
    return (float)x;
  }
 private:
  Biquad hp_, notch_, lp_;
  bool useHp_ = true, useNotch_ = true, useLp_ = false, haveOffset_ = false;
  double offset_ = 0.0;
};

// Real-time QRS detector after Pan & Tompkins (1985): 5-15 Hz band-pass, 5-point
// derivative, squaring, 150 ms moving-window integration (MWI), adaptive signal/noise
// thresholds, 200 ms refractory, T-wave slope check and RR-based search-back.
// Reports the sample index of the MWI peak; the caller refines it to the R peak.
class QrsDetector {
 public:
  static const int MWI_LEN   = 54;    // 150 ms
  static const int REFRACT   = 72;    // 200 ms
  static const int TWAVE_WIN = 130;   // 360 ms
  static const int LEARN     = 720;   // 2 s of threshold learning after (re)start
  static const int STALL     = 1080;  // 3 s without a beat -> relearn thresholds
  static const int SLOPE_RING = 256;

  void reset() {
    bp1_.set(0.006765413257, 0.013530826514, 0.006765413257, -1.791933833153, 0.841222057608);
    bp2_.set(1.0, -2.0, 1.0, -1.91937261708, 0.928744645206);
    for (int i = 0; i < 4; i++) dbuf_[i] = 0.0f;
    for (int i = 0; i < MWI_LEN; i++) mwiBuf_[i] = 0.0f;
    for (int i = 0; i < SLOPE_RING; i++) slope_[i] = 0.0f;
    mwiSum_ = 0.0; mwiPos_ = 0;
    prev_ = prev2_ = 0.0f;
    relearn();
    haveLast_ = false; lastSlope_ = 0.0f; rrAvg_ = 288.0f;  // 0.8 s
  }

  // Feed one conditioned sample with absolute index n (must increase by 1 per call).
  // Returns true and writes the detection's MWI-peak index when a QRS is confirmed.
  bool step(float x, uint32_t n, uint32_t* qrsIdx) {
    float b = (float)bp2_.step(bp1_.step(x));
    float d = (2.0f * b + dbuf_[0] - dbuf_[2] - 2.0f * dbuf_[3]) * 0.125f;
    dbuf_[3] = dbuf_[2]; dbuf_[2] = dbuf_[1]; dbuf_[1] = dbuf_[0]; dbuf_[0] = b;
    slope_[n % SLOPE_RING] = fabsf(d);

    float sq = d * d;
    mwiSum_ += (double)sq - (double)mwiBuf_[mwiPos_];
    mwiBuf_[mwiPos_] = sq;
    if (++mwiPos_ == MWI_LEN) mwiPos_ = 0;
    float mwi = (float)(mwiSum_ > 0.0 ? mwiSum_ / MWI_LEN : 0.0);

    bool found = false;
    if (learnCount_ < LEARN) {
      learnCount_++;
      if (mwi > learnMax_) learnMax_ = mwi;
      learnSum_ += mwi;
      if (learnCount_ == LEARN) {
        spki_ = 0.33f * learnMax_;
        npki_ = 0.5f * (float)(learnSum_ / LEARN);
        sinceBeat_ = 0;
      }
    } else {
      float thr = npki_ + 0.25f * (spki_ - npki_);
      bool inRefractory = haveLast_ && (n - lastQrs_) <= (uint32_t)REFRACT;
      if (!above_) {
        if (mwi > thr && !inRefractory) {
          above_ = true; candVal_ = mwi; candIdx_ = n;
        } else if (prev_ > prev2_ && prev_ >= mwi) {       // local MWI max at n-1 = noise peak
          uint32_t pi = n - 1;
          if (!(haveLast_ && (pi - lastQrs_) <= (uint32_t)REFRACT)) {
            npki_ = 0.125f * prev_ + 0.875f * npki_;
            if (prev_ > 0.5f * thr && (!sbValid_ || prev_ > sbVal_)) {
              sbValid_ = true; sbVal_ = prev_; sbIdx_ = pi;
            }
          }
        }
      } else {
        if (mwi > candVal_) { candVal_ = mwi; candIdx_ = n; }
        if (mwi < 0.5f * candVal_) {
          above_ = false;
          found = confirm(candVal_, candIdx_, n, false, qrsIdx);
        }
      }
      // Search-back: no beat for 1.66 x the average RR -> take the best sub-threshold peak.
      if (!found && !above_ && haveLast_ && sbValid_ &&
          (float)(n - lastQrs_) > 1.66f * rrAvg_) {
        found = confirm(sbVal_, sbIdx_, n, true, qrsIdx);
      }
      if (found) sinceBeat_ = 0;
      else if (++sinceBeat_ > (uint32_t)STALL) relearn();  // lost the signal level entirely
    }
    prev2_ = prev_; prev_ = mwi;
    return found;
  }

 private:
  void relearn() {
    learnCount_ = 0; learnMax_ = 0.0f; learnSum_ = 0.0;
    spki_ = npki_ = 0.0f; above_ = false; sbValid_ = false; sinceBeat_ = 0;
  }

  bool confirm(float val, uint32_t idx, uint32_t n, bool searchBack, uint32_t* qrsIdx) {
    float slope = -1.0f;  // max |derivative| over the MWI window ending at idx
    if (n - idx + MWI_LEN < (uint32_t)SLOPE_RING) {
      slope = 0.0f;
      for (int k = 0; k <= MWI_LEN; k++) {
        float s = slope_[(idx - k) % SLOPE_RING];
        if (s > slope) slope = s;
      }
    }
    if (!searchBack && haveLast_ && (idx - lastQrs_) < (uint32_t)TWAVE_WIN &&
        slope >= 0.0f && slope < 0.5f * lastSlope_) {
      npki_ = 0.125f * val + 0.875f * npki_;   // T wave, not a QRS
      return false;
    }
    spki_ = searchBack ? 0.25f * val + 0.75f * spki_ : 0.125f * val + 0.875f * spki_;
    if (haveLast_) {
      float rr = (float)(idx - lastQrs_);
      if (rr > 0.4f * rrAvg_ && rr < 3.0f * rrAvg_) rrAvg_ = 0.875f * rrAvg_ + 0.125f * rr;
    }
    lastQrs_ = idx; haveLast_ = true; sbValid_ = false;
    if (slope >= 0.0f) lastSlope_ = slope;
    *qrsIdx = idx;
    return true;
  }

  Biquad bp1_, bp2_;               // 4th-order 5-15 Hz band-pass (rejects T waves)
  float dbuf_[4];
  float mwiBuf_[MWI_LEN];
  double mwiSum_;
  int mwiPos_;
  float slope_[SLOPE_RING];
  float prev_, prev2_;
  int learnCount_; float learnMax_; double learnSum_;
  float spki_, npki_;
  bool above_; float candVal_; uint32_t candIdx_;
  bool sbValid_; float sbVal_; uint32_t sbIdx_;
  bool haveLast_; uint32_t lastQrs_; float lastSlope_;
  float rrAvg_;
  uint32_t sinceBeat_;
};

struct BeatFeatures {
  uint32_t r;         // absolute sample index of the R peak
  float preRr;        // s
  float postRr;       // s   (< 0 until the next beat is detected)
  float localRr;      // s
  float ratio;
};

// Keeps a ring of conditioned ECG, runs the detector, builds the notebook's RR features
// and hands out beats once their full 1250-sample window and post_rr are available.
class BeatPipeline {
 public:
  static const int HALF = WINDOW_SIZE / 2;         // 625
  static const uint32_t RING = 4096;               // 11.4 s of ECG
  static const uint32_t RING_MASK = RING - 1;
  static const int QUEUE = 16;
  static const int RR_HIST = 10;                   // notebook: pre_rr[max(0, i-10):i]
  static const uint32_t SETTLE = 2 * FS;           // ignore windows touching the first 2 s
  static const uint32_t MAX_POST_WAIT = 3000;      // give up on post_rr after ~8.3 s
  static const int R_SEARCH = 80;                  // samples searched back from the MWI peak

  void begin() { n_ = 0; reset(); }

  // Restart detection (e.g. after leads-off). Sample numbering continues.
  void reset() {
    det_.reset();
    qHead_ = qCount_ = 0;
    histCount_ = histPos_ = 0;
    haveLastR_ = false;
    validStart_ = n_ + SETTLE;
  }

  void push(float x) {
    ring_[n_ & RING_MASK] = x;
    uint32_t q;
    if (det_.step(x, n_, &q)) onQrs(q);
    n_++;
  }

  uint32_t samples() const { return n_; }
  uint32_t dropped() const { return dropped_; }

  // If the oldest pending beat is ready, write its features and its z-scored
  // 1250-sample window (normalize_batch) and return true.
  bool popReady(BeatFeatures* out, float* window) {
    while (qCount_ > 0) {
      BeatFeatures& f = queue_[qHead_];
      bool tooEarly = f.r < validStart_ + HALF;                   // window starts before valid data
      bool overwritten = (n_ + HALF) - f.r > RING;                // window start left the ring
      bool noNext = f.postRr < 0.0f && n_ > f.r + MAX_POST_WAIT;
      if (tooEarly || overwritten || noNext) { popFront(); dropped_++; continue; }
      if (f.postRr < 0.0f || n_ < f.r + HALF) return false;       // not ready yet

      double sum = 0.0, sumSq = 0.0;
      uint32_t start = f.r - HALF;
      for (int i = 0; i < WINDOW_SIZE; i++) {
        float v = ring_[(start + i) & RING_MASK];
        window[i] = v;
        sum += v; sumSq += (double)v * v;
      }
      double mean = sum / WINDOW_SIZE;
      double var = sumSq / WINDOW_SIZE - mean * mean;
      float stdv = (float)sqrt(var > 0.0 ? var : 0.0) + 1e-8f;
      for (int i = 0; i < WINDOW_SIZE; i++) window[i] = (float)((window[i] - mean) / stdv);

      *out = f;
      popFront();
      return true;
    }
    return false;
  }

 private:
  void popFront() { qHead_ = (qHead_ + 1) % QUEUE; qCount_--; }

  // Largest deviation from the local mean within R_SEARCH samples before the MWI peak.
  uint32_t refineR(uint32_t q) {
    uint32_t lo = (q > (uint32_t)R_SEARCH) ? q - R_SEARCH : 0;
    double sum = 0.0;
    for (uint32_t i = lo; i <= q; i++) sum += ring_[i & RING_MASK];
    float mean = (float)(sum / (q - lo + 1));
    uint32_t best = q; float bestV = -1.0f;
    for (uint32_t i = lo; i <= q; i++) {
      float v = fabsf(ring_[i & RING_MASK] - mean);
      if (v > bestV) { bestV = v; best = i; }
    }
    return best;
  }

  void onQrs(uint32_t q) {
    uint32_t r = refineR(q);
    if (haveLastR_ && r <= lastR_ + QrsDetector::REFRACT) return;

    if (haveLastR_) {
      float rr = (float)(r - lastR_) / FS;
      if (qCount_ > 0) {                                  // previous beat now has post_rr
        BeatFeatures& prev = queue_[(qHead_ + qCount_ - 1) % QUEUE];
        if (prev.r == lastR_) prev.postRr = rr;
      }
      float local = rr;                                   // notebook: beat 1 uses pre_rr[0] == rr
      if (histCount_ > 0) {
        float s = 0.0f;
        for (int i = 0; i < histCount_; i++) s += hist_[i];
        local = s / histCount_;
      }
      hist_[histPos_] = rr;
      histPos_ = (histPos_ + 1) % RR_HIST;
      if (histCount_ < RR_HIST) histCount_++;

      if (qCount_ == QUEUE) { popFront(); dropped_++; }
      BeatFeatures& f = queue_[(qHead_ + qCount_) % QUEUE];
      f.r = r; f.preRr = rr; f.postRr = -1.0f; f.localRr = local;
      f.ratio = rr / (local + 1e-6f);
      qCount_++;
    }
    lastR_ = r; haveLastR_ = true;
  }

  float ring_[RING];
  uint32_t n_ = 0;
  QrsDetector det_;
  BeatFeatures queue_[QUEUE];
  int qHead_ = 0, qCount_ = 0;
  float hist_[RR_HIST];
  int histCount_ = 0, histPos_ = 0;
  bool haveLastR_ = false;
  uint32_t lastR_ = 0;
  uint32_t validStart_ = 0;
  uint32_t dropped_ = 0;
};
// ==== TIBOK_DSP_END ====================================================================

// =======================================================================================
// SAADC sampling at 360 Hz from a timer interrupt
// =======================================================================================
// analogRead() on the mbed core takes a mutex and must not be called from an interrupt,
// and sampling from loop() would stall for the whole inference. So a hardware ticker
// fires every 1/360 s and does a short blocking SAADC conversion (~15 us) into a ring
// that loop() drains at its own pace.
static const uint32_t RAW_RING = 1024;          // 2.8 s of slack while inference runs
static volatile int16_t rawRing[RAW_RING];
static volatile uint32_t rawHead = 0;           // total samples written
static uint32_t rawTail = 0;                    // total samples consumed
static volatile int16_t saadcResult;
static mbed::Ticker sampleTicker;

// =======================================================================================
// TFLite Micro
// =======================================================================================
// Estimated arena need is ~13.6 KB (estimate_tflm_arena); the real figure is printed at
// boot as "arena used". 48 KB leaves generous headroom in the nRF52840's 256 KB RAM.
static const int kTensorArenaSize = 48 * 1024;
alignas(16) static uint8_t tensorArena[kTensorArenaSize];

static const tflite::Model* tflModel = nullptr;
static tflite::MicroInterpreter* interpreter = nullptr;
static TfLiteTensor* ecgInput = nullptr;
static TfLiteTensor* rrInput = nullptr;
static TfLiteTensor* modelOutput = nullptr;
static int int8CutoffCode = 127;                // arrhythmia when raw int8 output >= this

// =======================================================================================
// App state
// =======================================================================================
static EcgConditioner conditioner;
static BeatPipeline pipeline;
static float windowBuf[WINDOW_SIZE];

static bool leadsOff = false;
static uint32_t beatCount = 0;
static uint8_t recentFlags[ALERT_N];
static int recentPos = 0, recentFilled = 0;
static bool alertActive = false;
static bool eventMarkerPending = false;
static bool buttonLast = true;
static uint32_t buttonChangedMs = 0;

// =======================================================================================
// BLE
// =======================================================================================
// Beat characteristic (notify, 16 bytes, little-endian), one packet per classified beat:
//   uint32 beat_index
//   uint32 r_peak_ms        R-peak time, ms since sampling started
//   uint16 pre_rr_ms
//   uint16 post_rr_ms
//   uint8  heart_rate_bpm   60 / pre_rr, capped at 255
//   int8   raw_int8_output  model output code
//   uint8  probability_pct  0-100
//   uint8  flags            bit0 arrhythmia beat, bit1 alert active, bit2 leads off,
//                           bit3 event-marker button pressed, bit4 placeholder constants
// Status characteristic (read/notify, 1 byte): the same flags byte, sent on changes.
struct __attribute__((packed)) BeatPacket {
  uint32_t beatIndex;
  uint32_t rPeakMs;
  uint16_t preRrMs;
  uint16_t postRrMs;
  uint8_t heartRateBpm;
  int8_t rawCode;
  uint8_t probPct;
  uint8_t flags;
};

enum : uint8_t {
  FLAG_ARRHYTHMIA  = 1 << 0,
  FLAG_ALERT       = 1 << 1,
  FLAG_LEADS_OFF   = 1 << 2,
  FLAG_EVENT       = 1 << 3,
  FLAG_PLACEHOLDER = 1 << 4,
};

BLEService tibokService("7b1e0001-5d2a-4c5e-9f1a-3a6e1b7c0d01");
BLECharacteristic beatChar("7b1e0002-5d2a-4c5e-9f1a-3a6e1b7c0d01", BLERead | BLENotify,
                           sizeof(BeatPacket), true);
BLEByteCharacteristic statusChar("7b1e0003-5d2a-4c5e-9f1a-3a6e1b7c0d01", BLERead | BLENotify);
static bool bleOk = false;

// =======================================================================================
// Functions
// =======================================================================================
static void setLed(int pin, bool on) {
  if (pin >= 0) digitalWrite(pin, on ? LOW : HIGH);    // XIAO RGB LED is active-low
}

#if defined(LEDR) && defined(LEDG) && defined(LEDB)
  #define TIBOK_LED_R LEDR
  #define TIBOK_LED_G LEDG
  #define TIBOK_LED_B LEDB
#else
  #define TIBOK_LED_R LED_BUILTIN
  #define TIBOK_LED_G -1
  #define TIBOK_LED_B -1
#endif

static void fatal(const char* msg) {
  sampleTicker.detach();
  while (true) {
    Serial.print("FATAL: ");
    Serial.println(msg);
    setLed(TIBOK_LED_R, true); delay(200);
    setLed(TIBOK_LED_R, false); delay(800);
  }
}

static void saadcInit() {
  NRF_SAADC->ENABLE = SAADC_ENABLE_ENABLE_Disabled;
  for (int i = 0; i < 8; i++) {
    NRF_SAADC->CH[i].PSELP = SAADC_CH_PSELP_PSELP_NC;
    NRF_SAADC->CH[i].PSELN = SAADC_CH_PSELN_PSELN_NC;
  }
  // 12-bit, gain 1/6 with the 0.6 V internal reference -> 0 .. 3.6 V full scale,
  // covering the AD8232's 0 .. 3.3 V output.
  NRF_SAADC->RESOLUTION = SAADC_RESOLUTION_VAL_12bit;
  NRF_SAADC->OVERSAMPLE = SAADC_OVERSAMPLE_OVERSAMPLE_Bypass;
  NRF_SAADC->SAMPLERATE = SAADC_SAMPLERATE_MODE_Task << SAADC_SAMPLERATE_MODE_Pos;
  NRF_SAADC->CH[0].CONFIG =
      (SAADC_CH_CONFIG_RESP_Bypass << SAADC_CH_CONFIG_RESP_Pos) |
      (SAADC_CH_CONFIG_RESN_Bypass << SAADC_CH_CONFIG_RESN_Pos) |
      (SAADC_CH_CONFIG_GAIN_Gain1_6 << SAADC_CH_CONFIG_GAIN_Pos) |
      (SAADC_CH_CONFIG_REFSEL_Internal << SAADC_CH_CONFIG_REFSEL_Pos) |
      (SAADC_CH_CONFIG_TACQ_10us << SAADC_CH_CONFIG_TACQ_Pos) |
      (SAADC_CH_CONFIG_MODE_SE << SAADC_CH_CONFIG_MODE_Pos) |
      (SAADC_CH_CONFIG_BURST_Disabled << SAADC_CH_CONFIG_BURST_Pos);
  NRF_SAADC->CH[0].PSELP = ECG_SAADC_PSELP;
  NRF_SAADC->RESULT.PTR = (uint32_t)(uintptr_t)&saadcResult;
  NRF_SAADC->RESULT.MAXCNT = 1;
  NRF_SAADC->INTENCLR = 0xFFFFFFFF;
  NRF_SAADC->ENABLE = SAADC_ENABLE_ENABLE_Enabled;

  NRF_SAADC->EVENTS_CALIBRATEDONE = 0;
  NRF_SAADC->TASKS_CALIBRATEOFFSET = 1;
  while (!NRF_SAADC->EVENTS_CALIBRATEDONE) {}
  NRF_SAADC->EVENTS_CALIBRATEDONE = 0;
  while (NRF_SAADC->STATUS == (SAADC_STATUS_STATUS_Busy << SAADC_STATUS_STATUS_Pos)) {}
}

static void sampleIsr() {
  NRF_SAADC->EVENTS_STARTED = 0;
  NRF_SAADC->TASKS_START = 1;
  while (!NRF_SAADC->EVENTS_STARTED) {}
  NRF_SAADC->EVENTS_END = 0;
  NRF_SAADC->TASKS_SAMPLE = 1;
  while (!NRF_SAADC->EVENTS_END) {}
  NRF_SAADC->EVENTS_END = 0;
  rawRing[rawHead & (RAW_RING - 1)] = saadcResult;
  rawHead = rawHead + 1;
}

static void modelInit() {
  tflModel = tflite::GetModel(TIBOK_MODEL_DATA);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) fatal("model schema version mismatch");

  // Ops a Keras Conv1D/Dense graph lowers to under the TFLite converter (Conv1D becomes
  // EXPAND_DIMS + CONV_2D + RESHAPE/SQUEEZE, GlobalAveragePooling -> MEAN, sigmoid ->
  // LOGISTIC), plus a few the converter may emit depending on TF version / QAT.
  static tflite::MicroMutableOpResolver<18> resolver;
  resolver.AddConv2D();
  resolver.AddExpandDims();
  resolver.AddReshape();
  resolver.AddSqueeze();
  resolver.AddMean();
  resolver.AddFullyConnected();
  resolver.AddConcatenation();
  resolver.AddLogistic();
  resolver.AddQuantize();
  resolver.AddDequantize();
  resolver.AddRelu();
  resolver.AddPad();
  resolver.AddShape();
  resolver.AddStridedSlice();
  resolver.AddPack();
  resolver.AddAdd();
  resolver.AddMul();
  resolver.AddAveragePool2D();

  static tflite::MicroInterpreter staticInterpreter(tflModel, resolver, tensorArena,
                                                    kTensorArenaSize);
  interpreter = &staticInterpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk)
    fatal("AllocateTensors failed (see message above: missing op or arena too small)");

  // Identify inputs by rank, like _classify_inputs(): ECG is (1, 1250, 1), RR is (1, 4).
  // The converter does not guarantee the Keras input order.
  for (size_t i = 0; i < interpreter->inputs_size(); i++) {
    TfLiteTensor* t = interpreter->input(i);
    if (t->dims->size == 3) ecgInput = t;
    else if (t->dims->size == 2) rrInput = t;
  }
  modelOutput = interpreter->output(0);
  if (!ecgInput || !rrInput) fatal("could not identify ECG / RR model inputs");
  if (ecgInput->dims->data[1] != WINDOW_SIZE) fatal("model ECG input is not 1250 samples");
  if (rrInput->dims->data[1] != N_RR) fatal("model RR input is not 4 features");

  if (modelOutput->type == kTfLiteInt8) {
    // int8_threshold_grid(): prob > T  <=>  code >= cutoff
    float s = modelOutput->params.scale;
    int z = modelOutput->params.zero_point;
    int code = (int)floorf(DEPLOY_THRESHOLD / s + z);
    if ((code - z) * s <= DEPLOY_THRESHOLD) code++;
    if (code < -128) code = -128;
    if (code > 127) code = 127;
    int8CutoffCode = code;
  }

  Serial.print("Model: ");
  Serial.print(USE_QAT_MODEL ? "QAT" : "PTQ");
  Serial.print(" INT8, ");
  Serial.print((unsigned)sizeof(TIBOK_MODEL_DATA));
  Serial.print(" bytes flash, arena used ");
  Serial.print((unsigned)interpreter->arena_used_bytes());
  Serial.print(" / ");
  Serial.print(kTensorArenaSize);
  Serial.println(" bytes");
  Serial.print("ECG in: scale="); Serial.print(ecgInput->params.scale, 8);
  Serial.print(" zp="); Serial.println(ecgInput->params.zero_point);
  Serial.print("RR in:  scale="); Serial.print(rrInput->params.scale, 8);
  Serial.print(" zp="); Serial.println(rrInput->params.zero_point);
  Serial.print("Out:    scale="); Serial.print(modelOutput->params.scale, 8);
  Serial.print(" zp="); Serial.println(modelOutput->params.zero_point);
  Serial.print("Deploy threshold "); Serial.print(DEPLOY_THRESHOLD, 4);
  Serial.print(" -> int8 cutoff code "); Serial.println(int8CutoffCode);
}

static void writeInput(TfLiteTensor* t, int i, float v) {
  if (t->type == kTfLiteInt8) {
    long q = lroundf(v / t->params.scale) + t->params.zero_point;
    if (q < -128) q = -128;
    if (q > 127) q = 127;
    t->data.int8[i] = (int8_t)q;
  } else {
    t->data.f[i] = v;
  }
}

// Returns false if inference failed.
static bool classify(const BeatFeatures& f, float* prob, int* rawCode, bool* arrhythmia,
                     uint32_t* inferUs) {
  for (int i = 0; i < WINDOW_SIZE; i++) writeInput(ecgInput, i, windowBuf[i]);
  const float rr[N_RR] = {f.preRr, f.postRr, f.localRr, f.ratio};
  for (int i = 0; i < N_RR; i++) writeInput(rrInput, i, (rr[i] - RR_MEAN[i]) / RR_STD[i]);

  uint32_t t0 = micros();
  if (interpreter->Invoke() != kTfLiteOk) return false;
  *inferUs = micros() - t0;

  if (modelOutput->type == kTfLiteInt8) {
    int code = modelOutput->data.int8[0];
    *rawCode = code;
    *prob = (code - modelOutput->params.zero_point) * modelOutput->params.scale;
    *arrhythmia = code >= int8CutoffCode;
  } else {
    *prob = modelOutput->data.f[0];
    *rawCode = 0;
    *arrhythmia = *prob > DEPLOY_THRESHOLD;
  }
  return true;
}

static uint8_t statusFlags() {
  uint8_t fl = 0;
  if (alertActive) fl |= FLAG_ALERT;
  if (leadsOff) fl |= FLAG_LEADS_OFF;
  if (eventMarkerPending) fl |= FLAG_EVENT;
  if (!TIBOK_CONSTANTS_FILLED) fl |= FLAG_PLACEHOLDER;
  return fl;
}

static void publishStatus() {
  if (bleOk) statusChar.writeValue(statusFlags());
}

static void updateAlert(bool arrhythmia) {
  recentFlags[recentPos] = arrhythmia ? 1 : 0;
  recentPos = (recentPos + 1) % ALERT_N;
  if (recentFilled < ALERT_N) recentFilled++;
  int k = 0;
  for (int i = 0; i < recentFilled; i++) k += recentFlags[i];
  bool nowActive = k >= ALERT_K;
  if (nowActive && arrhythmia && PIN_BUZZER >= 0) tone(PIN_BUZZER, BUZZER_FREQ_HZ, BUZZER_MS);
  if (nowActive != alertActive) { alertActive = nowActive; publishStatus(); }
}

static void clearAlertHistory() {
  recentPos = recentFilled = 0;
  if (alertActive) { alertActive = false; publishStatus(); }
}

static void handleBeat(const BeatFeatures& f) {
  float prob; int code; bool arr; uint32_t us;
  if (!classify(f, &prob, &code, &arr, &us)) {
    Serial.println("WARN: Invoke failed");
    return;
  }
  beatCount++;
  updateAlert(arr);
  setLed(TIBOK_LED_R, arr);

  uint32_t rMs = (uint32_t)((uint64_t)f.r * 1000 / FS);
  float hr = 60.0f / f.preRr;

#if !SERIAL_PLOTTER_MODE
  // beat,index,r_ms,pre_rr,post_rr,local_rr,ratio,hr_bpm,prob,int8,label,alert,infer_us
  Serial.print("beat,"); Serial.print(beatCount);
  Serial.print(','); Serial.print(rMs);
  Serial.print(','); Serial.print(f.preRr, 3);
  Serial.print(','); Serial.print(f.postRr, 3);
  Serial.print(','); Serial.print(f.localRr, 3);
  Serial.print(','); Serial.print(f.ratio, 3);
  Serial.print(','); Serial.print(hr, 1);
  Serial.print(','); Serial.print(prob, 4);
  Serial.print(','); Serial.print(code);
  Serial.print(','); Serial.print(arr ? "ARRHYTHMIA" : "normal");
  Serial.print(','); Serial.print(alertActive ? 1 : 0);
  Serial.print(','); Serial.println(us);
#endif

  if (bleOk && BLE.connected()) {
    BeatPacket p;
    p.beatIndex = beatCount;
    p.rPeakMs = rMs;
    p.preRrMs = (uint16_t)fminf(65535.0f, f.preRr * 1000.0f);
    p.postRrMs = (uint16_t)fminf(65535.0f, f.postRr * 1000.0f);
    p.heartRateBpm = (uint8_t)fminf(255.0f, hr + 0.5f);
    p.rawCode = (int8_t)code;
    float pc = prob * 100.0f + 0.5f;
    p.probPct = (uint8_t)(pc < 0.0f ? 0.0f : (pc > 100.0f ? 100.0f : pc));
    p.flags = statusFlags() | (arr ? FLAG_ARRHYTHMIA : 0);
    beatChar.writeValue((const uint8_t*)&p, sizeof(p));
  }
  eventMarkerPending = false;
}

static bool readLeadsOff() {
  bool off = false;
  if (PIN_LO_PLUS >= 0 && digitalRead(PIN_LO_PLUS) == HIGH) off = true;
  if (PIN_LO_MINUS >= 0 && digitalRead(PIN_LO_MINUS) == HIGH) off = true;
  return off;
}

static void pollButton() {
  if (PIN_BUTTON < 0) return;
  bool level = digitalRead(PIN_BUTTON);            // pulled up: LOW = pressed
  uint32_t now = millis();
  if (level != buttonLast && now - buttonChangedMs > 30) {
    buttonChangedMs = now;
    buttonLast = level;
    if (level == LOW) {
      eventMarkerPending = true;                   // sent with the next beat packet
      if (PIN_BUZZER >= 0) noTone(PIN_BUZZER);
      clearAlertHistory();                         // acknowledge / silence current alert
      publishStatus();
      Serial.println("event,button");
    }
  }
}

void setup() {
  Serial.begin(115200);
  uint32_t t0 = millis();
  while (!Serial && millis() - t0 < 3000) {}      // runs on battery without USB too

  if (TIBOK_LED_R >= 0) pinMode(TIBOK_LED_R, OUTPUT);
  if (TIBOK_LED_G >= 0) pinMode(TIBOK_LED_G, OUTPUT);
  if (TIBOK_LED_B >= 0) pinMode(TIBOK_LED_B, OUTPUT);
  setLed(TIBOK_LED_R, false); setLed(TIBOK_LED_G, false); setLed(TIBOK_LED_B, false);
  if (PIN_LO_PLUS >= 0) pinMode(PIN_LO_PLUS, INPUT);
  if (PIN_LO_MINUS >= 0) pinMode(PIN_LO_MINUS, INPUT);
  if (PIN_BUTTON >= 0) pinMode(PIN_BUTTON, INPUT_PULLUP);
  if (PIN_BUZZER >= 0) { pinMode(PIN_BUZZER, OUTPUT); digitalWrite(PIN_BUZZER, LOW); }

  Serial.println();
  Serial.println("TIBOK arrhythmia screening - nRF52840");
  if (!TIBOK_CONSTANTS_FILLED)
    Serial.println("WARNING: RR normalisation / threshold are PLACEHOLDERS - fill them in "
                   "from tibok_combined_rr_cnn_summary.json before trusting any output.");

  modelInit();

  if (BLE.begin()) {
    BLE.setLocalName(BLE_DEVICE_NAME);
    BLE.setDeviceName(BLE_DEVICE_NAME);
    BLE.setAdvertisedService(tibokService);
    tibokService.addCharacteristic(beatChar);
    tibokService.addCharacteristic(statusChar);
    BLE.addService(tibokService);
    statusChar.writeValue(statusFlags());
    BLE.advertise();
    bleOk = true;
    Serial.println("BLE advertising as \"" BLE_DEVICE_NAME "\"");
  } else {
    Serial.println("WARN: BLE init failed - continuing with Serial output only");
  }

  conditioner.begin(USE_HIGHPASS_0P5HZ, NOTCH_HZ, USE_LOWPASS_40HZ);
  pipeline.begin();
  leadsOff = readLeadsOff();

  saadcInit();
  sampleTicker.attach(&sampleIsr, std::chrono::microseconds(1000000 / FS));  // 2777 us
  Serial.println("Sampling at 360 Hz. CSV columns:");
  Serial.println("beat,index,r_ms,pre_rr_s,post_rr_s,local_rr_s,rr_ratio,hr_bpm,prob,int8,label,alert,infer_us");
}

void loop() {
  if (bleOk) BLE.poll();
  pollButton();

  bool off = readLeadsOff();
  if (off != leadsOff) {
    leadsOff = off;
    // Electrode contact changed: the signal is garbage across the transition, so restart
    // filtering + detection and let it settle again.
    conditioner.reset();
    pipeline.reset();
    clearAlertHistory();
    setLed(TIBOK_LED_B, leadsOff);
    Serial.println(leadsOff ? "status,leads_off" : "status,leads_on");
    publishStatus();
  }

  // Drain the ADC ring.
  uint32_t head = rawHead;
  if (head - rawTail > RAW_RING) {                 // loop() fell too far behind
    Serial.println("WARN: ADC overrun, restarting detection");
    rawTail = head;
    conditioner.reset();
    pipeline.reset();
  }
  while (rawTail != head) {
    int16_t raw = rawRing[rawTail & (RAW_RING - 1)];
    rawTail++;
    float mv = raw * (3600.0f / 4096.0f);          // 12-bit, 3.6 V full scale -> mV
    float x = leadsOff ? 0.0f : conditioner.step(mv);
    pipeline.push(x);
#if SERIAL_PLOTTER_MODE
    Serial.println(x, 2);
#endif
  }

  // Classify at most one beat per pass so BLE and the button stay responsive.
  BeatFeatures f;
  if (!leadsOff && pipeline.popReady(&f, windowBuf)) {
    setLed(TIBOK_LED_G, true);
    handleBeat(f);
    setLed(TIBOK_LED_G, false);
  }
}
