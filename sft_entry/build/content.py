# Shared content for the SAGIP Word entry, prototype design doc and 6-slide deck.
# Text avoids semicolons and em dashes. Items in [BRACKETS] are highlighted for the team to fill or verify.

SCHOOL = "Quezon City Science High School"
ADVISER = "Skjoukje U. Jemoya"
TEAM = ["Aaron Jed E. Campo, Grade 10", "Raya Kalayaan R. Amparo, Grade 10",
        "Ayeza Leigh F. Delos Santos, Grade 10", "Sophia Laureen A. Tado, Grade 10"]
THEME = "Environmental Sustainability through Technology"

TITLE = "SAGIP: Solar-Powered Estero Guardian with On-Chip AI"

DESC = ("Our device is a low-cost, solar-powered unit that lifts floating plastic out of a creek and counts each item with a tiny on-chip AI model. "
        "Barangay officials get a weekly offline report of what was removed, plus a secondary water-level alert for blockages. "
        "Built for about PHP 6,000 from local parts, it adds anonymized records to an open dataset that other barangays can copy.")

# ---------------- WORD ENTRY ----------------
S1 = [
    "Plastic reaches the sea through rivers, and the Philippines ranks near the top in every estimate. Global models placed it among the "
    "leading sources of mismanaged plastic waste (Jambeck et al., 2015) and of river emissions (Lebreton et al., 2017), and a later model "
    "built on measurements from more than 1,000 rivers kept Philippine rivers at the top (Meijer et al., 2021) [VERIFY: figures]. Small urban "
    "waterways such as Metro Manila's esteros feed these rivers. Monthly records from Greater Jakarta tie debris release to rainfall "
    "(Cordova & Nurhati, 2019) [VERIFY], and water hyacinth mats can trap plastic and carry it downstream [VERIFY: Schreyers et al., 2021].",
    "Two gaps keep the problem going. Removal is manual and unrecorded, so cleanups weigh bulk waste and learn nothing about its contents. "
    "Product-level evidence is also scarce. River plastic research still lacks long-term monitoring data (van Emmerik & Schwarz, 2020), and "
    "brand audits, though valuable, are periodic, labor-intensive and mostly land-based (Break Free From Plastic, 2019). The Extended Producer "
    "Responsibility Act of 2022 (RA 11898) obliges large companies to recover plastic packaging [VERIFY: scope], yet enforcement needs proof of "
    "which packaging reaches waterways. The government is expanding estero trash traps and has said recovery audits could check EPR compliance "
    "(Manila Bulletin, 2026).",
    "What is missing is a continuous, inexpensive record taken at the creek itself that one barangay can run. A secondary hazard shares the "
    "channel. Debris-choked creeks add to flooding in low-lying neighborhoods [VERIFY: MMDA and DPWH reports], and residents learn of a "
    "blockage only after the water rises.",
]

GOAL = ("We want barangays to treat the plastic in their creeks as measurable evidence instead of invisible waste. In the long run, "
        "this means cleaner waterways and community-owned data that shifts the burden of proof toward the companies that produce "
        "the packaging.")
OBJ = [
    ("1. Remove plastic from the creek.",
     " In an 8-week pilot at [ESTERO SITE] starting in December 2026, lift at least [TARGET] kg of floating debris out of the water "
     "and capture at least [X]% of the floating debris that reaches the boom, measured against a baseline week recorded before installation."),
    ("2. Prove what the plastic is.",
     " By November 20, 2026, train an on-device model that reaches at least 85% precision and recall on photographs from places it has "
     "not seen. Across the pilot, weekly device counts should stay within 15% of a trained hand audit."),
    ("3. Make it copyable.",
     " By March 2027, publish a free English and Filipino build guide and an open dataset, and help at least [2] other barangays or "
     "schools build a unit for about PHP 6,000 each."),
]

