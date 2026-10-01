extends AppBase
## Ship's computer: a working command line.  exec(line) returns the text a command prints (the tests call it directly).

var _out: RichTextLabel
var _in: LineEdit
var _hist: Array = []
var _hist_i := 0

func title_text() -> String:
	return "COMPUTER"

func build() -> void:
	var v := vb(self, 6)
	_out = rich(v)
	_out.scroll_following = true
	_out.custom_minimum_size.y = 300
	var row := hb(v)
	lbl(row, ">", 18, T.ACCENT)
	_in = line_edit(row, "type a command - 'help' lists them", _submit)
	btn(row, "RUN", func() -> void: _submit(_in.text))
	say_line("[color=#5cd6e0]%s  -  %s[/color]" % [Lore.ship_info().get("name", "Ship"), Lore.ship_info().get("registry", "")])
	say_line("Ship's computer online. Type [b]help[/b] for commands.")
	_in.grab_focus.call_deferred()

func say_line(t: String) -> void:
	_out.append_text(t + "\n")

func _input(e: InputEvent) -> void:
	if _in != null and _in.has_focus() and e is InputEventKey and e.pressed:
		if e.keycode == KEY_UP and not _hist.is_empty():
			_hist_i = maxi(0, _hist_i - 1)
			_in.text = _hist[_hist_i]
			_in.caret_column = _in.text.length()
			get_viewport().set_input_as_handled()
		elif e.keycode == KEY_DOWN and not _hist.is_empty():
			_hist_i = mini(_hist.size(), _hist_i + 1)
			_in.text = "" if _hist_i >= _hist.size() else _hist[_hist_i]
			_in.caret_column = _in.text.length()
			get_viewport().set_input_as_handled()

func _submit(line: String) -> void:
	line = line.strip_edges()
	if line == "":
		return
	_hist.append(line)
	_hist_i = _hist.size()
	say_line("[color=#5cd6e0]> %s[/color]" % line.replace("[", "[lb]"))
	var r := exec(line)
	if r == "\u0001clear":
		_out.clear()
	else:
		say_line(r.replace("[", "[lb]"))
	_in.clear()
	_in.grab_focus.call_deferred()

const HELP := """Commands:
  help                     this list
  status                   ship status summary
  map                      decks and rooms
  locate <room|crew>       where is it
  specs <model>            machine data card (id or part of it)
  lore [term|system]       ship lore, glossary and star systems
  log [list|<n>]           ship event log / crew log entries
  list systems|rooms|doors|apps|models <category>
  alert <green|yellow|red> set the alert level
  lock <door> / unlock <door>   door by room id or name, e.g. lock brig
  lockall / unlockall
  dest <system>            plot a course          jump   start the jump
  warp <0-9.9>             set warp factor
  hangar <on|off>          hangar force field
  scram / restart          reactor
  time                     stardate and ship clock
  clear                    clear the screen"""

func exec(line: String) -> String:
	var parts := line.strip_edges().split(" ", false)
	if parts.is_empty():
		return ""
	var cmd := String(parts[0]).to_lower()
	var arg := " ".join(parts.slice(1)).strip_edges()
	match cmd:
		"help", "?":
			return HELP
		"status":
			return st.status_text()
		"time":
			return "Stardate %.2f   Ship time %s" % [st.stardate(), st.ship_clock()]
		"clear":
			return "\u0001clear"
		"map":
			return _cmd_map()
		"locate":
			return _cmd_locate(arg)
		"specs":
			return _cmd_specs(arg)
		"lore":
			return _cmd_lore(arg)
		"log":
			return _cmd_log(arg)
		"list":
			return _cmd_list(arg)
		"alert":
			if arg == "":
				return "Alert level: %s" % st.alert.to_upper()
			return ("Alert level set to %s." % arg.to_upper()) if st.set_alert(arg) else ("Unknown alert level '%s' (green, yellow, red)." % arg)
		"lock", "unlock":
			var want := cmd == "lock"
			var found := st.find_doors(arg)
			if arg == "" or found.is_empty():
				return "No door matches '%s'. Try 'list doors'." % arg
			var out: Array = []
			for i in found:
				st.set_door_locked(i, want)
				out.append(st.door_label(i))
			return "%s %d door(s):\n  %s" % ["Locked" if want else "Unlocked", found.size(), "\n  ".join(out)]
		"lockall":
			st.lock_all(true)
			return "All %d doors locked." % st.doors.size()
		"unlockall":
			st.lock_all(false)
			return "All doors unlocked."
		"dest", "destination", "plot":
			var sid := _find_system(arg)
			if sid == "":
				return "Unknown system '%s'. Try 'list systems'." % arg
			st.set_destination(sid)
			var names: Array = []
			for x in st.route:
				names.append(Lore.system_name(x))
			return "Course plotted to %s: %.1f ly via %s, ETA %s." % [Lore.system_name(sid), st.route_ly(), " > ".join(names), st.eta_text()]
		"jump":
			return "Jump started." if st.jump(_find_system(arg) if arg != "" else "") else "Cannot jump (no destination, already there, in transit, or reactor offline)."
		"warp":
			if not arg.is_valid_float():
				return "Warp factor is %.1f." % st.warp
			st.warp = clampf(float(arg), 0.0, float(Lore.ship_info().get("top_warp", 9.2)))
			st.changed.emit()
			return "Warp factor %.1f (%.2f ly/day)." % [st.warp, st.warp_ly_per_day()]
		"hangar":
			if arg in ["on", "off"]:
				st.set_hangar_field(arg == "on")
			return "Hangar force field is %s." % ("ON" if st.hangar_field_on else "OFF")
		"scram":
			st.set_scram(true)
			return "REACTOR SCRAM."
		"restart":
			st.set_scram(false)
			return "Reactor restarted."
	return "Unknown command '%s'. Type 'help'." % cmd

