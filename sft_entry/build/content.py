# Shared content for the SAGIP Word entry, prototype design doc and 6-slide deck.
# Text avoids semicolons and em dashes. Items in [BRACKETS] are highlighted for the team to fill or verify.

SCHOOL = "Quezon City Science High School"
ADVISER = "Skjoukje U. Jemoya"
TEAM = ["Aaron Jed E. Campo, Grade 10", "Raya Kalayaan R. Amparo, Grade 10",
        "Ayeza Leigh F. Delos Santos, Grade 10", "Sophia Laureen A. Tado, Grade 10"]
THEME = "Environmental Sustainability through Technology"

TITLE = "SAGIP: Floating Solar-Powered Estero Guardian with On-Chip AI"

DESC = ("SAGIP is a low-cost, floating, solar-powered raft that filters plastic out of a creek, lifts it into a sorted bin and names each item with a small on-chip image model. "
        "Barangay officials get a weekly offline report of what the creek carried, plus a secondary water-level alert for blockages. "
        "Built for about PHP 12,000 from local parts, it adds anonymized records to an open dataset that other barangays can copy.")

# ---------------- WORD ENTRY ----------------
S1 = [
    "Plastic reaches the sea through rivers, and the Philippines ranks near the top in every estimate. A global model built on measurements from "
    "more than 1,000 rivers ranked the Philippines first among countries and the Pasig River first among rivers, as a model estimate and not a measurement (Meijer et al., 2021). Floating plastic transport "
    "rises sharply with river discharge, reaching up to six times its normal rate at peak flow in a year-long monitoring study (van Emmerik et al., 2022), "
    "and in the Saigon River water hyacinth mats carried most of the floating plastic that observers counted (Schreyers et al., 2021).",
    "Two gaps keep the problem going. Removal is manual and unrecorded, so cleanups weigh bulk waste and learn nothing about its contents. "
    "Product-level evidence is also scarce. Community-run monitoring of freshwater plastic is still rare (Cook et al., 2021), and "
    "brand audits, though valuable, are periodic, labor-intensive and mostly land-based (Break Free From Plastic, 2021). The Extended Producer "
    "Responsibility Act of 2022 (RA 11898) obliges large companies to recover a rising share of their plastic packaging, and the DENR has begun "
    "auditing reported recovery rates (Food Packaging Forum, 2026). Enforcement still needs proof of which packaging reaches waterways.",
    "What is missing is a continuous, inexpensive record taken at the creek itself that one barangay can run. Large systems are arriving, such as solar-powered "
    "Interceptor barriers planned for the Pasig and Meycauayan rivers (Manila Bulletin, June 2026), but a narrow estero needs a unit a barangay can afford. A secondary hazard shares the channel. Clogged waterways "
    "worsen flooding in low-lying neighborhoods, and residents learn of a blockage only after the water rises.",
]

GOAL = ("We want barangays to treat the plastic in their creeks as measurable evidence instead of invisible waste. In the long run, "
        "this means cleaner waterways and community-owned data that shifts the burden of proof toward the companies that produce "
        "the packaging.")
OBJ = [
    ("1. Remove and measure plastic.",
     " In an 8-week pilot at [ESTERO SITE] starting in December 2026, capture at least 50% of the floating debris that reaches the boom, "
     "measured against a baseline week recorded before installation, lift at least 20 kg of plastic and log at least 1,000 classified items."),
    ("2. Prove what the plastic is.",
     " By November 20, 2026, train an on-device 2D convolutional neural network that reaches at least 85% precision and recall on photographs "
     "from places it has not seen. Across the pilot, weekly device counts should stay within 15% of a trained hand audit."),
    ("3. Make it copyable.",
     " By March 2027, publish a free English and Filipino build guide and an open dataset, and help at least 2 other barangays or "
     "schools build a unit for about PHP 12,000 each."),
]

S3 = ("Primary beneficiaries are the [N] households of [BARANGAY AND PUROK] along [ESTERO SITE] in Quezon City, who bear the creek's pollution "
      "and flooding, and the barangay sanitation officers, who will empty the bins weekly and use the report. Secondary beneficiaries are the "
      "city solid-waste office and the DENR, who need item-level evidence, at least 2 neighboring barangays or schools that "
      "copy the design by March 2027, and downstream fisherfolk as less plastic reaches Manila Bay. We chose a barangay estero because Quezon City "
      "already runs river programs with partners (Philstar, 2025), and citizen-science monitoring of freshwater plastic is still rare, so a barangay-run record adds new data (Cook et al., 2021). [Add the barangay's household count and its current cleanup program.]")

