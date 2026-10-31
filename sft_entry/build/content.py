# Shared content for the SAGIP Word entry, prototype design doc and 6-slide deck.
# Text avoids semicolons and em dashes. Bracketed items, if any, are highlighted for the team to fill or verify.

SCHOOL = "Quezon City Science High School"
ADVISER = "Skjoukje U. Jemoya"
TEAM = ["Aaron Jed E. Campo, Grade 10", "Raya Kalayaan R. Amparo, Grade 10",
        "Ayeza Leigh F. Delos Santos, Grade 10", "Sophia Laureen A. Tado, Grade 10"]
THEME = "Environmental Sustainability through Technology"

TITLE = "SAGIP: Autonomous Solar Vessel for Plastic Recovery and Monitoring"

DESC = ("SAGIP is a low-cost, solar-powered robot boat that patrols a creek, goes to floating debris, lifts it onto a conveyor and names each item using a small on-chip neural network running on an ESP32 chip. "
        "Barangay officials get a weekly report of the plastic collected by type and weight through an offline phone page, plus a float-switch flood alarm at the bank. "
        "Built for about PHP 15,800 from local parts, it adds anonymized records to an open dataset that other barangays can copy.")

# ---------------- WORD ENTRY ----------------
S1 = [
    "Plastic reaches the sea through rivers, and the Philippines is the largest source. A global model of more than 1,000 rivers estimated that "
    "Philippine rivers carry about 356,000 tonnes of plastic to the sea each year, the most of any country, and ranked the Pasig River first (Meijer et al., 2021). "
    "These are model estimates and not measurements. "
    "Floating plastic transport rises with river discharge, reaching up to six times its normal rate at peak flow (van Emmerik et al., 2022), "
    "and in the Saigon River water hyacinth mats carried most of the floating plastic that observers counted (Schreyers et al., 2021).",
    "Two gaps persist. Cleanups weigh bulk waste and record nothing about its contents, and product-level evidence is scarce because community monitoring of "
    "freshwater plastic is rare (Cook et al., 2021) and brand audits are periodic and mostly land-based (Break Free From Plastic, 2021). "
    "RA 11898, the Extended Producer Responsibility Act of 2022, obliges large companies to recover a rising share of their plastic packaging, "
    "and the DENR has begun auditing reported recovery rates (Food Packaging Forum, 2026). Enforcement needs proof of which packaging reaches waterways.",
    "What is missing is a sustainable, inexpensive record taken at the creek itself that one barangay can run. Large systems are arriving, such as solar "
    "Interceptor barriers planned for the Pasig and Meycauayan rivers (Manila Bulletin, June 2026), "
    "but a narrow estero needs a unit a barangay can afford. Clogged waterways also worsen flooding, and residents learn of a blockage only after the water rises.",
]

GOAL = ("We want barangays to treat creek plastic as measurable evidence instead of invisible waste. In the long run, "
        "this means cleaner waterways and community-owned data that shifts the burden of proof toward packaging producers.")
OBJ = [
    ("1. Remove and measure plastic.",
     " In an 8-week pilot at Dario River starting in January 2027, remove at least 50% of floating debris entering a 30 m patrol stretch, "
     "measured by hand-net sampling below the downstream barrier against a baseline week, lift at least 20 kg of plastic and log at least 1,000 classified items."),
    ("2. Prove what the plastic is.",
     " By December 5, 2026, train an on-device 2D convolutional neural network that reaches at least 85% precision and recall on photographs "
     "from places it has not seen, with weekly counts within 15% of a trained hand audit."),
    ("3. Make it copyable.",
     " By March 2027, publish a free English and Filipino build guide (parts list, wiring, code) and an open dataset of anonymized counts and photographs, and help at least 2 other barangays or "
     "schools build a unit for about PHP 15,800 each."),
]

S3 = ("Primary beneficiaries are the households along Dario River in Quezon City, who bear the creek's pollution "
      "and flooding, gain a flood alarm and see monthly results on a Plastic Trend Scoreboard at the Barangay Hall, and the sanitation officers, who empty the bins and use the report. "
      "Secondary beneficiaries are the city solid-waste office and the DENR, who need item-level evidence, and the barangays or schools that "
      "copy the design. A barangay-run record adds new data where citizen science is rare (Cook et al., 2021) "
      "and fits Quezon City's river programs (Philstar, 2025).")

S4_SELECT = ("We considered community problems against five criteria: significance, feasibility, STEM depth, replicability and originality. "
             "Creek plastic fit best because we can reach a creek and measure it weekly. RA 11898 has just made item-level data useful.")
