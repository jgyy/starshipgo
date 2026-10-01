class_name ShipMaterials
extends RefCounted
## Material factory for the ship shell (walls, floors, glass ...). All textures
## are the Blender-generated PBR maps in res://textures/surfaces.

static var _cache: Dictionary = {}
static var _index: Dictionary = {}
static var _index_loaded := false

## Metadata written by the texture generator (blender/starship/textures_ext.py): per surface kind its pixel size,
## the real-world size of one repeat in metres ("tile_m"), the group and whether it is a tint-friendly "neutral" set.
static func index() -> Dictionary:
	if not _index_loaded:
		_index_loaded = true
		var f := FileAccess.open("res://textures/surfaces/index.json", FileAccess.READ)
		if f != null:
			var d: Variant = JSON.parse_string(f.get_as_text())
			if d is Dictionary:
				_index = d
	return _index

static func has_kind(kind: String) -> bool:
	return ResourceLoader.exists("res://textures/surfaces/%s_albedo.png" % kind)

## Metres per texture repeat for a kind (what the generator designed it for), or `fallback`.
static func tile_of(kind: String, fallback: float = 2.0) -> float:
	return float(index().get(kind, {}).get("tile_m", fallback))

## Textured PBR material (albedo / normal / ORM maps from res://textures/surfaces), projected with world-space
## triplanar UVs so walls, floors and ceilings need no UVs and neighbouring rooms stay seamless.
## tile <= 0 uses the size the texture was designed for (index.json).
## Anti-flicker settings: trilinear + 16x anisotropic sampling of a mip-mapped texture (mipmaps come from the
## project-wide texture importer default in project.godot), moderate normal strength, roughness floor.
static func surface(kind: String, tint: Color = Color.WHITE, tile: float = 4.0, rough_mul: float = 1.0) -> StandardMaterial3D:
	if tile <= 0.0:
		tile = tile_of(kind, 2.0)
	var key := "%s|%s|%s|%s" % [kind, tint.to_html(), tile, rough_mul]
	if _cache.has(key):
		return _cache[key]
	var m := StandardMaterial3D.new()
	var base := "res://textures/surfaces/%s_" % kind
	if ResourceLoader.exists(base + "albedo.png"):
		m.albedo_texture = load(base + "albedo.png")
		m.normal_enabled = true
		m.normal_texture = load(base + "normal.png")
		m.normal_scale = 0.7
		var orm: Texture2D = load(base + "orm.png")
		m.ao_enabled = true
		m.ao_texture = orm
		m.ao_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
		m.ao_light_affect = 0.6
		m.roughness_texture = orm
		m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
		m.metallic_texture = orm
		m.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
		m.metallic = 1.0
		m.roughness = rough_mul
	m.albedo_color = tint
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_triplanar_sharpness = 4.0
	m.uv1_scale = Vector3.ONE / tile
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_cache[key] = m
	return m

static func glass(tint: Color = Color(0.7, 0.85, 1.0, 0.12)) -> StandardMaterial3D:
	var key := "glass|" + tint.to_html()
	if _cache.has(key):
		return _cache[key]
	var m := StandardMaterial3D.new()
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = tint
	m.roughness = 0.03
	m.metallic = 0.0
	m.specular_mode = BaseMaterial3D.SPECULAR_SCHLICK_GGX
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	_cache[key] = m
	return m

static func emissive(col: Color, energy: float = 2.0) -> StandardMaterial3D:
	var key := "em|%s|%s" % [col.to_html(), energy]
	if _cache.has(key):
		return _cache[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = col * 0.2
	m.emission_enabled = true
	m.emission = col
	m.emission_energy_multiplier = energy
	_cache[key] = m
	return m

static func forcefield() -> ShaderMaterial:
	if _cache.has("ff"):
		return _cache["ff"]
	var sh := Shader.new()
	sh.code = """
shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never;
uniform vec3 tint : source_color = vec3(0.2, 0.6, 1.0);
void fragment() {
	float t = TIME * 0.6;
	float bands = 0.5 + 0.5 * sin(UV.y * 60.0 + t * 4.0);
	float grid = step(0.94, fract(UV.x * 40.0)) + step(0.94, fract(UV.y * 24.0));
	float edge = pow(1.0 - abs(UV.y - 0.5) * 2.0, 0.3);
	ALBEDO = tint * (0.08 + 0.12 * bands + 0.25 * grid) * (0.6 + 0.4 * edge);
}
"""
	var m := ShaderMaterial.new()
	m.shader = sh
	_cache["ff"] = m
	return m
