# SFT 2026 — Proposal: SALOK

**Theme:** Environmental Sustainability through Technology
**Deadline:** Nov 2, 2026, 11:59 PM. Format: Word (≤3,000 words / 7 pages) or PPT (≤6 slides), exported as a PDF under 40 MB.

Facts marked **[VERIFY]** are from memory of public sources and must be checked against the primary source before submission. Items in `[BRACKETS]` are blanks only the team can fill. Nothing here is a measured result; targets are labelled as targets.

---

**Entrant's school:** Quezon City Science High School  **Adviser:** [NAME]
**Team (max 4):** [NAMES, Grade 10]

## Entry title

**SALOK: A Solar-Powered Estero Guardian that Traps Plastic, Warns Barangays Before Clogged Waterways Flood, and Builds the First Open, Brand-Level Plastic Data Commons the Philippines Needs to Hold Producers Accountable**

*(Salok = "to scoop" in Filipino. Rename if the team prefers.)*

## Project description (three sentences, for official write-ups)

SALOK is a low-cost, solar-powered estero guardian: a floating trap catches plastic while an on-device AI model counts and classifies every item by type and, where legible, by brand, and a water-level sensor warns the barangay when debris and rising water threaten to block the channel. Barangay officials get a weekly report of what was removed and who made it, plus a flood-risk alert, without internet and without recording faces. Every barangay's anonymized results join an open dataset, so one trap protects one creek and many traps build the evidence to hold producers accountable.

## 1. What problem are you trying to solve?

Plastic reaches the sea through creeks and esteros. Published river-emission studies rank Philippine rivers among the largest sources of ocean plastic **[VERIFY: Meijer et al., 2021, Science Advances]**, and Metro Manila's esteros and the Pasig and Tullahan river systems carry much of it. Single-use sachets, bags and cups are the dominant items in cleanups **[VERIFY: local cleanup audits]**.

Two gaps keep the problem going:

1. **Removal is manual and invisible.** Cleanups happen on schedule and the trash is weighed in bulk. Nobody records what was in it, so the same items return.
2. **There is no brand-level data.** The Extended Producer Responsibility Act of 2022 (RA 11898) makes large companies responsible for recovering plastic packaging **[VERIFY: scope and thresholds]**, but enforcement needs evidence of *which* packaging actually ends up in waterways. Barangays and LGUs have no cheap way to produce it.

3. **Clogged waterways flood neighbourhoods.** Plastic and other debris choke drainage and esteros, worsening flooding in low-lying communities **[VERIFY: MMDA/DPWH drainage-clearing reports and flood studies]**, and standing, trash-filled water also breeds mosquitoes. Barangays learn a channel is blocked only when it floods.

**The problem is therefore three-part: catching the plastic, proving what it is, and seeing the blockage before it floods people's homes.** One device addresses a pollution problem, an accountability problem and a safety problem at once, which is why a single barangay-owned unit matters more than a cleanup day.

**Scale of the opportunity.** The Philippines has tens of thousands of barangays **[VERIFY: PSA count, about 42,000]**, and esteros run through a large share of urban ones. Each is a data point nobody is collecting. A design that costs about one barangay's cleanup budget for a month, and shares its data openly, can add up to the first nationwide picture of what plastic is in our waterways.

## 2. What do you want to achieve?

**Goal:** remove plastic from one estero in our community and generate the first student-collected, brand-level waste data that a barangay can hand to the LGU, using a design any barangay can copy for low cost.

**Objectives (SMART)**

1. **Capture.** In an [8]-week pilot at [ESTERO SITE], keep a floating trap in place through [N] rain events and remove at least [TARGET] kg of plastic, logged by weekly weigh-in.
2. **Classify.** By Nov 20, 2026 (proposal stage: a prototype dataset), train an on-device model to detect [5] classes (PET bottle, sachet/foil pouch, plastic bag, foam container, cup/other) with at least [0.85] precision and recall on photos from locations *not used in training*.
3. **Count accurately.** In the pilot, the device's item counts should be within ±15% of a hand count of the same trap contents each week.
4. **Report.** Produce a one-page weekly barangay report (items, types, estimated weight, top legible brands) with no internet.
5. **Warn.** Add an ultrasonic water-level sensor on the same post. During the pilot, log water level against rainfall and trap fullness, and set a "channel nearly blocked" alert; success is the alert firing at least [N] minutes before the nearest known flood point is reached in at least [N] observed events (report whatever we measure).
6. **Open data.** Publish anonymized weekly counts (type, brand tallies, estimated kg, level readings, no images of people) as an open CSV with a data dictionary, so any school or LGU can use or extend it.
7. **Replicate.** By March 2027, publish a free English/Filipino build guide and help [1–2] other barangays or schools build one for no more than PHP [X], each contributing to the same open dataset.

