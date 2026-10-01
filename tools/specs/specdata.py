"""Engineering profiles used to derive a datasheet for every catalogue model (see gen_specs.py).

Everything here is invented but plausible.  Each catalogue category has a *profile*:
    (class, fill, mat, base_w, w_m3, maker)
mass = bounding volume x fill factor x material density (kg/m3); typical power = base_w + w_m3 x volume.
"""

MAKERS = {
    "COI": ("Calder-Okonkwo Industries", "Hull fittings, doors, hatches, structure"),
    "HPS": ("Halvorsen Power Systems", "Reactors, generators, turbines, energy storage"),
    "MAV": ("Meridian Avionics", "Bridge consoles, displays, holo, instruments"),
    "KCS": ("Kestrel Cognitive Systems", "Computing racks, terminals, data and comms hardware"),
    "BLS": ("Brightwater Life Systems", "Scrubbers, tanks, water and gas handling, hydroponics"),
    "LAM": ("Lindqvist-Aoki Medical", "Medical beds, scanners, cabinets, surgical equipment"),
    "ORI": ("Orrery Instruments", "Laboratory analysers, microscopes, science instruments"),
    "TAM": ("Tamsin Lighting", "Luminaires, signal and warning lights"),
    "IHW": ("Ironwake Heavy Works", "Hangar equipment, cargo handling, containers, craft"),
    "GGS": ("Greywater Galley Systems", "Galley equipment, vending, tableware, provisions"),
    "SHF": ("Sable Habitat Furnishings", "Crew furniture and fittings"),
    "FSS": ("Fennick Safety and Security", "Safety gear, security systems, force fields"),
    "AFC": ("Anvil Fluid Controls", "Pipes, valves, nozzles, pumps, coils and conduits"),
}

