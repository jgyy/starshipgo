"""Food and drink for the room recipes: table settings, serving lines, galley prep, harvest crates, bar and cold store.

The recipes of the mess, galley, hydroponics, lounge, captain's quarters ... call the `food_*` functions here at the end of
their room function.  Everything works on the props the recipe already placed (tables, counters, desks are found by model id)
and on the free wall length, so a changed hull or a moved table never breaks it; items that do not fit are skipped quietly
and a BOM line that ends up empty is dropped again (the audit demands >= 1 prop per BOM line).

Conventions: for a host prop `u` is the offset in metres along its long axis and `v` across it, from the middle of its top.
"""
from recipes_deck2_helpers import M


# ------------------------------------------------------------------ helpers
def hosts(R, *mids):
    """Placed props (with a footprint) of the given model ids, in placement order."""
    return [p for p in R.props if p["m"] in mids and "_fp" in p]


def on(R, B, host, mid, u=0.0, v=0.0, yaw=None):
    """Stand a table-mount model on `host` at (u, v); None when it does not fit or the id is unknown."""
    if host is None or mid not in B.cat.models:
        return None
    sw = abs(round(host["yaw"]) % 180) == 90          # host turned a quarter turn: its long axis is world z
    dx, dz = (v, u) if sw else (u, v)
    return R.on_top(host, M(B, mid), dx=dx, dz=dz, yaw=yaw)


def on_any(R, B, host, mid, spots):
    """First of several (u, v) candidates at which `mid` fits on `host`."""
    for u, v in spots:
        p = on(R, B, host, mid, u, v)
        if p:
            return p
    return None


def lay(R, B, host, spec):
    """Place a list of (model id, u, v) on one host; returns how many fitted."""
    return sum(1 for mid, u, v in spec if on(R, B, host, mid, u, v))


def _sides(R):
    return [e["side"] for e in R.edges]


def hang(R, B, mid, y=1.9, sides=None, step=0.3):
    """Hang a wall-mount model at the first free spot of the room's walls (scan along every wall)."""
    if mid not in B.cat.models:
        return None
    m = M(B, mid)
    for side in sides or _sides(R):
        span = R.wall_span(side) if R.edge(side) else None
        if not span:
            continue
        a, b = span
        hw = m["size"][0] / 2 + 0.06
        x = a + hw
        while x <= b - hw:
            p = R.wall_item(side, m, x, y=y)
            if p:
                return p
            x += step
    return None


def stand(R, B, mid, sides=None, step=0.3, gap=0.05, margin=0.0):
    """Stand a floor model with its back to the first free stretch of wall."""
    if mid not in B.cat.models:
        return None
    m = M(B, mid)
    for side in sides or _sides(R):
        span = R.wall_span(side) if R.edge(side) else None
        if not span:
            continue
        a, b = span
        hw = m["size"][0] / 2
        x = a + hw
        while x <= b - hw:
            p = R.against_wall(side, m, x, gap=gap, margin=margin)
            if p:
                return p
            x += step
    return None


def line(R, title, why):
    """Start a BOM line; use `done(R, ln, n)` afterwards so an empty line is removed again."""
    return R.line(title, why)


def done(R, ln, n):
    if n == 0 and R.lines and R.lines[-1] is ln:
        R.lines.pop()
        R.cur = R.lines[-1] if R.lines else None
    return n


# ------------------------------------------------------------------ shared menus
DRINKS = ["can_cola", "drink_water_glass_ice_lemon", "can_lime_fizz", "drink_orange_juice_glass", "drink_milk_glass_cookies", "can_blue_cooler_tall",
          "bottle_water_bottle_500ml", "drink_hot_cocoa_mug", "can_orange_soda", "drink_iced_coffee_glass", "can_grape_pop_mini",
          "drink_smoothie_strawberry_tall"]