## 3. Who will benefit?

- **Primary:** residents of [BARANGAY/PUROK] along [ESTERO], and the barangay's environmental/sanitation officers, who get cleaner water and flood-prone canals, plus data they have never had.
- **Secondary:** the LGU/DENR offices handling solid waste, who can use brand-level evidence; neighbouring barangays who can copy the design; students, who become the community's citizen scientists.
- **Wider:** downstream communities and fisherfolk affected by plastic reaching Manila Bay.

## 4. How did you come up with your proposal?

We scored five community problems on significance, feasibility, STEM depth, replicability and originality. Plastic in esteros won because we can reach one, measure it weekly, and the law (RA 11898) has just made the data useful.

We reviewed existing approaches and found two camps. Passive trash booms and traps catch plastic but record nothing beyond bulk weight. Research systems that use cameras and AI to detect river plastic exist **[VERIFY: e.g., published river-plastic monitoring with computer vision]**, but they typically need powerful hardware, a stable connection or an expert to run. **We found no low-cost design that combines a physical trap with a power-frugal on-device classifier built for a barangay to operate.** SALOK sits in that gap.

## 5. How will your tech solution work?

> **STEM map:** *Physics* (buoyancy, flow, solar power budget) · *Math/Statistics* (precision, recall, count error, sampling) · *Computer Science* (object detection, INT8 quantization) · *Engineering* (floating structure, mounting, weatherproofing) · *Environmental Science* (waterway pollution, EPR policy).

SALOK **traps, sees, counts and reports.**

**Trap (Physics, Engineering).** A V-shaped floating boom of reused PET bottles or bamboo floats guides surface debris into a mesh collection pocket at the estero's edge, anchored to the bank or a bridge post. Students never enter the water; emptying is done from the bank by trained, supervised adults. A simple flow check (float-and-time test) tells us if the boom angle suits the estero's current.

**See (Computer Science).** A camera on a post above the pocket looks *down at the water surface only*, so no faces or houses are in frame. A compact object-detection model, **quantized to INT8** and running on a low-power microcontroller or single-board board with a camera, classifies each item that enters the pocket. Training photos come from our own collections of real trash on the estero bank, labelled by students and checked by the adviser.

**Count and weigh (Math).** Each detected item increments a class counter. Weekly, students hand-count and weigh the pocket's contents; a per-class average weight turns counts into estimated kilograms, and the hand count becomes our accuracy test.

**Report (Design).** A small screen and a phone-readable offline page (no cellular needed) show running counts. A script produces the one-page weekly barangay report and a CSV for the LGU. Legible brand names that a person can read from the stored photos are tallied by a student volunteer, giving the brand-level audit that automated detection alone cannot yet promise; the AI's job is to flag and crop likely labels.

**Power (Feasibility).** Average load is small; a [10–20 W] solar panel, a charge controller and a rechargeable battery cover it, sized from bench measurements the team will report. A cloudy-week plan puts the camera on a duty cycle (e.g., wake on motion or every N seconds).

**Safety.** Low-voltage wiring in a sealed enclosure with desiccant; the trap away from boat routes; barangay sign-off on the site; no cameras on people.

**Honest limits.** Detection will degrade in rain, glare and murky water; we report that rather than hide it. The device counts and classifies plastic; it does not clean the estero by itself, and it is not a substitute for waste segregation at the source.

*Figure 1: trap layout. Figure 2: system block diagram (trap → camera → model → counts → report). Figure 3: sample detections.* (Include a photo of the site and the bench prototype.)

**How the tiny AI works, in plain words.** A model that has seen thousands of photos of bottles, sachets and bags learns what each looks like. Quantization stores its numbers as small whole numbers so it fits and runs on a few watts of solar power, with no internet and nothing leaving the estero.

## 6. How will you implement this?

**Materials and budget (estimates; confirm local prices):** camera microcontroller or SBC and enclosure [PHP], solar panel, charge controller and battery [PHP], reused bottles/bamboo, mesh and rope [PHP], post and mounting hardware [PHP], contingency 10%. **Pilot total: PHP [X]. Copyable unit target: PHP [Y].**

