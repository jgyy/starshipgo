class_name TextureFix
extends RefCounted
## Gives every texture of the ship a mip chain, whatever state the project's import cache is in.
##
## Godot imports a PNG / JPG with mipmaps OFF unless the editor has seen it used in a 3D material ("detect 3D"), and a
## headless `godot --import` (CI, a fresh checkout, the integrator's regenerate step) never does.  A mip-less texture is
## point-sampled at full resolution at a distance: the floor plates, wall panels, perforated ceiling tiles and prop decals
## crawl and sparkle while the player walks.  project.godot now sets [importer_defaults] texture mipmaps/generate=true
## (new imports are right), but `.import` files that already exist keep their old settings, so this pass repairs the
## textures of the built ship at load time: it reads the texture's .import file and, only when it says mipmaps are off,
## swaps the texture for an ImageTexture with generated mipmaps (cached per file, so each image is converted once).

const SLOTS := ["albedo_texture", "normal_texture", "ao_texture", "roughness_texture", "metallic_texture", "emission_texture",
		"heightmap_texture", "detail_albedo", "detail_normal"]

static var _fixed: Dictionary = {}       # res:// path -> Texture2D (the original or its mipmapped copy)
static var converted := 0                # textures swapped in this process (for tests / logging)

## True when the texture's import settings leave it without mipmaps.
static func lacks_mipmaps(tex: Texture2D) -> bool:
	if tex == null:
		return false
	var p := tex.resource_path
	if not p.begins_with("res://") or tex is ImageTexture:
		return false
	var cfg := ConfigFile.new()
	if cfg.load(p + ".import") != OK:
		return false                          # exported game / no import file: the project defaults apply
	return not bool(cfg.get_value("params", "mipmaps/generate", true))

## `force` converts regardless of the .import file (tests simulate a stale import with it).
static func with_mipmaps(tex: Texture2D, is_normal: bool = false, force: bool = false) -> Texture2D:
	if tex == null or not (force or lacks_mipmaps(tex)):
		return tex
	var p := tex.resource_path
	if _fixed.has(p):
		return _fixed[p]
	var img := tex.get_image()
	if img == null or img.is_empty() or img.is_compressed():
		_fixed[p] = tex
		return tex
	img = img.duplicate()
	if img.generate_mipmaps(is_normal) != OK:
		_fixed[p] = tex
		return tex
	var out := ImageTexture.create_from_image(img)
	out.resource_path = ""
	_fixed[p] = out
	converted += 1
	return out

static func fix_material(m: Material, seen: Dictionary = {}) -> void:
	if not (m is BaseMaterial3D) or seen.has(m):
		return
	seen[m] = true
	var bm := m as BaseMaterial3D
	for slot in SLOTS:
		var t: Variant = bm.get(slot)
		if t is Texture2D and lacks_mipmaps(t):
			bm.set(slot, with_mipmaps(t, slot.contains("normal")))

## Repairs every material under `root`: node overrides, mesh surface materials, MultiMesh meshes.
static func fix_tree(root: Node) -> void:
	var stack: Array[Node] = [root]
	var meshes := {}
	var seen := {}
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		var mesh: Mesh = null
		if n is MeshInstance3D:
			mesh = (n as MeshInstance3D).mesh
			fix_material((n as MeshInstance3D).material_override, seen)
		elif n is MultiMeshInstance3D and (n as MultiMeshInstance3D).multimesh != null:
			mesh = (n as MultiMeshInstance3D).multimesh.mesh
		if mesh != null and not meshes.has(mesh):
			meshes[mesh] = true
			for si in mesh.get_surface_count():
				fix_material(mesh.surface_get_material(si), seen)