# class defaults: price_kg (cr per kg), mtbf (h), svc (maintenance interval h), life (years), crew, ip, noise_base (dB(A) at typical load),
# temp (C range), iface, cert, lead (days), peak (x typical), idle (x typical), heat (fraction of electrical power that becomes heat)
CLASSES = {
    "furniture": dict(price_kg=38, mtbf=900000, svc=8760, life=30, crew=0, ip="IP20", noise=0, temp=(-20, 60), iface="", cert=["CSA-F1 fire and smoke"], lead=14, peak=1.0, idle=0.0),
    "structure": dict(price_kg=22, mtbf=1500000, svc=17520, life=40, crew=0, ip="IP40", noise=0, temp=(-40, 80), iface="", cert=["CSA-S2 structural"], lead=21, peak=1.0, idle=0.0),
    "light": dict(price_kg=260, mtbf=60000, svc=17520, life=12, crew=0, ip="IP44", noise=0, temp=(-20, 55), iface="Lighting bus LB-1 (dimming)", cert=["CSA-E24 electrical safety", "CSA-L3 photobiological"], lead=12, peak=1.1, idle=0.05),
    "electronics": dict(price_kg=1100, mtbf=85000, svc=8760, life=10, crew=1, ip="IP30", noise=28, temp=(0, 45), iface="Ship data bus SDB-2, 1 GbE", cert=["CSA-E24 electrical safety", "CSA-EMC4 compatibility"], lead=28, peak=1.5, idle=0.25),
    "bridge": dict(price_kg=1700, mtbf=75000, svc=8760, life=12, crew=1, ip="IP30", noise=30, temp=(0, 45), iface="Ship data bus SDB-2, 10 GbE", cert=["CSA-E24 electrical safety", "CSA-EMC4 compatibility", "CSA-B7 bridge systems"], lead=45, peak=1.4, idle=0.3),
    "machinery": dict(price_kg=620, mtbf=32000, svc=2000, life=20, crew=1, ip="IP54", noise=62, temp=(-20, 60), iface="Machinery control bus MCB-1", cert=["CSA-M5 machinery safety", "CSA-E24 electrical safety"], lead=90, peak=2.2, idle=0.35),
    "power": dict(price_kg=900, mtbf=50000, svc=4000, life=25, crew=2, ip="IP54", noise=68, temp=(-20, 55), iface="Power management bus PMB-1", cert=["CSA-M5 machinery safety", "CSA-E24 electrical safety", "CSA-R3 radiation (fusion)"], lead=120, peak=1.3, idle=0.2),
    "lifesupport": dict(price_kg=540, mtbf=45000, svc=3000, life=18, crew=1, ip="IP54", noise=55, temp=(-10, 55), iface="Environmental bus EB-1", cert=["CSA-LS1 life support", "CSA-P4 pressure equipment"], lead=60, peak=1.6, idle=0.4),
    "medical": dict(price_kg=2100, mtbf=60000, svc=4380, life=12, crew=1, ip="IP32", noise=38, temp=(10, 35), iface="Medical data bus MDB-1 (encrypted)", cert=["CSA-MD5 medical device", "CSA-E24 electrical safety"], lead=60, peak=1.8, idle=0.3),
    "science": dict(price_kg=2600, mtbf=55000, svc=4380, life=12, crew=1, ip="IP32", noise=40, temp=(5, 40), iface="Lab data bus LDB-1, 1 GbE", cert=["CSA-E24 electrical safety", "CSA-LAB2 laboratory"], lead=75, peak=1.7, idle=0.3),
    "galley": dict(price_kg=330, mtbf=40000, svc=2190, life=15, crew=1, ip="IP44", noise=48, temp=(0, 50), iface="", cert=["CSA-F2 food contact", "CSA-E24 electrical safety"], lead=30, peak=1.5, idle=0.3),
    "provision": dict(price_kg=16, mtbf=0, svc=0, life=1, crew=0, ip="sealed", noise=0, temp=(-20, 30), iface="", cert=["CSA-F2 food contact"], lead=7, peak=1.0, idle=0.0),
    "safety": dict(price_kg=180, mtbf=400000, svc=4380, life=15, crew=0, ip="IP44", noise=0, temp=(-30, 70), iface="", cert=["CSA-S3 safety equipment", "CSA-F1 fire and smoke"], lead=21, peak=1.0, idle=0.0),
    "security": dict(price_kg=760, mtbf=70000, svc=4380, life=15, crew=1, ip="IP54", noise=32, temp=(-10, 55), iface="Security bus SEB-1 (encrypted)", cert=["CSA-SEC2 security", "CSA-E24 electrical safety"], lead=45, peak=1.6, idle=0.3),
    "cargo": dict(price_kg=95, mtbf=500000, svc=8760, life=25, crew=0, ip="IP54", noise=0, temp=(-40, 70), iface="", cert=["CSA-C1 cargo handling"], lead=30, peak=1.0, idle=0.0),
    "hangar": dict(price_kg=170, mtbf=120000, svc=4380, life=20, crew=1, ip="IP55", noise=55, temp=(-40, 70), iface="Hangar control bus HCB-1", cert=["CSA-H2 flight deck", "CSA-E24 electrical safety"], lead=60, peak=1.8, idle=0.3),
    "craft": dict(price_kg=1900, mtbf=25000, svc=1000, life=30, crew=2, ip="IP67", noise=70, temp=(-60, 80), iface="Docking data link DDL-1", cert=["CSA-F9 flight certificate", "CSA-P4 pressure equipment"], lead=240, peak=2.0, idle=0.3),
    "plant": dict(price_kg=60, mtbf=0, svc=168, life=2, crew=0, ip="n/a", noise=0, temp=(10, 35), iface="", cert=["CSA-BIO1 biosafety"], lead=7, peak=1.0, idle=0.0),
}

