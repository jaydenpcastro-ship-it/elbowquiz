"""Elbow Muscle Review: Blender renders of the RIGHT arm from the Z-Anatomy atlas (CC BY-SA 4.0).
One muscle per picture is orange; the other arm muscles are see-through so deep muscles stay visible.
usage: blender -b Startup.blend --python eq_shots.py -- [preview] [shot ...]   -> out/<shot>.png
Coordinates: metres, +Z up, front of body = -Y, right arm at -X."""
import bpy, sys, os, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eq_lib as L

ARGS = L.args()
PREVIEW = "preview" in ARGS
WANT = [a for a in ARGS if a != "preview"]

FING = ["first", "second", "third", "fourth", "fifth"]
CARP = ["Scaphoid bone", "Lunate bone", "Triquetrum bone", "Pisiform bone", "Trapezium bone", "Trapezoid bone", "Capitate bone", "Hamate bone"]
META = [f"{n} metacarpal bone" for n in ("First", "Second", "Third", "Fourth", "Fifth")]
PH = [f"{p} phalanx of {f} finger of hand" for f in FING for p in ("Proximal", "Middle", "Distal") if not (f == "first" and p == "Middle")]
BONES = [n + ".r" for n in ["Humerus", "Radius", "Ulna", "Scapula", "Clavicle"] + CARP + META + PH]
M_ = {
    "biceps": ["Long head of biceps brachii.r", "Short head of biceps brachii.r"],
    "brachialis": ["Brachialis muscle.r"],
    "br": ["Brachioradialis muscle.r"],
    "triceps_long": ["Long head of triceps brachii.r"],
    "triceps": ["Long head of triceps brachii.r", "Lateral head of triceps brachii.r", "Medial head of triceps brachii.r"],
    "anconeus": ["Anconeus muscle.r"],
    "pt": ["Superficial head of pronator teres.r", "Deep head of pronator teres.r"],
    "pq": ["Pronator quadratus.r"],
    "supinator": ["Supinator.r"],
}
FOREARM = ["Flexor carpi radialis.r", "Humeral head of flexor carpi ulnaris.r", "Ulnar head of flexor carpi ulnaris.r", "Palmaris longus muscle.r",
           "Extensor carpi radialis longus.r", "Extensor carpi radialis brevis.r", "Humeral head of extensor carpi ulnaris.r",
           "Ulnar head of extensor carpi ulnaris.r", "Humero-ulnar head of flexor digitorum superficialis.r", "Radial head of flexor digitorum superficialis.r",
           "Flexor digitorum profundus.r", "Flexor pollicis longus.r", "Extensor digitorum.r", "Extensor indicis.r", "Extensor digiti minimi.r",
           "Extensor pollicis longus.r", "Extensor pollicis brevis.r", "Abductor pollicis longus.r", "Coracobrachialis muscle.r"]
ARM_MUS = sorted({n for v in M_.values() for n in v}) + FOREARM
KEEP = set(BONES + ARM_MUS)

def prune():
    keep = set()
    for n in KEEP:
        ob = bpy.data.objects.get(n)
        while ob is not None:
            keep.add(ob.name); ob = ob.parent
    bpy.data.batch_remove([o for o in bpy.data.objects if o.name not in keep])
prune()
for lst in (BONES, ARM_MUS):
    for n in [n for n in lst if n not in bpy.data.objects]:
        print("MISSING", n); lst.remove(n)

L.prepare(w=1600, h=1200, samples=16 if PREVIEW else 96, bg="161B2B")
SC = bpy.context.scene
SC.render.image_settings.compression = 15
SC.render.use_persistent_data = True
if PREVIEW:
    SC.render.resolution_percentage = 50

def objs(names):
    return [bpy.data.objects[n] for n in names if n in bpy.data.objects]
def pts(names):
    return np.vstack([L.wverts(o) for o in objs(names)])
def M(h, **kw):
    return L.mat(h, h, **kw)

H = L.wverts(L.O("Humerus.r")); SHO = H[H[:, 2] > H[:, 2].max() - 0.03].mean(0); ELB = H[H[:, 2] < H[:, 2].min() + 0.03].mean(0)
R = L.wverts(L.O("Radius.r")); WR = R[R[:, 2] < R[:, 2].min() + 0.02].mean(0)
AX = WR - SHO; AX /= np.linalg.norm(AX)

def cam(view):
    v = np.array(view, float); v /= np.linalg.norm(v)
    a = AX - v * AX.dot(v); a /= np.linalg.norm(a)
    L.camera(tuple(v), tuple(np.cross(-v, a)))   # screen-right = toward the hand

ANT, POST = (0, 1, 0), (0, -1, 0)
def antlat(deg):  # anterior view rotated toward the lateral side (-X) by deg
    r = math.radians(deg); return (math.sin(r), math.cos(r), 0)
def postlat(deg):
    r = math.radians(deg); return (math.sin(r), -math.cos(r), 0)

def seg(t0, t1, r=0.06):
    """frame points: the arm axis from fraction t0 to t1 (0 = shoulder, 1 = wrist), padded sideways by r"""
    L_ = np.linalg.norm(WR - SHO)
    P = []
    for t in np.linspace(t0, t1, 12):
        c = SHO + (WR - SHO) * t
        for d in ((r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0)):
            P.append(c + np.array(d))
    return np.array(P)

def shot(name, key, view, t0, t1, r=0.06, hidden=()):
    L.hide_all()
    L.show(objs(BONES), M("EDE5D2", rough=0.55))
    ctx = [n for n in ARM_MUS if n not in M_[key] and n not in hidden]
    L.show(objs(ctx), M("C98F86", alpha=0.22, rough=0.6))
    L.show(objs(M_[key]), M("F28C28", rough=0.45, emit=0.08))
    cam(view)
    c = L.fit(seg(t0, t1, r), margin=0.02)
    L.lights(c, view, up=(0, 0, 1), dist=0.7, scale=1.0)
    L.render(name)

SHOTS = {
    "brachialis": lambda: shot("brachialis", "brachialis", antlat(20), 0.15, 0.72, hidden=()),
    "biceps": lambda: shot("biceps", "biceps", ANT, -0.02, 0.68),
    "br": lambda: shot("br", "br", antlat(45), 0.3, 1.0),
    "anconeus": lambda: shot("anconeus", "anconeus", postlat(25), 0.38, 0.72, r=0.05),
    "pq": lambda: shot("pq", "pq", ANT, 0.45, 1.02),
    "supinator": lambda: shot("supinator", "supinator", antlat(80), 0.4, 0.75, r=0.05, hidden=("Brachioradialis muscle.r", "Extensor carpi radialis longus.r", "Extensor carpi radialis brevis.r", "Extensor digitorum.r")),
    "pt": lambda: shot("pt", "pt", ANT, 0.35, 0.95),
    "triceps_long": lambda: shot("triceps_long", "triceps_long", POST, -0.05, 0.62),
}
for s in (WANT or list(SHOTS)):
    SHOTS[s]()
print("ALL DONE")