S3 = ("Primary beneficiaries are the [N] households of [BARANGAY AND PUROK] along [ESTERO], who bear the creek's pollution and flooding, "
      "and the barangay sanitation officers, who will empty the bin weekly and use the report. Secondary beneficiaries are the city solid-waste "
      "office and the DENR, who need item-level evidence for EPR enforcement, at least [2] neighboring barangays or schools that copy the design "
      "by March 2027, and downstream fisherfolk as less plastic reaches Manila Bay. We chose the barangay because it already organizes estero "
      "cleanups (Manila Bulletin, 2026), and community-based monitoring has a long record of building local ownership of environmental data "
      "(Conrad & Hilchey, 2011). [Add the barangay's household count and its current cleanup program.]")

S4_SELECT = ("We listed five community problems and scored each on significance, feasibility, STEM depth, replicability and originality. "
             "Creek plastic won. We can reach a creek, we can measure it weekly, and RA 11898 has just made item-level data useful. "
             "[Edit this to match your team's actual brainstorming steps.]")
S4_EXISTS = "Five kinds of work address parts of the problem."
PRIOR = [
    ("Cameras with deep learning (van Lieshout et al., 2020)", "Count floating plastic from bridge-mounted cameras, tested in Jakarta", "Monitor only and remove nothing"),
    ("Low-cost robotic boats (HydroSentinel, 2026)", "Detect and collect plastic with a small onboard model", "Need radio, charging and an operator"),
    ("Estero trash traps (Manila Bulletin, 2026)", "Remove plastic at scale", "Record bulk weight only"),
    ("River interceptors and booms (Schmaltz et al., 2020)", "Review technologies that prevent and collect river and marine plastic", "Few designs report item-level data [VERIFY]"),
    ("Brand audits (Break Free From Plastic, 2019)", "Name the brands behind plastic waste", "Periodic, manual, mostly land-based"),
]
S4_GAP = ("None of these lifts plastic, counts it and shares open data in a unit a barangay can afford. Our search was limited and found no "
          "such system. We therefore ask one research question: can a PHP 6,000 on-chip counter match a trained hand audit within 15%, "
          "and does continuous counting reveal rain-driven pulses of plastic that weekly audits miss?")

S5_STEM = ("STEM is the core of the design. Physics sets the boom angle, the lever and torque of the arm and the solar energy budget. "
           "Mathematics and statistics define precision, recall and count error. Computer science supplies the object-detection model, "
           "INT8 quantization, which shrinks a model about fourfold with little loss of accuracy (Jacob et al., 2018), and TensorFlow Lite for "
           "Microcontrollers, which runs it in kilobytes of memory (David et al., 2021). Engineering joins them in a floating, weatherproof "
           "structure. Our key message is that proof of what plastic reaches a creek can be continuous, cheap and community-owned. Pairing a "
           "collector with a counter delivers it best, because one inexpensive chip then yields cleanup and evidence together.")
