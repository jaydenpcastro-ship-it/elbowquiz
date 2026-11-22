"""Render helpers for the Todd passive-anatomy elbow renders (run inside Blender 5.2 on Z-Anatomy Startup.blend). Copied from illness_study/blender/nts_lib.py.

Never saves the .blend: every script works on a scratch session.
Coordinates in Startup.blend: metres, +Z up, front of the body faces -Y, the body's LEFT is +X.
"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ZA = r"C:\Users\Jayden\Desktop\Z-anatomy\Z-Anatomy"
sys.path.insert(0, ZA)
sys.path.insert(0, os.path.join(ZA, "tools"))
from zclassify import is_geometry  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
SC = bpy.context.scene

# ------------------------------------------------------------------ colours (sRGB hex -> linear)
def lin(h):
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)

PAL = {
    "bone": "E9E0CB", "bone_dim": "D9D2C3", "cut": "E7B9A6",
    "ilium": "6FA8E8", "ischium": "62C08C", "pubis": "F29B5A", "sacrum": "F0C24E", "coccyx": "B48CD9",
    "hyaline": "5DB4EA", "fibro": "E9A23B", "disc": "EFE9DD", "nucleus": "4F8FE0",
    "lig": "2FB3A0", "nerve": "F3D24E", "fascia": "8A6FD1", "muscle": "C8574D", "muscle_dim": "D9A49E",
    "hl": "F2542D", "teal": "1F8FA3", "navy": "0B2239",
}

def O(name):
    return bpy.data.objects[name]

_mats = {}
def mat(name, hexcol, rough=0.5, emit=0.0, alpha=1.0, coat=0.0, sss=0.0, metal=0.0):
    key = (name, hexcol, rough, emit, alpha, coat, sss)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new("LSP_" + name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexcol)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit > 0:
        b.inputs["Emission Color"].default_value = lin(hexcol)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if coat > 0:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.15
    if sss > 0:
        b.inputs["Subsurface Weight"].default_value = sss
        b.inputs["Subsurface Radius"].default_value = (0.003, 0.0015, 0.001)
    m.diffuse_color = lin(hexcol)
    _mats[key] = m
    return m

def assign(ob, m):
    """Give the object one material at OBJECT level (mirrored objects may share mesh data)."""
    if not ob.material_slots:
        ob.data.materials.append(m)
    for s in ob.material_slots:
        s.link = 'OBJECT'
        s.material = m

def mask_mat(name, cols, attr="part", emit=0.0, rough=0.5):
    """Material that picks a colour per vertex from integer attribute `attr` (0..len(cols)-1), hard edges."""
    m = bpy.data.materials.new("LSP_" + name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = attr; a.attribute_type = 'GEOMETRY'
    prev = None
    for i, c in enumerate(cols):
        if i == 0:
            rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = lin(c); prev = rgb.outputs[0]
            continue
        cmp_ = nt.nodes.new("ShaderNodeMath"); cmp_.operation = 'GREATER_THAN'; cmp_.inputs[1].default_value = i - 0.5
        nt.links.new(a.outputs["Fac"], cmp_.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
        nt.links.new(cmp_.outputs[0], mix.inputs["Factor"])
        nt.links.new(prev, mix.inputs[6])
        mix.inputs[7].default_value = lin(c)
        prev = mix.outputs[2]
    nt.links.new(prev, b.inputs["Base Color"])
    if emit:
        nt.links.new(prev, b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    return m

def onehot_mat(name, cols, attrs, rough=0.55):
    """Colour = the attribute with the largest value (crisp, smooth boundaries between any two parts)."""
    m = bpy.data.materials.new("LSP_" + name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    att = []
    for a_ in attrs:
        n = nt.nodes.new("ShaderNodeAttribute"); n.attribute_name = a_; n.attribute_type = 'GEOMETRY'; att.append(n.outputs["Fac"])
    rgb0 = nt.nodes.new("ShaderNodeRGB"); rgb0.outputs[0].default_value = lin(cols[0])
    col, best = rgb0.outputs[0], att[0]
    for i in range(1, len(cols)):
        gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN'
        nt.links.new(att[i], gt.inputs[0]); nt.links.new(best, gt.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
        nt.links.new(gt.outputs[0], mix.inputs["Factor"]); nt.links.new(col, mix.inputs[6]); mix.inputs[7].default_value = lin(cols[i])
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = 'MAXIMUM'
        nt.links.new(att[i], mx.inputs[0]); nt.links.new(best, mx.inputs[1])
        col, best = mix.outputs[2], mx.outputs[0]
    nt.links.new(col, b.inputs["Base Color"])
    return m

def hl_mat(name, base, hl, attr="hl", emit=0.0, rough=0.5, hl_rough=None):
    """Base colour, switching to `hl` where point attribute `attr` > 0.5 (crisp edge)."""
    m = bpy.data.materials.new("LSP_" + name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = attr; a.attribute_type = 'GEOMETRY'
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.47; mr.inputs["From Max"].default_value = 0.53
    nt.links.new(a.outputs["Fac"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = lin(base); mix.inputs[7].default_value = lin(hl)
    nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    if hl_rough is not None:
        rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough; rr.inputs["To Max"].default_value = hl_rough
        nt.links.new(mr.outputs["Result"], rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    if emit:
        b.inputs["Emission Color"].default_value = lin(hl)
        em = nt.nodes.new("ShaderNodeMath"); em.operation = 'MULTIPLY'; em.inputs[1].default_value = emit
        nt.links.new(mr.outputs["Result"], em.inputs[0]); nt.links.new(em.outputs[0], b.inputs["Emission Strength"])
    return m

def subdivided(ob, cuts=1):
    """Give `ob` its own copy of its mesh, subdivided without smoothing (finer masks, same shape)."""
    import bmesh
    if ob.get("lsp_sub", 0) >= cuts:
        return ob
    ob["lsp_sub"] = cuts
    me = ob.data.copy()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bm.to_mesh(me); bm.free()
    ob.data = me
    return ob

def cutter_box(name, lo, hi, m=None):
    """Hidden box used as a boolean cutter; its material colours the cut faces (material_mode TRANSFER)."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); SC.collection.objects.link(ob)
    lo, hi = Vector(lo), Vector(hi)
    ob.location = (lo + hi) / 2
    ob.scale = hi - lo
    if m is not None:
        me.materials.append(m)
    ob.hide_render = True
    ob.display_type = 'WIRE'
    return ob

