# Samsung Solve for Tomorrow 2026 Philippines: Entry Proposal

**Entrant's school:** Quezon City Science High School
**Adviser:** [NAME]
**Team members:** [NAMES, Grade 10]
**Theme:** Environmental Sustainability through Technology

## Entry title

**SAGIP: A PHP 6,000 Solar-Powered Estero Guardian That Lifts Floating Plastic from the Water and Counts Every Item as Evidence for Producer Accountability**

## Project description

SAGIP is a low-cost, solar-powered unit in which a floating boom guides surface plastic toward the bank, a camera-triggered sweeper arm lifts it into a bin, and an ESP32-S3 camera running an on-device model counts each item by plastic type and, where legible, by brand. Barangay officials receive a weekly report of what was removed and who produced it, with no internet connection and no images of people, along with a secondary water-level alert for impending channel blockage. Built from local and upcycled parts for PHP 6,000, the unit contributes anonymized records to an open dataset that many barangays can extend to build evidence for producer accountability.

## 1. What problem are you trying to solve?

Plastic reaches the sea through creeks and esteros. Published river-emission estimates place Philippine rivers among the largest sources of ocean plastic **[VERIFY: Meijer et al., 2021]**, and the waterways of Metro Manila, including the Pasig and Tullahan systems, carry a substantial share. Single-use sachets, bags and cups dominate cleanup collections **[VERIFY: local audits]**.

Two gaps allow the problem to persist. Removal is manual and largely unrecorded. Cleanups follow a schedule, the collected waste is weighed in bulk, and nothing is kept about its composition, so the same items return. Evidence at the level of the individual product is also scarce. The Extended Producer Responsibility Act of 2022 (RA 11898) obliges large companies to recover plastic packaging **[VERIFY: scope and thresholds]**, yet enforcement depends on showing which packaging actually reaches waterways. Brand audits exist, but they are periodic, labor-intensive and conducted mostly on land (Break Free From Plastic, 2019). The government is expanding estero trash traps and has indicated that plastic-recovery audits could be used to check compliance with EPR (Manila Bulletin, 2026).

What is lacking is a continuous, inexpensive record taken at the waterway itself and operable by a single barangay. A related hazard shares the same channel. Debris-choked creeks contribute to flooding in low-lying neighborhoods **[VERIFY: MMDA and DPWH reports]**, and communities learn of a blockage only after water has risen.

## 2. What do you want to achieve?

**Goal.** To lift floating plastic from one estero in our community and to generate continuous, student-collected, item-level data that the barangay can present to the local government, using a design that other barangays can copy for about PHP 6,000.

**Research question.** Can a PHP 6,000 on-chip counter match a trained hand audit within 15 percent, and does continuous counting reveal rain-driven pulses of plastic that weekly audits miss?

**Objectives**

1. **Clean.** Over an [8]-week pilot at [ESTERO SITE], lift at least [TARGET] kg of floating debris from the water, achieve a measured capture rate of at least [X] percent of the floating debris reaching the boom, and compare results against a baseline week recorded before installation.
2. **Classify.** By November 20, 2026, train an on-device model on [5] plastic classes plus a vegetation class (PET bottle, sachet or foil pouch, bag, foam, cup or other, and hyacinth), reaching precision and recall of at least [0.85] on photographs from locations excluded from training.
3. **Count.** Keep weekly device counts within 15 percent of a hand count of the bin contents.
4. **Report and share.** Produce a one-page weekly report for the barangay (items, types, estimated weight, leading legible brands) and publish an anonymized open dataset with a data dictionary.
5. **Replicate.** By March 2027, release a free English and Filipino build guide and assist [1 to 2] other barangays or schools in building a unit for about PHP 6,000.
6. **Warn (secondary).** Log water level against rainfall and bin fullness with an ultrasonic sensor, raise an alert when blockage appears imminent, and report the warning time achieved across [N] observed events, whatever the outcome.

## 3. Who will benefit from this project?

The primary beneficiaries are the residents of [BARANGAY AND PUROK] along [ESTERO] and the barangay's environmental and sanitation officers, who gain a cleaner waterway and data they have not had before. The local government's solid-waste offices and the DENR can use the item-level records as evidence. Neighboring barangays can adopt the design, and students become participants in citizen science. Communities and fisherfolk downstream, whose catch and shoreline are affected by plastic reaching Manila Bay, benefit indirectly.

