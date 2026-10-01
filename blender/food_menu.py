#!/usr/bin/env python3
"""Write docs/FOOD.md (the menu of every food and drink model) from godot/data/catalog.json.

    python blender/food_menu.py            # rewrites docs/FOOD.md

Bare Python (no bpy).  The contact sheets docs/screenshots/food_sheet_*.jpg are rendered with blender/food_sheet.py (see the
command lines in the generated document).  Every food model in the catalog must have a line in MENU below - the script stops
otherwise, so the document can not fall behind the models.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))

# id -> what is on the model (ingredients / parts); the size, triangles and file size come from the catalog
MENU = """
bakery_bagel_poppy: boiled-and-baked bagel (torus) with poppy and sesame seeds
bakery_baguette: 0.52 m French baguette with five diagonal scoring cuts in lighter crumb
bakery_bread_loaf: tin loaf with domed, scored top and four slashes
bakery_brioche_loaf: golden brioche loaf with four risen domes, on a bread board
bakery_cake_slice_chocolate: layered chocolate sponge, cream filling, chocolate icing with drips and a cherry, on a dark plate
bakery_cinnamon_roll: dough spiral with cinnamon filling and a zig-zag of white icing, on a blue plate
bakery_cookies_on_plate: five chocolate-chip cookies plus two stacked on them, on a plate
bakery_croissant: crescent croissant with six layered ridges (bent surface of revolution, laminated-pastry texture)
bakery_cupcake_swirl: pink paper case, sponge, twisting piped vanilla frosting and a cherry with stalk
bakery_donut_chocolate: ring donut, dark chocolate glaze with white icing stripes
bakery_donut_pink_sprinkles: ring donut, pink icing with rainbow sprinkles
bakery_layer_cake_birthday: three sponge layers with pink icing between, chocolate coating with white drips, strawberries, cherries and three lit candles, on a stand
bakery_muffin_choc_chip: chocolate-chip muffin overflowing a paper case
bakery_pancake_stack: five pancakes, butter pat, maple syrup running down the side, two strawberries, plate
bakery_pie_apple_lattice: lattice-topped apple pie with crimped crust and fruit filling in a steel dish
bakery_pretzel_salted: soft pretzel knot with coarse salt
bakery_sourdough_boule: round sourdough loaf dusted with flour, three scoring cuts, on a board
bakery_toast_in_rack: wire rack holding two slices of golden toast
bakery_waffle_berries: Belgian waffle (raised grid), butter, strawberries, blueberries, honey, plate
dessert_brownie_stack: three fudge brownies, chocolate sauce, a scoop of vanilla and nuts, plate
dessert_cheesecake_slice: biscuit base, cream cheese, berry glaze, blueberries and mint, plate
dessert_chocolate_bar_open: milk chocolate bar of eight squares on its blue wrapper with gold foil
dessert_creme_caramel: baked custard with caramel pool and a mint sprig, plate
dessert_fruit_tart: pastry case, custard, rings of strawberries and blueberries, mint
dessert_ice_cream_cone_double: waffle cone with vanilla and strawberry scoops, sprinkles, in a steel holder
dessert_jelly_mould: translucent strawberry jelly with fruit pieces and a cherry, plate
dessert_macarons_plate: six pastel macarons (two shells and cream each), blue plate
dessert_sundae_glass: footed glass with chocolate and vanilla ice cream, sauce, strawberry scoop, cherry, two wafers
dessert_tiramisu_cup: glass cup of layered mascarpone and sponge, cocoa top, spoon
meal_beef_stew_pot: cast pot of beef, potato and carrot stew with herbs and a bail handle
meal_burger_with_fries: seeded bun, patty, cheese, tomato, lettuce, plus a pile of fries, blue plate
meal_burrito_plate: foil-wrapped burrito cut open (rice, beans, cheese), salsa, guacamole, tortilla chips
meal_caesar_salad: romaine leaves, croutons, parmesan shavings, grilled chicken, dressing drizzle
meal_club_sandwich: two triple-decker toast triangles (turkey, bacon, tomato, lettuce) on cocktail sticks, crisps
meal_curry_and_rice: rice mound, steel bowl of vegetable curry, naan, coriander
meal_double_cheeseburger: two patties, cheese, onion, pickles, tomato, lettuce, skewered olive, on paper
meal_dumplings_steamer: bamboo steamer of six pleated dumplings, soy dip, chopsticks
meal_fish_and_chips: battered cod fillets, chips, mushy peas, lemon, tartare sauce, blue plate
meal_fried_egg_breakfast: two fried eggs, bacon, sausage, toast, tomato and mushrooms
meal_fried_rice_bowl: egg fried rice with peas, carrot, prawns, spring onion and chopsticks
meal_hot_dog_mustard: bun, sausage, mustard and ketchup zig-zags, onion, paper
meal_lasagna_slice: seven layers (pasta, ragu, bechamel), browned cheese top, basil, plate
meal_mac_and_cheese: baked macaroni with a crisped cheddar top and parsley in a red dish
meal_maki_platter: eight maki rolls (nori, rice, tuna / salmon / cucumber / egg), soy dish, chopsticks, slate
meal_omelette_plate: folded herb omelette, cherry tomatoes, spinach leaves, plate
meal_paella_pan: wide pan of saffron rice, prawns, mussels, peas, peppers and lemon
meal_pho_bowl: bowl of broth with rice noodles, rare beef, spring onion, bean sprouts, lime, chopsticks
meal_pizza_margherita: 0.30 m pizza on a steel pan - puffy charred crust, tomato, mozzarella and basil
meal_pizza_pepperoni: 0.30 m pizza with pepperoni, black olives, melted cheese, herbs
meal_porridge_bowl: oat porridge with butter pats, berries, honey and a spoon
meal_ramen_bowl: broth, noodles, chashu pork, soft-boiled egg halves, nori, narutomaki, spring onion, chopsticks
meal_roast_chicken: whole roast chicken with crossed drumsticks, potatoes, rosemary, lemon halves, oval platter
meal_salad_bowl_wood: wooden bowl of lettuce, cherry tomatoes, cucumber, red onion rings, croutons, olives
meal_shepherds_pie_dish: oval dish of mince topped with piped mashed potato and herbs
meal_spaghetti_bolognese: nest of spaghetti, bolognese sauce, grated parmesan, basil
meal_steak_dinner: seared steak with grill marks, mashed potato, green beans, roast tomato, jus, plate
meal_sushi_nigiri_set: six nigiri (salmon, tuna, prawn, egg), wasabi, pickled ginger on a wooden geta
meal_tacos_trio: three tortilla shells in a rack with mince, lettuce, tomato, cheese, lime
meal_tomato_soup_bowl: bowl of tomato soup with cream swirl, croutons, basil, spoon, saucer
fruit_apple_green_pair: two Granny Smith apples with stalk and leaf
fruit_apple_red_and_slice: red apple with stalk and leaf, three crescent wedges
fruit_banana_bunch: hand of four bananas on a crown (five-sided skins, browned tips)
fruit_blueberries_bowl: bowl of 50 blueberries with a mint sprig
fruit_cherries_stems: six cherries on stalks with a leaf
fruit_coconut_cracked: whole coconut and a cracked half-shell with white flesh
fruit_grapes_green_vine: green grape bunch on its stem with a vine leaf
fruit_grapes_purple: purple grape bunch with stem and leaf
fruit_kiwi_halves: kiwi with fuzzy skin and two halves showing seeds around a white core
fruit_lemons_cut: two whole lemons and a halved lemon with segments
fruit_mango_hedgehog: mango and a scored 'hedgehog' cheek with cubes
fruit_orange_and_half: orange with dimpled peel, half orange with segments, a wedge
fruit_peaches_halved: two peaches and a halved peach with stone
fruit_pear_ripe: two pears, one standing with stalk and leaf
fruit_pineapple_whole: pineapple with diamond-patterned skin and a crown of 23 leaves
fruit_pomegranate_open: whole pomegranate with crown and a cut half full of ruby seeds
fruit_strawberries_bowl: bowl of eleven strawberries with calyxes
fruit_watermelon_wedge: striped rind, red flesh, black seeds
veg_asparagus_bundle: nine spears tied with raffia
veg_aubergine_pair: two glossy aubergines with calyx and stalk
veg_bell_peppers_trio: red, yellow and green peppers with stalks
veg_broccoli_cauliflower: broccoli crown and cauliflower on stalks
veg_cabbage_green: green cabbage with six wrapper leaves
veg_cabbage_red_halved: red cabbage and a half head showing its layered cross-section
veg_carrots_bunch: five carrots with leafy tops tied with string
veg_chili_peppers_pile: nine red and green chillies
veg_corn_cobs: corn cob with kernels and one half-husked cob
veg_cucumbers_sliced: whole cucumber and six slices with seed centres
veg_garlic_bulbs: two bulbs with papery skin and four cloves
veg_lettuce_heads: butterhead and green leaf lettuce heads with 20 frilly outer leaves
veg_mushrooms_brown_white: five button and chestnut mushrooms (cap and stem)
veg_onions_assorted: brown and red onions, stalks, onion rings
veg_pea_pods_open: four pods and an opened pod with peas
veg_potatoes_pile: seven lumpy potatoes with eyes and speckles
veg_pumpkin_ribbed: 0.29 m ribbed pumpkin with a curved stalk
veg_radish_bunch: six radishes with leaves
veg_tomatoes_on_vine: four tomatoes on a vine with calyxes and leaves
deli_butter_dish_and_knife: butter block on a porcelain dish with a knife
deli_charcuterie_board: walnut board with salami slices, ham, olives, bread, nuts and gherkins
deli_cheese_board: maple board with brie, cheddar, swiss with holes, grapes, crackers, walnuts and a knife
deli_egg_carton_dozen: pulp carton with twelve brown and white eggs and an open lid
deli_ham_leg_stand: cured ham leg on a wooden stand with sliced ham
deli_honey_pot_dipper: glass pot of honey with a wooden dipper
deli_jam_jars_trio: three glass jars (jam, honey, peanut butter) with labels and screw lids
deli_parmesan_wheel_wedge: 0.36 m parmesan wheel and a cut wedge
deli_sausage_plate: three bratwursts, mashed potato, mustard, plate
harvest_crate_cabbages: slatted wooden crate of green and red cabbages
harvest_crate_herbs: grey crate of basil, mint and dill bundles
harvest_crate_lettuce: grey crate of nine lettuces
harvest_crate_peppers: grey crate of red, yellow and green peppers
harvest_crate_potatoes: cardboard-coloured crate of potatoes
harvest_crate_strawberries: crate heaped with 42 strawberries
harvest_crate_tomatoes: blue crate of tomatoes with calyxes
harvest_tray_mushrooms: soil tray of 18 mushrooms
hanging_chili_ristra: string of 29 red chillies on a wooden hook board
hanging_garlic_braid: braid of eleven garlic bulbs
hanging_herb_bundles: four bundles of basil, dill, mint and spinach drying on a rail
hanging_sausage_links_hanging: four strings of salami and sausages on a steel rail
drink_bubble_tea_cup: clear plastic cup, milk tea, 34 tapioca pearls, domed lid, fat straw
drink_cappuccino_rosetta: cup and saucer, rosetta latte art, biscuit
drink_coffee_pot_and_mugs: glass carafe with a black collar, two mugs of black coffee
drink_espresso_cup_sugar: dark espresso cup with crema, two sugar cubes, spoon
drink_hot_cocoa_mug: red mug of cocoa with marshmallows
drink_iced_coffee_glass: glass with coffee, milk layer, ice cubes, straw
drink_latte_art_cup: white cup, saucer, heart-shaped latte art, spoon
drink_latte_macchiato_glass: layered coffee, milk and froth in a glass on a steel saucer, spoon
drink_lemonade_pitcher_set: glass pitcher with lemon slices and ice, two glasses, mint
drink_mason_jar_green_smoothie: mason jar of green smoothie with straw and spinach
drink_milk_glass_cookies: glass of milk with froth and three cookies
drink_milkshake_whipped: milkshake with whipped cream, cherry and straw
drink_orange_juice_glass: glass of orange juice with an orange slice and straw
drink_smoothie_strawberry_tall: tall strawberry smoothie, strawberry on the rim, straw
drink_tea_cup_with_bag: glass cup of tea with tea bag and saucer
drink_tea_pot_and_cups: blue teapot with two cups of tea on saucers
drink_water_glass_ice_lemon: tumbler of water with ice cubes and a lemon slice
can_blue_cooler_tall: 0.066 x 0.169 m 500 ml aluminium can with diagonal blue print
can_cola: standard 0.066 x 0.122 m can, red print with white discs, stay tab
can_cold_brew: stubby coffee can with diagonal brown print
can_energy_slim: slim 58 mm can with black print and yellow bars
can_grape_pop_mini: mini 150 ml can with purple spots
can_lime_fizz: standard can with bottle-shaped shoulder, green zig-zag print
can_orange_soda: orange can with a wave print and a slight belly
can_sixpack_cola: six cola cans held by a clear ring carrier
can_tonic_sleek: tall sleek can with white print and blue chevrons
bottle_beer_brown_longneck: brown glass bottle with label and gold crown cap
bottle_beer_lager_green: green glass bottle with zig-zag label and red cap
bottle_champagne_foil: dark bottle with gold foil neck, label with dots
bottle_gin_blue_flask: blue glass bottle with cork stopper
bottle_hip_flask_steel: steel hip flask with leather panel and screw cap
bottle_hot_sauce_bottle: green glass bottle of red sauce with shaker cap
bottle_milk_bottle_glass: glass milk bottle with foil cap and printed label
bottle_olive_oil_cruet: green glass cruet of oil with a steel pourer
bottle_sport_bottle_squeeze: squeeze bottle with a push-pull cap
bottle_thermos_vacuum_flask: steel vacuum flask with cup lid and handle
bottle_water_bottle_500ml: clear PET bottle, water, printed label, blue cap
bottle_whisky_decanter_square: square decanter of whisky with cork stopper and label
bottle_wine_red_bordeaux: dark Bordeaux bottle with label and wax seal
bottle_wine_white_hock: green hock bottle with label and gold foil
cocktail_beer_mug_foam: glass mug of beer with a foam head and a thick handle
cocktail_blue_lagoon_hurricane: hurricane glass of blue lagoon, ice, cherry, paper umbrella, straw
cocktail_champagne_flute: flute of champagne with rising bubbles
cocktail_margarita_salt_rim: margarita glass with salted rim and a lime wheel
cocktail_martini_olive: martini glass with an olive on a pick
cocktail_mojito_mint_highball: highball with ice, mint sprigs, lime wheel and straw
cocktail_old_fashioned_orange: tumbler with whisky, large ice cube, orange peel twist and cherry
cocktail_pint_stout: pint glass of stout with creamy head
cocktail_whisky_rocks_tumbler: heavy tumbler with whisky and two ice cubes
cocktail_wine_glass_red: stemmed glass of red wine
ration_bento_ration_box: four-compartment ration box (rice, broccoli, steak, orange segments), lid and spork
ration_canned_beans_open: tin of baked beans with the lid bent back, label and spoon
ration_cup_noodle_instant: printed cup noodle with a peeled lid and a fork
ration_freeze_dried_tray: compartment tray of freeze-dried pasta, rice and beans under peeling film
ration_mre_tray_pasta: foil tray of pasta bolognese, sauce pouch, spork
ration_nutrient_tubes_set: three crimped nutrient-paste tubes with caps and printed labels
ration_pouch_beef_stew: two stand-up retort pouches (stew and pasta) with tear-seal tops
ration_pouch_fruit_puree_spout: two spouted fruit-puree pouches with caps
ration_pouch_vegetable_flat: two flat vegetable and oats ration pouches with sealed edges
ration_protein_bars_stack: four wrapped protein bars, an unwrapped bar and a wrapper
ration_ration_boxes_stacked: three printed cardboard ration cartons
ration_ration_brick_pack: sleeve of compressed ration bricks with a tear strip
ration_water_pouches_stack: six emergency water pouches stacked crosswise
tray_bread_basket_wicker: wicker basket with a napkin and six rolls
tray_breakfast_tray_wood: wooden tray with eggs, toast, orange juice, a latte and strawberries
tray_cake_stand_afternoon_tea: three-tier stand with scones, sandwiches and cakes
tray_cloche_hot_dish: plate with a polished steel cloche
tray_coffee_set_tray: walnut tray with a steel coffee pot, milk jug, two cups and a sugar bowl
tray_drinks_tray_round: steel round tray with water, juice, cola and red wine
tray_fruit_bowl_mixed: porcelain bowl of apples, oranges, bananas, grapes and a pear
tray_hotel_pan_mash_gravy: steel hotel pan of mashed potato with gravy and roast potatoes, serving spoon
tray_hotel_pan_roast_veg: steel hotel pan of roasted vegetables with tongs
tray_meal_tray_brig: moulded brig tray (porridge, beans, rice, apple) with a plastic spork
tray_meal_tray_steel: steel five-compartment tray (mash, peas, steak, roll, berries, milk carton, spork)
tray_soup_tureen_ladle: porcelain tureen with soup, two handles, a ladle
buffet_bakery_display_stand: 1.45 m wooden stand with baguettes, loaves, rolls and croissants on three shelves
buffet_chafing_buffet_line: 1.9 m steel buffet counter with four hot pans (curry, rice, tomato soup, cheese sauce), sneeze guard and plates
buffet_dessert_display_case: glass dessert counter with cakes, pies and cupcakes on two levels
buffet_fruit_market_stand: tiered market stand with tilted shelves of apples, oranges, lemons and tomatoes
"""

INTRO = {
    "bakery": ("Bakery", "Breads, pastries and cakes from the galley oven."),
    "dessert": ("Desserts", "Puddings, ice cream and sweets."),
    "meal": ("Meals", "Plated dishes and bowls, each a complete serving on its own crockery."),
    "fruit": ("Fruit", "Whole, cut and bowled fruit."),
    "veg": ("Vegetables", "Fresh produce from the grow beds and cold store."),
    "deli": ("Deli and dairy", "Cheese, cured meat, eggs, spreads and boards."),
    "harvest": ("Hydroponic harvest", "Floor-standing crates of freshly picked crops (hydroponics, galley, cold store)."),
    "hanging": ("Hanging produce", "Wall-mounted drying produce, origin at the centre of the back plane."),
    "drink": ("Coffee, tea and cold drinks", "Cups, mugs, glasses and pitchers with liquids."),
    "can": ("Cans", "Brand-less aluminium cans in six sizes and shapes, printed with generic stripes and pictograms."),
    "bottle": ("Bottles and flasks", "Glass, PET and steel containers with printed labels."),
    "cocktail": ("Glassware and cocktails", "Bar glasses with their drinks and garnishes."),
    "ration": ("Space rations", "Shelf-stable mission food: pouches, tubes, bars, trays and tins."),
    "tray": ("Serving trays and dishes", "Meal, breakfast and drinks trays, hot pans, baskets, tureens and stands."),
    "buffet": ("Buffet and display furniture", "Floor-standing serving and display units that carry food."),
}
ORDER = ["meal", "bakery", "dessert", "fruit", "veg", "deli", "harvest", "hanging", "drink", "cocktail", "can", "bottle", "ration", "tray", "buffet"]
SHEETS = [
    ("meals", "Meals", ["meal"]), ("bakery_dessert", "Bakery and desserts", ["bakery", "dessert"]),
    ("fruit_veg", "Fruit and vegetables", ["fruit", "veg"]), ("deli_harvest", "Deli, harvest and hanging produce", ["deli", "harvest", "hanging"]),
    ("drinks", "Drinks and cocktails", ["drink", "cocktail"]), ("cans_bottles", "Cans and bottles", ["can", "bottle"]),
    ("rations_trays", "Rations, trays and buffet", ["ration", "tray", "buffet"]),
]


def main():
    with open(os.path.join(ROOT, "godot", "data", "catalog.json")) as fh:
        cat = json.load(fh)["models"]
    desc = {}
    for ln in MENU.strip().splitlines():
        k, v = ln.split(": ", 1)
        desc[k.strip()] = v.strip()
    food = [m for m in cat if m["category"] in INTRO]
    missing = [m["id"] for m in food if m["id"] not in desc]
    stale = [k for k in desc if k not in {m["id"] for m in food}]
    if missing or stale:
        sys.exit("MENU out of date: missing %s, unknown %s" % (missing, stale))
    out = []
    w = out.append
    n_tex = len({f[:-4] for f in os.listdir(os.path.join(ROOT, "godot", "textures", "food")) if f.endswith(".jpg")})
    w("# Food and drink menu\n")
    w("%d food and drink models in %d categories (`blender/starship/components/food*.py`), all generated headless in Blender (bpy). "
      "Sizes are real-world (metres in the game, shown here in centimetres as width x depth x height); every dish stands on a table, every "
      "crate on the floor, every hanging bunch on a wall (origins as in `blender/CONVENTIONS.md`).\n" % (len(food), len(INTRO)))
    w("## Contents\n")
    for sid, title, cats in SHEETS:
        w("* [%s](#%s)" % (title, title.lower().replace(",", "").replace(" ", "-")))
    w("* [How the food is modelled](#how-the-food-is-modelled)")
    w("* [Where the food appears](#where-the-food-appears)\n")
    for sid, title, cats in SHEETS:
        w("## %s\n" % title)
        w("![%s](screenshots/food_sheet_%s.jpg)\n" % (title, sid))
        for c in [c for c in ORDER if c in cats]:
            name, blurb = INTRO[c]
            rows = sorted([m for m in food if m["category"] == c], key=lambda m: m["id"])
            w("### %s (`%s`, %d)\n" % (name, c, len(rows)))
            w("%s Mount: `%s`.\n" % (blurb, rows[0]["mount"]))
            w("| Model | Size w x d x h (cm) | On the model | Tris | KB |")
            w("|---|---|---|---|---|")
            for m in rows:
                sx, sy, sz = m["size"]
                w("| `%s` | %.0f x %.0f x %.0f | %s | %d | %d |" % (m["id"], sx * 100, sz * 100, sy * 100, desc[m["id"]], m["tris"], round(m["bytes"] / 1024)))
            w("")
    w("""## How the food is modelled