S5_STEPS = [
    ("Trap.", " A V-shaped boom of reused PET bottles and bamboo guides surface debris to the bank, where a bar screen stops oversized items at the "
              "foot of a sloped mesh ramp. A wide-gapped deflector upstream pushes water hyacinth mats past the intake. The current does the herding, so the boom needs no energy."),
    ("Lift.", " A small geared DC motor, mounted above the flood line, turns a rake arm that sweeps debris up the ramp into a covered bin. It runs "
              "in short bursts and only when the camera sees plastic rather than vegetation. A sacrificial shear pin protects the gearbox, and a "
              "guard, stop switch and lockout protect people."),
    ("Protect.", " The chip reads motor current, ignores the start-up surge, and trips on sustained high current. A Hall sensor on the arm shaft "
                 "confirms the arm is moving, which exposes slipping on greasy surfaces. After a jam it stops, reverses briefly, retries at most "
                 "three times, then locks out and alerts the barangay. The motor driver defaults to off, so a crashed chip cannot leave the motor running."),
    ("Count.", " An ESP32-S3 camera on a post looks down at the water surface only, so no faces or houses appear. A compact object-detection model, "
               "quantized to INT8 and run with TensorFlow Lite for Microcontrollers, classifies each item. The camera views a pocket one to two meters "
               "away, so items appear large. Training photographs come from our own collection along the creek bank, labelled by students and "
               "checked by the adviser. Every week, students hand-count and weigh the bin, and that count is the accuracy test."),
    ("Report.", " A phone reads an offline Wi-Fi page hosted by the chip, and a script builds the weekly report and an anonymized open dataset. Each "
                "record stores class, time, water level and an image hash in an append-only log. A student volunteer tallies legible brand names from the "
                "stored photographs, since automated brand reading is not yet reliable. Plotting counts against rainfall shows whether plastic "
                "arrives in rain-driven pulses."),
    ("Warn (secondary).", " A waterproof ultrasonic sensor measures the distance to the water surface against a painted staff gauge. It raises an LED "
                          "and report alert when the level rises quickly or the bin nears capacity, and the arm stops above a set level."),
    ("Power.", " Planning figures, to be replaced by bench measurements. Duty-cycled electronics draw about 6 Wh per day and the arm "
               "about 0.3 Wh. A 10 W panel yields about 18 Wh per day at 3 effective sun-hours and 60% efficiency, and two 18650 cells store about "
               "18 Wh. On cloudy days the chip lengthens its capture interval when the battery is low."),
    ("Scope.", " SAGIP lifts light floating debris such as bottles, sachets, bags, foam and cups. Heavy or tangled items, hyacinth mats, sunken waste, "
               "sediment, oil and dissolved pollutants fall outside its reach, so we report a measured capture rate instead of claiming a clean creek."),
]
S5_PLAIN = ("Picture a sanitation worker who can tell a PET bottle from a sachet at a glance. The model is that skill, saved as a file of numbers. "
            "Quantization rounds the numbers to whole 8-bit values, like a gradebook recording 87 and not 87.3416, so the file fits in the chip's "
            "memory. No internet is needed.")

BUDGET = [
    ("ESP32-S3 camera board, microSD card, sealed enclosure", "1,800"),
    ("Solar panel (6 to 10 W), charge controller, two 18650 cells, converter", "1,300"),
    ("Boom rope and net, anchor and post, bin and staff gauge, wiring and fuse", "1,200"),
    ("Waterproof ultrasonic level sensor", "350"),
    ("Geared motor, driver, current and motion sensing, ramp, rake arm, bar screen, spare shear pins", "1,000"),
    ("Subtotal", "5,650"),
    ("Contingency", "350"),
    ("Total", "6,000"),
]
TOOLS = ("Arduino IDE or PlatformIO, Python with TensorFlow Lite, a borrowed soldering iron and multimeter, and our phones for photography. "
         "All prices are estimates to confirm locally.")
STAGES = [
    ("Stage 1, bench (about PHP 1,800).", " Train and test the model and measure power draw. Gate: precision and recall on held-out photographs meet the target."),
    ("Stage 2, passive trap (about PHP 2,500).", " Install the boom, deflector, screen, ramp, bin, post and solar supply. Gate: the boom survives [N] rain events and weekly counts fall within 15% of hand counts."),
    ("Stage 3, arm and sensor (about PHP 1,350).", " Fit the motor, jam protection and level sensor. Gate: a wet bench test with real hyacinth, estero silt and a little cooking oil, then solar-only lifts at the target jam rate."),
]
TIMELINE = ("Site visit, barangay letter and starter dataset by November 2. Model and a baseline week by November 20. Early results on December 7 if "
            "shortlisted. Full pilot from December to February. Build guide and further sites by March 2027.")
STAKE = [
    ("Barangay captain and sanitation officers:", " site approval, weekly emptying, and use of the reports under a one-page maintenance agreement."),
    ("City solid-waste office and DENR:", " use of the data and fit with existing estero programs [VERIFY: current programs]."),
    ("Adviser and school head:", " supervision and safety sign-off."),
    ("Students and residents:", " students build, label, count and report. Residents give consent and help keep the site clear."),
]
RISKS = [
    ("Hyacinth mats:", " a deflector, a vegetation class that stops the arm, and daily screen clearing."),
    ("Jams and burnout:", " shear pin, current and Hall sensing, three retries, driver off by default."),
    ("Oil and silt:", " motor mounted high, sealed bearings with marine grease, hooded lens."),
    ("Model errors in new light or water:", " test on unseen places and keep the weekly hand count."),
    ("Arm failure:", " the boom, bin and camera still work, so the data pilot survives."),
    ("Safety and privacy:", " no student enters the water, the arm is guarded, and the camera sees the water only."),
    ("Storms and theft:", " a quick-release line, electronics retrieved before a typhoon, and the camera mounted high."),
]

