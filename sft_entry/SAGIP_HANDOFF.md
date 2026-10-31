# SAGIP Handoff for a new chat (Samsung Solve for Tomorrow 2026 PH)

**Updated:** Oct 31, 2026, end of day. **Entry deadline: Nov 2, 2026, 11:59 PM.** Work branch: `claude/wonderful-gates-pl9vmk` (repo `tmommu/research`). The older branch `claude/affectionate-maxwell-ld4ech` still holds `old_versions/`, which was not copied here. Latest commit: see `git log`.
Team: Quezon City Science High School, Grade 10 (Aaron Jed E. Campo, Raya Kalayaan R. Amparo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado). Adviser: Skjoukje U. Jemoya. Theme: Environmental Sustainability through Technology.

## 1. What to do first in the new chat
1. Read this file, then `sft_entry/build/content.py` (single source of the Word entry text). Do not start over.
2. All entry files are built and consistent but **not final**: the yellow placeholders in section 8 are still open. Show a summary and ask before declaring anything final.
3. The user wants files edited in place. Do not create new copies of existing files.

## 2. Judging process (given by the user)
- Nov 9 to 13: qualifying screening of the written entry by SEPCO, DOST-SEI, DICT, DENR, DOST-CEST judges, to pick the Top 10.
- Nov 16 to Dec 5: mentorship with Samsung coaches. Top 10 build **mock-ups** and expand slides (max 20).
- Dec 7: 30-minute pitch to the board of judges.
- Criteria: Design Innovation 20, Relevance to Community 20, Feasibility 20, STEM Integration 15, Sustainability 15, Clarity 10.
- Official entry rules: 7 sections, 3,000 words max (team cap 2,500), Arial 11, 1.5 spacing, PPT max 6 slides, project description exactly 3 sentences, submit PDFs (each under 40 MB) through the Google Form.

## 3. Feedback received
**Mentor (Oct 31):** prefer standardized recycled-plastic shapes at scale (reuse is fine for a proof of concept if stated). The structure must not break or capsize. Prioritize a 3D model (Tinkercad) and a wiring schematic (Fritzing) with every numbered part labelled. Power is the hardest part (two 18650 cells and a 10 W panel were too weak). Do not sense things in the water. A predetermined path is easier than real-time navigation. LIDAR is expensive. Frame it as a feasible proof of concept.
**Adviser (Google Doc comments, all addressed):** "through?" (reports are read through an offline phone page), "using?" (a small on-chip neural network running on an ESP32 chip), "vague, back up with data" and "lacks clarity" (Meijer figure added), "sustainable" (replaced "continuous"), "choose the nearest to the school, most in need" (Dario River chosen, justification still to confirm), "what?" (build guide defined as parts list, wiring, code, plus an open dataset of anonymized counts and photographs).
**Reviewer criteria notes (all addressed in the boat version):** light leakage (skirted hood, fixed LED), anti-fog (hydrophobic film, angled window, desiccant), community output (monthly Plastic Trend Scoreboard at the Barangay Hall), barrier mechanics (10 mm rope, float every 30 cm, about 30 degrees to the flow, bank posts), deep sleep (numbers added), object detector and overlapping items (bow ESP32-CAM detector, one item per cleat pocket, blob count flags "mixed"), data augmentation, end of life, protected 18650 in an IP67 box (flood node only, the boat has a lead-acid battery), clarity and transitions.

