"""Blender (bpy 5.2) helper library: scene setup, physical sky + sun, PBR materials, cameras, render settings.

Run inside the venv with bpy: /home/user/aihouse/.venv-render/bin/python -I script.py
Coordinates: Blender X = east (e), Y = north (n), Z = up — identical to the project's local grid (metres).
"""
from __future__ import annotations
import math
import bpy
from mathutils import Vector, Euler


# ----------------------------------------------------------------------------- scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    return sc


def render_settings(sc, w, h, samples=128, adaptive=0.015, denoise=True, exposure=0.0, look=None, threads=0,
                    max_bounces=8, clamp_indirect=6.0, transparent=False):
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cy.device = 'CPU'
    cy.samples = samples
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = adaptive
    cy.use_denoising = denoise
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
        cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    except Exception:
        pass
    cy.max_bounces = max_bounces
    cy.diffuse_bounces = 4
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 16
    cy.sample_clamp_indirect = clamp_indirect
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 0.5
    sc.render.resolution_x, sc.render.resolution_y = int(w), int(h)
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    if threads:
        sc.render.threads_mode = 'FIXED'; sc.render.threads = threads
    vs = sc.view_settings
    for vt in ('AgX', 'Filmic'):
        try:
            vs.view_transform = vt
            break
        except TypeError:
            continue
    if look:
        try:
            vs.look = look
        except TypeError:
            pass
    vs.exposure = exposure
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '16'
    return sc


def sky_and_sun(sc, az_deg, el_deg, sun_strength=4.0, sky_strength=1.0, turbidity_air=1.0, dust=1.0, ozone=1.0,
                sun_angle_deg=0.53, sun_color=(1.0, 0.95, 0.88), use_sky_texture=True):
    """Physical sky (multiple scattering) as world + an explicit sun lamp matching its direction."""
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get('Background') or nt.nodes.new('ShaderNodeBackground')
    out = nt.nodes.get('World Output') or nt.nodes.new('ShaderNodeOutputWorld')
    if use_sky_texture:
        sky = nt.nodes.new('ShaderNodeTexSky')
        try:
            sky.sky_type = 'MULTIPLE_SCATTERING'
        except TypeError:
            sky.sky_type = 'NISHITA'
        sky.sun_disc = False
        sky.sun_elevation = math.radians(max(el_deg, 0.5))
        sky.sun_rotation = math.radians((90 - az_deg))  # Blender: rotation from +X toward +Y
        for attr, val in (('air_density', turbidity_air), ('dust_density', dust), ('ozone_density', ozone)):
            if hasattr(sky, attr):
                setattr(sky, attr, val)
        nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = sky_strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    # sun lamp
    ld = bpy.data.lights.new("Sun", 'SUN')
    ld.energy = sun_strength
    ld.angle = math.radians(sun_angle_deg)
    ld.color = sun_color
    so = bpy.data.objects.new("Sun", ld)
    sc.collection.objects.link(so)
    a, e = math.radians(az_deg), math.radians(el_deg)
    to_sun = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
    so.rotation_euler = to_sun.to_track_quat('Z', 'Y').to_euler()
    return so


# ----------------------------------------------------------------------------- cameras
def camera(sc, loc, target, lens_mm=28.0, sensor_mm=36.0, shift_x=0.0, shift_y=0.0, level=True, name="Cam", clip_end=5000):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens_mm
    cd.sensor_width = sensor_mm
    cd.sensor_fit = 'HORIZONTAL'
    cd.shift_x, cd.shift_y = shift_x, shift_y
    cd.clip_start, cd.clip_end = 0.1, clip_end
    co = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(co)
    co.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    if level:
        # two-point perspective: keep verticals vertical (pitch 0), frame via shift_y
        yaw = math.atan2(d.y, d.x) - math.pi / 2
        co.rotation_euler = Euler((math.pi / 2, 0, yaw))
    else:
        co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    return co