## 4. How did you come up with your proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Plastic in esteros ranked highest because a creek is within reach of our school, weekly measurement is practical, and RA 11898 has made item-level data useful for enforcement.

A review of existing approaches showed four families of work, summarized below.

| Existing approach | Contribution | Remaining gap |
|---|---|---|
| Cameras with deep learning for river plastic (van Lieshout et al., 2020) | Counts floating plastic from bridge-mounted cameras, tested in Jakarta | Monitors only and removes nothing. Requires a bridge and offline analysis. |
| Low-cost robotic boats (HydroSentinel, 2026) | Detect and collect plastic with a small onboard model | A moving vehicle that needs radio, charging and an operator. |
| Estero trash traps and cleanup programs (Manila Bulletin, 2026) | Remove plastic at scale | Record bulk weight only. |
| Waste and brand audits (Break Free From Plastic, 2019, Greenpeace) | Name the brands behind plastic waste | Periodic, manual, mostly land-based, and dependent on volunteers. |

None of these components is new. The combination is. SAGIP is a fixed, solar-powered unit that lifts plastic out of a creek, classifies it on the chip, and produces open item-level data suitable for EPR evidence. The camera serves as both counter and trigger for the arm, so a single inexpensive chip yields evidence and conserves energy. Our search did not locate a published system that joins these functions at a cost a barangay can bear, although the search was limited in scope. In effect, SAGIP is a continuous, community-owned and low-cost counterpart to the brand audits that NGOs now conduct by hand.

## 5. How will your tech solution work?

The design draws on physics (buoyancy, flow, solar energy budgeting, ultrasonic ranging, torque), mathematics and statistics (precision, recall, count error, sampling), computer science (object detection, INT8 quantization, fault-tolerant control), engineering (floating structures, lever mechanisms, jam protection, weatherproofing) and environmental science (waterway pollution, EPR policy). The unit operates in four steps: trap, lift, count and report.

**Trap.** A V-shaped boom of reused PET bottles and bamboo directs surface debris toward the bank, where it meets a bar screen at the foot of a sloped mesh ramp. A wide-gapped deflector placed upstream pushes large mats of water hyacinth past the intake. The estero's own current supplies the energy for herding. A float-and-time test sets the boom angle.

**Lift.** A small geared DC motor, mounted above the flood line, turns a rake arm that sweeps debris up the ramp into a covered bin. The arm runs in short bursts and only when the camera detects plastic rather than vegetation. A sacrificial shear pin, with spares kept on site, protects the gearbox from shock loads. A guard, a stop switch and a lockout during emptying protect people. Students do not enter the water, and adults empty the bin weekly.

**Jam protection.** The ESP32-S3 reads motor current through a dedicated sensor, disregards the start-up surge, and trips on sustained high current. A magnet and Hall sensor on the arm shaft confirm that the arm is moving, which exposes slippage on greasy surfaces. After a jam the controller stops, pauses, reverses briefly and retries at most three times before locking out and alerting the barangay. An hourly run-time budget limits heating, and the driver's enable line defaults to off so that a crashed controller cannot leave the motor running.

**Count.** An ESP32-S3 camera on a post looks down at the water surface only, keeping faces and houses out of frame. A compact object-detection model, quantized to INT8 and executed with TensorFlow Lite for Microcontrollers, classifies each item. Because the camera views a pocket one to two meters away, items appear large in the frame, and a small model on an ESP32-S3 with PSRAM is realistic. The first build stage tests this before further expense. Training photographs come from our own collection of trash along the estero bank, labelled by students and checked by the adviser. Detections increment class counters on a microSD card. Each week, students hand-count and weigh the bin contents, and a per-class average weight converts counts to mass. The hand count serves as the accuracy test. A hood and a hydrophobic cover protect the lens, and a drop in image sharpness flags fouling.

**Report.** The controller hosts an offline Wi-Fi page that a phone can read, and a script compiles the weekly report and the open dataset. Brand names legible in stored photographs are tallied by a student volunteer, with the model flagging and cropping probable labels, since automated brand reading remains unreliable. Each record carries class, time, water level and an image hash in an append-only log. The weekly hand audit uses the same categories as NGO brand audits, which makes the results comparable. Plotting counts against rainfall and water level shows whether plastic arrives in rain-driven pulses, and the barangay can then time its emptying and cleanups accordingly.