MEALS = [["meal_burger_with_fries", "meal_pizza_pepperoni", "meal_fish_and_chips", "meal_tomato_soup_bowl"],
         ["meal_steak_dinner", "meal_spaghetti_bolognese", "meal_ramen_bowl", "meal_curry_and_rice"],
         ["bakery_pancake_stack", "meal_fried_egg_breakfast", "meal_porridge_bowl", "bakery_waffle_berries"],
         ["meal_salad_bowl_wood", "meal_lasagna_slice", "meal_fried_rice_bowl", "meal_club_sandwich"],
         ["meal_pho_bowl", "meal_mac_and_cheese", "meal_omelette_plate", "meal_caesar_salad"],
         ["meal_pizza_margherita", "meal_burrito_plate", "meal_dumplings_steamer", "meal_tacos_trio"]]
CENTRES = ["tray_bread_basket_wicker", "tray_fruit_bowl_mixed", "tray_soup_tureen_ladle", "deli_cheese_board", "drink_lemonade_pitcher_set",
           "bakery_pie_apple_lattice"]


# ------------------------------------------------------------------ DECK 2
def mess_tables(R, B, longs, shorts):
    """Different full meals, drinks and a centrepiece on every table of the mess hall."""
    ln = line(R, "Table settings and the day's menu",
              "Each table is laid for its diners with a different full meal at the seats, a drink beside each plate and a shared centrepiece "
              "(bread, fruit, soup, cheese) on the centre line within everybody's reach; the menu is varied from table to table so the hall "
              "reads as a working dining room.")
    n = 0
    seats = ((-1.0, -0.2), (-1.0, 0.2), (1.0, -0.2), (1.0, 0.2))
    for i, t in enumerate(longs):
        if t is None:
            continue
        for k, (u, v) in enumerate(seats):
            n += bool(on(R, B, t, MEALS[i % 6][k], u, v))
        n += bool(on(R, B, t, CENTRES[i % 6], 0.0, 0.0))
        for k, (u, v) in enumerate(((-0.62, -0.27), (0.62, 0.27), (-0.62, 0.27), (0.62, -0.27))):
            n += bool(on(R, B, t, DRINKS[(i * 3 + k) % len(DRINKS)], u, v))
        n += bool(on(R, B, t, "tableware_condiments" if i % 2 else "tableware_napkin_dispenser", 0.0, 0.33 if i % 2 else -0.3))
    for i, t in enumerate(shorts):
        if t is None:
            continue
        n += bool(on(R, B, t, MEALS[(i + 3) % 6][i % 4], -0.38, -0.12))
        n += bool(on(R, B, t, MEALS[(i + 4) % 6][(i + 1) % 4], 0.38, 0.12))
        n += bool(on(R, B, t, DRINKS[(i * 2 + 5) % len(DRINKS)], 0.0, -0.22))
        n += bool(on(R, B, t, DRINKS[(i * 2 + 6) % len(DRINKS)], 0.0, 0.25))
    return done(R, ln, n)


def food_mess(R, B):
    # serving line extras: buffet counter with hot pans and a bakery stand where the free wall allows
    ln = line(R, "Buffet and bakery stand",
              "A hot-pan buffet counter and a bakery display stand let a second queue help itself at busy sittings while the galley "
              "passes only the main course; both stand with their backs to a wall, clear of the tables and the 1.2 m aisles.")
    n = 0
    n += bool(stand(R, B, "buffet_chafing_buffet_line", sides=["S", "N", "E"], step=0.35))
    n += bool(stand(R, B, "buffet_bakery_display_stand", sides=["E", "S", "N"], step=0.3))
    done(R, ln, n)
    ln = line(R, "Fruit and water at the tray return",
              "Fruit and a water bottle sit on the benches by the exit so crew can take something to the watch without queueing again.")
    n = 0
    for b in hosts(R, "bench_mess_bench")[:2]:
        n += bool(on_any(R, B, b, "fruit_apple_green_pair", [(0.0, 0.0), (0.4, 0.0)]))
    done(R, ln, n)


