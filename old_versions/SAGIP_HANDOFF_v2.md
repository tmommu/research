# SAGIP Handoff (Samsung Solve for Tomorrow 2026 PH)

**Updated:** Oct 29, 2026. **Deadline: Nov 2, 2026, 11:59 PM.** Branch: `claude/affectionate-maxwell-ld4ech`.
Team: Quezon City Science High School, Grade 10 (Aaron Jed E. Campo, Raya Kalayaan R. Amparo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado). Adviser: Skjoukje U. Jemoya. Theme: Environmental Sustainability through Technology.

## Project

**SAGIP** ("to rescue"), a PHP 6,000 solar-powered estero guardian: a floating boom with a hyacinth deflector guides plastic to a bar screen and ramp, a camera-triggered rake arm lifts it into a bin, and an ESP32-S3 camera counts each item on the chip with an INT8 model. A weekly offline report and open dataset go to the barangay. Water-level warning is secondary. Rejected: the classroom heat device, Lamok Lens, and the PHP 10,000 conveyor (Phase 2 only).

Research question: can a PHP 6,000 on-chip counter match a trained hand audit within 15%, and does continuous counting reveal rain-driven pulses that weekly audits miss?

## Current files (`sft_entry/`)

| File | Status |
| --- | --- |
| `SAGIP_SFT2026_Proposal.docx` | Official Word template filled in place, 2,358 words (limit 2,500 set by the team, official 3,000), Arial 11, 1.5 spacing, 2 figures, REMINDERS removed |
| `SAGIP_SFT2026_Entry_PPT.pptx` | Official PPT template filled in place, 6 slides, no shapes moved, reminders slide deleted |
| `SAGIP_SFT2026_Prototype_Design.docx` | 3-page prototype design in the v5 format, with a "why it is built this way" section |
| `build/` | Scripts and shared text (`content.py`) that regenerate all three files |

Older versions are in `old_versions/` (and the old proposal Doc is in the Drive "old versions" folder). Edit `build/content.py` and rebuild rather than editing text in three places.

## Not done

- **Drive upload.** The `.docx` and `.pptx` are not in the SFT Drive folder. The session has no Drive login and the connector cannot carry files this size. Drag the three files in by hand.
- **Placeholders (yellow in Word).** [ESTERO SITE], [BARANGAY AND PUROK], [N] households, [TARGET] kg, [X]%, [2] sites, and the barangay household count and cleanup program. These are the team's facts and goals. Do not claim results before they are measured.
- **Section 4 "Select" paragraph.** It is a template of the process. Rewrite it to match what the team really did.
- **Open flags.** MMDA and DPWH flood reports, current estero programs. HydroSentinel authors, and the Manila Bulletin (Aug 24, 2026) headline and byline. Neither HydroSentinel nor the Manila Bulletin item could be found online in this session, so confirm them or cut the claims that rest on them.
- **Evidence.** A signed barangay approval and maintenance memorandum, labelled photos of real trash, a first detection run, a bench photo and one measured power figure. List only what exists.
- **Hardware and prices.** Confirm the ESP32-S3 board has PSRAM and runs the model. All prices are estimates. Keep the total within PHP 6,000.

## Citations

Checked online: Schreyers et al. 2021 (Frontiers in Environmental Science 9, 686334), Cordova & Nurhati 2019 (Scientific Reports), Meijer et al. 2021 (Science Advances 7, eaaz5803), Schmaltz et al. 2020 (Environment International 144, 106067), David et al. 2021 (MLSys), RA 11898. Cited from memory, so open them once: Jambeck 2015, Lebreton 2017, Jacob 2018, Conrad & Hilchey 2011, van Emmerik & Schwarz 2020, van Lieshout 2020, Break Free From Plastic 2019.

## Scoring

Samsung rubric: Design Innovation 20, Relevance 20, Feasibility 20, STEM 15, Sustainability 15, Clarity 10. Self-assessment about 76/100. Feasibility is the weak point because nothing is built yet. The biggest gains are the barangay letter and real evidence, not more writing. The novelty claim is the combination (lifts, counts, shares open data at barangay cost) and the continuous, community-owned angle. The text says the literature search was limited.

## Build order (gated)

1. Stage 1, bench (about PHP 1,800). Gate: held-out precision and recall of at least 85%.
2. Stage 2, passive trap (about PHP 2,500). Gate: boom survives rain events, weekly counts within 15% of hand counts.
3. Stage 3, arm and sensor (about PHP 1,350). Gate: wet bench test with hyacinth, silt and a little cooking oil.
4. Contingency PHP 350.

Timeline: site visit and barangay letter by Nov 2, model and baseline week by Nov 20, early results Dec 7 if shortlisted, pilot Dec to Feb, build guide by March 2027.

## Submission checklist

1. Fill every yellow placeholder and delete bracketed notes.
2. Resolve the open flags above.
3. Check the entry against the official form once more.
4. Export Word and PPT to PDF (each under 40 MB) and submit through the Google Form before Nov 2, 11:59 PM.
5. Search for existing projects named SAGIP before submitting.

## Notes for a new session

samsung.com was not reachable from the cloud session, so rubric, themes and dates came from screenshots. The team's heat-device Google Docs are in their Drive and must not be overwritten. Re-read `build/content.py` first and update it instead of starting over.