**Timeline**
| Dates | Milestone |
|---|---|
| Oct 28 – Nov 2 | Site visit and barangay approval; photograph and label a starter dataset; draft and submit the proposal |
| Nov 3 – Nov 20 | Train and quantize the first model; build and float-test the trap; bench-test power |
| Nov 16 – Dec 5 | Refine with Samsung coaches (if shortlisted) |
| Dec 7 | Present early results: model metrics and first trap weights |
| Dec – Feb | Full pilot, weekly hand-count validation, barangay reports |
| By Mar 2027 | Build guide published; 1–2 more sites |

**Stakeholders:** barangay captain and sanitation/environment officers (site, emptying, using reports), the LGU solid-waste office (data), our adviser and school head (supervision), students (build, label, count, report), residents (consent and awareness).

**Maintenance and handover.** A one-page weekly checklist: empty the pocket, wipe the lens, check the mooring, read the battery, upload the CSV. The barangay names a focal person; students own the data and model updates. Parts are common and repairable locally.

**Risks and mitigation**
- *Flood or storm damages the trap:* secure mooring, a quick-release line, and a plan to retrieve electronics before a typhoon.
- *Model fails in new light or water:* collect across times of day and weather, report held-out-location scores, keep a manual fallback count.
- *Biofouling or theft:* lens cleaning schedule, discreet mounting, barangay tanod awareness.
- *Safety:* no student enters the water; adult emptying with gloves; barangay and school approval first.
- *Over-claiming:* targets stated as targets; we report the measured result and what failed.

## 7. Impact and long-term vision

**Success means** plastic physically removed from a real estero **and** a weekly, trustworthy record of what it was, giving the barangay a tool it can use to push for producer accountability under RA 11898.

**Measurable outcomes**
1. [TARGET] kg removed over the pilot, with weekly weigh-ins.
2. Model precision and recall ≥ [0.85] on held-out locations; weekly count error within ±15% of hand counts.
3. A published weekly barangay report series and a first brand-level audit of the estero.
4. A build guide and at least [1–2] additional sites by March 2027, each at no more than PHP [Y].

**Sustainability.** The barangay runs it with local parts, solar power and a one-page checklist; no subscription, server or internet is needed; the dataset and model are open so other barangays can retrain on their own waste.

**Long-term vision.** A student-built, barangay-owned network of low-cost SALOK units along connected esteros, feeding an open dataset that shows:
- where plastic enters the waterway and which products dominate;
- which channels clog first, so drainage clearing can be targeted before floods;
- whether EPR commitments are actually changing what the water carries, measured by the communities who live beside it.

Each added barangay makes every other unit's data more valuable, so impact grows faster than cost. A Science High School team could become the founding node of a national citizen-science network.

**Key takeaway.** Catching plastic is not enough; proving what it is makes producers accountable. SALOK does both, for the cost of one trap.

## References **[VERIFY each; add the exact citations]**

Meijer et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances*.
Republic Act 11898, Extended Producer Responsibility Act of 2022.
[Local cleanup/brand audit source, e.g., a recognised NGO audit].
[A published river-plastic computer-vision monitoring study].
[A TinyML or object-detection source on low-power microcontrollers].

---

## How this maps to the rubric

| Criterion (weight) | How SALOK earns it |
|---|---|
| Design Innovation (20%) | Trap + on-device AI + brand-level audit + flood early warning in one low-cost unit; links physical cleanup to policy evidence and to disaster prevention; open data commons. |
| Relevance to the Community (20%) | A real estero, a named barangay partner, a current law, and a problem the community sees daily. |
| Feasibility (20%) | Common parts, solar, one-page upkeep, a barangay focal person, a safety plan, and a realistic pilot. |
| STEM Integration (15%) | Explicit STEM map; physics, statistics, computer science, engineering and environmental science all used. |
| Sustainability (15%) | Solar, upcycled floats, no server, open model, replicable by any barangay. |
| Clarity (10%) | One problem, one device, one measured outcome, plus the report the community can act on. |

## Pre-submission checklist

- [ ] Choose the real estero and get written barangay/LGU approval; fill in `[SITE]`, `[BARANGAY]`.
- [ ] Spend this week photographing and labelling real trash to show a starter dataset and sample detections.
- [ ] Verify every **[VERIFY]** fact and add exact citations.
- [ ] Bench-measure the camera device's power draw and report the real number.
- [ ] Fill the budget with real local prices.
- [ ] Add photos or a labelled drawing of the trap and a sample detection image.
- [ ] Check against the official entry templates (the Drive connector could not list them) and export to PDF under 40 MB.
