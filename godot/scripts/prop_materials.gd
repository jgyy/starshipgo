class_name PropMaterials
extends RefCounted
## Replaces the flat Blender colours of the 1000 prop models with texture-backed materials.
##
## The GLBs only carry a Principled BSDF per material *name* (wood_dark, fabric_navy, brushed_alu, paint_red ...).
## apply_mesh() looks at each surface of an imported mesh and, when the name is in RULES (or matches a family rule),
## swaps in a StandardMaterial3D that
##   * keeps the original albedo colour as a tint (the textures are "neutral": near-white albedo),
##   * keeps the original metallic / roughness values (the ORM roughness is a relative modulation around ~0.9),
##   * projects the texture with object-space triplanar UVs, so props, MultiMesh instances and doors need no UVs
##     and the texture scales with the model, not with the room,
##   * uses trilinear + 16x anisotropic sampling of a mip-mapped texture (see project.godot) and a moderate normal
##     scale, so nothing shimmers at a distance.
## Materials are cached and shared per (kind, colour, metallic, roughness), so draw calls do not increase.
## Emissive, glass / transparent and screen materials are never touched.

const DIR := "res://textures/surfaces/"

# material name -> [texture kind, metres per texture repeat, normal scale]
const RULES := {
	"wood_dark": ["p_wood_fine", 0.5, 0.8], "wood_light": ["p_wood_fine", 0.5, 0.8],
	"leather_black": ["p_leather", 0.4, 0.8], "leather_brown": ["p_leather", 0.4, 0.8],
	"fabric_navy": ["p_weave", 0.3, 0.7], "fabric_grey": ["p_weave", 0.3, 0.7], "fabric_red": ["p_weave", 0.3, 0.7],
	"fabric_tan": ["p_weave", 0.3, 0.7], "fabric_teal": ["p_weave", 0.3, 0.7],
	"steel": ["p_brushed", 0.5, 0.6], "brushed_alu": ["p_brushed", 0.5, 0.6], "chrome": ["p_scratched", 0.8, 0.5],
	"gunmetal": ["p_scratched", 0.8, 0.6], "black_metal": ["p_scratched", 0.8, 0.6],
	"hull_light": ["p_metal_satin", 0.8, 0.6], "hull_mid": ["p_metal_satin", 0.8, 0.6], "hull_dark": ["p_metal_satin", 0.8, 0.6],
	"carbon": ["carbon_fibre_twill", 0.4, 0.6], "concrete": ["p_concrete", 1.5, 0.8],
	"cardboard": ["p_cardboard", 0.4, 0.8], "foam": ["p_foam", 0.4, 0.8], "rubber": ["p_rubber", 0.4, 0.6],
	"plastic_white": ["p_plastic", 0.5, 0.4], "plastic_black": ["p_plastic", 0.5, 0.4], "plastic_grey": ["p_plastic", 0.5, 0.4],
	"ceramic": ["p_ceramic", 0.6, 0.3], "leaf": ["p_leaf", 0.3, 0.7], "soil": ["p_soil", 0.6, 0.8],
	"copper": ["p_brushed", 0.4, 0.6], "brass": ["p_brushed", 0.4, 0.6], "gold_trim": ["p_brushed", 0.4, 0.6],
	"hazard_yellow": ["p_paint", 0.6, 0.5],
	"crew_sheet": ["p_weave", 0.3, 0.7], "crew_pillow": ["p_weave", 0.3, 0.7], "crew_mustard": ["p_weave", 0.3, 0.7],
	"crew_plum": ["p_weave", 0.3, 0.7], "crew_olive": ["p_weave", 0.3, 0.7], "st_carpet": ["p_weave", 0.3, 0.7],
	"crew_tile": ["p_ceramic", 0.6, 0.3], "crew_pot": ["p_ceramic", 0.6, 0.3], "crew_moss": ["p_leaf", 0.3, 0.7],
	"ls_dleaf": ["p_leaf", 0.3, 0.7], "ls_tub": ["p_soil", 0.6, 0.8], "sec_mat": ["p_rubber", 0.4, 0.6],
	"cm_rack": ["p_scratched", 0.8, 0.6], "sec_blaster": ["p_scratched", 0.8, 0.6],
}

