# SAGIP Handoff (Samsung Solve for Tomorrow 2026 PH) - DRAFT v7

**Updated:** Oct 31, 2026. **Entry deadline: Nov 2, 2026, 11:59 PM.** Branch: `claude/affectionate-maxwell-ld4ech`.
Team: Quezon City Science High School, Grade 10 (Aaron Jed E. Campo, Raya Kalayaan R. Amparo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado). Adviser: Skjoukje U. Jemoya.

## How judging works (from the team)
- Nov 9 to 13: qualifying screening of the written entry by SEPCO, DOST-SEI, DICT, DENR and DOST-CEST judges. Top 10 are picked.
- Nov 16 to Dec 5: mentorship with Samsung coaches. Top 10 build **mock-ups** and expand the slides (max 20).
- Dec 7: 30-minute pitch to the board of judges.
- Criteria: Design Innovation 20, Relevance to Community 20, Feasibility 20, STEM Integration 15, Sustainability 15, Clarity 10.
So the entry is judged on paper first. A full boat is not needed by Dec 7. A bench demo, a scaled mock-up, a 3D model and a wiring schematic are.

## Design (draft, about PHP 16,000)
An autonomous solar skimmer boat plus a flood node on the bank:
- Twin 6-inch PVC floats, foam fill, wide beam, battery low, tilt cut-off. 30 W panel flat on the deck, 12 V 12 Ah battery, two buck converters, fused motor branches.
- Patrols a ~30 m stretch between two floating barriers, following the bank with side ultrasonic sensors and a compass. Phone remote takeover. Stays docked from the flood alert level.
- Bow ESP32-CAM runs a tiny detector. The boat steers to plastic, a scoop lifts it onto a cleated conveyor, an ESP32-S3 camera under a hood runs a 2D CNN, a servo gate sorts into Bin A (plastic) and Bin B (plants, unsure).
- Plastic accounting: counts become estimated kg and recovery value, corrected by a weekly weigh-in, in an evidence sheet for the barangay and the DENR.
- Flood node on the bank: three float switches, buzzer and beacon, small solar panel and cell, ESP-NOW link to the boat.
- Limits stated in the entry: people still empty bins and clear snags, one creek stretch only, no heavy or tangled items.

## Files in `sft_entry/` (all drafts)
| File | Status |
| --- | --- |
| `SAGIP_SFT2026_Proposal.docx` | Official Word template filled in place, about 2,480 words (cap 2,500), 2 figures |
| `SAGIP_SFT2026_Entry_PPT.pptx` | Official PPT template filled in place, 6 slides |
| `SAGIP_SFT2026_Prototype_Design.docx` | 4 pages: parts key with functions, wiring schematic, itemized budget, build plan |
| `SAGIP_Skimmer_Boat_Draft.png`, `SAGIP_Wiring_Schematic.png` | Boat drawings and wiring |
| `build/` | Scripts and `content.py` (single source of text) |
Older versions are in `old_versions/`. The 3D model for the new boat is not built yet (the old raft model is in `old_versions/`).

## Decisions still open
1. Approve the design and the PHP 16,000 budget. Level B comes to about 16,000 with two thrusters, about 15,400 with one thruster and a rudder.
2. Whether to build the 3D model (Tinkercad) for the mentorship period.

## Before submitting (team only)
1. Fill the yellow placeholders: [ESTERO SITE], [BARANGAY AND PUROK], [N] households, household count and cleanup program (Word Objective 1 and Section 3, PPT slide 2).
2. Rewrite the "Select" paragraph (Word Section 4, PPT slide 3) to match what the team really did.
3. Get the barangay approval letter. Ask about city approval (and DENR where required) for the patrol stretch and barriers.
4. Confirm prices (Shopee: 30 W panel with 20 A controller about PHP 1,084). Check battery, belt motor, thrusters and PVC pipe.
5. Open each citation once (all are 2021 or later). Confirm Cook 2021, Break Free From Plastic 2021, Food Packaging Forum 2026, Mendez-Cruz 2024, Manila Bulletin 2025 and 2026, Philstar 2022 and 2025.
6. Export both files to PDF (each under 40 MB) and submit through the Google Form before the deadline.

## Notes
- All power, size and cost figures are planning estimates. Measure power on the bench before claiming results.
- samsung.com was unreachable from this session. The team's heat-device Google Docs must not be overwritten.
