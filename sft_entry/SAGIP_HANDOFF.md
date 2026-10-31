# SAGIP Handoff for a new chat (Samsung Solve for Tomorrow 2026 PH)

**Written:** Oct 31, 2026. **Entry deadline: Nov 2, 2026, 11:59 PM.** Repo branch: `claude/affectionate-maxwell-ld4ech` (repo `tmommu/research`). Latest commit when written: see `git log`.
Team: Quezon City Science High School, Grade 10 (Aaron Jed E. Campo, Raya Kalayaan R. Amparo, Ayeza Leigh F. Delos Santos, Sophia Laureen A. Tado). Adviser: Skjoukje U. Jemoya. Theme: Environmental Sustainability through Technology.

## 1. What to do first in the new chat
1. Read this file, then `sft_entry/build/content.py` (single source of the entry text). Do not start over.
2. The user said **"before finalizing consult with me first"**. Show a summary and ask before declaring anything final.
3. Nothing in `sft_entry/` is final. All files are DRAFT v7.

## 2. Judging process (given by the user)
- Nov 9 to 13: qualifying screening of the written entry by SEPCO, DOST-SEI, DICT, DENR, DOST-CEST judges, to pick the Top 10.
- Nov 16 to Dec 5: mentorship with Samsung coaches. Top 10 build **mock-ups** and expand slides (max 20).
- Dec 7: 30-minute pitch to the board of judges.
- Criteria: Design Innovation 20, Relevance to Community 20, Feasibility 20, STEM Integration 15, Sustainability 15, Clarity 10.
- Official entry rules: 7 sections, 3,000 words max (team cap 2,500), Arial 11, 1.5 spacing, PPT max 6 slides, project description exactly 3 sentences, submit PDFs (each under 40 MB) through the Google Form.

## 3. Mentor feedback the user received (transcript, Oct 31)
- Reused PET bottles lack uniformity at scale, so prefer standardized recycled-plastic shapes. Reuse is fine for a proof of concept if stated.
- Structure must not break or capsize. Consider enclosures for sensitive parts.
- Prioritize a **3D model (Tinkercad)** and a proper **wiring schematic (Fritzing)** this weekend. Label what every numbered part does.
- Power supply is the hardest part. Two 18650 cells and a 10 W panel were called too weak. Motors may need a separate supply.
- Do not sense things in the water. Navigation: a predetermined path is easier than real-time navigation. LIDAR is expensive.
- Samsung expects the proposal to be feasible and implementable. Frame as proof of concept.

## 4. Current design (draft v7, autonomous solar skimmer boat plus a flood node)
- **Boat:** twin 6-inch PVC floats with foam fill, deck, 30 W panel flat on the deck, 12 V 12 Ah battery low between floats, two buck converters (5 V), motors on fused 12 V branches with drivers that default to off, tilt cut-off.
- **Patrol:** a ~30 m creek stretch between two floating barriers. Two thrusters (differential steering), side ultrasonic sensors, compass, bump switches. Phone remote takeover. Stays docked from the flood alert level.
- **Detect and scoop:** bow ESP32-CAM runs a tiny detector (plastic versus plants), the boat steers to plastic, a scoop lifts it onto a cleated conveyor.
- **Count and sort:** ESP32-S3 camera under a lit hood runs a 2D CNN (INT8, TFLite Micro), a servo gate sends plastic to Bin A and plants or unsure items to Bin B. Weekly hand counts check accuracy.
- **Plastic accounting (the extra feature the user asked for):** counts become estimated kg and recovery value, corrected by a weekly weigh-in, in an evidence sheet for the barangay and the DENR (RA 11898).
- **Flood node on the bank:** ESP32, three float switches (watch, alert, danger), buzzer and beacon, 2 W panel and 18650, ESP-NOW link to the boat. The user chose float switches over an ultrasonic sensor.
- **Honest limits written in the entry:** people still empty bins and clear snags, one creek stretch, no heavy or tangled items, planning figures not measured.
- History: earlier versions (bank rake-arm unit, hybrid floating foot at PHP 6,800, floating raft at PHP 12,000 to 13,000) are in `old_versions/`. The user rejected a heat device, a dengue "Lamok Lens" idea and the PHP 6,000 first design.

