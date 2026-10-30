# SAGIP Handoff (Samsung Solve for Tomorrow 2026 PH)

**Updated:** Oct 30, 2026. **Deadline: Nov 2, 2026, 11:59 PM.** Branch: `claude/affectionate-maxwell-ld4ech`.
Team: Quezon City Science High School, Grade 10 (Aaron Jed E. Campo, Raya Kalayaan R. Amparo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado). Adviser: Skjoukje U. Jemoya. Theme: Environmental Sustainability through Technology.

## Design (optimized version)

SAGIP is a bank-mounted, solar-powered estero guardian for about PHP 6,000 (5,850 plus 150 contingency):
- Floating boom with net skirt and a hyacinth deflector, then coarse bars and a fine mesh basket (both sloped).
- Ramp whose foot is hinged on bottle floats so it follows the water level, and a worm-gear motor above the flood mark driving a rake arm with a shear pin.
- Motor speed follows measured current (slows under load), with Hall sensing, three retries and a lockout for jams.
- ESP32-S3 camera under a hood with LED lighting runs a small 2D CNN (INT8, TensorFlow Lite for Microcontrollers). A servo gate sends plastic to Bin A and plants or unsure items to Bin B.
- Clock module, microSD log, offline Wi-Fi weekly report, open dataset. Ultrasonic level sensor is secondary.
- Power: 6 W panel, two 18650 cells. Planning figures only: about 11 Wh/day produced, about 6 Wh/day used.
- Limit stated in the entry: people must still empty bins weekly, clear the screen, wipe the lens and check the battery. Hours are logged.

Research question: can a PHP 6,000 on-chip counter match a trained hand audit within 15%, and does continuous counting reveal rain-driven pulses that weekly audits miss?

## Files in `sft_entry/`

| File | Status |
| --- | --- |
| `SAGIP_SFT2026_Proposal.docx` | Official Word template filled in place, about 2,465 words (team cap 2,500, official 3,000), 2 figures |
| `SAGIP_SFT2026_Entry_PPT.pptx` | Official PPT template filled in place, 6 slides |
| `SAGIP_SFT2026_Prototype_Design.docx` | 3-page prototype design, itemized PHP 6,000 table |
| `SAGIP_Device_Cutaway.png`, `SAGIP_Project_Design.png` | Device cutaway and flow diagram |
| `build/` | Scripts and `content.py`, the single source of text. Edit it, then rebuild |

Earlier versions are in `old_versions/` (v2 files, prev files, old handoffs). In Drive, the old proposal and prototype docs are in the "old versions" folder.

## Still to do before submitting (team only)

1. **Fill the yellow placeholders** in the Word entry: [ESTERO SITE], [BARANGAY AND PUROK], [N] households, the barangay household count and cleanup program. Fix the same three in the PPT (slide 2). Pick a narrow Quezon City estero that drains to the San Juan or Tullahan River.
2. **Rewrite the "Select" paragraph** (Word Section 4, PPT slide 3) so it matches how the team really chose the topic, then delete the bracketed note.
3. **Get the barangay approval and maintenance letter**, photos of real trash, and one measured power figure. List only evidence that exists.
4. **Check the numeric targets** (50% capture, 20 kg, 1,000 items) after a baseline week. Change them in `build/content.py` if the baseline says otherwise.
5. **Open the citations once.** Checked online this session: Schreyers 2021, Cordova & Nurhati 2019, Meijer 2021, David 2021, RA 11898, and the Ocean Cleanup, Manila Bulletin and Philstar items. From memory only: Jambeck 2015, Lebreton 2017, Jacob 2018, Conrad & Hilchey 2011, van Emmerik & Schwarz 2020, van Lieshout 2020, Break Free From Plastic 2019, Food Packaging Forum 2026.
6. **Confirm hardware and prices.** ESP32-S3 board needs PSRAM. Prices are estimates. The model must reach 85% on a held-out set before Stage 2.
7. **Upload to Drive.** The session could not upload the `.docx` and `.pptx`. Drag them into the SFT folder.
8. **Export Word and PPT to PDF** (each under 40 MB) and submit through the Google Form before Nov 2, 11:59 PM. Search for existing projects named SAGIP first.

## Gated build order

1. Stage 1, bench (about PHP 1,850). Gate: 85% precision and recall on held-out photos.
2. Stage 2, passive trap (about PHP 2,650). Gate: survives 3 rain events, counts within 15% of hand counts.
3. Stage 3, arm and sorter (about PHP 1,350). Gate: wet bench test with hyacinth, silt and a little cooking oil.
4. Contingency PHP 150, so ask the barangay for posts, rope and bins in kind.

## Notes for a new session

- samsung.com was unreachable, so rubric and dates came from screenshots. Rubric: Design Innovation 20, Relevance 20, Feasibility 20, STEM 15, Sustainability 15, Clarity 10.
- A fully floating platform adds about PHP 3,000 to 6,000. The hybrid (hinged floating ramp foot) is in the budget.
- The team's heat-device Google Docs are in their Drive and must not be overwritten.
