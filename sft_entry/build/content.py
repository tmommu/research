# Shared content for the SAGIP Word entry, prototype design doc and 6-slide deck.
# Text avoids semicolons and em dashes. Items in [BRACKETS] are highlighted for the team to fill or verify.

SCHOOL = "Quezon City Science High School"
ADVISER = "Skjoukje U. Jemoya"
TEAM = ["Aaron Jed E. Campo, Grade 10", "Raya Kalayaan R. Amparo, Grade 10",
        "Ayeza Leigh F. Delos Santos, Grade 10", "Sophia Laureen A. Tado, Grade 10"]
THEME = "Environmental Sustainability through Technology"

TITLE = "SAGIP: Autonomous Solar Skimmer Boat with On-Chip AI"

DESC = ("SAGIP is a low-cost, solar-powered robot boat that patrols a creek, goes to floating debris, lifts it onto a conveyor and names each item with a small on-chip image model. "
        "Barangay officials get a weekly offline report of the plastic collected by type and weight, plus a float-switch flood alarm at the bank. "
        "Built for about PHP 16,000 from local parts, it adds anonymized records to an open dataset that other barangays can copy.")

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
    "Interceptor barriers planned for the Pasig and Meycauayan rivers (Manila Bulletin, June 2026) and an AI boat piloted on the Pasig (Manila Bulletin, October 2025), "
    "but a narrow estero needs a unit a barangay can afford. Clogged waterways also worsen flooding, and residents learn of a blockage only after the water rises.",
]

GOAL = ("We want barangays to treat the plastic in their creeks as measurable evidence instead of invisible waste. In the long run, "
        "this means cleaner waterways and community-owned data that shifts the burden of proof toward packaging producers.")
OBJ = [
    ("1. Remove and measure plastic.",
     " In an 8-week creek pilot at [ESTERO SITE] starting in January 2027, remove at least 50% of the floating debris that enters a patrol stretch of about 30 m, "
     "measured by hand-net sampling below the downstream barrier against a baseline week, lift at least 20 kg of plastic and log at least 1,000 classified items."),
    ("2. Prove what the plastic is.",
     " By December 5, 2026, train an on-device 2D convolutional neural network that reaches at least 85% precision and recall on photographs "
     "from places it has not seen. Across the pilot, weekly device counts should stay within 15% of a trained hand audit."),
    ("3. Make it copyable.",
     " By March 2027, publish a free English and Filipino build guide and an open dataset, and help at least 2 other barangays or "
     "schools build a unit for about PHP 16,000 each."),
]

S3 = ("Primary beneficiaries are the [N] households of [BARANGAY AND PUROK] along [ESTERO SITE] in Quezon City, who bear the creek's pollution "
      "and flooding and gain a flood alarm, and the barangay sanitation officers, who will empty the bins and use the report. Secondary beneficiaries are the "
      "city solid-waste office and the DENR, who need item-level evidence, at least 2 neighboring barangays or schools that "
      "copy the design by March 2027, and downstream fisherfolk as less plastic reaches Manila Bay. We chose a barangay estero because Quezon City "
      "already runs river programs with partners (Philstar, 2025), and citizen-science monitoring of freshwater plastic is still rare, so a barangay-run record adds new data (Cook et al., 2021). "
      "[Add the barangay's household count and its current cleanup program.]")

S4_SELECT = ("We listed five community problems and scored each on significance, feasibility, STEM depth, replicability and originality. "
             "Creek plastic won. We can reach a creek, we can measure it weekly, and RA 11898 has just made item-level data useful. "
             "[Edit this to match your team's actual brainstorming steps.]")
S4_EXISTS = "Six kinds of work address parts of the problem."
PRIOR = [
    ("Cameras with deep learning (Kataoka et al., 2024)", "Detect floating plastic in images from fixed river cameras", "Monitor only and remove nothing"),
    ("Solar river barriers (The Ocean Cleanup, 2026)", "Intercept and lift river plastic with a solar-powered conveyor", "Built for large rivers, announced for the Pasig and Meycauayan"),
    ("AI cleanup boats (Manila Bulletin, 2025)", "Collect plastic with a solar-powered, AI-enabled vessel in a Pasig pilot", "Built for a large river, not for a barangay-run estero"),
    ("Tiny on-chip classifiers (Mendez-Cruz et al., 2024)", "Classify microplastics and waste on an ESP32 camera, 91.7% accuracy on 229 images", "Controlled tests only, no collection, no field data"),
    ("Trash traps (Philstar, 2022)", "Remove plastic in bulk at river tributaries", "Record bulk weight only"),
    ("Brand audits (Break Free From Plastic, 2021)", "Name the brands behind plastic waste", "Periodic, manual, mostly land-based"),
]
S4_GAP = ("None of these patrols a creek, collects plastic, counts it item by item and shares open data in a unit a barangay can afford, and the tiny classifiers have not left the lab. "
          "Our search found no such system. We therefore ask one research question: can a PHP 16,000 robot boat match a trained hand audit within 15%, "
          "and does continuous counting reveal rain-driven pulses of plastic that weekly audits miss?")