* **Surfaces of revolution and bmesh organics.** Plates, bowls, glasses, bottles, cans, fruit and cakes are lathe surfaces (`foodkit.lathe`):
  an outline of (radius, height) points swept around the Y axis, with optional **fractal noise displacement** (`mathutils.noise`), a **warp
  function** (bends a lathe into a croissant or banana, twists a frosting swirl, pinches a pouch) and smooth shading with a 52 degree crease
  angle. `foodkit.blob` makes displaced ellipsoids, `tube3` sweeps a smooth tube along a Catmull-Rom spline (noodles, sausages, vines,
  stalks), `extrude` makes wedges and slices with separate cap and side materials, `slab` rounded blocks, `crate` slatted harvest crates.
* **Several parts, several materials.** A burger is bun, lettuce frill, tomato slices, patty, cheese, sesame seeds; a ramen bowl is bowl,
  broth, 22 noodle strands, egg halves, pork, nori, scallions and chopsticks.
* **Procedural textures** (`blender/starship/textures_food.py`): %d tileable 256 x 256 albedo maps generated with numpy (fractal noise,
  Voronoi cells, ramps, stripes, polar patterns) and stored as JPEG in `godot/textures/food/`: crusts, crumb, pizza top, steak with grill marks,
  salami, bacon, tomato / apple / citrus / banana / strawberry / watermelon / pineapple skins, leaf veins, cabbage, cheese with holes,
  pasta, rice, curry, broth, wood grain, wicker, latte art (heart, rosetta, swirl), beer foam and the printed can, pouch and bottle labels
  (brand-less stripes and pictograms - no text). The kit material prefix `tex:<name>` loads a map; models project UVs (cylindrical, spherical,
  planar or box) so every textured part has UVs, and the GLB embeds the JPEG.