# category -> (class, fill, mat kg/m3, base_w, w_m3, maker)
PROFILES = {
    "analyzer": ("science", 0.22, 1800, 120, 300, "ORI"), "antenna": ("electronics", 0.06, 2200, 40, 80, "KCS"),
    "barrel": ("cargo", 0.035, 1200, 0, 0, "IHW"), "beacon": ("light", 0.08, 1500, 6, 0, "TAM"),
    "bed": ("furniture", 0.05, 200, 0, 0, "SHF"), "bench": ("furniture", 0.12, 500, 0, 0, "SHF"),
    "bin": ("furniture", 0.06, 1200, 0, 0, "SHF"), "cabinet": ("furniture", 0.08, 1800, 0, 0, "SHF"),
    "cabletray": ("structure", 0.04, 2700, 0, 0, "AFC"), "camera": ("security", 0.10, 1500, 8, 100, "FSS"),
    "capacitor": ("power", 0.35, 2200, 0, 0, "HPS"), "ceilinglight": ("light", 0.10, 1500, 10, 120, "TAM"),
    "ceilingpanel": ("structure", 0.06, 1200, 0, 0, "COI"), "cell": ("security", 0.04, 3000, 20, 10, "FSS"),
    "chair": ("furniture", 0.05, 400, 0, 0, "SHF"), "cleaningbot": ("electronics", 0.30, 800, 150, 300, "KCS"),
    "clock": ("electronics", 0.10, 1000, 2, 0, "MAV"), "coil": ("machinery", 0.25, 3500, 20000, 150000, "AFC"),
    "commsunit": ("electronics", 0.20, 1500, 15, 400, "KCS"), "console": ("bridge", 0.10, 1400, 150, 120, "MAV"),
    "controlpanel": ("electronics", 0.30, 1500, 1, 3000, "MAV"), "couch": ("furniture", 0.10, 300, 0, 0, "SHF"),
    "craft": ("craft", 0.12, 2800, 2000, 50, "IHW"), "crate": ("cargo", 0.05, 1200, 0, 0, "IHW"),
    "cryo": ("medical", 0.20, 1500, 800, 1500, "LAM"), "cylinder": ("lifesupport", 0.06, 7800, 0, 0, "BLS"),
    "desk": ("furniture", 0.06, 500, 0, 0, "SHF"), "display": ("bridge", 0.05, 1400, 25, 350, "MAV"),
    "door": ("structure", 0.08, 2700, 15, 50, "COI"), "doorframe": ("structure", 0.04, 2700, 0, 0, "COI"),
    "duct": ("lifesupport", 0.03, 2700, 0, 0, "BLS"), "engtool": ("machinery", 0.15, 3000, 0, 0, "AFC"),
    "floorpanel": ("structure", 0.08, 2700, 0, 0, "COI"), "forcefield": ("security", 0.10, 2500, 5000, 80000, "FSS"),
    "fountain": ("galley", 0.08, 1500, 60, 400, "GGS"), "galley": ("galley", 0.10, 1800, 80, 800, "GGS"),
    "generator": ("power", 0.30, 4500, 0, 0, "HPS"), "gym": ("furniture", 0.10, 800, 0, 0, "SHF"),
    "hangartool": ("hangar", 0.08, 2500, 0, 0, "IHW"), "hatch": ("structure", 0.10, 2700, 0, 0, "COI"),
    "holo": ("bridge", 0.08, 1500, 200, 500, "MAV"), "instrument": ("bridge", 0.15, 1500, 5, 300, "MAV"),
    "junction": ("electronics", 0.15, 1800, 5, 100, "HPS"), "labbench": ("furniture", 0.08, 1200, 0, 0, "ORI"),
    "lamp": ("light", 0.10, 1000, 8, 150, "TAM"), "loader": ("hangar", 0.06, 3000, 100, 300, "IHW"),
    "locker": ("furniture", 0.05, 1800, 0, 0, "SHF"), "medbed": ("medical", 0.10, 1200, 80, 100, "LAM"),
    "medcabinet": ("medical", 0.10, 1500, 40, 300, "LAM"), "medscanner": ("medical", 0.12, 1800, 300, 1500, "LAM"),
    "medsupply": ("medical", 0.10, 800, 0, 0, "LAM"), "medtool": ("medical", 0.20, 1000, 0, 0, "LAM"),
    "microscope": ("science", 0.15, 2000, 20, 500, "ORI"), "noticeboard": ("bridge", 0.05, 1400, 15, 300, "MAV"),
    "nozzle": ("machinery", 0.20, 4500, 500, 2000, "AFC"), "pallet": ("cargo", 0.06, 600, 0, 0, "IHW"),
    "panellight": ("light", 0.08, 1500, 5, 100, "TAM"), "particle": ("science", 0.15, 4000, 5000, 80000, "ORI"),
    "pillar": ("structure", 0.10, 7800, 0, 0, "COI"), "pipe": ("structure", 0.02, 7800, 0, 0, "AFC"),
    "plant": ("plant", 0.30, 300, 0, 0, "BLS"), "planter": ("lifesupport", 0.20, 700, 150, 400, "BLS"),
    "rack": ("electronics", 0.12, 1600, 400, 2000, "KCS"), "railing": ("structure", 0.05, 2700, 0, 0, "COI"),
    "reactor": ("power", 0.25, 5000, 0, 0, "HPS"), "router": ("electronics", 0.20, 1500, 12, 600, "KCS"),
    "safety": ("safety", 0.05, 2000, 0, 0, "FSS"), "sciinstrument": ("science", 0.15, 2000, 8, 600, "ORI"),
    "sconce": ("light", 0.08, 1200, 4, 0, "TAM"), "scrubber": ("lifesupport", 0.15, 2500, 300, 3000, "BLS"),
    "seat": ("furniture", 0.08, 400, 0, 0, "SHF"), "shelving": ("cargo", 0.03, 2700, 0, 0, "IHW"),
    "sign": ("structure", 0.05, 1200, 0, 0, "COI"), "specimen": ("science", 0.10, 1500, 100, 500, "ORI"),
    "spotlight": ("light", 0.10, 1500, 20, 200, "TAM"), "storage": ("electronics", 0.30, 1800, 100, 1000, "KCS"),
    "storagebin": ("cargo", 0.04, 1200, 0, 0, "IHW"), "striplight": ("light", 0.10, 1200, 6, 300, "TAM"),
    "suitrack": ("safety", 0.06, 1800, 0, 0, "FSS"), "surgical": ("medical", 0.12, 1500, 150, 800, "LAM"),
    "table": ("furniture", 0.06, 600, 0, 0, "SHF"), "tableware": ("galley", 0.20, 1500, 0, 0, "GGS"),
    "tank": ("lifesupport", 0.08, 7800, 0, 0, "BLS"), "telescope": ("science", 0.10, 2000, 40, 300, "ORI"),
    "terminal": ("electronics", 0.20, 1200, 3, 400, "KCS"), "toolbox": ("machinery", 0.10, 3000, 0, 0, "AFC"),
    "turbine": ("power", 0.30, 5000, 0, 0, "HPS"), "valve": ("structure", 0.05, 7800, 0, 0, "AFC"),
    "vending": ("galley", 0.10, 1500, 80, 300, "GGS"), "wallpanel": ("structure", 0.06, 1800, 0, 0, "COI"),
    "warnlight": ("light", 0.08, 1500, 5, 100, "TAM"), "watertank": ("lifesupport", 0.06, 4500, 0, 0, "BLS"),
    "weaponrack": ("security", 0.08, 3000, 5, 50, "FSS"),
}