S4_SELECT = ("We listed five community problems and scored each on significance, feasibility, STEM depth, replicability and originality. "
             "Creek plastic won. We can reach a creek, we can measure it weekly, and RA 11898 has just made item-level data useful. We then fitted "
             "the design to about PHP 12,000. "
             "[Edit this to match your team's actual brainstorming steps.]")
S4_EXISTS = "Six kinds of work address parts of the problem."
PRIOR = [
    ("Cameras with deep learning (Kataoka et al., 2024)", "Detect floating plastic in images from fixed river cameras", "Monitor only and remove nothing"),
    ("Solar river barriers (The Ocean Cleanup, 2026)", "Intercept and lift river plastic with a solar-powered conveyor", "Built for large rivers, announced for the Pasig and Meycauayan"),
    ("AI cleanup boats (Manila Bulletin, 2025)", "Collect plastic with a solar-powered, AI-enabled vessel in a Pasig pilot", "Mobile boats on a large river, not fixed estero units"),
    ("Tiny on-chip classifiers (Mendez-Cruz et al., 2024)", "Classify microplastics and waste on an ESP32 camera, 91.7% accuracy on 229 images", "Controlled tests only, no collection, no field data"),
    ("Trash traps (Philstar, 2022)", "Remove plastic in bulk at river tributaries", "Record bulk weight only"),
    ("Brand audits (Break Free From Plastic, 2021)", "Name the brands behind plastic waste", "Periodic, manual, mostly land-based"),
]
S4_GAP = ("None of these lifts plastic, counts it item by item and shares open data in a unit a barangay can afford, and the tiny classifiers have not left the lab. Our search was limited and found no "
          "such system. We therefore ask one research question: can a PHP 12,000 on-chip counter match a trained hand audit within 15%, "
          "and does continuous counting reveal rain-driven pulses of plastic that weekly audits miss?")

S5_STEM = ("STEM is the core of the design. Physics sets the raft's buoyancy, the boom angle, the lever and torque of the arm and the solar energy budget. "
           "Mathematics and statistics define precision, recall and count error. Computer science supplies a small 2D convolutional neural network "
           "(CNN) with INT8 quantization, which shrinks a model about fourfold with little loss of accuracy (Gholami et al., 2021), running on "
           "TensorFlow Lite for Microcontrollers (David et al., 2021). Engineering joins them in a weatherproof structure. Our key message is "
           "that proof of what plastic reaches a creek can be continuous, cheap and community-owned.")