def food_galley(R, B):
    isl = (hosts(R, "galley_kitchen_island") or [None])[0]
    cnts = hosts(R, "galley_prep_counter")
    ln = line(R, "Raw ingredients on the prep island",
              "Vegetables, eggs and a cabbage are laid out on the island for the cook to prepare, one cooking step from the fridges; "
              "ingredients stay on the island, not on the serving counters, so raw and cooked food are kept apart.")
    n = 0
    if isl:
        n += lay(R, B, isl, [("veg_carrots_bunch", -0.8, 0.0), ("veg_cabbage_green", -0.4, 0.0), ("deli_egg_carton_dozen", 0.0, 0.0),
                             ("veg_tomatoes_on_vine", 0.9, 0.0)])
    done(R, ln, n)
    ln = line(R, "Finished dishes on the prep counters",
              "Roast chicken, a loaf, butter and a pie stand on the prep counter nearest the range, ready to be carved and sliced; "
              "dishes go from range to counter to serving line without crossing the raw-food area.")
    n = 0
    if cnts:
        n += lay(R, B, cnts[0], [("meal_roast_chicken", -0.55, 0.0), ("bakery_bread_loaf", -0.1, 0.0), ("deli_butter_dish_and_knife", 0.7, 0.0)])
    done(R, ln, n)
    ln = line(R, "Hot and cold serving counters",
              "The hot counter holds steam pans of mash, roast vegetables and a stew; the cold counter has salad, pie, cake and fruit; "
              "each dish sits where the queue passes it in the order people build a plate.")
    n = 0
    if len(cnts) > 1:
        n += lay(R, B, cnts[1], [("tray_hotel_pan_mash_gravy", -0.55, 0.0), ("tray_hotel_pan_roast_veg", 0.1, 0.0), ("meal_beef_stew_pot", 0.65, 0.0)])
    if len(cnts) > 2:
        n += lay(R, B, cnts[2], [("meal_salad_bowl_wood", -0.6, 0.0), ("bakery_pie_apple_lattice", -0.2, 0.0), ("dessert_tiramisu_cup", 0.12, 0.0),
                                 ("tray_fruit_bowl_mixed", 0.58, 0.0)])
    done(R, ln, n)
    ln = line(R, "Hanging produce and drying rack",
              "Garlic, chilli, herb bundles and cured sausages hang on the wall above the dry stores, in the dry airflow that keeps them "
              "for weeks and within a step of the prep island.")
    n = 0
    for mid, y in (("hanging_garlic_braid", 2.0), ("hanging_chili_ristra", 2.0), ("hanging_herb_bundles", 2.0), ("hanging_sausage_links_hanging", 2.0)):
        n += bool(hang(R, B, mid, y))
    done(R, ln, n)
    ln = line(R, "Fresh harvest delivery",
              "Crates of tomatoes and potatoes from the hydroponics deck wait at the wall by the door, in the order the cook will use them, "
              "so deliveries never cross the cooking area.")
    n = 0
    for mid in ("harvest_crate_tomatoes", "harvest_crate_potatoes", "harvest_crate_cabbages"):
        n += bool(stand(R, B, mid, sides=["E", "W", "N"], step=0.3))
    done(R, ln, n)


def food_hydro(R, B):
    tb = (hosts(R, "table_round_mess_table") or [None])[0]
    ln = line(R, "Harvest crates",
              "Freshly picked crops are packed in crates beside the beds they came from and carried to the galley the same day; "
              "each crate is one crop so the galley can count what it receives.")
    n = 0
    for mid in ("harvest_crate_lettuce", "harvest_crate_herbs", "harvest_crate_strawberries", "harvest_crate_peppers", "harvest_tray_mushrooms"):
        n += bool(stand(R, B, mid, step=0.35))
    done(R, ln, n)
    ln = line(R, "Tasting table and drying herbs",
              "Gardeners taste what they grow: fruit and a salad on the table by the entrance, and herb bundles hung to dry on the wall.")
    n = 0
    if tb:
        n += lay(R, B, tb, [("fruit_strawberries_bowl", -0.3, 0.2), ("meal_salad_bowl_wood", 0.28, -0.22), ("veg_tomatoes_on_vine", 0.0, 0.42)])
    n += bool(hang(R, B, "hanging_herb_bundles", 2.0))
    done(R, ln, n)