**Warning (secondary).** A waterproof ultrasonic sensor on the post measures the distance to the water surface against a painted staff gauge. The unit raises an alert through an LED and a report flag when the level rises quickly or the bin nears capacity, and the arm stops above a set level.

**Power budget.** The following figures are planning arithmetic under stated assumptions and will be replaced by bench measurements. Duty-cycled electronics draw about 0.25 W, or about 6 Wh per day. The arm draws about 5 W for 10 seconds per lift at 20 lifts per day, or about 0.3 Wh per day. A 10 W panel with about 3 effective sun-hours at 60 percent system efficiency yields about 18 Wh per day. Two 18650 cells store about 18 Wh. The margin is thin on cloudy days, so the controller lengthens its capture interval when the battery is low and withholds motor power below a minimum voltage.

**Scope.** SAGIP lifts light floating debris reaching the boom, such as bottles, sachets, bags, foam and cups, in small batches. Heavy or tangled items, hyacinth mats, sunken waste, sediment, oil and dissolved pollutants lie outside its reach, as does any stretch of the estero downstream of the boom. We therefore report a measured capture rate in place of any claim that the estero is clean.

## 6. How will you implement this?

**Staged construction.** Each stage is funded only after the preceding one meets its gate.

1. **Stage 1, bench (about PHP 1,800).** Assemble the camera board, microSD card and enclosure, train and test the model, and measure power draw. *Gate:* precision and recall on held-out photographs meet the target.
2. **Stage 2, passive trap (about PHP 2,500).** Install the boom, deflector, bar screen, ramp, bin, post and solar supply at the estero. *Gate:* the boom survives [N] rain events and weekly counts fall within 15 percent of hand counts.
3. **Stage 3, arm and sensor (about PHP 1,350).** Fit the motor, driver, jam protection and level sensor. *Gate:* a wet bench rig with real hyacinth, estero silt and a little cooking oil first yields stall current, slip and lifts per run, after which the arm must lift debris on solar power alone at the target jam rate.
4. **Contingency:** PHP 350.

**Budget.** All prices are estimates to be confirmed locally.

| Item | PHP |
|---|---|
| ESP32-S3 camera board | 1,300 |
| microSD card | 200 |
| Sealed enclosure, glands, desiccant | 300 |
| Waterproof ultrasonic level sensor | 350 |
| Solar panel (about 6 to 10 W) | 600 |
| Charge controller, two 18650 cells, holder, converter | 700 |
| Rope, net and zip ties (bottles and bamboo reused) | 450 |
| Anchor, post, clamps, concrete | 350 |
| Bin (reused) and painted staff gauge | 150 |
| Wiring, fuse, switch, connectors | 250 |
| Small geared DC motor (6 to 7.4 V) | 500 |
| Motor driver | 200 |
| Current and motion sensing | 150 |
| Ramp, rake arm, shaft, bar screen, spare shear pins | 150 |
| **Subtotal** | **5,650** |
| Contingency | 350 |
| **Total** | **6,000** |

**Tools.** Arduino IDE or PlatformIO, Python with TensorFlow Lite for Microcontrollers, a borrowed soldering iron and multimeter, and team members' phones for photography.

**Evidence available at submission.** [N] labelled photographs and a first detection screenshot, a photograph of the bench prototype, one measured power figure, and the barangay's signed approval letter. *(Complete only with what exists.)*

**Timeline**

| Dates | Milestone |
|---|---|
| Oct 28 to Nov 2 | Site visit and barangay letter, starter dataset, bench power test, submission |
| Nov 3 to Nov 20 | Stage 1 gate and a baseline week at the estero, with hyacinth cover and flow recorded |
| Nov 16 to Dec 5 | Refinement with Samsung coaches if shortlisted |
| Dec 7 | Presentation of model metrics, baseline data and Stage 2 progress |
| Dec to Feb | Stages 2 and 3, followed by the full pilot with weekly hand-count validation |
| By Mar 2027 | Build guide published, one or two further sites, larger conveyor if funded |

**Site selection.** We will choose a stretch with moderate flow and accessible banks, and record hyacinth cover and silt as variables.