S7_INTRO = ("Success means floating plastic lifted from a real creek and a trustworthy weekly record of what it was. One unit lifts little mass, "
            "so its value lies in a design cheap enough to copy and data open enough to combine.")
OUTCOMES = [
    ("1. Less plastic in the creek:", " at least [TARGET] kg lifted in 8 weeks, with a capture rate of at least [X]% against the baseline week."),
    ("2. Trustworthy counts:", " weekly device error of 15% or less against the hand audit, at least 85% precision and recall on unseen places, and the rain-pulse question answered with data."),
    ("3. Replication:", " at least [2] more sites by March 2027 at about PHP 6,000 each, sharing one open data format. Until a second barangay builds a unit, we treat wider reach as a plan."),
]
VISION = ("We see a student-built, barangay-owned network of units along connected creeks that feeds one open dataset showing where plastic enters, "
          "which products dominate, and whether EPR commitments change what the water carries. Planned upgrades are a belt conveyor for higher "
          "volumes and a second camera angle. Each barangay added raises the value of every other unit's data. The pilot proves the method at one creek and claims no more.")
TAKEAWAY = ("The Philippines already knows who makes much of its plastic. SAGIP makes the proof continuous, cheap and community-owned, "
            "and it lifts some of the plastic out along the way.")

REFS = [
    "Break Free From Plastic and GAIA (2019). Plastics Exposed: How Waste Assessments and Brand Audits Are Helping Philippine Cities Fight Plastic Pollution.",
    "Conrad, C. C., & Hilchey, K. G. (2011). A review of citizen science and community-based environmental monitoring. Environmental Monitoring and Assessment, 176, 273-291. [VERIFY]",
    "Cordova, M. R., & Nurhati, I. S. (2019). Major sources and monthly variations in the release of land-derived marine debris from the Greater Jakarta area, Indonesia. Scientific Reports, 9, 18730. [VERIFY]",
    "David, R., et al. (2021). TensorFlow Lite Micro: Embedded machine learning for TinyML systems. Proceedings of Machine Learning and Systems, 3. [VERIFY]",
    "HydroSentinel (2026). An IoT-enabled autonomous surface vehicle for dual-scale riverine plastic detection and remediation. ScienceDirect. [add authors]",
    "Jacob, B., et al. (2018). Quantization and training of neural networks for efficient integer-arithmetic-only inference. CVPR. [VERIFY]",
    "Jambeck, J. R., et al. (2015). Plastic waste inputs from land into the ocean. Science, 347, 768-771.",
    "Lebreton, L. C. M., et al. (2017). River plastic emissions to the world's oceans. Nature Communications, 8, 15611.",
    "Manila Bulletin (August 24, 2026). Report on government estero trash traps and EPR audits. [add headline and byline]",
    "Meijer, L. J. J., et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions into the ocean. Science Advances. [VERIFY]",
    "Republic Act No. 11898 (2022). Extended Producer Responsibility Act of 2022. [VERIFY]",
    "Schmaltz, E., et al. (2020). Plastic pollution solutions: Emerging technologies to prevent and collect marine plastic pollution. Environment International, 144, 106067. [VERIFY]",
    "Schreyers, L., et al. (2021). Water hyacinth and river plastic transport. [VERIFY: full citation]",
    "van Emmerik, T., & Schwarz, A. (2020). Plastic debris in rivers. WIREs Water, 7, e1398. [VERIFY]",
    "van Lieshout, C., et al. (2020). Automated river plastic monitoring using deep learning and cameras. Earth and Space Science, 7, e2019EA000960.",
]