## 4. Current design (skimmer boat plus a flood node)
- **Boat:** twin 6-inch PVC floats (one 1.5 m pipe each) with foam in the bow and stern, deck, 30 W panel flat on the deck, 12 V 12 Ah sealed lead-acid battery low between floats, motors on fused branches with drivers that default to off, tilt cut-off.
- **Two fixed cameras (decided Oct 31):** navigation = ESP32-CAM Type C at the bow (OV2640, 4 MB PSRAM, USB-C, Makerlab PHP 599). Sorting = ESP32-S3 N16R8 camera board under a lit hood (Shopee, about PHP 345 to 530). The pan servo, mast and long lens were dropped to keep it simple.
- **Patrol:** about 30 m creek stretch between two floating barriers. Two thrusters (differential steering), two side ultrasonic sensors, bump switches, phone remote takeover. Stays docked from the flood alert level. A compass is a row marked "to decide": the MPU6050 the user linked gives tilt only, no heading.
- **Detect and scoop:** bow ESP32-CAM runs a small INT8 object detector, the boat steers to plastic, a scoop lifts it onto a cleated conveyor.
- **Count and sort:** ESP32-S3 camera runs a 2D CNN (INT8, TFLite Micro). A servo gate sends plastic to Bin A and plants, mixed or unsure items to Bin B.
- **Plastic accounting:** counts become estimated kg and junk-shop value, corrected by a weekly weigh-in, as evidence for the barangay and DENR (RA 11898).
- **Flood node on the bank:** ESP32, three float switches (watch, alert, danger), buzzer and small LED (the 12 V beacon was cut), 2 W panel, protected 18650 in an IP67 box, ESP-NOW link to the boat.
- **Deep sleep:** AI-Thinker lists the ESP32-CAM board at about 180 mA awake and 6 mA asleep at 5 V (about 22 Wh a day against 0.7 Wh). These are datasheet-style values from reseller pages, not measured. The entry says so.
- **Site:** Dario River, Quezon City. **Barangay Santo Cristo, Bago Bantay is provisional** (it is the school's barangay, per the school's history page). It is not confirmed that the river runs along it. One Wikipedia line says Barangay San Antonio is bounded by the Dario River on the east. Check on a map before submitting.
- History: earlier versions (rake-arm bank unit, hybrid floating foot, floating raft at PHP 12,000 to 13,000) are in `old_versions/` on the older branch. The user rejected a heat device, a dengue "Lamok Lens" idea and the PHP 6,000 first design.

## 5. Budget status
The entry still says **about PHP 16,000** (subtotal 15,350, contingency 650) with the item lines in `content.py` `BUDGET`. The real total is not final.
- **Estimate (Oct 31):** about PHP 17,500, or about 16,400 if the user's thruster price (PHP 1,080, listing says "1PCS") covers both thrusters. Savings found: S3 board at PHP 345 instead of 530, bow camera as a second S3 board, cheaper end caps, lunch boxes for the camera and battery boxes, two ultrasonic sensors, two foam cans, no beacon.
- **The user is filling prices into the Materials Tracker sheet** (see section 7). So far entered: pipe 540, couplers 464, end caps 964, foam 334, plywood 610, U-bolts 162, L brackets 78, thrusters 1,080. Ask whether each price is per piece or for the whole row. The pipe listing is 1.5 m, so check it covers both floats and whether couplers are needed.
- **Still unpriced:** battery (a larger one may be needed), driver, gear motor, belt, buck converters, wire, flood node parts, bolts, cement, epoxy.
- **Weight warning:** orange pipe is about 2.5 kg per meter, boat about 32 kg empty, about 60% submerged. Be ready to add a third float. Float and tilt tests decide.
- **Power plan (planning figures):** 30 W panel about 54 Wh/day, 20-minute patrol about 25 Wh, battery 144 Wh with about 72 Wh usable.
- If the budget changes, change `BUDGET` in `content.py`, then every "PHP 16,000" in content, PPT (`build_off2.py` slides 2, 5, 6 hardcode numbers), prototype doc and Google Doc.

