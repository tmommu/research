# SFT 2026 — Proposal: SAGIP (PHP 6,000 build)

**Theme:** Environmental Sustainability through Technology
**Deadline:** Nov 2, 2026, 11:59 PM. Format: Word (≤3,000 words / 7 pages) or PPT (≤6 slides), exported as a PDF under 40 MB.

**How to read this draft.** `[BRACKETS]` are blanks only the team can fill. **[VERIFY]** marks facts from memory that must be checked against the primary source. Prices are estimates to confirm locally. Targets are targets, not results. The power arithmetic uses stated assumptions that bench tests must replace.

---

**Entrant's school:** Quezon City Science High School  **Adviser:** [NAME]
**Team (max 4):** [NAMES, Grade 10]

## Entry title

**SAGIP: A PHP 6,000 Solar-Powered Estero Guardian that Lifts Plastic Out of the Water and Counts Every Item as Evidence for Producer Accountability**

*(Sagip = "to rescue" in Filipino. Rename if the team prefers.)*

**One-sentence pitch.** SAGIP removes floating plastic from a creek and counts every item with a camera, giving the barangay the evidence the law needs to hold packaging makers accountable, and, as a bonus, warns when the channel is about to block.

## Project description (three sentences, for official write-ups)

SAGIP is a low-cost, solar-powered unit in which a floating boom guides surface plastic to the bank, a small camera-triggered sweeper arm lifts it into a bin, and an ESP32 camera with an on-device AI model counts every item by plastic type and, where legible, by brand. Barangay officials get a weekly report of what was removed and who made it, with no internet and no images of people, plus a secondary water-level alert when debris and rising water threaten to block the channel. Built for PHP 6,000 from local and upcycled parts, its anonymized results join an open dataset so many barangays can build the evidence to hold producers accountable.

## 1. What problem are you trying to solve?

Plastic reaches the sea through creeks and esteros. Published river-emission studies rank Philippine rivers among the largest sources of ocean plastic **[VERIFY: Meijer et al., 2021, Science Advances]**, and Metro Manila's waterways, including the Pasig and Tullahan systems, carry much of it. Single-use sachets, bags and cups are dominant items in cleanups **[VERIFY: local audits]**.

Two gaps keep the problem going:

1. **Removal is manual and invisible.** Cleanups happen on schedule and the trash is weighed in bulk. Nobody records what was in it, so the same items return.
2. **There is no continuous brand-level data.** The Extended Producer Responsibility Act of 2022 (RA 11898) makes large companies responsible for recovering plastic packaging **[VERIFY: scope]**, but enforcement needs evidence of *which* packaging ends up in waterways. Brand audits exist, but they are periodic, manual and mostly land-based. The government is expanding estero trash traps and says plastic-recovery audits could check EPR compliance (Manila Bulletin, 2026).

**What is missing is a continuous, low-cost record from the waterway itself that one barangay can run.** A secondary problem sits on the same creek: debris-choked channels flood neighbourhoods **[VERIFY: MMDA/DPWH reports]**, and barangays learn a channel is blocked only when it floods.

## 2. What do you want to achieve?

**Goal:** lift floating plastic out of one estero in our community and generate continuous, student-collected, item-level waste data that a barangay can hand to the LGU, with a design any barangay can copy for about PHP 6,000.

**Research question:** can a PHP 6,000 on-chip counter match a trained hand audit within ±15%, and does continuous counting reveal rain-driven plastic pulses that weekly audits miss?

**Core objectives (SMART)**

1. **Clean.** In an [8]-week pilot at [ESTERO SITE], lift at least [TARGET] kg of floating debris out of the water, with a measured **capture rate** of at least [X]% of the floating debris reaching the boom, compared against a **baseline week** before installation.
2. **Classify.** By Nov 20, 2026, train an on-device model for [5] plastic classes plus a **vegetation** class (PET bottle, sachet/foil pouch, bag, foam, cup/other; hyacinth), with at least [0.85] precision and recall on photos from locations *not used in training*.
3. **Count accurately.** Weekly device counts within ±15% of a hand count of the bin's contents.
4. **Report and share.** A one-page weekly barangay report (items, types, estimated weight, top legible brands) and an anonymized open CSV with a data dictionary.
5. **Replicate.** By March 2027, publish a free English/Filipino build guide and help [1–2] other barangays or schools build one for no more than about PHP 6,000.