func _find_system(q: String) -> String:
	q = q.to_lower().strip_edges()
	if q == "":
		return ""
	for s in Lore.systems():
		if s["id"] == q or String(s["name"]).to_lower() == q:
			return s["id"]
	for s in Lore.systems():
		if String(s["name"]).to_lower().contains(q) or String(s["id"]).contains(q):
			return s["id"]
	return ""

func _cmd_map() -> String:
	var out: Array = []
	for d in st.ship.get("decks", []):
		out.append("DECK %d - %s" % [int(d["id"]), d["name"]])
		var names: Array = []
		for r in st.ship.get("rooms", []):
			if int(r["deck"]) == int(d["id"]) and r.get("dept", "") != "transit":
				names.append("%s (%s)" % [r["name"], r["id"]])
		out.append("  " + ", ".join(names))
	return "\n".join(out)

func _cmd_locate(q: String) -> String:
	if q == "":
		return "locate <room or crew member>"
	q = q.to_lower()
	for r in st.ship.get("rooms", []):
		if String(r["id"]).to_lower() == q or String(r["name"]).to_lower().contains(q):
			var rc: Array = r["rect"]
			var here := ""
			if st.player_room != "":
				for pr in st.ship.get("rooms", []):
					if pr["id"] == st.player_room:
						var pc: Array = pr["rect"]
						var dx: float = (rc[0] + rc[2]) * 0.5 - (pc[0] + pc[2]) * 0.5
						var dz: float = (rc[1] + rc[3]) * 0.5 - (pc[1] + pc[3]) * 0.5
						here = "\n  from %s: %.0f m %s, %.0f m %s, %+d deck(s)" % [pr["name"], absf(dz), "aft" if dz > 0 else "forward", absf(dx), "starboard" if dx > 0 else "port", int(pr["deck"]) - int(r["deck"])]
			return "%s [%s]\n  Deck %d, %s, %.0f m2, centre (%.0f, %.0f)%s" % [r["name"], r["id"], int(r["deck"]), r.get("dept", ""), r.get("area", 0.0), (rc[0] + rc[2]) * 0.5, (rc[1] + rc[3]) * 0.5, here]
	var c := st.crew_by_name(q)
	if not c.is_empty():
		return "%s (%s) is in %s." % [c["name"], c["role"], _cmd_locate(String(c["room"])).split("\n")[0]]
	return "Nothing called '%s'." % q

func _cmd_specs(q: String) -> String:
	if q == "":
		return "specs <model id or part of it>, e.g. specs reactor"
	q = q.to_lower().replace(" ", "_")
	var hits: Array = []
	for id in st.catalog.keys():
		if id == q:
			hits = [id]
			break
		if String(id).contains(q):
			hits.append(id)
	if hits.is_empty():
		return "No model matches '%s'." % q
	if hits.size() > 1:
		hits.sort()
		return "%d models match: %s%s" % [hits.size(), ", ".join(hits.slice(0, 12)), " ..." if hits.size() > 12 else ""]
	var id: String = hits[0]
	var e: Dictionary = st.catalog[id]
	var lines: Array = ["%s  (%s)" % [String(e.get("label", id)).capitalize(), id],
		"  category %s, mount %s, size %.2f x %.2f x %.2f m" % [e.get("category", ""), e.get("mount", ""), e["size"][0], e["size"][1], e["size"][2]]]
	var sp := Lore.spec(id)
	if sp.is_empty():
		lines.append("  (no manufacturer record in specs.json)")
	for k in sp.keys():
		lines.append("  %s: %s" % [String(k).replace("_", " "), str(sp[k])])
	return "\n".join(lines)