# words in a category name that mark provisions (food and drink models added by the food workers)
PROVISION_WORDS = ("food", "drink", "beverage", "meal", "snack", "dessert", "produce", "fruit", "vegetable", "bread", "soup", "ingredient",
                   "dish", "bottle", "cup", "pastry", "dairy", "grain", "spice", "sauce", "salad", "cake", "pizza", "noodle", "rice", "coffee", "tea")
PROVISION_PROFILE = ("provision", 0.55, 900, 0, 0, "GGS")
DEFAULT_PROFILE = ("structure", 0.08, 1500, 0, 0, "COI")

# label keyword adjustments: (category, keywords, changes).  First match wins.  Changes: passive (True: no electrical load), role
# (conv, gen, store, load), wmul (multiplies typical power), wset (typical W), massmul, genkw_m3 (kW per m3 for producers), note
ADJUST = [
    ("reactor", ("control pillar",), dict(role="load", wset=1500)),
    ("reactor", ("injector",), dict(role="load", wset=450000, note="Feeds the warp core; draws power while injecting.")),
    ("reactor", ("auxiliary",), dict(genkw_m3=450.0)),
    ("reactor", ("emergency",), dict(genkw_m3=250.0, note="Hot-standby; starts in under 20 s on loss of main power.")),
    ("reactor", ("fusion core", "tokamak"), dict(genkw_m3=900.0)),
    ("generator", ("transformer", "substation", "regulator", "inverter", "rectifier", "distribution cabinet"), dict(role="conv")),
    ("generator", ("fuel processor",), dict(role="load", wset=9000)),
    ("generator", ("micro fusion",), dict(role="gen", genkw_m3=2500.0)),
    ("generator", ("motor generator",), dict(role="gen", genkw_m3=180.0)),
    ("generator", ("genset",), dict(role="gen", genkw_m3=160.0)),
    ("capacitor", ("charging", "dock", "cradle"), dict(role="load", wset=600)),
    ("capacitor", ("fuel cell",), dict(role="gen", genkw_m3=120.0)),
    ("capacitor", ("capacitor", "marx", "power core"), dict(role="store", kwh_kg=0.01, discharge_c=60.0)),
    ("capacitor", ("battery", "cell", "locker", "crate", "pack"), dict(role="store", kwh_kg=0.20, discharge_c=2.0)),
    ("turbine", ("steam turbine",), dict(role="gen", genkw_m3=180.0)),
    ("turbine", ("flywheel",), dict(role="store", kwh_kg=0.02, discharge_c=30.0)),
    ("turbine", ("gyroscope",), dict(role="load", wset=8000)),
    ("turbine", ("compressor", "impeller", "turbopump"), dict(role="load", wset=45000)),
    ("coil", ("conduit",), dict(role="conv", note="Passive plasma conduit.")),
    ("coil", ("warp coil", "field coil", "helical"), dict(wmul=1.6)),
    ("galley", ("oven", "range", "kettle", "steamer", "microwave", "dishwasher", "coffee"), dict(wmul=2.5)),
    ("galley", ("refrigerator", "freezer", "cooler"), dict(wmul=0.3)),
    ("galley", ("shelving", "counter", "island", "drawer", "rack", "sink", "trash"), dict(passive=True)),
    ("tank", ("pump", "condenser", "filtration", "exchanger", "radiator coil", "radiator panel"), dict(role="load", wset=3500)),
    ("watertank", ("purifier",), dict(role="load", wset=1800)),
    ("controlpanel", ("switch", "breaker", "fuse", "isolator"), dict(passive=True)),
    ("suitrack", ("decontamination",), dict(role="load", wset=900)),
    ("junction", ("strip", "outlet", "box"), dict(passive=True)),
    ("hatch", ("wheel",), dict(passive=True)),
]

