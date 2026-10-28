# SALOK — Handoff (Samsung Solve for Tomorrow 2026 PH)

**Written:** Oct 28, 2026. **Deadline: Nov 2, 2026, 11:59 PM.** Branch: `claude/affectionate-maxwell-ld4ech`. Main file: `samsung_sft2026_proposal_salok.md`.

## Decision

The team is building **SALOK**, a PHP 6,000 solar-powered estero guardian:
- A floating boom with a hyacinth deflector guides surface plastic to the bank.
- A camera-triggered sweeper arm lifts it up a ramp into a bin.
- An ESP32-S3 camera runs an INT8 on-device model that counts items (5 plastic classes plus vegetation).
- Flood warning (ultrasonic level sensor) is **secondary**.

Rejected along the way: the classroom heat device (the team's earlier entry; its Google Docs are untouched), Lamok Lens (dengue), and the PHP 10,000 conveyor version. The conveyor is a Phase 2 idea only.

## Why it should score well (self-assessment, not official: about 76/100 as drafted)

Samsung's rubric: Design Innovation 20, Relevance to the Community 20, Feasibility 20, STEM Integration 15, Sustainability 15, Clarity 10. Weakest area is **Feasibility**, because nothing is built or measured yet. The biggest gains come from evidence and a real partner, not more writing.

## What the proposal already contains

Entry-form answers for all 7 questions, a prior-art table, a staged PHP 6,000 budget, a power budget, a jam-protection design, a maintenance agreement, a rubric map and a pre-submission checklist.

## What only the team can do (priority order)

1. **Pick the real estero** and get a **signed barangay approval and maintenance memorandum**. Fill `[SITE]`, `[BARANGAY]`, `[NAMES]`, `[NAME]` (adviser).
2. **Evidence before Nov 2:** photograph and label real trash (aim for as many as possible), run a first detection, take a photo of the bench prototype, and measure one real power figure. List in "Evidence" only what exists.
3. **Verify every [VERIFY] fact** and open every reference. Unconfirmed: Meijer et al. (2021), RA 11898 scope, the barangay count, MMDA/DPWH flood reports, and the HydroSentinel and Manila Bulletin details (authors, headline, byline).
4. **Confirm hardware:** the ESP32-S3 board must have PSRAM and run the model. Replace all budget estimates with real local prices; keep the total within PHP 6,000.
5. **Fill the [BRACKET] targets** with honest numbers. Do not claim a result before it is measured.
6. **Trim to under 3,000 words** (the body is about 2,820 now), then export a PDF under 40 MB.

## Known gaps and caveats

- **Entry templates not seen.** The Drive folder `2026 SFT Entry Templates` (owned by another account) listed no files to the connector. Compare the proposal against the official forms before submitting.
- **samsung.com was unreachable** from the cloud session, so rubric, themes and dates came from the user's screenshots. Dates: entries Sept 15 – Nov 2; the proposal's later milestones (Nov 16, Dec 7) come from a web search and should be confirmed.
- **All prices are estimates from memory.**
- **Novelty claim is limited.** Brand audits, camera-AI river monitoring and trash traps all exist. SALOK claims the *combination* and the *continuous, community-owned* angle, and says its search was limited.
- **Flood-warning feature** and the arm are the riskiest build items. The passive boom plus camera still works if the arm fails.
- **Estero hazards:** hyacinth mats, silt, oil and grease are the likely failure causes. The design mitigates them but only a wet bench test will prove it.

## Build order (decision gates)

1. **Stage 1, bench (about PHP 1,800):** ESP32-S3 camera, microSD, enclosure; train and test the model; measure power. *Gate: held-out precision and recall meet the target.*
2. **Stage 2, passive trap (about PHP 2,500):** boom, deflector, bar screen, ramp, bin, post, solar.
3. **Stage 3, arm and sensor (about PHP 1,350):** motor, driver, jam protection, level sensor. *Gate: wet bench rig test first.*
4. Contingency PHP 350.

## Suggested next steps for a new session

- Ask for the Word (≤3,000 words) or six-slide (≤6 slides) version once the blanks are filled.
- Re-read this file and `samsung_sft2026_proposal_salok.md` first. Update the proposal rather than starting over.
- If the user wants the Drive entry updated, the existing heat-device Google Docs are in their Drive; do not overwrite them without asking.