* **Glass and liquids** use alpha-blended materials (`f_glass`, `f_water`, `f_juice_orange`, `f_wine_red`, `f_beer` ...): a glass is a thin
  closed shell, its liquid a slightly smaller lathe, with an opaque textured surface disc where the top matters (coffee art, cocoa, foam).
* **Budget.** Models are 500 - 6000 triangles; GLBs are mostly 60 - 150 KB (the embedded textures included); the hard limit in
  `tests/test_project.py` is 400 KB.

Rebuild just the food: `python blender/build_all.py --out godot --only '^(bakery|dessert|meal|fruit|veg|deli|harvest|hanging|drink|can|bottle|cocktail|ration|tray|buffet)_'`
(missing textures are generated first). Render a contact sheet with Blender Cycles (needs bpy and Pillow):

```bash
python blender/food_sheet.py docs/screenshots/food_sheet_meals.jpg --cols 7 --size 260 --samples 16 godot/models/meal/*.glb
python blender/food_menu.py        # regenerate this document
```

## Where the food appears

`tools/layout/policy.py` lists which food families may stand in which room (`FOOD_*` sets; alcohol only in the wardroom, lounge, captain's
quarters and the galley stores) and registers the two new rooms `wardroom` and `provisions`. `tools/layout/recipes_food.py` dresses the rooms:

* **Mess hall** - six long tables and three short tables, each laid with a *different* set of full meals, a drink at each place and a
  centrepiece (bread basket, fruit bowl, soup tureen, cheese board, lemonade, pie); a hot-pan buffet counter and a bakery stand.
* **Galley** - raw ingredients on the prep island, finished dishes on the counters, hot pans and cold dishes on the serving counters,
  garlic / chilli / herbs / sausages hung on the wall, harvest crates by the door.
* **Hydroponics** - harvest crates beside the beds, tasting table, drying herbs.
* **Lounge, captain's quarters, conference room, ready room, bridge, cabins, rec room, crew quarters, medical bay, brig, security office** -
  bar glassware, a captain's dinner, refreshments for meetings, coffee for the watch, patient meal trays, the detainee's tray ...
* **Wardroom and provisions hold** - `food_wardroom(R, B)` and `food_provisions(R, B)` in `recipes_food.py` are ready for the recipes of the
  two new rooms (bar counters and dinner tables; crates, hanging store and rations on the shelving).
""" % n_tex)
    with open(os.path.join(ROOT, "docs", "FOOD.md"), "w") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote docs/FOOD.md,", len(food), "models")


if __name__ == "__main__":
    main()