def boolean(ob, cutter, op='DIFFERENCE'):
    mod = ob.modifiers.new("LSPcut", 'BOOLEAN')
    mod.operation = op
    mod.object = cutter
    mod.solver = 'EXACT'
    mod.material_mode = 'TRANSFER'
    try:
        mod.use_hole_tolerant = True
    except Exception:
        pass
    return mod

def clear_cuts(ob):
    for m in [m for m in ob.modifiers if m.name.startswith("LSP")]:
        ob.modifiers.remove(m)

def tube(name, pts, radius, m, closed=False, smooth=True):
    """Bevelled curve through world points (NURBS-like smooth if smooth)."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER' if smooth else 'POLY')
    if smooth:
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = Vector(p); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    else:
        sp.points.add(len(pts) - 1)
        for q, p in zip(sp.points, pts):
            q.co = (*p, 1)
    sp.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, cu); SC.collection.objects.link(ob)
    cu.materials.append(m)
    ob.hide_render = False
    return ob

_marks = []
def markers(points, r=0.0015, col="FF0033"):
    """Small emissive spheres at world points (preview only)."""
    import bmesh
    m = mat("marker", col, emit=4.0)
    for p in points:
        me = bpy.data.meshes.new("mk"); bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=r)
        bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new("mk", me); SC.collection.objects.link(ob)
        ob.location = Vector(p); assign(ob, m); ob.hide_render = False
        _marks.append(ob)

def clear_markers():
    for ob in _marks:
        bpy.data.objects.remove(ob, do_unlink=True)
    _marks.clear()

def set_attr(ob, values, attr="part", copy=True):
    """Per-vertex float attribute. copy=False writes into shared mesh data (all users get it)."""
    if copy and ob.data.users > 1:
        ob.data = ob.data.copy()
    me = ob.data
    if attr in me.attributes:
        me.attributes.remove(me.attributes[attr])
    at = me.attributes.new(attr, 'FLOAT', 'POINT')
    at.data.foreach_set("value", np.asarray(values, dtype=np.float32))

# ------------------------------------------------------------------ geometry
def wverts(ob):
    """World-space vertex positions (N x 3) of a mesh object."""
    me = ob.data
    a = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", a)
    a = a.reshape(-1, 3)
    M = np.array(ob.matrix_world)
    return a @ M[:3, :3].T + M[:3, 3]

def eval_points(ob):
    """World-space points of any geometry object (curves are evaluated to their bevelled mesh)."""
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    me = e.to_mesh()
    a = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", a)
    a = a.reshape(-1, 3)
    M = np.array(e.matrix_world)
    e.to_mesh_clear()
    return a @ M[:3, :3].T + M[:3, 3]

_bvh_cache = {}
def bvh(obs):
    """World-space BVH of one or more objects (evaluated, so modifiers count). Cached by name."""
    if not isinstance(obs, (list, tuple)):
        obs = [obs]
    key = tuple(o.name for o in obs)
    if key in _bvh_cache:
        return _bvh_cache[key]
    dg = bpy.context.evaluated_depsgraph_get()
    V, F = [], []
    for ob in obs:
        e = ob.evaluated_get(dg)
        me = e.to_mesh()
        M = e.matrix_world
        base = len(V)
        V.extend([M @ v.co for v in me.vertices])
        F.extend([[base + i for i in p.vertices] for p in me.polygons])
        e.to_mesh_clear()
    t = BVHTree.FromPolygons(V, F)
    _bvh_cache[key] = t
    return t

def bvh_reset():
    _bvh_cache.clear()

def dist_to_obj(points, ob):
    """Distance from world points to the surface of `ob` (or a list of objects)."""
    t = bvh(ob)
    out = np.empty(len(points))
    for i, p in enumerate(points):
        r = t.find_nearest(Vector(p))
        out[i] = r[3] if r[0] is not None else 1e9
    return out

def ray(origin, direction, ob, dist=10.0):
    """First hit of a world-space ray on `ob` (or list): (location, normal, distance) or None."""
    r = bvh(ob).ray_cast(Vector(origin), Vector(direction).normalized(), dist)
    return None if r[0] is None else (np.array(r[0]), np.array(r[1]), r[3])

def smooth(ob, m, iters=2):
    me = ob.data
    e = np.empty(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get("vertices", e)
    e = e.reshape(-1, 2)
    m = np.asarray(m, dtype=np.float64)
    deg = np.bincount(e.ravel(), minlength=len(m)).astype(np.float64) + 1
    for _ in range(iters):
        s = m.copy()
        np.add.at(s, e[:, 0], m[e[:, 1]]); np.add.at(s, e[:, 1], m[e[:, 0]])
        m = s / deg
    return m

def pin(name):
    """Z-Anatomy landmark pin '<name>.j': returns its 2 world vertices."""
    ob = bpy.data.objects.get(name + ".j")
    if ob is None or ob.type != 'MESH' or len(ob.data.vertices) == 0:
        return None
    return wverts(ob)

# ------------------------------------------------------------------ scene / render
def prepare(w=1600, h=1200, samples=96, bg="FFFFFF"):
    sc = SC
    sc.render.engine = 'CYCLES'
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'OPTIX'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == 'OPTIX'
        sc.cycles.device = 'GPU'
    except Exception as ex:
        print("GPU setup failed:", ex)
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 16
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.use_freestyle = False
    sc.render.use_compositing = False
    sc.render.use_sequencer = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = 0
    sc.view_settings.gamma = 1
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    # world: the camera sees a flat card colour; lighting sees a soft grey environment
    wd = bpy.data.worlds.new("LSPWorld"); sc.world = wd; wd.use_nodes = True
    nt = wd.node_tree; nt.nodes.clear()
    outn = nt.nodes.new("ShaderNodeOutputWorld")
    lp = nt.nodes.new("ShaderNodeLightPath")
    env = nt.nodes.new("ShaderNodeBackground"); env.inputs[0].default_value = (0.8, 0.82, 0.85, 1); env.inputs[1].default_value = 0.16
    card = nt.nodes.new("ShaderNodeBackground"); card.inputs[0].default_value = lin(bg); card.inputs[1].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(env.outputs[0], mix.inputs[1])
    nt.links.new(card.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], outn.inputs[0])
    # every collection renderable, every object hidden until shown
    vl = sc.view_layers[0]
    def walk(lc):
        lc.exclude = False
        lc.collection.hide_render = False
        for ch in lc.children:
            walk(ch)
    for lc in vl.layer_collection.children:
        walk(lc)
    for o in bpy.data.objects:
        o.hide_render = True

_shown = []
def show(obs, m=None):
    for ob in obs:
        if isinstance(ob, str):
            ob = O(ob)
        ob.hide_render = False
        if m is not None:
            assign(ob, m)
        _shown.append(ob)
    return obs

def hide_all():
    for o in bpy.data.objects:
        o.hide_render = True
    _shown.clear()

_lights = []
def area_light(name, loc, target, power, size):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.size = size
    ob = bpy.data.objects.new(name, ld); SC.collection.objects.link(ob)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    ob.hide_render = False
    _lights.append(ob)
    return ob

def lights(center, view_dir, up=(0, 0, 1), dist=1.0, scale=1.0):
    """Key / fill / rim around the camera direction; power scales with dist^2 (constant exposure)."""
    for l in _lights:
        bpy.data.objects.remove(l, do_unlink=True)
    _lights.clear()
    c = Vector(center); v = Vector(view_dir).normalized(); u = Vector(up).normalized()
    r = v.cross(u).normalized()
    key = c + (-v * 0.8 - r * 0.7 + u * 0.8).normalized() * dist
    fill = c + (-v * 0.9 + r * 0.9 + u * 0.1).normalized() * dist
    rim = c + (v * 0.9 + u * 0.6 + r * 0.3).normalized() * dist
    k = dist * dist * scale
    area_light("Key", key, c, 9 * k, dist * 0.6)
    area_light("Fill", fill, c, 2.5 * k, dist * 0.9)
    area_light("Rim", rim, c, 7 * k, dist * 0.5)

_cam = None
def look_matrix(view_dir, up, loc):
    z = -Vector(view_dir).normalized()
    y = Vector(up) - z * Vector(up).dot(z); y.normalize()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4(); m.translation = Vector(loc)
    return m

def camera(view_dir, up=(0, 0, 1)):
    global _cam
    if _cam is None:
        cd = bpy.data.cameras.new("LSPCam"); cd.type = 'ORTHO'; cd.clip_start = 0.001; cd.clip_end = 20
        _cam = bpy.data.objects.new("LSPCam", cd); SC.collection.objects.link(_cam)
    _cam.hide_render = False
    _cam.matrix_world = look_matrix(view_dir, up, Vector((0, 0, 0)))
    SC.camera = _cam
    return _cam

def fit(points, margin=0.06, shift=(0, 0)):
    """Centre the ortho camera on world points and size it to fit (shift in fractions of the frame)."""
    cam = _cam
    bpy.context.view_layer.update()
    m = cam.matrix_world.to_3x3()
    right = np.array(m @ Vector((1, 0, 0))); up = np.array(m @ Vector((0, 1, 0))); fwd = np.array(m @ Vector((0, 0, -1)))
    P = np.asarray(points)
    xs, ys, zs = P @ right, P @ up, P @ fwd
    w, h = xs.max() - xs.min(), ys.max() - ys.min()
    aspect = SC.render.resolution_x / SC.render.resolution_y
    scale = max(w, h * aspect) * (1 + 2 * margin) if aspect >= 1 else max(h, w / aspect) * (1 + 2 * margin)
    cam.data.ortho_scale = scale
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    fw = scale if aspect >= 1 else scale * aspect
    fh = fw / aspect
    cx -= shift[0] * fw; cy -= shift[1] * fh
    centre = Vector(right * cx + up * cy + fwd * ((zs.min() + zs.max()) / 2))
    cam.location = centre - Vector(fwd) * 3.0
    bpy.context.view_layer.update()
    return centre

def px(p):
    co = world_to_camera_view(SC, _cam, Vector(p))
    return [round(co.x * SC.render.resolution_x, 1), round((1 - co.y) * SC.render.resolution_y, 1)]

def render(name, anchors=None, extra=None):
    path = os.path.join(OUT, name + ".png")
    SC.render.filepath = path
    bpy.ops.render.render(write_still=True)
    meta = {"file": name + ".png", "w": SC.render.resolution_x, "h": SC.render.resolution_y,
            "anchors": {k: px(v) for k, v in (anchors or {}).items()}}
    if extra:
        meta.update(extra)
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("RENDERED", path, flush=True)
    return meta

def args():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