## 5. Budget status (planning estimates, about PHP 16,000 in the files, about PHP 17,400 after hull update)
The files still show the hull as PHP 2,300. Shopee screenshots show it is more.
**Verified from the user's Shopee screenshots (Oct 2026):**
- 30 W panel with 20 A controller: PHP 1,084 (4.9 stars, 5K+ sold). Panel is 350 x 600 mm.
- Orange S-600 PVC pipe, 6-inch, 100 cm: PHP 460. The 150 cm length is greyed out. 50 cm exists, price not seen.
- 6-inch end cap: PHP 135 (ships from Indonesia). A PHP 30 Laguna listing has 2 to 6-inch options, 6-inch price not seen.
- PU foam spray 750 ml: PHP 124 to 149 per can.
- Marine plywood 2 x 4 ft: about PHP 295. Use thin (1/4-inch) for weight.
- Stainless U-bolt set for pipes up to 6 inches: about PHP 75.
**Unverified guesses (ask the user for Shopee screenshots):** 12 V 12 Ah battery (about 1,500), thrusters (about 1,200 for two), dual driver (about 600), belt gear motor (about 700), belt material, ESP32-S3 CAM board (about 1,300), ESP32-CAM (about 450), JSN-SR04T ultrasonic x3, float switches, servo.
**Corrected hull estimate:** pipe 2 x (100 + 50 cm) with couplers about 1,700, four caps about 540, foam 300, thin plywood deck 600 to 900, clamps 300, frame 300 = about 3,700 (was 2,300). New total about PHP 17,400.
**Weight warning:** the orange pipe is about 2.5 kg per meter. The boat is probably about 32 kg empty. Two 1.5 m floats give about 60 L buoyancy, so about 60% submerged. Use a light deck. Be ready to add a third float (about PHP 900). The float and tilt tests decide.
**Power plan (planning figures):** 30 W panel about 54 Wh/day, 20-minute patrol about 25 Wh, battery 144 Wh with about 72 Wh usable (SLA at 50% depth).
Cost levels discussed: A (keep all, about 16,000), B (lean, chosen), C (leanest). One thruster plus rudder would save about PHP 600 but needs a wider creek.

## 6. Files
`sft_entry/` (drafts): `SAGIP_SFT2026_Proposal.docx` (about 2,480 words, official Word template filled in place), `SAGIP_SFT2026_Entry_PPT.pptx` (official PPT template, 6 slides), `SAGIP_SFT2026_Prototype_Design.docx` (4 pages), `SAGIP_Skimmer_Boat_Draft.png`, `SAGIP_Wiring_Schematic.png`, `SAGIP_FINAL_CHECKLIST.md` (stale, written for the 12,000 raft), this handoff.
`sft_entry/build/`: `content.py` (single source of text), `build_word2.py`, `build_off2.py` (PPT, edits the official template in place), `build_proto.py`, `gen_html.py`, `figures/` (HTML sources for the boat and wiring drawings and the Playwright screenshot scripts), `templates/` (official Word and PPT templates and the prototype template), PNG figures. **Scripts use absolute scratchpad paths** (for example `fmt/off.pptx`, `tplproto.docx`, `templates_zip/...`). Edit the paths to `sft_entry/build/templates/` before rebuilding. After editing `content.py`, rebuild all three files so numbers stay consistent.
`old_versions/`: all earlier versions, including the raft versions and the old 3D model.
Not built: a 3D model of the new boat (the old raft model is in `old_versions/`).

## 7. Google Drive state
SFT folder id `1BuNJSFG6lIQewRYZiqBMkwVO2yQx6PgZ`. It holds two Google Docs, "SAGIP SFT 2026 - Proposal (final)" and "SAGIP SFT 2026 - Final Checklist". **Both are stale** (they describe the PHP 12,000 raft). The folder "old versions" (id `1qAeLEdP5hoFUyhcq69I8IzRlKtdlIIWa`) holds older docs. The team's heat-device Google Docs elsewhere in Drive must not be overwritten.
**The Drive connector cannot upload .docx or .pptx** (content must be pasted in the call). The user downloads the files from the chat or repo and drags them in. Text can be pushed as Google Docs by converting HTML (see `gen_html.py`), but figures are not included.

## 8. Still open (user decisions and team tasks)
Decisions: approve the design and budget, one thruster versus two, whether to build the 3D model, final hull choice (two 1.5 m floats versus a third float).
Team tasks: fill the yellow placeholders [ESTERO SITE], [BARANGAY AND PUROK], [N] households, household count and cleanup program (Word Objective 1 and Section 3, PPT slide 2); rewrite the "Select" paragraph (Word Section 4, PPT slide 3); get the barangay approval letter (ask about city approval and DENR for the patrol stretch and barriers); confirm prices; open every citation; export Word and PPT to PDF and submit through the Google Form.
Citations (all 2021 or later): checked online by search: Meijer 2021, van Emmerik 2022, Schreyers 2021, Gholami 2021, David 2021, Kataoka 2024, RA 11898, and the Ocean Cleanup, Manila Bulletin, Philstar items. Verify before submitting: Cook 2021 exact title, Break Free From Plastic 2021 report title, Food Packaging Forum 2026, Mendez-Cruz 2024 (found only via a repository listing, check authors and IEEE venue), HydroSentinel was dropped (could not be found).

## 9. Style and working rules from the user
- Final text style: scholarly, no em dashes, no semicolons, no clichés (Furthermore, It is important to note, Delve, Testament, Game-changer), varied sentence length, keep facts and citations intact, no "not X but Y".
- Keep the official templates exact. Fill text only. Do not move or resize shapes.
- Keep references 2021 or later. Keep the Word entry at or under 2,500 words.
- Move older versions to `old_versions/` (repo and Drive) when replacing files. Do not upload PDFs.
- Commit and push to the branch above. Do not open a pull request unless asked.
- Environment limits: samsung.com, arxiv.org and CDNs (jsdelivr, cdnjs) are blocked from the cloud session. No Drive login for raw API upload. Playwright and LibreOffice work for rendering.
