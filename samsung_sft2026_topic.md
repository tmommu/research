# Samsung Solve for Tomorrow 2026 (PH) — Proposed Topic

**Theme:** (3) Any local community problem solved with AI (overlaps Environmental Sustainability)
**Deadline:** entries accepted Sept 15 – Nov 2, 2026 (Grades 8–10, gov't-managed science high school, max 4 students + 1 adviser)

## Title

**LAMOK LENS: An On-Device AI Smartphone Tool that Lets Barangay Health Workers and Students Find, Map, and Eliminate Dengue Mosquito Breeding Sites Before Outbreaks Start**

## Why this topic

Dengue is a recurring, seasonal, nationwide public-health emergency in the Philippines, and it is *preventable at the source*: *Aedes* mosquitoes breed in small containers of stagnant water (tires, drums, pots, clogged gutters, discarded cups) inside and around homes. Barangay clean-up and "4S" campaigns exist, but inspection is manual, inconsistent, unrecorded, and reactive — it is usually intensified only after cases spike. Health workers are few, and nobody can see *which* streets hold the breeding sites.

Lamok Lens turns every phone a barangay already owns into a breeding-site detector and a hot-spot map, so clean-up effort goes where the risk is, before the cases appear.

> Evidence to cite in the paper (verify each from the primary source before use; none are quoted here from memory): latest DOH national dengue case/death counts, WHO dengue fact sheet, DOH "4S" strategy, PSA/DOH barangay health worker counts.

## The solution

1. **Capture** — a BHW or student photographs a yard, drum, gutter, or tire pile with a phone.
2. **Detect (on-device AI)** — a compact image model (TensorFlow Lite, INT8-quantized) labels likely breeding containers and whether they hold standing water. Runs **offline**, so it works in places with no signal and no data cost; no photos leave the phone by default (privacy).
3. **Act** — the app gives the household an instant, plain-language action (cover / empty / scrub / dispose) in Filipino.
4. **Map** — geotagged findings roll up into a barangay **risk heat map** and weekly "clean-up priority list" for the barangay health center, exportable as a simple CSV/PDF.
5. **Close the loop** — a before/after re-scan marks a site "cleared", giving a measurable clean-up rate.

Why AI rather than a checklist: it standardizes what counts as a breeding site across inspectors, trains non-experts as they use it, and produces structured data the barangay never had.

## Scoring map (official rubric)

| Criterion | Weight | How this topic earns it |
|---|---|---|
| **Design Innovation** | 20% | Moves dengue control from reactive to *predictive-by-inspection*; offline on-device detection plus a geotagged action map is a new combination for barangay use; student-collected data builds a local dataset that does not exist. |
| **Relevance to the Community** | 20% | Real, recurring, locally felt problem; directly serves barangay health workers and households; partnership with a barangay health center gives named, real users. |
| **Feasibility** | 20% | Uses phones already owned; free tooling (TFLite, open-source libs); small-scale pilot of one barangay or school zone; no special hardware; costs listed with a bill of materials. |
| **STEM Integration** | 15% | Biology (*Aedes* life cycle: eggs to adults in ~7–10 days, the basis of the weekly cycle), math/statistics (precision/recall, risk scoring), computer science (CNN, quantization), engineering (app design, offline-first). |
| **Sustainability** | 15% | Barangay can run it with no subscription or server; replicable to any barangay by retraining with local photos; supports the community's own clean-up routine; reduces insecticide reliance and healthcare burden. |
| **Clarity of Proposal** | 10% | One problem → one solution → one measured result; six-slide structure below. |

## Must-have evidence (to out-compete past winners)

Past winners (mangrove monitor, egg sorter, solar UV pest trap) were all *working, measured* prototypes. So:

- **Dataset:** collect and label a few hundred to a few thousand photos locally; document consent and privacy (no faces, no house numbers).
- **Model metrics:** report precision, recall and a confusion matrix on a held-out set *from different streets than training* (to avoid inflated scores); report model size and phone inference time.
- **Field pilot:** 1 barangay, 2–4 weeks; compare sites found by the tool vs. a manual walkthrough; record sites cleared and time per inspection.
- **Safety/ethics:** health-center sign-off, no personal data in the map, household consent, advice limited to source reduction (no medical claims).
- **Honest limits:** state what it cannot do (it detects breeding *sites*, not infection; not a diagnostic).

## Six-slide outline (PowerPoint option, PDF under 40 MB)

1. **Problem** — dengue, why breeding sites, why current inspection falls short (cited numbers).
2. **Solution** — Lamok Lens flow diagram (capture → detect → act → map → re-scan).
3. **STEM** — life cycle, model architecture, quantization, risk scoring.
4. **Prototype and results** — screenshots, metrics, pilot data.
5. **Feasibility and sustainability** — bill of materials, who maintains it, how another barangay adopts it.
6. **Impact and next steps** — projected/measured clean-up rate, partner letter, replication plan.

## Timeline to Nov 2

| By | Milestone |
|---|---|
| Week 1 | Barangay health center partner confirmed; consent and data protocol |
| Weeks 1–2 | Photo collection and labeling; baseline model |
| Weeks 2–3 | App prototype (offline detection, Filipino advice screen, map export) |
| Week 4 | Field pilot and metrics; re-train on gaps |
| Final days | Six-slide deck, proofread, PDF export, submit before Nov 2, 11:59 PM |

## Risks and mitigations

- *Model fails on new streets/lighting* → collect across times of day and locations; report the held-out-street score honestly.
- *Privacy* → on-device by default, strip location precision to the purok/street level on shared maps.
- *Overclaiming impact* → report pilot findings as pilot findings; avoid claiming reduced dengue cases from a few weeks of data.
- *Scope creep* → ship detect + advise + map; defer prediction/forecasting to "next steps".