def food_rec(R, B):
    ln = line(R, "Snacks and drinks in the lounge corner",
              "Off-duty crew gather round the low table and the bolted table: a snack board, pretzels and drinks make it a place to stay, "
              "and are one step from the vending machines.")
    n = 0
    for t in hosts(R, "table_coffee_table")[:1]:
        n += lay(R, B, t, [("bakery_pretzel_salted", -0.3, 0.0), ("can_cola", 0.28, 0.0), ("can_lime_fizz", 0.4, 0.15)])
    for t in hosts(R, "table_bolted_table")[:1]:
        n += lay(R, B, t, [("deli_charcuterie_board", -0.4, 0.0), ("bottle_beer_lager_green", 0.12, 0.2), ("can_energy_slim", 0.3, -0.2), ("dessert_macarons_plate", 0.55, 0.0)])
    done(R, ln, n)


def food_dorm(R, B):
    ln = line(R, "Snacks and drinks at the crew table",
              "A hot drink, a fruit and a ration cup are on the crew table for off-watch snacks; crew eat in the mess but keep a little "
              "food in the quarters for the night watch.")
    n = 0
    for t in hosts(R, "table_bolted_table")[:1]:
        n += lay(R, B, t, [("ration_cup_noodle_instant", 0.0, -0.22), ("fruit_apple_green_pair", 0.45, 0.2), ("drink_hot_cocoa_mug", -0.55, 0.2)])
    for d in hosts(R, "desk_writing_desk")[:1]:
        n += lay(R, B, d, [("can_cold_brew", 0.4, 0.15), ("bakery_donut_chocolate", 0.0, 0.0)])
    done(R, ln, n)


def food_medbay(R, B):
    ln = line(R, "Patient meals and nutrition",
              "Patients on a bed get a meal tray, juice and fruit puree at the bedside, and the nurse's desk has fruit and water: "
              "nutrition is part of treatment and a tray at the bed avoids trips to the mess.")
    n = 0
    beds = hosts(R, "medbed_diagnostic_biobed")
    if beds:
        n += bool(on_any(R, B, beds[0], "tray_meal_tray_steel", [(0.45, 0.0), (0.6, 0.0), (0.0, 0.0)]))
    if len(beds) > 1:
        n += bool(on_any(R, B, beds[1], "drink_orange_juice_glass", [(0.45, 0.2), (0.3, 0.2), (0.0, 0.2)]))
        n += bool(on_any(R, B, beds[1], "ration_pouch_fruit_puree_spout", [(0.6, -0.2), (0.4, -0.2), (0.0, -0.2)]))
    for d in hosts(R, "desk_officer_desk")[:1]:
        n += lay(R, B, d, [("fruit_apple_red_and_slice", 0.55, 0.0), ("drink_water_glass_ice_lemon", 0.2, 0.2)])
    done(R, ln, n)


def food_brig(R, B):
    ln = line(R, "Guard coffee and detainee meal",
              "The guard keeps coffee and a doughnut on the desk for the long watch; the detainee's meal arrives on a one-piece moulded tray "
              "with a plastic spork, left on the desk until the cell is opened.")
    n = 0
    for d in hosts(R, "desk_computer_desk")[:1]:
        n += lay(R, B, d, [("tray_meal_tray_brig", -0.3, 0.0), ("drink_espresso_cup_sugar", 0.45, 0.1), ("bakery_donut_pink_sprinkles", 0.6, -0.1)])
    done(R, ln, n)


def food_secoff(R, B):
    ln = line(R, "Watch coffee and snacks",
              "The watch runs on coffee: a pot and mugs at the briefing table, mugs and a snack on each duty desk, so officers on a long "
              "shift never leave the monitor wall for food.")
    n = 0
    for t in hosts(R, "holo_briefing_table")[:1]:
        n += bool(on_any(R, B, t, "drink_coffee_pot_and_mugs", [(0.45, 0.4), (0.4, -0.4), (-0.4, 0.4)]))
    for i, d in enumerate(hosts(R, "desk_officer_desk")):
        n += lay(R, B, d, [(("drink_hot_cocoa_mug", "drink_espresso_cup_sugar", "can_energy_slim")[i % 3], 0.5, 0.18),
                           (("bakery_donut_chocolate", "bakery_muffin_choc_chip", "bakery_croissant")[i % 3], 0.78, -0.12)])
    done(R, ln, n)