## 6. Files
`sft_entry/`: `SAGIP_SFT2026_Proposal.docx` (2,493 words by script count, official template filled in place, the "What exists" lead-in sentence was removed to stay under the cap), `SAGIP_SFT2026_Entry_PPT.pptx` (official template, 6 slides, slide 4 is full), `SAGIP_SFT2026_Prototype_Design.docx` (4 pages), `SAGIP_Boat_3D_Model.stl` and `SAGIP_Boat_3D_Model.png`, `SAGIP_Electronics_List.md` (all electronic parts, pin map, open design points), `SAGIP_Wiring_Boat.png` and `SAGIP_Wiring_FloodNode.png` (pictorial wiring diagrams, SVG too, from `build/make_wiring_diagram.py`), `SAGIP_KiCad_Schematic.png` (preview of the KiCad render), `kicad/SAGIP.kicad_sch` and `.kicad_pro` (opens in KiCad 7, netlist checked against the intended 62 nets, ERC not run), `SAGIP_Skimmer_Boat_Draft.png`, `SAGIP_Wiring_Schematic.png` (not redrawn for the two-camera change), `SAGIP_FINAL_CHECKLIST.md` (mirrors the Drive checklist doc), this handoff.
`sft_entry/build/`: `content.py`, `build_word2.py`, `build_off2.py` (PPT text is hardcoded in this script except title, team and description), `build_proto.py`, `make_3d_model.py`, `make_kicad.py` (writes the schematic and `nets_expected.json`, check with `kicad-cli sch export netlist`), `make_simple_diagram.py`, `gen_html.py`, `figures/`, `templates/`, PNG figures including `fig_3d_iso.png`.
**Build commands** (run from `sft_entry/build`, paths are now relative):
`python3 -I build_word2.py ../SAGIP_SFT2026_Proposal.docx` (prints the word count),
`python3 -I build_off2.py ../SAGIP_SFT2026_Entry_PPT.pptx`,
`python3 -I build_proto.py` (writes `../SAGIP_SFT2026_Prototype_Design.docx`),
`python3 -I make_3d_model.py` (writes the STL and PNG into `sft_entry/`, needs `pip install matplotlib trimesh`; only numpy, trimesh and pillow are actually used).
After editing `content.py`, rebuild all three documents. Check PPT slides in a render (LibreOffice to PDF, then `pdftoppm`): text overflows silently on slides 2 and 4.
**3D model:** parametric, in mm, planning sizes. The STL is one merged shape with overlapping parts, a visual and dimension reference, not print-ready. The numbering 1 to 12 matches the prototype parts table. It has not been opened in Tinkercad yet.

## 7. Google Drive state
SFT folder id `1BuNJSFG6lIQewRYZiqBMkwVO2yQx6PgZ`. "old versions" folder id `1qAeLEdP5hoFUyhcq69I8IzRlKtdlIIWa`.
**Current native Google files in the SFT folder:**
- Proposal Google Doc `1p7bja0o1ircf9AA7ZB4GtN4Xx9mgbBxa_O1mj5cwVBY`: updated to the boat version, the adviser's 7 comments still anchored. Still to do: insert the two new figures at the yellow placeholders, delete the reviewer notes at the end, fill placeholders.
- Materials Tracker sheet `1i5ucorRv9VnnwRvoeCwL_9gW_R5jhCliwlwTizRxiOw`: 39 items, Status dropdown, summary row, planned total PHP 16,630 (a stale planning figure). The user edits it directly (prices, links). Never overwrite rows without re-reading first.
- Final Checklist doc `1y2PASTRbHB9jSdbnkxVpVwLouDUhjIy4BMG5ELqnf-0`: updated for the boat version.
**Stale or old:** the Word, PPT and prototype .docx/.pptx copies in Drive (owned by Raya and Sophia, in "old versions") are the raft versions. "SAGIP Materials Checklist" doc (id `1-zRkunc4pu-mr-cEq54o00VhRD89IzHZQfJrg4PM_Dk`) is superseded by the sheet. Do not overwrite the team's heat-device docs.
**Connector limits:** the Drive connector cannot upload .docx or .pptx (the whole file must be pasted in the call; they are 270 KB to 850 KB). The user drags files in by hand. The Docs connector edits native Google Docs well with `replaceAllText` (no positions needed) and can insert text at positions (the `docs_index.py` helper in the google-workspace skill reads saved `read_doc` JSON; unwrap the `content` key first). It cannot insert images from local files. Drive search uses `title contains`, not `name` or `parents`.