# categories whose models carry a screen even if the GLB cannot be scanned
SCREEN_CATEGORIES = ("console", "display", "terminal", "holo", "vending", "medscanner", "medbed", "analyzer", "sciinstrument", "instrument",
                     "commsunit", "clock", "noticeboard")

CATEGORY_TITLES = {
    "analyzer": "Laboratory analyser", "antenna": "Antenna", "barrel": "Barrel / drum", "beacon": "Signal beacon", "bed": "Bed", "bench": "Bench",
    "bin": "Waste / recycling bin", "cabinet": "Cabinet", "cabletray": "Cable tray", "camera": "Security sensor", "capacitor": "Energy storage",
    "ceilinglight": "Ceiling luminaire", "ceilingpanel": "Ceiling panel", "cell": "Detention fitting", "chair": "Chair", "cleaningbot": "Service robot",
    "clock": "Chronometer", "coil": "Warp / plasma coil", "commsunit": "Communications unit", "console": "Bridge console", "controlpanel": "Control panel",
    "couch": "Couch / sofa", "craft": "Craft", "crate": "Crate / container", "cryo": "Cryo / stasis", "cylinder": "Gas cylinder", "desk": "Desk",
    "display": "Display", "door": "Door", "doorframe": "Door frame", "duct": "HVAC duct", "engtool": "Engineering tool", "floorpanel": "Floor panel",
    "forcefield": "Force-field emitter", "fountain": "Water fountain", "galley": "Galley equipment", "generator": "Power generation / conversion",
    "gym": "Gym equipment", "hangartool": "Hangar equipment", "hatch": "Hatch", "holo": "Holographic projector", "instrument": "Bridge instrument",
    "junction": "Electrical junction", "labbench": "Lab bench", "lamp": "Lamp", "loader": "Cargo loader", "locker": "Locker", "medbed": "Medical bed",
    "medcabinet": "Medical cabinet", "medscanner": "Medical scanner", "medsupply": "Medical supply", "medtool": "Medical tool", "microscope": "Microscope",
    "noticeboard": "Notice board", "nozzle": "Thruster / nozzle", "pallet": "Pallet / rack", "panellight": "Panel light", "particle": "Particle physics equipment",
    "pillar": "Structural pillar", "pipe": "Pipe", "plant": "Plant", "planter": "Hydroponic planter", "rack": "Equipment rack", "railing": "Railing",
    "reactor": "Reactor", "router": "Network router", "safety": "Safety equipment", "sciinstrument": "Science instrument", "sconce": "Wall sconce",
    "scrubber": "Atmosphere processor", "seat": "Seat", "shelving": "Shelving", "sign": "Sign", "specimen": "Specimen storage", "spotlight": "Spotlight",
    "storage": "Data storage", "storagebin": "Storage bin", "striplight": "Strip light", "suitrack": "Suit rack", "surgical": "Surgical equipment",
    "table": "Table", "tableware": "Tableware", "tank": "Tank / fluid handling", "telescope": "Telescope", "terminal": "Terminal", "toolbox": "Toolbox",
    "turbine": "Turbomachinery", "valve": "Valve / coupling", "vending": "Vending machine", "wallpanel": "Wall panel", "warnlight": "Warning light",
    "watertank": "Water system", "weaponrack": "Weapon rack",
}