**Secondary objective**

6. **Warn.** An ultrasonic level sensor logs water level against rainfall and bin fullness and raises a "channel nearly blocked" alert; we report the warning time it gave in the [N] events we observe, whatever the result.

## 3. Who will benefit?

- **Primary:** residents of [BARANGAY/PUROK] along [ESTERO] and its environmental/sanitation officers, who get a cleaner waterway and data they have never had.
- **Secondary:** the LGU/DENR solid-waste offices, who can use item-level evidence; neighbouring barangays who can copy the design; students, who become the community's citizen scientists.
- **Wider:** downstream communities and fisherfolk affected by plastic reaching Manila Bay.

## 4. How did you come up with your proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Plastic in esteros won because we can reach one, measure it weekly, and RA 11898 has just made the data useful.

**What already exists, and how SAGIP differs.**

| Existing approach | What it does | What it leaves open |
|---|---|---|
| Cameras and deep learning for river plastic (van Lieshout et al., 2020) | Counts floating plastic from bridge-mounted cameras, tested in Jakarta | Monitors only; removes nothing; needs a bridge and offline analysis |
| Low-cost robotic boats (HydroSentinel, 2026) | Detect and collect plastic with a small onboard model | A moving vehicle needing radio, charging and an operator, not a fixed community-run unit |
| Estero trash traps and clean-up programs (Manila Bulletin, 2026) | Remove plastic at scale | Record only bulk weight, not what the plastic is |
| Waste and brand audits (Break Free From Plastic; Greenpeace) | Name the brands behind plastic waste | Periodic, manual, mostly land-based, volunteer-dependent |

**What is new.** The parts are not new; the combination is. SAGIP is a fixed, solar-powered unit that physically lifts plastic out of a creek, counts it by type on the chip, and produces open item-level data for EPR evidence. The camera is both the *counter* and the *trigger* for the arm, so one inexpensive chip produces evidence and saves energy. We did not find a published system combining all of these at a barangay-affordable cost, though our search was limited. SAGIP is the continuous, community-owned, low-cost counterpart of the brand audits NGOs already run by hand.

## 5. How will your tech solution work?

> **STEM map:** *Physics* (buoyancy, flow, solar energy budget, ultrasonic ranging, torque) · *Math/Statistics* (precision, recall, count error, sampling) · *Computer Science* (object detection, INT8 quantization, fault-tolerant control) · *Engineering* (floating structure, lever arm, jam protection, weatherproofing) · *Environmental Science* (waterway pollution, EPR policy).

SAGIP **traps, lifts, counts and reports.**

**Trap (Physics, Engineering).** A V-shaped boom of reused PET bottles and bamboo guides surface debris toward the bank, where it meets a bar screen at the foot of a sloped mesh ramp. A wide-spaced deflector ahead of the intake pushes large water-hyacinth mats past the unit. The estero's current does the herding, so the boom needs no energy. A float-and-time test sets the boom angle.

**Lift (Engineering).** A small geared DC motor, mounted high above the flood line, turns a rake arm that sweeps debris up the ramp into a covered bin. It runs only when the camera sees *plastic* and not vegetation, in short bursts. The drive includes a **sacrificial shear pin** (spares kept on site) so a shock load breaks a PHP 5 bolt, not the gearbox. The arm is guarded, with a stop switch and a lockout during emptying; students never enter the water, and adults empty the bin weekly.