## 8. Still open (user decisions and team tasks)
**Placeholders (yellow in Word, PPT slide 2 and 3, Google Doc):**
- Households: the text now says "[6,531 on record, confirm creek-side count]". 6,531 is the barangay-wide figure from the Barangay Directory page for Santo Cristo (labelled RBI, average household size 3.4 from PSA 2020, population 25,783 in 2020). Get the number living along the creek from the barangay hall. Purok was dropped from the text (Quezon City barangays rarely use it, use sitio or street names if needed).
- The barangay's current cleanup program.
- Confirm Barangay Santo Cristo, Bago Bantay (or the right barangay) actually borders the river, and why Dario River is the nearest estero to the school and most in need. The Section 3 bracket asks for this.
- The "Select" paragraph (Word Section 4, PPT slide 3) must describe how the team really chose the topic.
**Electronics decision (Oct 31):** the schematic needs a **third ESP32 on the boat (DevKit, the boat controller)** because the camera boards leave too few free pins for three motor drivers, two sonars, I2C sensors and two UARTs. The user has not approved this yet. It also assumes three BTS7960-class drivers (the sheet has one dual driver and no belt driver), fuse values are guesses until motor ratings are known, and neither camera board's pinout has been checked. The sheet is missing: boat controller DevKit, belt driver, main fuse, master switch, MOSFET, RTC, MT3608 boost, NPN, resistor and capacitor kit. The old `fig_wiring.png` and `SAGIP_Wiring_Schematic.png` do not show the two-camera, three-board layout.
**Other tasks:** get the barangay approval letter (ask about city and DENR approval for the boat and barriers); finish prices and decide the compass; decide thrusters (one plus a rudder saves about PHP 600 to 1,000 but needs a wider creek); check the S3 listing includes the camera and 8 MB PSRAM; measure the real sleep currents; open Tinkercad and import the STL; redraw the wiring schematic for the two-camera layout; export Word and PPT to PDF; submit through the Google Form; search for other projects called SAGIP.
**Citations (all 2021 or later):** checked online by search: Meijer 2021 (the new "about 356,000 tonnes a year for the Philippines" figure came from news reports, so check it in the paper, DOI 10.1126/sciadv.aaz5803), van Emmerik 2022, Schreyers 2021, Gholami 2021, David 2021, Kataoka 2024, RA 11898, Ocean Cleanup, Manila Bulletin, Philstar items. Verify before submitting: Cook 2021 exact title, Break Free From Plastic 2021 report title, Food Packaging Forum 2026, Mendez-Cruz 2024 (found only via a repository listing, check authors and IEEE venue). **Novelty claim:** the entry says "Our search found no system that does all four" because ClearBot (dual cameras, RTK GPS, lidar, echo sounder, water sensors) exists. Re-check this sentence, and cite a 2021 or later source if ClearBot is named.

## 9. Style and working rules from the user
- Final text style: scholarly, no em dashes, no semicolons, no clichés (Furthermore, It is important to note, Delve, Testament, Game-changer), varied sentence length, keep facts and citations intact, no "not X but Y". `grep -c "—\|;" content.py` should print 0.
- Keep the official templates exact. Fill text only. Do not move or resize shapes (the PPT script only zeroes paragraph spacing on slides 3 and 4 to fit text).
- Keep references 2021 or later. Keep the Word entry at or under 2,500 words (every added sentence needs a cut elsewhere).
- Edit existing files in place. Move older versions to `old_versions/` only when replacing a whole file. Do not upload PDFs.
- Commit and push to the work branch above with the attribution lines. Do not open a pull request unless asked.
- Ask before declaring anything final.
- **Environment limits:** samsung.com, arxiv.org, CDNs (jsdelivr, cdnjs), `overpass-api.de` and `nominatim.openstreetmap.org` are blocked from the cloud session (the user can add a host under Network access in the environment settings). WebSearch works. Playwright and LibreOffice work for rendering. Do not use `rm` with a shell variable in the target (the safety check blocks it).