# ------------------------------------------------------------------ DECK 1
def food_lounge(R, B):
    bars = hosts(R, "table_bar_counter")
    ln = line(R, "Bar counter glassware and bottles",
              "The observation lounge has a small bar: cocktail glasses, a decanter and wine on one counter, beer mugs and bottles on the other, "
              "each family of glassware grouped so the bartender reaches everything without turning.")
    n = 0
    if bars:
        n += lay(R, B, bars[0], [("cocktail_martini_olive", -0.62, 0.0), ("cocktail_margarita_salt_rim", -0.35, 0.05), ("bottle_whisky_decanter_square", 0.0, -0.05),
                                 ("cocktail_whisky_rocks_tumbler", 0.26, 0.05), ("bottle_wine_red_bordeaux", 0.55, -0.05), ("cocktail_wine_glass_red", 0.75, 0.05)])
    if len(bars) > 1:
        n += lay(R, B, bars[1], [("cocktail_beer_mug_foam", -0.65, 0.0), ("cocktail_pint_stout", -0.4, 0.05), ("bottle_beer_brown_longneck", -0.18, -0.05),
                                 ("bottle_beer_lager_green", 0.0, 0.05), ("bottle_champagne_foil", 0.3, -0.05), ("cocktail_champagne_flute", 0.5, 0.05),
                                 ("cocktail_mojito_mint_highball", 0.7, 0.0)])
    done(R, ln, n)
    ln = line(R, "Snacks on the low tables",
              "Cake, coffee and a fruit plate on the low tables turn the lounge into somewhere to linger over the view.")
    n = 0
    tabs = hosts(R, "table_coffee_table")
    specs = (("dessert_cheesecake_slice", -0.25, 0.0), ("drink_cappuccino_rosetta", 0.25, 0.0)), (("fruit_cherries_stems", -0.2, 0.0), ("drink_tea_cup_with_bag", 0.25, 0.0))
    for t, sp in zip(tabs, specs):
        n += lay(R, B, t, sp)
    for t in hosts(R, "table_side_table")[:1]:
        n += lay(R, B, t, [("cocktail_old_fashioned_orange", 0.0, 0.0)])
    done(R, ln, n)


def food_capt(R, B):
    ln = line(R, "The captain's table",
              "The captain dines alone or with a guest at the round table: a steak dinner with wine, a fruit bowl at the centre, and a coffee "
              "and whisky on the desk and the low table for late work.")
    n = 0
    for dt in hosts(R, "table_round_mess_table")[:1]:
        n += lay(R, B, dt, [("meal_steak_dinner", -0.42, 0.0), ("meal_sushi_nigiri_set", 0.42, 0.0), ("cocktail_wine_glass_red", 0.0, 0.42), ("cocktail_champagne_flute", 0.0, -0.42),
                            ("bottle_wine_red_bordeaux", 0.2, 0.2)])
    for d in hosts(R, "desk_officer_desk")[:1]:
        n += bool(on_any(R, B, d, "drink_espresso_cup_sugar", [(0.3, 0.2), (0.2, 0.25), (0.8, 0.2)]))
        n += bool(on_any(R, B, d, "cocktail_whisky_rocks_tumbler", [(-0.3, 0.2), (0.0, 0.25), (-0.8, 0.2)]))
    for t in hosts(R, "table_coffee_table")[:1]:
        n += bool(on_any(R, B, t, "fruit_pear_ripe", [(0.0, 0.0), (0.25, 0.0)]))
    done(R, ln, n)