S5_STEM = ("STEM is the core of the design. Physics sets the hull's buoyancy and stability, the thrust, the belt torque and the solar energy budget. "
           "Mathematics and statistics define precision, recall and count error. Computer science supplies a small 2D convolutional neural network "
           "(CNN) with INT8 quantization, which shrinks a model about fourfold with little loss of accuracy (Gholami et al., 2021), running on "
           "TensorFlow Lite for Microcontrollers (David et al., 2021). Engineering joins them in a weatherproof boat. Our key message is "
           "that proof of what plastic reaches a creek can be continuous, cheap and community-owned.")
S5_STEPS = [
    ("Float.", " Two sealed 6-inch PVC floats filled with foam carry a deck. For a planning load of about 25 kg the boat rides high. A wide beam and a low battery keep it stable, "
               "and a tilt sensor stops the motors if it leans past 20 degrees."),
    ("Patrol.", " Two thrusters steer by differential thrust. The boat follows the bank with side ultrasonic sensors and a compass, turns at two floating barriers about 30 m apart, "
                "and returns to a bank dock when its bins are full or its battery is low. Staff can take over with a phone remote."),
    ("Detect and scoop.", " A bow camera on an ESP32-CAM runs a tiny detector that boxes floating debris ahead and separates plastic from plants. The boat steers toward it, "
                          "and a scoop lifts it onto a cleated conveyor belt."),
    ("Count and sort.", " The belt spreads items into one layer under an ESP32-S3 camera with a lit hood. The CNN classifies each item as PET bottle, sachet or film, bag, foam, cup, plant or other. "
                        "A servo gate drops plastic into Bin A and plants or low-confidence items into Bin B, so a person can check them. Training photographs come from our own collection "
                        "along the creek bank, labelled by students and checked by the adviser. Weekly hand counts of both bins test accuracy."),
    ("Protect.", " The chip reads belt and thruster current. After a jam it reverses briefly, retries at most three times, then stops and returns to the dock. "
                 "Motor drivers default to off, so a crashed chip cannot leave a motor running."),
    ("Software.", " We train in Keras on a laptop, start from small pretrained MobileNet-style networks, quantize to INT8 and deploy on the ESP32 boards."),
    ("Report.", " Each record stores class, time and an image hash in an append-only log on a microSD card, with time from a clock module. When the boat is docked, a phone reads "
                "an offline Wi-Fi page with the weekly report and an anonymized open dataset, and counts are plotted against rainfall and water level."),
    ("Plastic accounting.", " Counts are converted to estimated kilograms using typical weights per item class, and each weekly weigh-in corrects them. A weekly sheet lists items by type "
                            "and their estimated recovery value at local junk-shop rates, giving the barangay and the DENR item-level evidence for RA 11898 and a reason to keep the unit running."),
    ("Flood warning.", " A separate solar node on the bank carries three float switches set at watch, alert and danger levels on a painted staff gauge. A buzzer and beacon sound locally, "
                       "the level is logged with the time, and the boat stays docked from the alert level."),
    ("Power.", " Planning figures until measured. A 30 W panel flat on the deck yields about 54 Wh per day at 3 effective sun-hours and 60% efficiency and charges a 12 V 12 Ah battery of about 144 Wh. "
               "Two buck converters give the boards and the servo separate 5 V rails, and the motors run from the 12 V rail through their own fuses and drivers. A 20-minute patrol uses about 25 Wh, "
               "and a low battery skips the patrol."),
    ("Scope.", " SAGIP lifts light floating debris such as bottles, sachets, bags, foam and cups. It cannot lift heavy or tangled items, hyacinth mats or sunken waste, "
               "and it covers one stretch of creek, so we report a measured capture rate."),
]
S5_PLAIN = ("The model is the skill of a sanitation worker who can tell a bottle from a sachet at a glance, saved as a file of numbers. No internet is needed.")