S4_EXISTS = ""
PRIOR = [
    ("Cameras with deep learning (Kataoka et al., 2024)", "Detect floating plastic in fixed river camera images", "Monitor only, remove nothing"),
    ("Solar river barriers (The Ocean Cleanup, 2026)", "Intercept and lift river plastic with a solar conveyor", "Built for large rivers such as the Pasig"),
    ("AI cleanup boats (Manila Bulletin, 2025)", "Collect plastic with a solar AI vessel in a Pasig pilot", "Built for a large river, not a barangay estero"),
    ("Tiny on-chip classifiers (Mendez-Cruz et al., 2024)", "Classify microplastics and waste on an ESP32 camera, 91.7% accuracy on 229 images", "Controlled tests only, no collection or field data"),
    ("Trash traps (Philstar, 2022)", "Remove plastic in bulk at river tributaries", "Record bulk weight only"),
    ("Brand audits (Break Free From Plastic, 2021)", "Name the brands behind plastic waste", "Periodic, manual, mostly land-based"),
]
S4_GAP = ("None of these patrols a creek, collects plastic, counts it item by item and shares open data at a price a barangay can pay. "
          "Our search found no system that does all four. We therefore ask one question: can a PHP 15,800 robot boat match a trained hand audit within 15%, "
          "and does continuous counting reveal rain-driven pulses that weekly audits miss?")

S5_STEM = ("Physics sets buoyancy, thrust, belt torque and the solar energy budget, and mathematics defines precision, recall and count error. "
           "A small 2D convolutional neural network (CNN) with INT8 quantization, which shrinks a model about fourfold with little loss of accuracy "
           "(Gholami et al., 2021), runs on TensorFlow Lite for Microcontrollers (David et al., 2021).")
S5_PARAS = [
    "Two sealed, foam-filled 6-inch PVC floats carry a 1.4 m deck. The boat measures about 1.7 by 0.85 by 0.55 m, draws about 10 cm and weighs about 30 kg. "
    "A wide beam and a low battery keep it stable, and a tilt sensor stops the motors past 20 degrees. "
    "It follows a preset route between two floating barriers 30 m apart, steering with two thrusters. "
    "Side ultrasonic sensors keep it off the bank, bump switches cover the bow, and it docks when its bins are full or its battery is low. "
    "The upstream barrier is a 10 mm rope with a float every 30 cm, angled at 30 degrees to the flow so hyacinth mats slide to the bank. "
    "The downstream barrier is the same rope strung straight across, and a pond test checks sag and hold.",
    "A bow ESP32-CAM runs a small INT8 object detector that separates plastic from plants. The boat steers to the nearest plastic, "
    "and a scoop lifts it onto a cleated belt whose pockets hold one item each. "
    "Items reach an ESP32-S3 camera singly under a skirted black hood with a fixed LED strip, so every photograph is lit the same way. "
    "A hydrophobic film, angled window and desiccant pack keep the housing clear of fog. "
    "The CNN labels each item as PET bottle, sachet or film, bag, foam, cup, plant or other, and a blob count against an empty-belt photograph flags two items in one frame as mixed. "
    "A servo gate sends plastic to Bin A and plants, mixed or unsure items to Bin B for a hand count.",
    "We train in Keras from small pretrained MobileNet-style networks and quantize to INT8. Photographs are augmented with color shifts, blur, rotation, crops, "
    "random erasing and synthetic mud and droplets to hold accuracy in muddy water. "
    "The chip reads belt and thruster current and, after a jam, reverses, retries up to three times, then stops and docks, and drivers default to off. "
    "Each item is logged with class, time and image hash on a microSD card. A docked phone reads an offline Wi-Fi page with the weekly report and an open dataset, "
    "and each month the barangay posts a Plastic Trend Scoreboard at the Barangay Hall showing top plastic types, estimated kilograms and flood alarms.",
    "Counts become estimated kilograms, corrected by a weekly weigh-in, and a weekly sheet lists items by type with junk-shop value as evidence for RA 11898. "
    "A solar node on the bank carries float switches at watch, alert and danger levels on a staff gauge, with a buzzer and a small LED. "
    "The boat stays docked from the alert level.",
    "A 30 W panel on the deck yields about 54 Wh per day (planning figure, 3 sun-hours at 60% efficiency) and charges a sealed 12 V 12 Ah lead-acid battery of about 144 Wh. "
    "A 20-minute patrol uses about 25 Wh, and a low battery skips it. "
    "A camera board draws about 180 mA awake and 6 mA asleep at 5 V (datasheet values), about 22 Wh a day against 0.7 Wh, so docked boards sleep and wake on a timer. "
    "On patrol the bow camera idles until it sees plastic, the belt camera and LED wake only for an item, and the flood node reports every ten minutes.",
    "The floats, bins and stainless hardware are materials local junk shops take, foam only keeps a holed float afloat, and the lead-acid battery returns to a dealer. "
    "The flood node's protected 18650 cell sits in an IP67 box with overcharge and over-discharge protection. "
    "SAGIP lifts light floating debris, not heavy or tangled items or sunken waste, so we report a measured capture rate for one creek stretch.",
]
S5_FIG2_AFTER = 2   # Figure 2 follows the third paragraph
S5_PLAIN = ("Put plainly, the model is a sanitation worker's eye for bottles and sachets, saved as a file of numbers.")