# name prefix / substring families for the many module-specific materials (paint_*, steel_*, wood_*, ...)
const PREFIX_RULES := [
	["paint_", "p_paint", 0.6, 0.5], ["wood_", "p_wood_fine", 0.5, 0.8], ["wooden", "p_wood_coarse", 0.5, 0.8],
	["steel_", "p_brushed", 0.5, 0.6], ["plastic_", "p_plastic", 0.5, 0.4], ["fabric_", "p_weave", 0.3, 0.7],
	["leather_", "p_leather", 0.4, 0.8], ["sci_epoxy", "p_paint", 0.6, 0.4], ["sci_white", "p_paint", 0.6, 0.4],
	["sci_teal", "p_paint", 0.6, 0.4], ["md_teal", "p_paint", 0.6, 0.4], ["md_sheet", "p_weave", 0.3, 0.7],
	["crew_seam", "p_weave", 0.3, 0.7], ["st_", "p_paint", 0.6, 0.5], ["cg_", "p_paint", 0.6, 0.4],
]

static var _cache: Dictionary = {}
static var _tex: Dictionary = {}

static func _rule_for(name: String, m: StandardMaterial3D) -> Array:
	if RULES.has(name):
		return RULES[name]
	for r in PREFIX_RULES:
		if name.begins_with(r[0]):
			return [r[1], r[2], r[3]]
	if m.metallic >= 0.6:
		return ["p_metal_satin", 0.8, 0.6]
	return []

static func _load(path: String) -> Texture2D:
	if not _tex.has(path):
		_tex[path] = load(path) if ResourceLoader.exists(path) else null
	return _tex[path]

## Texture-backed replacement for the imported material `src` (cached), or null if the material is left alone.
static func material_for(src: Material) -> Material:
	var m := src as StandardMaterial3D
	if m == null or m.albedo_texture != null or m.emission_enabled:
		return null
	if m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or m.albedo_color.a < 0.99:
		return null
	var name := String(m.resource_name)
	if name == "" or name.begins_with("screen") or name.begins_with("em_") or name.begins_with("glass"):
		return null
	var rule := _rule_for(name, m)
	if rule.is_empty():
		return null
	var kind: String = rule[0]
	var key := "%s|%s|%.2f|%.2f|%d" % [kind, m.albedo_color.to_html(false), m.metallic, m.roughness, m.cull_mode]
	if _cache.has(key):
		return _cache[key]
	var base := DIR + kind + "_"
	var alb := _load(base + "albedo.png")
	if alb == null:
		return null
	var own := not kind.begins_with("p_")             # full PBR sets (carbon fibre): physical ORM, own colour
	var out := StandardMaterial3D.new()
	out.resource_name = name + "_tex"
	out.albedo_texture = alb
	out.albedo_color = Color.WHITE if own else m.albedo_color
	var nrm := _load(base + "normal.png")
	if nrm != null:
		out.normal_enabled = true
		out.normal_texture = nrm
		out.normal_scale = float(rule[2])
	var orm := _load(base + "orm.png")
	if orm != null:
		out.ao_enabled = true
		out.ao_texture = orm
		out.ao_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
		out.ao_light_affect = 0.5
		out.roughness_texture = orm
		out.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
	if own:
		out.roughness = 1.0
		if orm != null:
			out.metallic_texture = orm
			out.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
		out.metallic = 1.0
	else:
		out.roughness = clampf(m.roughness / 0.9, 0.04, 1.0)       # neutral ORM roughness is ~0.9 on average
		out.metallic = m.metallic
	out.metallic_specular = m.metallic_specular
	out.cull_mode = m.cull_mode
	out.uv1_triplanar = true
	out.uv1_world_triplanar = false                                  # object space: scales with the model, needs no UVs
	out.uv1_triplanar_sharpness = 3.0
	out.uv1_scale = Vector3.ONE / float(rule[1])
	out.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_cache[key] = out
	return out

## Swap the materials of every surface of an imported mesh (once per mesh resource).
static func apply_mesh(mesh: Mesh) -> void:
	if mesh == null or mesh.has_meta("pm_done"):
		return
	mesh.set_meta("pm_done", true)
	for i in mesh.get_surface_count():
		var nm := material_for(mesh.surface_get_material(i))
		if nm != null:
			mesh.surface_set_material(i, nm)

## Same for every MeshInstance3D below `root` (door models).
static func apply_tree(root: Node) -> void:
	var stack: Array = [root]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			apply_mesh(mi.mesh)
			if mi.material_override != null:
				var o := material_for(mi.material_override)
				if o != null:
					mi.material_override = o
		for c in n.get_children():
			stack.append(c)