**Maintenance agreement.** A one-page memorandum will name the barangay focal person who empties the bin weekly, the student team who clear jams, clean the lens and upload data, and the adviser who signs off the checklist. The checklist covers emptying the bin, clearing the bar screen and deflector, inspecting the arm, ramp and shear pin, wiping the lens, checking the mooring, reading the battery and uploading the data. The routine fits alongside the barangay's existing estero cleanup work **[VERIFY: current DENR and LGU programs]**. *[Confirm with the barangay before submission.]*

**Typhoon and theft.** A quick-release line and a rule to retrieve the electronics before a typhoon signal reduce storm losses. The camera and controller are mounted discreetly high on the post, and barangay tanod are informed.

**Risks and mitigation**

- *Hyacinth mats.* A deflector, a vegetation class that inhibits the arm, daily screen clearing, and a plain report that heavy mats may pause operation.
- *Arm jams, slip or burnout.* Shear pin, current and motion sensing, bounded retries, a heat budget and a fail-safe driver.
- *Oil and silt.* Motor and bearings mounted high, sealed bearings with marine grease, stainless fasteners and a hooded lens.
- *Model degradation in new light or water.* Photographs across times of day and weather, reporting of held-out scores, and a manual fallback count.
- *Arm failure.* The boom, bar screen and bin continue to trap passively and the camera continues to count, so the data pilot remains intact.
- *Overstatement.* Targets are reported as targets, and the final report states what was measured and what failed.

## 7. What impact do you hope to achieve, and what is the long-term vision?

NGOs already document, largely by hand, which companies produce the most plastic in Philippine waste, and RA 11898 now makes producers responsible for recovering it **[VERIFY]**. A continuous record that is inexpensive and owned by the community beside the water remains missing. SAGIP supplies that record at the waterway and lifts part of the plastic out as it does so. The mass removed by a single unit is small. Its significance rests on a design cheap enough for a thousand barangays to copy and on data open enough to be combined.

**Pilot measures.** The pilot will report kilograms of floating debris lifted, with weekly weigh-ins, a measured capture rate and a baseline comparison. It will report precision and recall of at least [0.85] on held-out locations and weekly count error within 15 percent of hand counts. It will also yield a weekly report series, an item-level audit of what the estero carried, and, as a secondary result, a record of level alerts with the warning time each provided.

**Replication.** We will publish a free English and Filipino build guide and secure at least [1 to 2] additional sites by March 2027 at about PHP 6,000 each, sharing one open data format. Until a second barangay builds the unit, we regard its wider reach as a plan and not a result.

**Sustainability.** The barangay operates the unit with local parts, solar power and a one-page checklist under a named maintenance agreement. No subscription, server or internet connection is required. The dataset and model are open, so other barangays can retrain on their own waste, and reused floats and bamboo keep replacement inexpensive.

**Long-term vision.** We envisage a student-built, barangay-owned network of SAGIP units along connected esteros that feeds an open dataset showing where plastic enters the waterway, which products dominate, and whether EPR commitments change what the water carries. Each added barangay raises the value of every other unit's data. The pilot establishes the method at one creek and makes no larger claim.

**Key takeaway.** The Philippines already knows who makes much of its plastic. SAGIP makes the proof continuous, cheap and community-owned, and it lifts some of the plastic out along the way.

## References

Break Free From Plastic and GAIA (2019). *Plastics Exposed: How Waste Assessments and Brand Audits Are Helping Philippine Cities Fight Plastic Pollution.* no-burn.org.

Greenpeace International. *Nestlé and Unilever identified as top plastic polluters in Philippines waste audits.* greenpeace.org.

HydroSentinel (2026). An IoT-enabled autonomous surface vehicle for dual-scale riverine plastic detection and remediation. *ScienceDirect.* **[add authors and journal details]**

Manila Bulletin (August 24, 2026). Report on government estero trash traps and EPR audits. **[add headline and byline]**

Meijer, L. J. J., et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances.* **[VERIFY]**

Republic Act No. 11898 (2022). Extended Producer Responsibility Act of 2022. **[VERIFY]**

van Lieshout, C., et al. (2020). Automated river plastic monitoring using deep learning and cameras. *Earth and Space Science, 7*, e2019EA000960.

**[Add a TinyML or object-detection source on low-power microcontrollers.]**