def food_conf(R, B):
    ln = line(R, "Refreshments for meetings",
              "Long meetings need coffee, water and something to eat: a coffee pot and mugs, a pastry basket and a water bottle for each "
              "place on both tables, within reach of the people who sit in the middle.")
    n = 0
    for i, t in enumerate(hosts(R, "table_conference_table")):
        n += bool(on_any(R, B, t, "drink_coffee_pot_and_mugs", [(1.0, 0.0), (-1.1, 0.0), (1.1, 0.3)]))
        n += bool(on_any(R, B, t, "tray_bread_basket_wicker" if i == 0 else "tray_cake_stand_afternoon_tea", [(0.0, 0.3), (-0.3, 0.3), (0.3, -0.3)]))
        for k, u in enumerate((-1.2, -0.7, 0.7, 1.2)):
            n += bool(on_any(R, B, t, "bottle_water_bottle_500ml" if k % 2 else "can_cola", [(u, 0.42), (u, -0.42), (u + 0.1, 0.35)]))
    done(R, ln, n)


def food_ready(R, B):
    ln = line(R, "Coffee and a snack in the ready room",
              "The captain takes coffee at the desk and a pastry with visitors at the low table; the tray stays within reach of the chair.")
    n = 0
    for d in hosts(R, "desk_officer_desk")[:1]:
        n += bool(on_any(R, B, d, "drink_cappuccino_rosetta", [(0.35, 0.2), (0.25, 0.25), (-0.8, 0.2)]))
        n += bool(on_any(R, B, d, "fruit_apple_red_and_slice", [(0.8, 0.2), (-0.35, 0.2)]))
    for t in hosts(R, "table_coffee_table")[:1]:
        n += bool(on_any(R, B, t, "bakery_croissant", [(0.0, 0.0), (0.2, 0.0)]))
    for t in hosts(R, "table_side_table")[:1]:
        n += bool(on_any(R, B, t, "can_cold_brew", [(0.0, 0.0)]))
    done(R, ln, n)


def food_bridge(R, B):
    ln = line(R, "Coffee on the bridge",
              "A flask of coffee and mugs by the briefing table keep a long watch alert; cans on the side consoles are kept clear of the "
              "controls and screens.")
    n = 0
    for t in hosts(R, "holo_briefing_table")[:1]:
        n += bool(on_any(R, B, t, "drink_coffee_pot_and_mugs", [(0.45, 0.4), (0.4, -0.4), (-0.4, 0.4)]))
    done(R, ln, n)


def food_cabin(R, B):
    ln = line(R, "Drink and fruit at the desk",
              "Officers keep a drink and a piece of fruit at the desk for late work and keep the cabin supplied from the wardroom.")
    n = 0
    for i, d in enumerate(hosts(R, "desk_writing_desk")):
        n += bool(on_any(R, B, d, ("can_cold_brew", "drink_hot_cocoa_mug", "drink_tea_cup_with_bag")[i % 3], [(0.4, 0.15), (0.0, 0.15), (-0.4, 0.15)]))
        if i % 2 == 0:
            n += bool(on_any(R, B, d, "fruit_apple_green_pair", [(-0.2, 0.0), (0.1, 0.0), (-0.45, 0.1)]))
    for t in hosts(R, "table_side_table")[:1]:
        n += bool(on_any(R, B, t, "drink_tea_cup_with_bag", [(0.0, 0.0)]))
    done(R, ln, n)