def auto_shift_for_target(cam_loc, target, lens_mm, sensor_mm, aspect_hw):
    """shift_y that places the target point vertically centred for a level camera."""
    d = Vector(target) - Vector(cam_loc)
    horiz = math.hypot(d.x, d.y)
    if horiz < 1e-6:
        return 0.0
    tan_v = d.z / horiz
    # image plane half-width in sensor units = sensor/2; shift is in units of the larger sensor dimension
    return tan_v * lens_mm / sensor_mm


# ----------------------------------------------------------------------------- materials
def _bsdf(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    p = nt.nodes.get('Principled BSDF')
    return nt, p


def mat_basic(name, color, rough=0.5, metal=0.0, spec=0.5, coat=0.0, emission=None, emission_strength=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, p = _bsdf(m)
    p.inputs['Base Color'].default_value = (*color, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in p.inputs:
        p.inputs['Specular IOR Level'].default_value = spec
    if coat and 'Coat Weight' in p.inputs:
        p.inputs['Coat Weight'].default_value = coat
    if emission is not None:
        p.inputs['Emission Color'].default_value = (*emission, 1.0)
        p.inputs['Emission Strength'].default_value = emission_strength
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
    return m


def mat_glass(name="Glass", tint=(0.86, 0.90, 0.90), rough=0.02, ior=1.52, reflect_only=False):
    """Architectural double/triple glazing approximated as thin glass; reflect_only for façade glass seen from outside
    without modelled interiors (dark interior + strong reflections)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, p = _bsdf(m)
    p.inputs['Base Color'].default_value = (*tint, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['IOR'].default_value = ior
    if reflect_only:
        p.inputs['Base Color'].default_value = (0.02, 0.025, 0.03, 1.0)
        p.inputs['Metallic'].default_value = 0.0
        if 'Specular IOR Level' in p.inputs:
            p.inputs['Specular IOR Level'].default_value = 1.0
    else:
        p.inputs['Transmission Weight'].default_value = 1.0
    return m


def mat_brick(name="Brick", c1=(0.42, 0.20, 0.12), c2=(0.30, 0.14, 0.09), mortar=(0.62, 0.58, 0.52), scale=1.0,
              brick_w=0.25, brick_h=0.065, mortar_w=0.010, rough=0.85, bump=0.25):
    """Procedural brick bond on object/world coords: textured via box-projected Brick Texture (works on vertical faces)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, p = _bsdf(m)
    N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord')
    # map world XZ / YZ via geometry normal blend: use 'Object' coords and a box mapping through Separate/Combine
    sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    geo = N.new('ShaderNodeNewGeometry')
    nsep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], nsep.inputs[0])
    absx = N.new('ShaderNodeMath'); absx.operation = 'ABSOLUTE'; L.new(nsep.outputs['X'], absx.inputs[0])
    absy = N.new('ShaderNodeMath'); absy.operation = 'ABSOLUTE'; L.new(nsep.outputs['Y'], absy.inputs[0])
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; L.new(absx.outputs[0], gt.inputs[0]); L.new(absy.outputs[0], gt.inputs[1])
    mix_u = N.new('ShaderNodeMix'); mix_u.data_type = 'FLOAT'
    L.new(gt.outputs[0], mix_u.inputs['Factor']); L.new(sep.outputs['X'], mix_u.inputs['A']); L.new(sep.outputs['Y'], mix_u.inputs['B'])
    comb = N.new('ShaderNodeCombineXYZ'); L.new(mix_u.outputs['Result'], comb.inputs['X']); L.new(sep.outputs['Z'], comb.inputs['Y'])
    br = N.new('ShaderNodeTexBrick')
    br.offset = 0.5; br.squash = 1.0
    br.inputs['Scale'].default_value = 1.0 * scale
    br.inputs['Brick Width'].default_value = brick_w
    br.inputs['Row Height'].default_value = brick_h
    br.inputs['Mortar Size'].default_value = mortar_w
    br.inputs['Mortar Smooth'].default_value = 0.1
    br.inputs['Bias'].default_value = 0.0
    br.inputs['Color1'].default_value = (*c1, 1)
    br.inputs['Color2'].default_value = (*c2, 1)
    br.inputs['Mortar'].default_value = (*mortar, 1)
    L.new(comb.outputs[0], br.inputs['Vector'])
    noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 3.0; noise.inputs['Detail'].default_value = 6
    L.new(comb.outputs[0], noise.inputs['Vector'])
    mixc = N.new('ShaderNodeMix'); mixc.data_type = 'RGBA'; mixc.blend_type = 'MULTIPLY'
    mixc.inputs['Factor'].default_value = 0.25
    L.new(br.outputs['Color'], mixc.inputs['A']); L.new(noise.outputs['Color'], mixc.inputs['B'])
    L.new(mixc.outputs['Result'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    bmp = N.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump; bmp.invert = True
    L.new(br.outputs['Fac'], bmp.inputs['Height']); L.new(bmp.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_noise_color(name, base, var=0.08, scale=6.0, rough=0.6, metal=0.0, bump=0.05):
    """Solid material with subtle large-scale colour/roughness variation (concrete, stone, render, anodised metal)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    nt, p = _bsdf(m)
    N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 8
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*[max(0, c * (1 - var)) for c in base], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + var)) for c in base], 1)
    L.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if bump:
        bmp = N.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump
        L.new(nz.outputs['Fac'], bmp.inputs['Height']); L.new(bmp.outputs['Normal'], p.inputs['Normal'])
    return m


def mat_shadow_catcher(obj):
    obj.is_shadow_catcher = True
    return obj


# ----------------------------------------------------------------------------- mesh helpers
def mesh_from_pydata(name, verts, faces, mat=None, coll=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate(); me.update()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    return ob


def extrude_polygon(name, ring, z0, z1, mat=None, coll=None, cap_top=True, cap_bottom=True):
    """Vertical prism from a CCW ring [(e,n),...] between z0 and z1. Uses bmesh for robust n-gon caps."""
    import bmesh
    bm = bmesh.new()
    n = len(ring)
    vb = [bm.verts.new((x, y, z0)) for x, y in ring]
    vt = [bm.verts.new((x, y, z1)) for x, y in ring]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    if cap_top:
        bm.faces.new(vt)
    if cap_bottom:
        bm.faces.new(list(reversed(vb)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def box(name, center, size, mat=None, coll=None, rot_z=0.0):
    cx, cy, cz = center; sx, sy, sz = size
    hx, hy = sx / 2, sy / 2
    c, s = math.cos(rot_z), math.sin(rot_z)
    ring = [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]
    return extrude_polygon(name, ring, cz - sz / 2, cz + sz / 2, mat, coll)


def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


# ----------------------------------------------------------------------------- dodatki (kontekst 3D, 2026-11)
def mesh_from_arrays(name, verts, faces, mat_index=None, mats=None, coll=None, smooth=False, face_attrs=None,
                     point_attrs=None, validate=False):
    """Szybkie tworzenie siatki (foreach_set) z tablic.

    verts: (n,3) float; faces: lista list indeksów (dowolna liczba wierzchołków) albo tablica (m,k);
    mat_index: (m,) int – indeks slotu materiału; mats: lista materiałów (sloty);
    face_attrs / point_attrs: {nazwa: (m,) float} – atrybuty FLOAT na ścianach / wierzchołkach (do shaderów).
    Obiekt dostaje transformację jednostkową (współrzędne obiektu = świata).
    """
    import numpy as np
    V = np.asarray(verts, dtype=np.float32).reshape(-1, 3)
    if isinstance(faces, np.ndarray) and faces.ndim == 2:
        tot = np.full(len(faces), faces.shape[1], np.int32)
        flat = faces.astype(np.int32).ravel()
    else:
        tot = np.fromiter((len(f) for f in faces), np.int32, len(faces))
        flat = np.fromiter((i for f in faces for i in f), np.int32, int(tot.sum()))
    start = np.zeros(len(tot), np.int32)
    if len(tot) > 1:
        start[1:] = np.cumsum(tot)[:-1]
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V))
    me.vertices.foreach_set('co', V.ravel())
    me.loops.add(len(flat))
    me.loops.foreach_set('vertex_index', flat)
    me.polygons.add(len(tot))
    me.polygons.foreach_set('loop_start', start)
    if mat_index is not None and len(tot):
        me.polygons.foreach_set('material_index', np.asarray(mat_index, np.int32))
    if smooth:
        me.polygons.foreach_set('use_smooth', np.ones(len(tot), bool))
    for nm, arr in (face_attrs or {}).items():
        a = me.attributes.new(nm, 'FLOAT', 'FACE')
        a.data.foreach_set('value', np.asarray(arr, np.float32))
    for nm, arr in (point_attrs or {}).items():
        a = me.attributes.new(nm, 'FLOAT', 'POINT')
        a.data.foreach_set('value', np.asarray(arr, np.float32))
    me.update(calc_edges=True)
    if validate:
        me.validate()
    ob = bpy.data.objects.new(name, me)
    if coll is not None:
        coll.objects.link(ob)
    for m in (mats or []):
        me.materials.append(m)
    return ob


class NodeBuilder:
    """Zwięzłe budowanie drzew węzłów materiału: nb = NodeBuilder(mat); n = nb.n('ShaderNodeTexNoise', Scale=4)."""

    def __init__(self, mat, clear=True):
        mat.use_nodes = True
        self.nt = mat.node_tree
        if clear:
            self.nt.nodes.clear()
        self.out = self.nt.nodes.new('ShaderNodeOutputMaterial')

    def n(self, typ, props=None, **inputs):
        node = self.nt.nodes.new(typ)
        for k, v in (props or {}).items():
            setattr(node, k, v)
        for k, v in inputs.items():
            self.set(node, k, v)
        return node

    def set(self, node, key, val):
        sock = node.inputs[key] if not isinstance(key, int) else node.inputs[key]
        if hasattr(val, 'bl_idname') or hasattr(val, 'links'):  # socket lub węzeł
            src = val if hasattr(val, 'links') else val.outputs[0]
            self.nt.links.new(src, sock)
        else:
            if isinstance(val, (tuple, list)) and len(val) == 3 and getattr(sock, 'type', '') == 'RGBA':
                val = (*val, 1.0)
            sock.default_value = val

    def l(self, a, b):
        a = a if hasattr(a, 'links') else a.outputs[0]
        self.nt.links.new(a, b)

    def math(self, op, a, b=None, clamp=False):
        m = self.n('ShaderNodeMath', {'operation': op, 'use_clamp': clamp})
        self.set(m, 0, a)
        if b is not None:
            self.set(m, 1, b)
        return m

    def mix(self, fac, a, b, blend='MIX', dtype='RGBA'):
        """Węzeł Mix; zwraca GNIAZDO wyniku odpowiedniego typu (Result kolor/float/wektor)."""
        m = self.n('ShaderNodeMix', {'data_type': dtype, 'blend_type': blend} if dtype == 'RGBA' else {'data_type': dtype})
        self.set(m, 0, fac)
        ia, ib, io = (6, 7, 2) if dtype == 'RGBA' else ((2, 3, 0) if dtype == 'FLOAT' else (4, 5, 1))
        self.set(m, ia, a)
        self.set(m, ib, b)
        return m.outputs[io]

    def output(self, shader, displacement=None):
        self.l(shader, self.out.inputs['Surface'])
        if displacement is not None:
            self.l(displacement, self.out.inputs['Displacement'])
