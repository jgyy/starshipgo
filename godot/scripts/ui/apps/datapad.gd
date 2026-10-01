extends AppBase
## Datapad: documents (lore datapads), the glossary, and the timeline of the Compact.

var _tabs: TabContainer
var _docs: Tree
var _gloss: Tree
var _reader: RichTextLabel
var _g_reader: RichTextLabel
var _time: RichTextLabel

func title_text() -> String:
	return "DATAPAD"

func build() -> void:
	_tabs = tab_container(self, ["DOCUMENTS", "GLOSSARY", "TIMELINE"])
	var row := hb(page(_tabs, 0), 10)
	_docs = table(row, ["Document"], [240])
	var rows: Array = []
	var metas: Array = []
	var dps := Lore.datapads()
	for i in dps.size():
		rows.append([dps[i]["title"]])
		metas.append(i)
	table_fill(_docs, rows, metas)
	_docs.item_selected.connect(func() -> void:
		var m: Variant = table_selected(_docs)
		if m != null:
			_reader.text = "[b][color=#5cd6e0]%s[/color][/b]\n\n%s" % [dps[int(m)]["title"], dps[int(m)]["text"]])
	_reader = rich(row)
	_reader.size_flags_stretch_ratio = 1.8
	if dps.is_empty():
		_reader.text = "[color=#7a95a0]No datapads in lore.json.[/color]"
	var grow := hb(page(_tabs, 1), 10)
	_gloss = table(grow, ["Term"], [200])
	var gl := Lore.glossary()
	var gr: Array = []
	var gm: Array = []
	for i in gl.size():
		gr.append([gl[i]["term"]])
		gm.append(i)
	table_fill(_gloss, gr, gm)
	_gloss.item_selected.connect(func() -> void:
		var m: Variant = table_selected(_gloss)
		if m != null:
			_g_reader.text = "[b][color=#5cd6e0]%s[/color][/b]\n\n%s" % [gl[int(m)]["term"], gl[int(m)]["text"]])
	_g_reader = rich(grow)
	_g_reader.size_flags_stretch_ratio = 1.8
	_time = rich(page(_tabs, 2))
	var out := ""
	for t in Lore.data().get("timeline", []):
		out += "[b][color=#ffc247]%s[/color][/b]  [color=#5cd6e0]%s[/color]\n%s\n\n" % [str(t.get("year", "")), t.get("title", ""), t.get("text", "")]
	_time.text = out if out != "" else "[color=#7a95a0]No timeline in lore.json.[/color]"