S5_STEPS = [
    ("Float.", " Four sealed 200 L plastic drums carry a deck frame. For a planning load of about 60 kg the raft rides high. Two mooring lines hold the bow upstream, and a haul line lets adults pull the raft to the bank to empty the bins or to shelter from a typhoon. It sits along one side of the channel and leaves a clear flow path."),
    ("Catch and filter.", " A boom of reused PET bottles with a net skirt guides surface debris to the raft's bow, and a wide-gapped deflector upstream turns water hyacinth mats aside. "
                          "Coarse bars stop large debris and a fine mesh basket catches small plastic. Both slope so leaves and mud shed."),
    ("Lift.", " A worm-gear DC motor on the deck turns a short rake arm that sweeps debris up the ramp in bursts. A sacrificial shear pin "
              "protects the gearbox. A guard, stop switch and lockout protect people."),
    ("Protect.", " The chip reads motor current and adjusts speed. Under heavy load it slows and keeps torque, and under light load it speeds up, within a limit "
                 "set by the solar budget. A Hall sensor confirms the arm is moving. If current rises sharply, the arm reverses briefly, retries at most three "
                 "times, then locks out and alerts the barangay. The driver defaults to off, so a crashed chip cannot leave the motor running."),
    ("Count and sort.", " An ESP32-S3 camera looks down at a fixed landing plate under a hood with LED lighting, so every item appears in the same light. "
                        "The CNN classifies it as PET bottle, sachet or film, bag, foam, cup, plant or other. A servo gate then drops plastic into Bin A "
                        "and plants or low-confidence items into Bin B for a person to check. If the servo fails, items still land in one bin and are still "
                        "counted. Training photographs come from our own collection along the creek bank, labelled by students and checked by the adviser. "
                        "Items landing together may count as one, so weekly hand counts of both bins test accuracy."),
    ("Software.", " We train in Keras on a laptop, start from a small pretrained MobileNet-style network at 96 by 96 pixels, quantize to INT8 and deploy with "
                  "TensorFlow Lite for Microcontrollers on the ESP32-S3."),
    ("Report.", " A phone reads an offline Wi-Fi page hosted by the chip. Each record stores class, time, water level and an image hash in an append-only log "
                "on a microSD card, with time from a clock module. A script builds the weekly report and an anonymized open dataset, and counts are plotted "
                "against rainfall."),
    ("Warn (secondary).", " A waterproof ultrasonic sensor measures the distance to the water against a painted staff gauge. It raises an alert when the level "
                          "rises quickly or a bin nears capacity, and the arm stops above a set level."),
    ("Power.", " Planning figures until measured. The camera runs only when an item is present. Electronics draw about 6 Wh per day "
               "and the arm about 0.3 Wh. A 10 W panel yields about 18 Wh per day at 3 effective sun-hours and 60% efficiency, and two 18650 cells store "
               "about 18 Wh. When the battery is low the chip lengthens its capture interval."),
    ("Scope.", " SAGIP lifts light floating debris such as bottles, sachets, bags, foam and cups. Heavy or tangled items, hyacinth mats, sunken waste "
               "and dissolved pollutants fall outside its reach, so we report a measured capture rate."),
]
S5_PLAIN = ("The model is the skill of a sanitation worker who can tell a PET bottle from a sachet at a glance, saved as a file of numbers. "
            "Quantization rounds them like a gradebook recording 87, not 87.3416, so the file fits the chip. No internet is needed.")

BUDGET = [
    ("ESP32-S3 camera board with PSRAM, microSD card, clock module, sealed enclosure with light hood", "1,850"),
    ("10 W solar panel, charge controller, two 18650 cells, converter", "1,400"),
    ("Wiring, fuse, switch, two bins, staff gauge", "400"),
    ("Waterproof ultrasonic level sensor", "350"),
    ("Worm-gear motor, driver, current and motion sensing, servo gate", "1,000"),
    ("Ramp, rake arm, coarse bars, fine mesh, spare shear pins", "500"),
    ("Pontoons: four reused 200 L drums with sealed caps", "2,000"),
    ("Deck frame and guard rails", "1,900"),
    ("Boom arms, net skirt, floats and rope", "600"),
    ("Mooring: two anchors, swivels, rope, quick release, bank haul line and cleat", "900"),
    ("Stainless hardware, sealant and waterproofing", "600"),
    ("Subtotal", "11,500"),
    ("Contingency", "500"),
    ("Total", "12,000"),
]
TOOLS = ("Python, Keras, TensorFlow Lite for Microcontrollers, Arduino IDE, a borrowed multimeter, a kitchen scale and our phones. "
         "Prices are estimates, and we will ask the barangay for drums, rope and bins in kind.")
STAGES = [
    ("Stage 1, bench (about PHP 1,850).", " Train and test the model and measure power draw. Gate: precision and recall on held-out photographs reach 85%."),
    ("Stage 2, raft and passive trap (about PHP 8,150).", " Build the drums, deck, boom, intake, mooring, solar supply, bins and level sensor. Gate: a pond test with a 60 kg dummy load shows the raft level and stable, then it survives at least 3 rain events at the site and weekly counts fall within 15% of hand counts."),
    ("Stage 3, arm and sorter (about PHP 1,500).", " Fit the ramp, motor, jam protection, current sensing and servo gate. Gate: a wet bench test with real hyacinth, silt and a little cooking oil."),
]
TIMELINE = ("Site visit, barangay letter and starter dataset by November 2. Model and a baseline week by November 20. Early results on December 7 if "
            "shortlisted. Pilot from December to February. Build guide and further sites by March 2027.")