BUDGET = [
    ("Two 6-inch PVC floats with foam fill, frame and deck", "2,300"),
    ("Two 12 V thrusters and dual driver", "1,800"),
    ("Short cleated conveyor, gear motor and driver", "2,000"),
    ("ESP32-S3 camera board, hood, LED, enclosure (belt camera and brain)", "1,850"),
    ("ESP32-CAM bow detector", "600"),
    ("Compass with tilt sensor, three waterproof ultrasonic sensors, bump switches", "900"),
    ("Gate servo and reused bins", "300"),
    ("12 V 12 Ah battery, converters, fuses, wiring", "2,400"),
    ("30 W solar panel and 20 A charge controller", "1,100"),
    ("Waterproofing and hardware", "500"),
    ("Flood node: ESP32, three float switches, buzzer and beacon, mini panel, cell, staff gauge", "1,000"),
    ("Bank dock and two barriers, with rope, floats and post from the barangay", "600"),
    ("Subtotal", "15,350"),
    ("Contingency", "650"),
    ("Total", "16,000"),
]
TOOLS = ("Python, Keras, TensorFlow Lite for Microcontrollers, Arduino IDE, a borrowed multimeter, a kitchen scale and our phones. "
         "Prices are estimates from online shops, and we will ask the barangay for rope, floats, a post and bins in kind.")
STAGES = [
    ("Stage 1, bench (about PHP 7,650).", " Build the conveyor, camera, CNN, gate, battery and panel on a bench. Gate: precision and recall on held-out photographs reach 85%, the belt passes a wet-debris run and the battery carries a simulated patrol."),
    ("Stage 2, boat (about PHP 6,100).", " Build the floats, deck, thrusters, bow detector, sensors and waterproofing. Gate: float and tilt tests, then remote driving, then a pond test where the boat reaches and scoops at least 70% of 20 floating items placed 2 to 5 m ahead."),
    ("Stage 3, dock, barriers and flood node (about PHP 1,600).", " Gate: the boat patrols between barriers in a pond or canal without help, and the flood alarm sounds at all three marks in a bucket test."),
]
TIMELINE = ("Site visit, barangay letter and starter dataset by November 2. If shortlisted after the November 9 to 13 screening, the mentorship from November 16 to December 5 "
            "finishes Stage 1 on a bench and builds a scaled boat mock-up and the flood node for the December 7 pitch. The creek pilot runs January to February 2027 if supported. "
            "Guide and further sites by March 2027.")

STAKE = [
    ("Barangay captain and sanitation officers:", " site approval, bin emptying, the flood alarm and use of the reports under a one-page maintenance agreement."),
    ("City solid-waste office and DENR:", " use of the data and fit with Quezon City's river programs (Philstar, 2025)."),
    ("Adviser and school head:", " supervision and safety sign-off."),
    ("Students and residents:", " students build, label and count. Residents give consent."),
]
RISKS = [
    ("Manual labor:", " people must still empty the bins, clear snags and wipe the lenses. We will log those hours."),
    ("Stability and sinking:", " foam-filled floats, a tilt cut-off and pond tests before launch."),
    ("Navigation in the creek:", " barriers set the stretch, side sensors and a compass follow the bank, and the phone remote takes over."),
    ("Hyacinth and snags:", " the detector sends plants to Bin B, propellers are shrouded, and current sensing reverses a jam."),
    ("Fast water:", " the boat stays docked from the alert level."),
    ("Model and detector errors:", " test on unseen places, send unsure items to Bin B and keep the weekly hand count."),
    ("Safety, privacy, theft:", " no student rides the boat or enters the water, the cameras see the water only, and the boat is docked when unattended."),
    ("Permission:", " the stretch needs barangay and city approval, and the DENR where required."),
]

S7_INTRO = ("Success means floating plastic lifted from a real creek, a trustworthy weekly record of what it was and a flood alarm that works. One unit lifts little mass, "
            "so its value lies in cheap copies and open data.")
OUTCOMES = [
    ("1. Less plastic in the creek:", " at least 50% of floating debris removed in the patrol stretch against the baseline week and at least 20 kg lifted in 8 weeks."),
    ("2. Trustworthy counts and warnings:", " at least 1,000 classified items, weekly device error of 15% or less against the hand audit, at least 85% precision and recall on unseen places, and a flood alarm that sounds at all three marks."),
    ("3. Replication:", " at least 2 more sites by March 2027 at about PHP 16,000 each, sharing one open data format, with weekly labor hours reported."),
]
VISION = ("We see a student-built, barangay-owned network of units along connected creeks that feeds one open dataset showing where plastic enters, "
          "which products dominate, and whether EPR commitments change what the water carries. Planned upgrades are a longer patrol stretch and a second boat.")
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
