extends AppBase
## Communications: pick a station (factions' nearest systems, the crew intercom), tune the carrier, hail and chat.
## Replies depend on the faction's stance in lore.json.

var _contacts: Tree
var _log: RichTextLabel
var _in: LineEdit
var _freq: HSlider
var _sig: UIW.Meter
var _who: Array = []
var _last := ""

func title_text() -> String:
	return "COMMUNICATIONS"

func build() -> void:
	_who = [{"id": "intercom", "name": "Ship intercom", "stance": "crew"}]
	for f in Lore.factions():
		if f["id"] != "none":
			_who.append({"id": f["id"], "name": f["name"], "stance": f.get("stance", "")})
	_who.append({"id": "unknown", "name": "Unknown carrier 14.2 GHz", "stance": "unknown"})
	var row := hb(self, 10)
	var left := vb(row, 8)
	left.custom_minimum_size.x = 320
	left.size_flags_horizontal = Control.SIZE_FILL
	_contacts = table(left, ["Station", "Stance"], [180, 90])
	var rows: Array = []
	var metas: Array = []
	for i in _who.size():
		rows.append([_who[i]["name"], _who[i]["stance"]])
		metas.append(i)
	table_fill(_contacts, rows, metas)
	_contacts.item_selected.connect(refresh)
	_freq = slider(left, "Carrier (GHz)", 1.0, 30.0, 14.2, func(_v: float) -> void: refresh(), 0.1, "%.1f")
	_sig = meter(left, "SIGNAL", 0.0, 0.0)
	_sig.invert = true
	_sig.warn = 0.5
	_sig.crit = 0.25
	btn(left, "OPEN HAILING CHANNEL", _hail)
	var right := panel(row, "Transcript")
	_log = rich(right)
	_log.scroll_following = true
	var ir := hb(right)
	_in = line_edit(ir, "message...", _send)
	btn(ir, "SEND", func() -> void: _send(_in.text))
	table_select(_contacts, 0)

func _cur() -> Dictionary:
	var m: Variant = table_selected(_contacts)
	return {} if m == null else _who[int(m)]

func _hail() -> void:
	var w := _cur()
	if w.is_empty():
		return
	_reply(w, "hail")

func _send(t: String) -> void:
	t = t.strip_edges()
	var w := _cur()
	if t == "" or w.is_empty():
		return
	st.comm_log.append({"who": w["id"], "text": t, "mine": true})
	st.say("Comms to %s: %s" % [w["name"], t], "comms")
	_in.clear()
	_reply(w, t)

func _reply(w: Dictionary, t: String) -> void:
	var r := ""
	match w["stance"]:
		"crew": r = "Acknowledged, bridge."
		"friendly": r = "Meridian Dawn, this is %s. Good to hear you. Lanes are clear; mail is waiting." % w["name"]
		"wary": r = "%s control. State your route and cargo. Remain on the marked lane." % w["name"]
		"home": r = "Compact command. Message received, Meridian Dawn. Keep the logs coming."
		_: r = "No response."
	if w["id"] == "unknown":
		r = "[carrier only: repeating tone, 14.2 GHz, no modulation. Source bearing: Kepler Gate.]"
	st.comm_log.append({"who": w["id"], "text": r, "mine": false})
	st.changed.emit()

func refresh() -> void:
	var w := _cur()
	if w.is_empty():
		return
	var out := ""
	for m in st.comm_log:
		if m["who"] != w["id"]:
			continue
		var txt := String(m["text"]).replace("[", "[lb]")
		if m["mine"]:
			out += "[color=#5cd6e0]YOU:[/color] %s\n" % txt
		else:
			out += "[color=#ffc247]%s:[/color] %s\n" % [w["name"], txt]
	if out == "":
		out = "[color=#7a95a0]Channel idle. Hail %s or type a message.[/color]\n" % w["name"]
	if out != _last:
		_last = out
		_log.text = out
	var q := 0.2 + 0.75 * (1.0 - absf(_freq.value - 14.2) / 16.0)
	if w["id"] == "intercom":
		q = 1.0
	_sig.set_value(q * (0.5 if st.brownout() else 1.0), "%.0f%%" % (q * 100.0))