**Jam protection (Computer Science, Engineering).** The ESP32 reads motor current with a dedicated sensor, ignores the start-up surge, and trips on sustained high current. A magnet and Hall sensor on the arm shaft confirm it actually moves, which catches slipping on greasy surfaces. On a jam it stops, pauses, reverses briefly and retries at most three times, then locks out and alerts the barangay, so it never burns out the motor in endless retries. A run-time budget per hour limits heating, and the motor driver's enable line defaults to off, so a crashed ESP32 cannot leave the motor running.

**See and count (Computer Science, Math).** An ESP32-S3 camera on a post looks *down at the water surface only*, so no faces or houses are in frame. A compact object-detection model, **quantized to INT8** and run with TensorFlow Lite for Microcontrollers, classifies each item. The camera views a pocket one to two metres away, so items are large in frame and a small model on an ESP32-S3 with PSRAM is realistic; our Stage 1 gate tests it before we build more. Training photos come from our own collections of real trash on the estero bank, labelled by students and checked by the adviser. Detections increment class counters on a microSD card. Each week students hand-count and weigh the bin's contents; a per-class average weight converts counts to kilograms, and the hand count is our accuracy test. A hood and hydrophobic cover protect the lens, and a drop in image sharpness flags fouling.

**Report (Design).** The ESP32 hosts an offline Wi-Fi page a phone can read. A script produces the weekly report and the CSV. Brand names that a person can read from stored photos are tallied by a student volunteer; the AI flags and crops likely labels, because automated brand reading is not yet reliable.

**Audit-grade data (Math, Computer Science).** Each record stores class, time, water level and an image hash in an append-only log. Each week the counter is checked against a hand audit that uses the same categories as NGO brand audits, so results are comparable and hard to dispute. Plotting counts against rainfall and level shows whether plastic arrives in rain-driven pulses, which lets the barangay time its emptying and clean-ups.

**Secondary: warn (Physics).** A waterproof ultrasonic sensor on the post measures the distance to the water surface against a painted staff gauge and raises an alert (LED and report flag) when the level rises fast or the bin is nearly full. Above a set level, the arm stops.

**Power budget (Physics, Math).** *Planning arithmetic, to be replaced by bench measurements:* electronics, duty-cycled, about 0.25 W, or about 6 Wh/day; arm, about 5 W for 10 s per lift at 20 lifts/day, about 0.3 Wh/day; a 10 W panel at about 3 effective sun-hours and 60% efficiency, about 18 Wh/day; storage of two 18650 cells, about 18 Wh. The margin is thin on cloudy days, so the device lengthens its capture interval when the battery is low, and the motor is locked out under a minimum battery voltage.

**What it will and will not clean.** SAGIP lifts **light floating debris** that reaches the boom: bottles, sachets, bags, foam and cups, in small batches. It does not lift heavy or tangled items, hyacinth mats, sunken waste, sediment, oil or dissolved pollution, and it cleans only the stretch upstream of the boom. We report the measured capture rate rather than claiming the estero is "clean".

*Figure 1: boom, ramp and arm layout. Figure 2: block diagram (boom → ramp and arm → bin; camera → model → counts → report; level sensor → alert). Figure 3: sample detections.*

## 6. How will you implement this?

**Staged build with decision gates.** We never commit the next stage's money before the previous stage works.
1. **Stage 1 (about PHP 1,800): bench.** ESP32-S3 camera, microSD, enclosure; train and test the model on our photos; measure real power draw. *Gate: held-out precision and recall meet the target.*
2. **Stage 2 (about PHP 2,500): passive trap.** Boom, deflector, bar screen, ramp, bin, post and solar power installed at the estero. *Gate: the boom holds through [N] rain events and weekly counts are within ±15% of hand counts.*
3. **Stage 3 (about PHP 1,350): arm and sensor.** Motor, driver, jam protection, level sensor. *Gate: a wet bench rig (real hyacinth, estero silt, a little cooking oil) first shows stall current, slip and lifts per run; then the arm lifts debris on solar power alone at the target jam rate.*
4. Contingency PHP 350.

