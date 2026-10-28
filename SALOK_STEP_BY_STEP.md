# SALOK — Step-by-Step Plan

Today is **Oct 28, 2026**. Entry deadline: **Nov 2, 11:59 PM**. That is 5 days. Phase 1 gets a credible, evidence-backed entry submitted; phases 2–4 are the build and pilot if you are shortlisted (shortlist announced about Nov 16 per a web search; confirm).

**Suggested roles (one person can hold two):** **Lead/Writer** (proposal, deadline, checklist) · **Data/AI** (photos, labels, model) · **Hardware** (parts, bench tests) · **Partner** (barangay, adviser, approvals).

## Phase 1 — Submit a strong entry (Oct 28 – Nov 2)

### Day 1 — Wed Oct 28: lock the plan and the partner
1. **Lead:** read `samsung_sft2026_proposal_salok.md` and `SALOK_HANDOFF.md`. Agree on the name and the one-sentence pitch.
2. **Partner:** tell the adviser and school head the plan. Ask which barangay and estero are closest and safe to visit.
3. **Partner:** message or visit the **barangay captain / sanitation or environment officer**. Ask for (a) permission to photograph floating trash at a creek stretch, (b) a signed letter of support, and (c) a named focal person for weekly bin emptying. A short letter is enough: *"[Barangay] supports the QCSHS team's SALOK pilot at [estero], and designates [name] to empty the bin weekly."*
4. **Hardware:** make a parts list with real prices from Shopee/Lazada and local electronics shops. Replace the estimates in the budget table.

### Day 2 — Thu Oct 29: collect the evidence
5. **Data/AI:** visit the site **with an adult**. Do not enter the water; photograph from the bank or a bridge.
6. Take photos of floating and bank trash: bottles, sachets, bags, foam, cups, and water hyacinth. Aim for **at least 200–300 photos** across different times and angles (more is better). Record the **site, date, time, weather**, and note hyacinth cover and flow.
7. **Data/AI:** keep faces and houses out of frame. Photograph the water surface only.
8. **Hardware:** order the **Stage 1 parts only** (ESP32-S3 camera board with PSRAM, microSD, enclosure; about PHP 1,800). Do not buy motor or conveyor parts yet. If shipping will not arrive in time, borrow a board from school.

### Day 3 — Fri Oct 30: label and train a first model
9. **Data/AI:** label the photos with a free tool (e.g., Label Studio, CVAT or Roboflow **[verify current free-tier limits]**). Use classes: `pet_bottle, sachet, plastic_bag, foam, cup_other, vegetation`. Have a second person spot-check about 10% of labels.
10. Train a small detection model on a laptop or Colab. A beginner-friendly path for ESP32 boards is a platform such as **Edge Impulse** or TensorFlow Lite for Microcontrollers **[verify that the board and model fit]**. Hold out photos from a different time or spot as the **test set**.
11. Save a **screenshot of a few correct and incorrect detections** and the precision/recall numbers. Report them honestly, even if low. "First model, [N] photos, precision [x]" is credible.

### Day 4 — Sat Oct 31: bench test and prototype photo
12. **Hardware:** if parts arrived, run the camera on the ESP32-S3 and log a few detections to the microSD card. Take a **photo of the bench setup**.
13. **Hardware:** measure **real power draw** with a multimeter or USB meter while the camera runs on its duty cycle. Write the real number into the proposal in place of the planning arithmetic.
14. **Hardware:** draw a labelled sketch of the boom, deflector, ramp, arm and bin (Figure 1), and a block diagram (Figure 2).
15. **Lead:** fill every `[BRACKET]` that you now have an answer for. Leave the rest honestly blank or reword them as targets.

### Day 5 — Sun Nov 1: verify and format
16. **Lead:** open every **[VERIFY]** item and reference. Confirm Meijer et al. (2021), RA 11898, the barangay count, HydroSentinel's details and the Manila Bulletin headline. Correct anything wrong, and delete any claim you cannot confirm.
17. **Lead:** compare the proposal against the **official entry template** from the Samsung Drive folder (`2026 SFT Entry Templates`). Match its fields exactly.
18. **Lead:** trim to under **3,000 words**. Convert to the required format (Word or six-slide PPT) and export a **PDF under 40 MB**.
19. **Adviser:** read and sign off.

### Day 6 — Mon Nov 2: submit early
20. **Lead:** submit **well before 11:59 PM**. Do not wait for the last hour; upload sites fail near deadlines.
21. **Lead:** save the confirmation and the submitted PDF.

## Phase 2 — If shortlisted: build in stages (about Nov 16 – Dec 5)

Use **decision gates**. Do not spend the next stage's money until the previous stage passes.

**Stage 1 — bench (about PHP 1,800).**
22. Finish the model with more photos. *Gate: precision and recall on a held-out set meet your target (e.g., ≥ 0.85); if not, collect more or reduce classes.*
23. Confirm the model fits and runs on the ESP32-S3. Measure power again.

**Stage 2 — passive trap (about PHP 2,500).**
24. Build the boom from reused PET bottles and bamboo, add the deflector, bar screen, ramp, bin and post. Install the solar panel and battery.
25. Run a **baseline week** before installing: hand-net count at the site, plus hyacinth cover and flow.
26. Install with the barangay focal person and an adult. *Gate: the boom holds through rain events, and weekly device counts are within ±15% of hand counts.*

**Stage 3 — arm and sensor (about PHP 1,350).**
27. Build the **wet bench rig** first: test the arm with real hyacinth, estero silt and a little cooking oil. Record stall current, slip and lifts per run.
28. Set the shear pin, current threshold and retry limit from those numbers, then fit the level sensor and jam protection. *Gate: the arm lifts debris on solar power alone at the target jam rate.*

## Phase 3 — Present and pilot (Dec – Feb)
29. **Dec 7 (if confirmed):** present model metrics, baseline data and Stage 2 progress. Show a real photo and a real number, not only slides.
30. Run the pilot: weekly bin emptying, weigh-in and hand count, report to the barangay, and upload the anonymized CSV.
31. Each week, write one paragraph: what worked, what failed, what you changed.

## Phase 4 — Replicate (by March 2027)
32. Publish a free English/Filipino build guide and the open dataset.
33. Help [1–2] other barangays or schools build one. Get each site's agreement in writing. Until a second site copies it, describe reach as a plan.

## Rules to keep
- **Never claim a result you have not measured.** Targets are targets.
- **Safety first:** no student enters the water; adults handle emptying; guard the arm; barangay and school approval before installing anything.
- **Passive fallback:** if the arm fails, the boom, bin and camera still deliver the data.