BUDGET = [
    ("Two 6-inch PVC floats, foam, frame and deck", "3,228"),
    ("Two 12 V thrusters and dual driver", "2,410"),
    ("Cleated conveyor, gear motor and driver", "1,500"),
    ("ESP32-S3 camera board, hood, LED, enclosure", "700"),
    ("ESP32-CAM bow detector", "600"),
    ("Tilt and ultrasonic sensors, bump switches", "680"),
    ("Gate servo and reused bins", "300"),
    ("12 V 12 Ah battery, converters, fuses, wiring", "2,400"),
    ("30 W solar panel and 20 A charge controller", "1,100"),
    ("Waterproofing and hardware", "500"),
    ("Flood node: ESP32, float switches, buzzer, mini panel, cell, gauge", "1,000"),
    ("Bank dock and two barriers (rope, floats, post)", "600"),
    ("Subtotal", "15,018"),
    ("Contingency", "782"),
    ("Total", "15,800"),
]
TOOLS = ("Python, Keras, TensorFlow Lite for Microcontrollers, a borrowed multimeter, a kitchen scale and our phones. "
         "Prices are online-shop estimates, and the barangay may give rope, floats, a post and bins in kind.")
STAGES = [
    ("Stage 1, bench (about PHP 6,000).", " Conveyor, camera, CNN, gate, battery and panel. Gate: 85% precision and recall on held-out photographs and a simulated patrol on battery."),
    ("Stage 2, boat (about PHP 7,400).", " Floats, deck, thrusters, bow detector and sensors. Gate: float and tilt tests, then a pond test where the boat scoops at least 70% of 20 items placed 2 to 5 m ahead."),
    ("Stage 3, dock, barriers and flood node (about PHP 1,600).", " Gate: the boat patrols between barriers without help, and the flood alarm sounds at all three marks in a bucket test."),
]
TIMELINE = ("Site visit, barangay letter and starter dataset by November 2. If shortlisted, mentorship from November 16 to December 5 "
            "finishes Stage 1 and builds a scaled mock-up and flood node for the December 7 pitch. The pilot runs January to February 2027 if supported.")

STAKE = [
    ("Barangay captain and sanitation officers:", " site approval, bin emptying, the flood alarm and reports under a one-page agreement."),
    ("City solid-waste office and DENR:", " data use and fit with Quezon City's river programs."),
    ("Adviser and school head:", " supervision and safety sign-off."),
    ("Students and residents:", " students build, label and count, and residents give consent."),
]
RISKS = [
    ("Manual labor:", " people still empty the bins, clear snags and wipe the lenses, and we log those hours."),
    ("Stability and navigation:", " foam-filled floats, a tilt cut-off, pond tests, barriers that set the stretch and a stop switch."),
    ("Fast water and permission:", " the boat stays docked from the alert level, and the stretch needs barangay, city and DENR approval."),
    ("Hyacinth and snags:", " the upstream barrier turns mats aside, the detector sends plants to Bin B and current sensing reverses a jam."),
    ("Model errors:", " test on unseen places, send unsure and mixed items to Bin B and keep the weekly hand count."),
    ("Safety, privacy, theft:", " no student rides the boat or enters the water, the cameras see only the water, and the boat is docked when unattended."),
]

S7_INTRO = ("Success means plastic lifted from a real creek, a trustworthy weekly record of what it was and a flood alarm that works.")
OUTCOMES = [
    ("1. Less plastic in the creek:", " at least 50% of floating debris removed against the baseline week and 20 kg lifted in 8 weeks."),
    ("2. Trustworthy counts and warnings:", " at least 1,000 classified items, weekly error of 15% or less, 85% precision and recall on unseen places and a flood alarm at all three marks."),
    ("3. Replication:", " at least 2 more sites by March 2027 at about PHP 15,800 each, one open data format and weekly labor hours reported."),
]
VISION = ("We see a student-built, barangay-owned network of units along connected creeks that feeds one open dataset showing where plastic enters, "
          "which products dominate, and whether EPR commitments change what the water carries.")
TAKEAWAY = ("The Philippines already knows who makes much of its plastic. SAGIP makes the proof continuous, cheap and community-owned.")

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