**Budget: PHP 6,000 (estimates; confirm local prices).**

| Item | PHP |
|---|---|
| ESP32-S3 camera board | 1,300 |
| microSD card | 200 |
| Sealed enclosure, glands, desiccant | 300 |
| Waterproof ultrasonic level sensor | 350 |
| Small solar panel (about 6–10 W) | 600 |
| Charge controller, 2× 18650 cells, holder, boost converter | 700 |
| Rope, net, zip ties (bottles and bamboo reused) | 450 |
| Anchor, post, clamps, concrete | 350 |
| Bin (reused) and painted staff gauge | 150 |
| Wiring, fuse, switch, connectors | 250 |
| Small geared DC motor (6–7.4 V) | 500 |
| Motor driver | 200 |
| Current and motion sensing | 150 |
| Ramp, rake arm, shaft, bar screen, spare shear pins (recycled plastic, bolts) | 150 |
| **Subtotal** | **5,650** |
| Contingency | 350 |
| **Total** | **6,000** |

**Evidence we will show before Nov 2:** [N] labelled trash photos and a first detection screenshot; a photo of the bench prototype; one measured power figure; and the barangay's signed approval letter. *(Fill in only what exists.)*

**Timeline**
| Dates | Milestone |
|---|---|
| Oct 28 – Nov 2 | Site visit and barangay letter; photograph and label starter dataset; bench power test; submit |
| Nov 3 – Nov 20 | Stage 1 gate; baseline week at the estero (also record hyacinth cover and flow) |
| Nov 16 – Dec 5 | Refine with Samsung coaches (if shortlisted) |
| Dec 7 | Present model metrics, baseline data and Stage 2 progress |
| Dec – Feb | Stages 2 and 3; full pilot with weekly hand-count validation |
| By Mar 2027 | Build guide published; 1–2 more sites; larger conveyor if funded |

**Site choice.** We pick a stretch with moderate flow and accessible banks, and record hyacinth cover and silt as variables, not hide them.

**Maintenance agreement.** A one-page memorandum names the barangay focal person who empties the bin weekly, the student team that clears jams, cleans the lens and uploads the data, and the school adviser who signs off the checklist: empty the bin, clear the bar screen and deflector, check the arm, ramp and shear pin, wipe the lens, check the mooring, read the battery, upload the CSV. It fits alongside the barangay's existing estero clean-up work **[VERIFY: current DENR/LGU programs]**. *[Confirm with the barangay before submission.]*

**Typhoon and theft plan.** A quick-release line and a rule to retrieve the electronics before a typhoon signal; the camera and controller mounted discreetly high on the post; barangay tanod informed.

**Risks and mitigation**
- *Hyacinth mats:* deflector, vegetation class that inhibits the arm, daily screen clearing, and honest reporting that heavy mats may pause operation.
- *Arm jams, slip or burnout:* shear pin, current and motion sensing, bounded retries, heat budget, fail-safe driver.
- *Oil and silt:* motor and bearings mounted high, sealed bearings with marine grease, stainless fasteners, hooded lens.
- *Model fails in new light or water:* collect across times of day and weather; report held-out scores; keep the manual count.
- *Arm fails entirely:* the boom, bar screen and bin still trap passively and the camera still counts, so the data pilot is not at risk.
- *Over-claiming:* targets stated as targets; we report what was measured and what failed.

## 7. Impact and long-term vision

**Why this matters.** NGOs already prove, by hand, which companies make the most plastic in Philippine waste, and RA 11898 now makes producers responsible for recovering it **[VERIFY]**. What is missing is proof that is continuous, cheap and owned by the community beside the water. SAGIP makes that proof continuous at the waterway and lifts some of the plastic out while it does so. One unit's kilograms are small; its significance is that the design is cheap enough for a thousand barangays to copy and its data is open enough to add up.