func _cmd_lore(q: String) -> String:
	q = q.to_lower().strip_edges()
	if q == "":
		var terms: Array = []
		for g in Lore.glossary():
			terms.append(g["term"])
		var sysn: Array = []
		for s in Lore.systems():
			sysn.append(s["name"])
		return "%s - %s\n%s\n\"%s\"\nGlossary: %s\nSystems: %s" % [Lore.ship_info().get("name", ""), Lore.ship_info().get("class", ""),
			Lore.ship_info().get("description", ""), Lore.ship_info().get("motto", ""), ", ".join(terms), ", ".join(sysn)]
	for g in Lore.glossary():
		if String(g["term"]).to_lower().contains(q):
			return "%s: %s" % [g["term"], g["text"]]
	var sid := _find_system(q)
	if sid != "":
		var s := Lore.system(sid)
		var pl: Array = []
		for p in s.get("planets", []):
			pl.append("%s (%s%s)" % [p["name"], p.get("type", ""), ", habitable" if p.get("habitable", false) else ""])
		return "%s - %s, %s, class %s\n  %s\n  Planets: %s\n  Faction: %s" % [s["name"], s.get("kind", ""), "visited" if st.visited.has(sid) else "unvisited",
			s.get("star", {}).get("class", "?"), s.get("summary", ""), ", ".join(pl) if not pl.is_empty() else "none charted", Lore.faction(s.get("faction", ""))["name"]]
	return "No lore entry for '%s'." % q

func _cmd_log(arg: String) -> String:
	if arg == "list":
		var out: Array = []
		var i := 1
		for l in Lore.logs():
			out.append("%d. [%s] %s - %s" % [i, l["stardate"], l["role"], l["title"]])
			i += 1
		return "\n".join(out) if not out.is_empty() else "No crew logs."
	if arg.is_valid_int():
		var n := int(arg)
		var logs := Lore.logs()
		if n >= 1 and n <= logs.size():
			var l: Dictionary = logs[n - 1]
			return "%s - %s (SD %s)\n%s" % [l["role"], l["title"], l["stardate"], l["text"]]
		return "No log entry %d." % n
	var out2: Array = []
	for m in st.messages.slice(maxi(0, st.messages.size() - 12)):
		out2.append("[%s] %s" % [m["t"], m["text"]])
	return "\n".join(out2)

func _cmd_list(arg: String) -> String:
	var p := arg.split(" ", false)
	var what := "" if p.is_empty() else String(p[0])
	match what:
		"systems":
			var out: Array = []
			for s in Lore.systems():
				out.append("%-18s %-9s %5.1f ly  %s" % [s["name"], s.get("kind", ""), Lore.distance(st.current_system, s["id"]), "visited" if st.visited.has(s["id"]) else ""])
			return "\n".join(out)
		"rooms":
			var out: Array = []
			for r in st.ship.get("rooms", []):
				out.append("%-8s %s" % [r["id"], r["name"]])
			return "\n".join(out)
		"doors":
			var out: Array = []
			for i in st.doors.size():
				out.append("%2d  %-60s %s" % [i, st.door_label(i), "LOCKED" if st.door_locked(i) else "open"])
			return "\n".join(out)
		"apps":
			return ", ".join(AppCatalog.APPS.keys())
		"models":
			var cat := "" if p.size() < 2 else String(p[1])
			if cat == "":
				var cats := {}
				for id in st.catalog.keys():
					cats[st.catalog[id].get("category", "")] = true
				var cl: Array = cats.keys()
				cl.sort()
				return "%d categories: %s\n(list models <category>)" % [cl.size(), ", ".join(cl)]
			var ids: Array = []
			for id in st.catalog.keys():
				if st.catalog[id].get("category", "") == cat:
					ids.append(id)
			ids.sort()
			return "%d models in %s:\n  %s" % [ids.size(), cat, "\n  ".join(ids)]
	return "list systems | rooms | doors | apps | models <category>"

func demo() -> void:
	for c in ["status", "alert yellow", "locate bridge", "specs reactor", "lore kepler", "alert green"]:
		say_line("[color=#5cd6e0]> %s[/color]" % c)
		say_line(exec(c).replace("[", "[lb]"))