STAKE = [
    ("Barangay captain and sanitation officers:", " site approval, weekly emptying, and use of the reports under a one-page maintenance agreement."),
    ("City solid-waste office and DENR:", " use of the data and fit with Quezon City's river programs (Philstar, 2025)."),
    ("Adviser and school head:", " supervision and safety sign-off."),
    ("Students and residents:", " students build, label, count and report. Residents give consent."),
]
RISKS = [
    ("Manual labor:", " people must still empty both bins weekly, clear the screen after storms, wipe the lens and check the battery. We will log those hours."),
    ("Raft stability and mooring:", " a pond test with a dummy load, two mooring lines and a quick-release haul line, and the raft is hauled ashore before a typhoon."),
    ("Blocking the channel and permission:", " the raft takes one side only and needs barangay and city approval."),
    ("Hyacinth mats:", " a deflector, sloped filters and a plant class that sends mats to Bin B."),
    ("Jams and burnout:", " shear pin, current and Hall sensing, three retries, driver off by default."),
    ("Oil and silt:", " motor mounted high, sealed bearings with marine grease, hooded lens."),
    ("Model errors in new light or water:", " test on unseen places, send unsure items to Bin B and keep the weekly hand count."),
    ("Safety, privacy, theft:", " no student boards the raft or enters the water, the arm is guarded, the camera sees the water only, and electronics are retrieved before a typhoon."),
]

S7_INTRO = ("Success means floating plastic lifted from a real creek and a trustworthy weekly record of what it was. One unit lifts little mass, "
            "so its value lies in a design cheap to copy and data open to combine.")
OUTCOMES = [
    ("1. Less plastic in the creek:", " a capture rate of at least 50% against the baseline week and at least 20 kg lifted in 8 weeks."),
    ("2. Trustworthy counts:", " at least 1,000 classified items, weekly device error of 15% or less against the hand audit, and at least 85% precision and recall on unseen places."),
    ("3. Replication:", " at least 2 more sites by March 2027 at about PHP 12,000 each, sharing one open data format, with weekly labor hours reported so other barangays know the real workload."),
]
VISION = ("We see a student-built, barangay-owned network of units along connected creeks that feeds one open dataset showing where plastic enters, "
          "which products dominate, and whether EPR commitments change what the water carries. Planned upgrades are a belt conveyor for higher "
          "volumes and a second camera angle.")
TAKEAWAY = ("The Philippines already knows who makes much of its plastic. SAGIP makes the proof continuous, cheap and community-owned, "
            "and it lifts some of the plastic out along the way.")

REFS = [
    "Break Free From Plastic (2021). BRANDED Volume IV: Holding corporations accountable for the plastic and climate crisis.",
    "Cook, S., Abolfathi, S., & Gilbert, N. I. (2021). Goals and approaches in the use of citizen science for exploring plastic pollution in freshwater ecosystems: A review. Freshwater Science, 40.",
    "David, R., et al. (2021). TensorFlow Lite Micro: Embedded machine learning for TinyML systems. Proceedings of Machine Learning and Systems, 3.",
    "Food Packaging Forum (2026). Philippines steps up enforcement of plastic packaging recovery requirements. foodpackagingforum.org",
    "Gholami, A., et al. (2021). A survey of quantization methods for efficient neural network inference. arXiv:2103.13630.",
    "Kataoka, T., Yoshida, T., & Yamamoto, N. (2024). Instance segmentation models for detecting floating macroplastic debris from river surface images. Frontiers in Earth Science, 12, 1427132.",
    "Manila Bulletin (June 6, 2026). DENR, The Ocean Cleanup forge alliance for Pasig River.",
    "Manila Bulletin (October 12, 2025). AI-powered robot waterway cleaning vehicle launched in Pasig.",
    "Mendez-Cruz, Silva-Cuzqui, et al. (2024). Proof of concept: A TinyML-based image classifier for detecting microplastics and waste in simulated marine environments. IEEE.",
    "Meijer, L. J. J., et al. (2021). More than 1,000 rivers account for 80% of global riverine plastic emissions. Science Advances, 7, eaaz5803.",
    "Philstar (August 28, 2025). Quezon City government, SMC team up for river cleanup.",
    "Philstar (July 14, 2022). DENR-EMB to install trash traps in polluted rivers.",
    "Republic Act No. 11898 (2022). Extended Producer Responsibility Act of 2022.",
    "Schreyers, L., et al. (2021). Plastic plants: The role of water hyacinths in plastic transport in tropical rivers. Frontiers in Environmental Science, 9, 686334.",
    "The Ocean Cleanup (2026). Meycauayan plastic Interceptor rollout. Press release.",
    "van Emmerik, T. H. M., et al. (2022). Hydrology as a driver of floating river plastic transport. Earth's Future, 10, e2022EF002811.",
]