# ------------------------------------------------------------------ the two new rooms (called by their recipes)
def food_wardroom(R, B):
    """Wardroom and bar: bar counters with glassware and bottles, tables laid for dinner, buffet pieces on the walls."""
    bars = hosts(R, "table_bar_counter")
    ln = line(R, "Bar counter, glassware and spirits",
              "The bar counters carry the cocktail glasses, spirits, wine and beer in groups by glass type, so the barman reaches each "
              "drink without crossing the counter; taps and bottles stand at the back, glasses at the front.")
    n = 0
    sets = ([("cocktail_martini_olive", -0.7, 0.0), ("cocktail_margarita_salt_rim", -0.45, 0.05), ("cocktail_blue_lagoon_hurricane", -0.22, 0.0),
             ("bottle_whisky_decanter_square", 0.05, -0.05), ("cocktail_old_fashioned_orange", 0.3, 0.05), ("bottle_gin_blue_flask", 0.52, -0.05),
             ("cocktail_whisky_rocks_tumbler", 0.72, 0.05)],
            [("cocktail_beer_mug_foam", -0.7, 0.0), ("cocktail_pint_stout", -0.45, 0.05), ("bottle_beer_brown_longneck", -0.22, -0.05),
             ("bottle_beer_lager_green", -0.05, 0.05), ("bottle_champagne_foil", 0.2, -0.05), ("cocktail_champagne_flute", 0.42, 0.05),
             ("cocktail_wine_glass_red", 0.6, 0.0), ("bottle_wine_white_hock", 0.78, -0.05)])
    for i, b in enumerate(bars):
        n += lay(R, B, b, sets[i % 2])
    done(R, ln, n)
    ln = line(R, "Dinner tables",
              "The wardroom tables are laid for officers' dinner: a full meal and a glass at each place and a centrepiece, with the menu "
              "different from table to table.")
    n = 0
    tabs = hosts(R, "table_round_mess_table", "table_square_mess_table", "table_bolted_table", "table_long_mess_table", "table_briefing_table")
    for i, t in enumerate(tabs):
        n += lay(R, B, t, [(MEALS[i % 6][0], -0.3, -0.15), (MEALS[i % 6][1], 0.3, 0.15), (CENTRES[i % 6], 0.0, 0.0) if i % 2 == 0 else ("cocktail_wine_glass_red", 0.0, 0.0)])
    for t in hosts(R, "table_coffee_table"):
        n += lay(R, B, t, [("dessert_sundae_glass", -0.25, 0.0), ("drink_latte_art_cup", 0.25, 0.0)])
    done(R, ln, n)
    ln = line(R, "Display and buffet pieces",
              "A dessert case and a bakery stand along the wall give the wardroom a self-service end without a kitchen of its own.")
    n = 0
    n += bool(stand(R, B, "buffet_dessert_display_case", step=0.3))
    n += bool(stand(R, B, "buffet_bakery_display_stand", step=0.3))
    done(R, ln, n)


def food_provisions(R, B):
    """Provisions hold / cold store: harvest crates, hanging produce and ration boxes on the shelving."""
    ln = line(R, "Crates of fresh produce",
              "Fresh produce is stored in the crates it was picked in, one crop per crate, at the wall nearest the galley lift so the "
              "oldest crate can be taken first.")
    n = 0
    for mid in ("harvest_crate_potatoes", "harvest_crate_cabbages", "harvest_crate_tomatoes", "harvest_crate_peppers", "harvest_crate_lettuce",
                "harvest_crate_herbs", "harvest_crate_strawberries", "harvest_tray_mushrooms"):
        n += bool(stand(R, B, mid, step=0.3))
    done(R, ln, n)
    ln = line(R, "Hanging store",
              "Garlic, chilli, herbs and cured sausages hang from the wall rail where cool dry air keeps them for months.")
    n = 0
    for mid in ("hanging_garlic_braid", "hanging_chili_ristra", "hanging_herb_bundles", "hanging_sausage_links_hanging"):
        n += bool(hang(R, B, mid, 2.0))
    done(R, ln, n)
    ln = line(R, "Rations and dry goods on the shelving",
              "Sealed ration boxes, water pouches and canned goods sit on top of the shelving units in their original cartons, "
              "labelled for the stock rotation; the lower shelves carry the bulk stores.")
    n = 0
    shelves = hosts(R, "shelving_pigeonhole", "galley_storage_shelving", "shelving_cage_lockers", "storagebin_drawer_cabinet")
    pool = ["ration_ration_boxes_stacked", "ration_water_pouches_stack", "ration_pouch_beef_stew", "ration_canned_beans_open", "ration_protein_bars_stack",
            "ration_freeze_dried_tray", "ration_mre_tray_pasta", "bottle_olive_oil_cruet"]
    for i, s in enumerate(shelves):
        n += bool(on_any(R, B, s, pool[i % len(pool)], [(0.0, 0.0), (-0.3, 0.0), (0.3, 0.0)]))
    done(R, ln, n)