**What we will measure (our pilot).**
1. [TARGET] kg of floating debris lifted, with weekly weigh-ins, a measured capture rate and a baseline comparison.
2. Model precision and recall ≥ [0.85] on held-out locations; weekly count error within ±15% of hand counts.
3. A weekly report series and an item-level audit of what the estero carried.
4. (Secondary) a logged record of level alerts and the warning time they gave.

**What we will show about replication.** A free English/Filipino build guide and at least [1–2] additional sites by March 2027 at about PHP 6,000 each, sharing the same open data format. Until a second barangay copies it, we describe SAGIP's reach as a plan, not a result.

**Sustainability.** The barangay runs it with local parts, solar power and a one-page checklist under a named maintenance agreement; no subscription, server or internet is needed. The dataset and model are open so other barangays can retrain on their own waste, and reused floats and bamboo keep replacement cheap.

**Long-term vision.** A student-built, barangay-owned network of SAGIP units along connected esteros, feeding an open dataset that shows where plastic enters the waterway, which products dominate, and whether EPR commitments are changing what the water carries. Each added barangay makes every other unit's data more valuable. The pilot proves the method at one creek; we claim no more.

**Key takeaway.** The Philippines already knows who makes the plastic; SAGIP makes the proof continuous, cheap and community-owned, and lifts some of the plastic out while it does it.

## References **[open each source and confirm details before submitting]**

Break Free From Plastic / GAIA (2019). *Plastics Exposed: How Waste Assessments and Brand Audits are Helping Philippine Cities Fight Plastic Pollution*. no-burn.org.
Greenpeace International. *Nestlé and Unilever identified as top plastic polluters in Philippines waste audits.* greenpeace.org.
HydroSentinel (2026). An IoT-enabled autonomous surface vehicle for dual-scale riverine plastic detection and remediation. *ScienceDirect*. **[add authors and journal details]**
Manila Bulletin (Aug 24, 2026). Report on government estero trash traps and EPR audits. **[add headline and byline]**
Meijer et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances*. **[VERIFY]**
Republic Act 11898, Extended Producer Responsibility Act of 2022. **[VERIFY]**
van Lieshout, C., et al. (2020). Automated river plastic monitoring using deep learning and cameras. *Earth and Space Science*, 7, e2019EA000960.
[A TinyML or object-detection source on low-power microcontrollers].

---

## How this maps to the rubric (self-assessment, not official)

| Criterion (weight) | How SAGIP earns it |
|---|---|
| Design Innovation (20%) | A prior-art table shows what exists; the novelty is the combination: a fixed, low-cost unit that lifts plastic, counts it on-chip, and feeds open EPR-ready data, with the camera as both counter and trigger. |
| Relevance to the Community (20%) | A real estero, a barangay partner and letter, a current law, and a gap officials say they want filled. |
| Feasibility (20%) | Staged build with decision gates, an itemized PHP 6,000 budget, power arithmetic, a wet bench test, jam protection, and a passive fallback. |
| STEM Integration (15%) | Explicit STEM map across physics, statistics, computer science, engineering and environmental science. |
| Sustainability (15%) | Solar, reused parts, a written maintenance agreement, spare shear pins, a typhoon plan, an open replicable design. |
| Clarity (10%) | One pitch sentence, two core jobs (lift and prove), flood warning clearly secondary. |

## Pre-submission checklist

- [ ] Choose the real estero; get the **signed barangay approval and maintenance memorandum**; fill `[SITE]` and `[BARANGAY]`.
- [ ] Photograph and label real trash and capture a sample detection image.
- [ ] Bench-measure the real power draw and replace the planning arithmetic.
- [ ] Take a photo of the bench prototype; list in "Evidence" only what exists.
- [ ] Verify every **[VERIFY]** fact; confirm every reference's details.
- [ ] Confirm the ESP32-S3 board can run your model (RAM/PSRAM) before buying.
- [ ] Replace budget estimates with real local prices; keep the total within PHP 6,000.
- [ ] Trim to under 3,000 words, check against the official entry templates (the Drive connector could not list them) and export a PDF under 40 MB.
