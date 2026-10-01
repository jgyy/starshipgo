"""Medical components: beds, scanners, cabinets, tools, surgical gear, cryo pods, supplies."""
import math

from ..kit import family, register_material
from .lifesupport import (bolts, cabinet, door, gauge, hazard, label_plate, lean, led)

register_material("md_teal", "#2aa6a0", 0.1, 0.5)
register_material("md_sheet", "#c8dde6", 0.0, 0.9)
register_material("md_bag", "#3a5a48", 0.0, 0.85)
register_material("md_frost", "#b8d8e8", 0.1, 0.5)
register_material("md_biohaz", "#d8341c", 0.2, 0.5)
register_material("md_blood", "#8a1420", 0.0, 0.3)
register_material("md_curtain", "#a8d8d0", 0.0, 0.6, alpha=0.4)


def wheels(m, xs, zs, r=0.07, y=None):
    y = r if y is None else y
    for x in xs:
        for z in zs:
            m.cyl(r, 0.05, (x, y, z), "rubber", axis="x", seg=10)
            m.box((0.04, 0.08, 0.05), (x, y + r, z), "steel")


def rails(m, x, y, z0, z1, h=0.2):
    m.box((0.03, 0.03, z1 - z0), (x, y + h, (z0 + z1) / 2), "steel")
    for z in (z0, z1):
        m.box((0.03, h, 0.03), (x, y + h / 2, z), "steel")


def ivhook(m, x, y, z):
    m.cyl(0.015, 1.0, (x, y + 0.5, z), "steel", seg=6)
    m.link((x, y + 1.0, z), (x + 0.12, y + 1.05, z), 0.012, "steel", 5)
    m.link((x, y + 1.0, z), (x - 0.12, y + 1.05, z), 0.012, "steel", 5)


# ================================================================ MEDBEDS
BED = ["Diagnostic Biobed", "Exam Table", "Surgical Table", "Recovery Bed", "Field Stretcher", "Isolation Bed"]


@family("medbed", BED, mount="floor", tags=["medical", "bed"], solid=True)
def medbed(m, i, label, rng):
    lean(m)
    BEDS[i](m, rng)


def b_bio(m, rng):
    m.box((0.5, 0.4, 1.5), (0, 0.22, 0), "hull_light", 0.03)
    m.box((0.6, 0.06, 1.7), (0, 0.03, 0), "hull_dark", 0.01)
    m.box((0.9, 0.1, 2.0), (0, 0.5, 0), "hull_dark", 0.02)
    m.box((0.86, 0.12, 1.96), (0, 0.61, 0), "md_sheet", 0.04)
    m.box((0.6, 0.1, 0.35), (0, 0.72, -0.72), "plastic_white", 0.04)
    for s in (-1, 1):
        m.box((0.03, 0.03, 1.8), (s * 0.45, 0.71, 0.0), "md_teal")
        m.box((0.03, 0.06, 1.9), (s * 0.45, 0.56, 0.0), "em_cyan")
    # canopy arch
    for k in range(9):
        t = math.pi * k / 8
        m.box((0.1, 0.1, 0.1), (math.cos(t) * 0.6, 0.67 + math.sin(t) * 0.6, 0.2), "hull_light", 0.01, rot=(0, 0, t))
        if k < 8:
            t2 = t + math.pi / 16
            m.box((0.1, 0.1, 0.1), (math.cos(t2) * 0.6, 0.67 + math.sin(t2) * 0.6, 0.2), "hull_light", rot=(0, 0, t2))
    m.box((0.14, 0.14, 0.7), (0, 1.3, 0.2), "hull_light", 0.03)
    m.box((0.08, 0.02, 0.62), (0, 1.22, 0.2), "em_cyan")
    for z in (-0.02, 0.42):
        m.box((0.08, 0.06, 0.06), (-0.6, 0.67, z), "black_metal")
        m.box((0.08, 0.06, 0.06), (0.6, 0.67, z), "black_metal")
    # monitor arm
    m.box((0.1, 1.6, 0.1), (0.62, 0.8, -1.0), "hull_dark", 0.01)
    m.link((0.62, 1.55, -1.0), (0.3, 1.6, -0.8), 0.03, "steel", 6)
    m.screen((0.42, 0.28), (0.3, 1.55, -0.72), "lifesigns", bezel=0.02, rot=(0, 0, 0))
    m.box((0.1, 0.1, 0.06), (0.3, 1.55, -0.78), "hull_dark", 0.01)
    wheels(m, (-0.3, 0.3), (-0.75, 0.75), 0.05)


def b_exam(m, rng):
    m.box((0.55, 0.5, 1.0), (0, 0.25, 0.1), "hull_light", 0.03)
    m.box((0.5, 0.06, 0.94), (0, 0.03, 0.1), "hull_dark", 0.01)
    for k in range(2):
        m.box((0.45, 0.14, 0.02), (0, 0.15 + k * 0.17, 0.62), "hull_mid", 0.004)
        m.box((0.16, 0.025, 0.03), (0, 0.15 + k * 0.17, 0.64), "steel")
    m.box((0.7, 0.12, 0.7), (0, 0.56, 0.4), "leather_black", 0.04)
    m.box((0.7, 0.12, 0.9), (0, 0.75, -0.3), "leather_black", 0.04, rot=(-0.4, 0, 0))
    m.box((0.72, 0.1, 0.4), (0, 0.5, 0.9), "leather_black", 0.04)
    m.cyl(0.05, 0.75, (0, 0.85, -0.85), "md_sheet", axis="x", seg=10)  # paper roll
    m.box((0.02, 0.05, 0.14), (0.38, 0.85, -0.85), "steel")
    m.box((0.02, 0.05, 0.14), (-0.38, 0.85, -0.85), "steel")
    m.box((0.06, 0.06, 0.06), (0.36, 0.55, 0.15), "black_metal", rot=(0, 0, 0))
    m.link((0.36, 0.5, 0.1), (0.36, 0.5, 0.75), 0.015, "steel", 6)
    m.link((-0.36, 0.5, 0.1), (-0.36, 0.5, 0.75), 0.015, "steel", 6)
    # foot pedal + stirrup hint
    led(m, 0.24, 0.33, 0.63, "em_green")


def b_surgical(m, rng):
    m.box((0.9, 0.1, 0.7), (0, 0.05, 0), "hull_dark", 0.02)
    m.cyl(0.14, 0.7, (0, 0.45, 0), "chrome", seg=14)
    m.cyl(0.2, 0.15, (0, 0.85, 0), "steel", seg=14)
    m.box((0.62, 0.06, 2.0), (0, 0.98, 0), "steel", 0.02)
    for z, l in ((-0.75, 0.5), (-0.2, 0.55), (0.55, 0.85)):
        pass
    m.box((0.6, 0.04, 0.5), (0, 1.03, -0.7), "brushed_alu", 0.01)
    m.box((0.6, 0.04, 0.6), (0, 1.03, 0.0), "md_sheet", 0.01)
    m.box((0.6, 0.04, 0.7), (0, 1.03, 0.65), "brushed_alu", 0.01)
    m.box((0.7, 0.02, 0.02), (0, 1.02, -0.32), "black_metal")
    for s in (-1, 1):
        m.box((0.03, 0.05, 1.8), (s * 0.34, 1.0, 0.0), "chrome")
    # light stand at head
    m.box((0.5, 0.08, 0.4), (0.0, 0.04, -1.3), "hull_dark", 0.02)
    m.cyl(0.04, 2.6, (0, 1.3, -1.3), "steel", seg=8)
    m.link((0, 2.6, -1.3), (0, 2.6, -0.4), 0.03, "steel", 6)
    m.link((0, 2.6, -0.9), (-0.25, 2.5, -0.6), 0.02, "steel", 6)
    m.cyl(0.24, 0.06, (0.0, 2.5, -0.4), "hull_light", seg=14)
    m.cyl(0.2, 0.02, (0.0, 2.465, -0.4), "em_white", seg=14)
    m.cyl(0.05, 0.06, (0.0, 2.56, -0.4), "steel", seg=8)
    m.cyl(0.2, 0.06, (-0.25, 2.42, -0.6), "hull_light", seg=14)
    m.cyl(0.16, 0.02, (-0.25, 2.385, -0.6), "em_white", seg=14)


def b_recovery(m, rng):
    m.box((0.7, 0.16, 1.7), (0, 0.32, 0), "hull_dark", 0.02)
    wheels(m, (-0.36, 0.36), (-0.7, 0.7), 0.08)
    m.box((0.92, 0.12, 1.9), (0, 0.5, 0.05), "md_sheet", 0.04, rot=(0, 0, 0))
    m.box((0.8, 0.12, 1.15), (0, 0.63, 0.5), "fabric_teal", 0.04)
    m.box((0.9, 0.1, 0.72), (0, 0.7, -0.45), "md_sheet", 0.04, rot=(-0.3, 0, 0))
    m.box((0.6, 0.1, 0.32), (0, 0.85, -0.78), "plastic_white", 0.04, rot=(-0.3, 0, 0))
    m.box((1.0, 0.7, 0.06), (0, 0.72, -1.02), "wood_light", 0.02)
    m.box((1.0, 0.55, 0.06), (0, 0.66, 1.0), "wood_light", 0.02)
    for s in (-1, 1):
        rails(m, s * 0.5, 0.65, -0.5, 0.6, 0.28)
    ivhook(m, -0.52, 0.5, 0.95)
    m.box((0.3, 0.16, 0.02), (0, 0.8, 1.04), "black_metal", 0.004)
    m.box((0.24, 0.1, 0.012), (0, 0.8, 1.052), "em_green")


def b_stretcher(m, rng):
    m.box((0.66, 0.05, 1.9), (0, 0.75, 0), "steel", 0.01)
    m.box((0.6, 0.06, 1.85), (0, 0.8, 0), "md_bag", 0.02)
    for s in (-1, 1):
        m.box((0.05, 0.05, 2.1), (s * 0.36, 0.78, 0), "brushed_alu", 0.01)
        for z in (-1.05, 1.05):
            m.box((0.04, 0.08, 0.1), (s * 0.36, 0.78, z), "rubber")
    # x frame legs
    for z in (-0.55, 0.55):
        m.link((-0.3, 0.72, z), (0.3, 0.14, z), 0.02, "brushed_alu", 6)
        m.link((0.3, 0.72, z), (-0.3, 0.14, z), 0.02, "brushed_alu", 6)
        wheels(m, (-0.3, 0.3), (z,), 0.07)
        m.box((0.6, 0.03, 0.04), (0, 0.14, z), "steel")
    for z in (-0.3, 0.3, 0.0):
        m.box((0.7, 0.04, 0.06), (0, 0.85, z * 1.6), "fabric_red")
    m.box((0.5, 0.08, 0.3), (0, 0.87, -0.75), "md_sheet", 0.03)
    m.box((0.14, 0.03, 0.04), (0.37, 0.84, -0.4), "hazard_yellow")
    m.box((0.14, 0.03, 0.04), (-0.37, 0.84, 0.5), "hazard_yellow")
    m.box((0.06, 0.02, 0.2), (0, 0.84, 0.9), "paint_red")
    m.box((0.2, 0.02, 0.06), (0, 0.84, 0.9), "paint_red")


def b_isolation(m, rng):
    m.box((0.7, 0.3, 1.8), (0, 0.3, 0), "hull_dark", 0.02)
    wheels(m, (-0.38, 0.38), (-0.7, 0.7), 0.08)
    m.box((0.9, 0.12, 1.9), (0, 0.52, 0), "md_sheet", 0.04)
    m.box((0.6, 0.1, 0.3), (0, 0.63, -0.72), "plastic_white", 0.04)
    # frame posts and roof
    for x in (-0.55, 0.55):
        for z in (-1.0, 1.0):
            m.box((0.05, 1.6, 0.05), (x, 1.3, z), "steel")
    m.box((1.2, 0.05, 2.1), (0, 2.1, 0), "hull_light", 0.02)
    for x in (-0.55, 0.55):
        m.box((0.05, 0.05, 2.0), (x, 0.52, 0), "steel")
        m.box((0.05, 0.05, 2.0), (x, 1.3, 0), "steel")
    for z in (-1.0, 1.0):
        m.box((1.1, 0.05, 0.05), (0, 0.52, z), "steel")
        m.box((1.1, 0.05, 0.05), (0, 1.3, z), "steel")
    # curtain panels (sealed)
    m.box((0.02, 1.2, 1.9), (0.56, 1.4, 0), "md_curtain")
    m.box((0.02, 1.2, 0.9), (-0.56, 1.4, -0.5), "md_curtain")
    m.box((1.08, 1.2, 0.02), (0, 1.4, -1.0), "md_curtain")
    m.box((0.6, 1.0, 0.02), (-0.25, 1.4, 1.0), "md_curtain")
    m.box((0.5, 0.2, 0.6), (0, 2.25, 0.3), "hull_mid", 0.03)  # HEPA blower
    m.box((0.4, 0.04, 0.5), (0, 2.16, 0.3), "black_metal")
    hazard(m, 0, 2.1, 1.06, 1.1, 0.06)
    led(m, 0.5, 2.1, 1.06, "em_amber", 0.05)


BEDS = [b_bio, b_exam, b_surgical, b_recovery, b_stretcher, b_isolation]


# ================================================================ MEDSCANNERS
SCAN = ["Whole-Body Scanner Arch", "MRI Ring Scanner", "Bio-Scanner Pillar", "X-Ray Unit", "Ultrasound Cart",
        "Handheld Scanner Dock", "Vitals Monitor Stand", "Blood Analyser"]


@family("medscanner", SCAN, mount="floor", tags=["medical", "scanner"], solid=True)
def medscanner(m, i, label, rng):
    lean(m)
    SCANS[i](m, rng)


def s_arch(m, rng):
    m.box((1.9, 0.1, 3.0), (0, 0.05, 0), "hull_dark", 0.02)
    m.torus(0.9, 0.12, (0, 1.1, 0.0), "hull_light", axis="z", seg=24, tseg=8)
    m.torus(0.9, 0.05, (0, 1.1, 0.14), "em_cyan", axis="z", seg=24, tseg=5)
    m.torus(0.9, 0.05, (0, 1.1, -0.14), "em_cyan", axis="z", seg=24, tseg=5)
    m.torus(0.78, 0.03, (0, 1.1, 0.0), "chrome", axis="z", seg=24, tseg=5)
    for s in (-1, 1):
        m.box((0.3, 0.3, 0.5), (s * 0.95, 0.25, 0.0), "hull_mid", 0.03)
    m.box((0.6, 0.06, 2.6), (0, 0.8, 0.0), "md_sheet", 0.02)
    m.box((0.4, 0.55, 1.0), (0, 0.5, 1.0), "hull_light", 0.03)
    m.box((0.5, 0.5, 0.3), (0, 0.5, -1.15), "hull_light", 0.03)
    m.box((0.1, 0.9, 0.1), (1.05, 0.5, 0.7), "hull_dark", 0.01)
    m.screen((0.34, 0.24), (1.05, 1.05, 0.77), "lifesigns", bezel=0.015)
    m.box((0.5, 0.1, 0.3), (0, 2.1, 0.0), "hull_mid", 0.02)
    m.box((0.3, 0.04, 0.12), (0, 2.1, 0.16), "em_cyan")


def s_mri(m, rng):
    m.box((1.8, 0.2, 1.6), (0, 0.1, 0.0), "hull_dark", 0.02)
    m.box((1.9, 2.1, 1.2), (0, 1.15, -0.2), "hull_light", 0.06)
    m.torus(0.75, 0.35, (0, 1.15, 0.45), "plastic_white", axis="z", seg=28, tseg=10)
    m.torus(0.42, 0.03, (0, 1.15, 0.6), "em_cyan", axis="z", seg=28, tseg=5)
    hazard(m, 0, 0.35, 0.62, 1.4, 0.08)
    m.box((0.5, 0.06, 2.4), (0, 0.84, 0.65), "md_sheet", 0.02)
    m.box((0.4, 0.45, 0.9), (0, 0.55, 1.35), "hull_mid", 0.03)
    m.box((0.1, 0.26, 0.04), (0.92, 1.5, 0.59), "black_metal")
    led(m, 0.92, 1.5, 0.615, "em_amber", 0.04)
    label_plate(m, -0.7, 1.9, 0.6, 0.3, "em_red")


def s_pillar(m, rng):
    m.cyl(0.6, 0.15, (0, 0.075, 0), "hull_dark", seg=20)
    m.cyl(0.4, 2.4, (0, 1.35, 0), "hull_light", seg=20)
    m.cyl(0.42, 0.1, (0, 2.5, 0), "hull_dark", seg=20)
    m.cyl(0.32, 0.1, (0, 2.6, 0), "steel", seg=16)
    m.box((0.5, 1.4, 0.3), (0, 1.3, 0.28), "glass_blue", 0.02)
    m.box((0.36, 1.2, 0.05), (0, 1.3, 0.33), "em_cyan")
    m.torus(0.42, 0.04, (0, 0.6, 0), "chrome", seg=20, tseg=5)
    m.torus(0.42, 0.04, (0, 2.05, 0), "chrome", seg=20, tseg=5)
    m.cyl(0.43, 0.3, (0, 0.35, 0), "hazard_yellow", seg=20)
    m.torus(0.5, 0.03, (0, 1.3, 0), "em_cyan", seg=24, tseg=4)
    for a in (0.6, 2.2, 3.8, 5.4):
        m.box((0.05, 0.05, 0.14), (math.cos(a) * 0.5, 1.3, math.sin(a) * 0.5), "chrome", rot=(0, -a, 0))
    m.box((0.14, 0.14, 0.14), (0, 2.75, 0), "hull_mid", 0.02)
    led(m, 0.0, 2.75, 0.075, "em_cyan", 0.05)
    m.screen((0.26, 0.14), (0.0, 0.7, 0.4), "medical", bezel=0.01, rot=(-0.0, 0, 0))


def s_xray(m, rng):
    m.box((1.6, 0.1, 1.2), (0, 0.05, 0), "hull_dark", 0.02)
    m.box((0.2, 2.2, 0.3), (-0.55, 1.15, -0.35), "hull_light", 0.03)
    m.box((0.14, 0.14, 0.9), (-0.55, 1.4, 0.1), "hull_mid", 0.02)
    m.box((0.5, 0.4, 0.35), (-0.55, 1.4, 0.65), "hull_light", 0.04)  # tube head
    m.cyl(0.1, 0.1, (-0.55, 1.2, 0.65), "black_metal", seg=12)
    m.box((0.2, 0.03, 0.03), (-0.55, 1.62, 0.83), "em_amber")
    # detector table
    m.box((0.7, 0.08, 1.4), (0.35, 0.85, 0.0), "md_sheet", 0.02)
    m.box((0.5, 0.75, 0.5), (0.35, 0.4, -0.2), "hull_mid", 0.03)
    m.box((0.08, 0.5, 0.35), (0.85, 1.1, 0.2), "carbon", 0.01)  # upright detector
    m.box((0.06, 0.06, 0.1), (0.85, 0.85, 0.2), "steel")
    m.box((0.3, 0.2, 0.06), (0.35, 0.9, -0.9), "hull_dark", 0.01)
    hazard(m, -0.55, 0.15, 0.161, 0.16, 0.08)
    m.screen((0.24, 0.16), (-0.55, 0.9, -0.19), "diagnostic", bezel=0.01)


def s_ultra(m, rng):
    m.box((0.6, 0.08, 0.8), (0, 0.24, 0), "hull_dark", 0.02)
    m.box((0.5, 0.5, 0.65), (0, 0.55, 0), "hull_light", 0.03)
    wheels(m, (-0.25, 0.25), (-0.35, 0.35), 0.08)
    m.cyl(0.03, 0.5, (0, 1.0, -0.2), "steel", seg=8)
    m.box((0.5, 0.4, 0.05), (0, 1.35, -0.2), "black_metal", 0.02)
    m.screen((0.44, 0.34), (0, 1.35, -0.17), "lifesigns", bezel=0.0)
    m.box((0.6, 0.07, 0.3), (0, 0.82, 0.22), "hull_mid", 0.02)
    m.box((0.5, 0.04, 0.04), (0, 0.87, 0.3), "em_cyan")
    for x in (-0.28, 0.28):
        m.box((0.08, 0.16, 0.06), (x, 0.9, 0.05), "black_metal", 0.01)
    # probes
    m.link((0.28, 0.98, 0.05), (0.42, 0.82, 0.05), 0.02, "plastic_white", 6)
    m.box((0.06, 0.1, 0.05), (0.44, 0.78, 0.05), "paint_teal", 0.01)
    m.tube([(-0.28, 0.95, 0.05), (-0.42, 0.7, 0.2), (-0.35, 0.4, 0.34)], 0.012, "rubber")
    m.box((0.05, 0.4, 0.05), (0.3, 1.0, -0.36), "black_metal")
    m.box((0.05, 0.05, 0.3), (0.3, 1.2, -0.25), "black_metal")


def s_dock(m, rng):
    m.cyl(0.25, 0.05, (0, 0.025, 0), "black_metal", seg=14)
    m.cyl(0.05, 0.9, (0, 0.5, 0), "hull_mid", seg=10)
    m.box((0.28, 0.5, 0.2), (0, 1.15, 0), "hull_light", 0.03)
    m.box((0.2, 0.34, 0.03), (0, 1.15, 0.11), "black_metal", 0.01)
    m.screen((0.18, 0.1), (0, 1.3, 0.126), "medical", bezel=0.006)
    # handheld in cradle
    m.box((0.1, 0.24, 0.07), (0, 1.08, 0.15), "paint_teal", 0.015)
    m.box((0.07, 0.07, 0.014), (0, 1.14, 0.19), "em_cyan")
    m.box((0.14, 0.05, 0.1), (0, 0.95, 0.14), "black_metal", 0.01)
    led(m, 0.1, 0.92, 0.11, "em_green", 0.025)


def s_vitals(m, rng):
    m.cyl(0.32, 0.05, (0, 0.025, 0), "black_metal", seg=5)
    for k in range(5):
        a = k * 2 * math.pi / 5
        m.cyl(0.03, 0.06, (math.cos(a) * 0.3, 0.06, math.sin(a) * 0.3), "rubber", axis="x", seg=8)
    m.cyl(0.035, 1.3, (0, 0.7, 0), "steel", seg=10)
    m.box((0.5, 0.36, 0.08), (0, 1.5, 0), "hull_dark", 0.02)
    m.screen((0.44, 0.3), (0, 1.5, 0.045), "vitals", bezel=0.0)
    m.box((0.2, 0.14, 0.14), (0, 1.16, 0.06), "hull_light", 0.02)
    m.box((0.14, 0.06, 0.014), (0, 1.16, 0.132), "em_green")
    m.box((0.08, 0.16, 0.06), (-0.22, 1.05, 0.0), "black_metal", 0.01)
    m.tube([(-0.22, 1.1, 0.0), (-0.3, 0.9, 0.1), (-0.25, 0.7, 0.1)], 0.012, "rubber")
    m.box((0.14, 0.06, 0.1), (0.22, 1.02, 0.0), "paint_teal", 0.01)
    m.tube([(0.22, 1.05, 0.0), (0.3, 0.9, 0.1), (0.25, 0.6, 0.1)], 0.012, "plastic_white")


def s_blood(m, rng):
    cabinet(m, 0.9, 1.2, 0.7, "paint_white")
    m.box((0.8, 0.5, 0.45), (0, 1.45, -0.08), "hull_light", 0.04)
    m.cyl(0.24, 0.05, (0, 1.72, -0.08), "glass", seg=16)
    m.cyl(0.2, 0.02, (0, 1.74, -0.08), "chrome", seg=16)
    m.screen((0.34, 0.22), (0.2, 0.85, 0.36), "diagnostic", bezel=0.015)
    # sample racks / tubes
    m.box((0.36, 0.12, 0.02), (-0.2, 0.88, 0.36), "black_metal", 0.004)
    for k in range(5):
        m.cyl(0.018, 0.09, (-0.32 + k * 0.05, 0.95, 0.36), "md_blood" if k % 2 else "glass", seg=6)
        m.cyl(0.02, 0.02, (-0.32 + k * 0.05, 1.0, 0.36), "paint_red" if k % 2 else "paint_blue", seg=6)
    m.box((0.5, 0.05, 0.16), (0, 0.6, 0.4), "steel", 0.006)
    door(m, -0.2, 0.3, 0.35, 0.4, 0.3, "hull_light")
    led(m, 0.3, 0.65, 0.36, "em_green")


SCANS = [s_arch, s_mri, s_pillar, s_xray, s_ultra, s_dock, s_vitals, s_blood]


# ================================================================ MEDCABINETS
CAB = ["Medicine Cabinet", "Drug Dispensing Cabinet", "Sample Fridge", "Sterilizer Autoclave",
       "Instrument Tray Cabinet", "Medical Supply Cart"]


@family("medcabinet", CAB, mount="floor", tags=["medical", "storage"], solid=True)
def medcabinet(m, i, label, rng):
    lean(m)
    CABS[i](m, rng)


def c_medicine(m, rng):
    cabinet(m, 0.9, 1.9, 0.4, "paint_white")
    for s in (-1, 1):
        m.box((0.4, 1.3, 0.02), (s * 0.21, 1.15, 0.21), "black_metal", 0.004)
        m.box((0.36, 1.26, 0.012), (s * 0.21, 1.15, 0.225), "glass_blue")
        m.box((0.03, 0.2, 0.03), (s * 0.03, 1.15, 0.24), "steel")
    for k in range(4):
        m.box((0.8, 0.02, 0.3), (0, 0.62 + k * 0.33, 0.0), "steel")
        for j in range(4):
            m.box((0.08, 0.12, 0.08), (-0.3 + j * 0.2, 0.7 + k * 0.33, -0.02), ["paint_red", "paint_white", "hazard_yellow", "paint_teal"][(j + k) % 4], 0.006)
    m.box((0.8, 0.4, 0.02), (0, 0.32, 0.21), "hull_mid", 0.004)
    m.cyl(0.03, 0.03, (0.3, 0.32, 0.23), "em_red", axis="z", seg=8)
    m.box((0.14, 0.05, 0.02), (0.0, 1.85, 0.21), "paint_red")
    m.box((0.05, 0.14, 0.02), (0.0, 1.85, 0.21), "paint_red")


def c_dispense(m, rng):
    cabinet(m, 1.0, 1.8, 0.6, "hull_mid")
    m.screen((0.34, 0.24), (-0.22, 1.5, 0.31), "medical", bezel=0.015)
    m.box((0.2, 0.28, 0.03), (0.28, 1.5, 0.31), "black_metal", 0.006)
    for r in range(3):
        for c in range(3):
            m.box((0.05, 0.04, 0.012), (0.2 + c * 0.07, 1.6 - r * 0.08, 0.33), "plastic_grey")
    for r in range(5):
        y = 0.28 + r * 0.19
        m.box((0.9, 0.16, 0.02), (0, y, 0.31), "hull_light", 0.006)
        m.box((0.3, 0.03, 0.03), (0, y, 0.34), "steel")
        led(m, 0.4, y, 0.325, "em_green" if r != 2 else "em_red", 0.03)
    m.box((0.4, 0.16, 0.06), (-0.22, 1.2, 0.33), "black_metal", 0.01)


def c_fridge(m, rng):
    cabinet(m, 0.8, 1.7, 0.7, "paint_white")
    m.box((0.68, 1.3, 0.03), (0, 0.98, 0.36), "black_metal", 0.006)
    m.box((0.62, 1.24, 0.014), (0, 0.98, 0.38), "glass_blue")
    for k in range(4):
        m.box((0.56, 0.02, 0.4), (0, 0.5 + k * 0.28, 0.12), "steel")
        for j in range(3):
            m.cyl(0.03, 0.12, (-0.18 + j * 0.18, 0.58 + k * 0.28, 0.12), "md_blood" if (j + k) % 2 else "glass", seg=6)
    m.box((0.6, 0.02, 0.02), (0, 1.58, 0.35), "em_cyan")
    m.box((0.04, 0.5, 0.04), (0.3, 0.98, 0.4), "steel")
    m.box((0.2, 0.06, 0.02), (0, 0.15, 0.36), "black_metal")
    m.box((0.14, 0.03, 0.02), (0, 0.15, 0.37), "em_blue")
    m.cyl(0.06, 0.1, (0.0, 1.78, -0.15), "black_metal", seg=8)


def c_autoclave(m, rng):
    cabinet(m, 1.0, 1.3, 0.8, "hull_light")
    m.cyl(0.32, 0.08, (0, 0.85, 0.42), "chrome", axis="z", seg=20)
    m.cyl(0.27, 0.06, (0, 0.85, 0.46), "glass_dark", axis="z", seg=20)
    m.torus(0.32, 0.03, (0, 0.85, 0.44), "steel", axis="z", seg=20, tseg=5)
    for k in range(8):
        a = k * math.pi / 4
        m.cyl(0.012, 0.03, (math.cos(a) * 0.37, 0.85 + math.sin(a) * 0.37, 0.45), "black_metal", axis="z", seg=5)
    m.cyl(0.03, 0.14, (0.0, 0.85, 0.53), "steel", axis="y", seg=6)
    m.screen((0.34, 0.22), (0.0, 1.16, 0.41), "power", bezel=0.012)
    gauge(m, -0.35, 1.14, 0.41, 0.04, "em_amber")
    gauge(m, 0.35, 1.14, 0.41, 0.04, "em_green")
    hazard(m, 0, 0.12, 0.405, 0.8)
    m.cyl(0.05, 0.3, (-0.35, 1.45, -0.25), "steel", seg=8)
    m.box((0.12, 0.05, 0.02), (0.0, 0.4, 0.41), "em_orange")


def c_instr(m, rng):
    cabinet(m, 0.9, 1.4, 0.55, "hull_light")
    m.box((0.94, 0.05, 0.6), (0, 1.43, 0), "steel", 0.008)
    for k in range(5):
        y = 0.24 + k * 0.22
        m.box((0.8, 0.19, 0.03), (0, y, 0.29), "brushed_alu", 0.008)
        m.box((0.4, 0.03, 0.04), (0, y + 0.02, 0.32), "steel")
        m.box((0.1, 0.05, 0.012), (-0.32, y - 0.03, 0.31), "em_cyan") if k % 2 == 0 else None
    # open tray on top with tools
    m.box((0.6, 0.03, 0.4), (0, 1.5, 0.0), "steel", 0.006)
    for j in range(5):
        m.box((0.03, 0.015, 0.22), (-0.2 + j * 0.1, 1.53, 0), "chrome", rot=(0, 0.3 * (j - 2) * 0.3, 0))
    m.sphere(0.03, (0.25, 1.55, 0.1), "chrome", seg=6, ring=4)
    label_plate(m, 0.32, 1.32, 0.3, 0.2, "em_cyan")


def c_cart(m, rng):
    m.box((0.8, 0.05, 0.5), (0, 0.15, 0), "steel", 0.006)
    wheels(m, (-0.35, 0.35), (-0.2, 0.2), 0.06, 0.06)
    m.box((0.8, 0.05, 0.5), (0, 0.98, 0), "steel", 0.006)
    m.box((0.7, 0.6, 0.44), (0, 0.55, 0.0), "hull_light", 0.02)
    for k in range(3):
        m.box((0.64, 0.16, 0.02), (0, 0.32 + k * 0.19, 0.23), "hull_mid", 0.005)
        m.box((0.2, 0.03, 0.03), (0, 0.32 + k * 0.19 + 0.04, 0.26), "steel")
    for x in (-0.38, 0.38):
        m.box((0.04, 0.84, 0.04), (x, 0.57, -0.22), "steel")
    m.box((0.8, 0.14, 0.03), (0, 1.07, 0.24), "steel")
    for j in range(3):
        m.box((0.16, 0.1, 0.12), (-0.25 + j * 0.25, 1.06, 0.0), ["paint_red", "paint_white", "paint_teal"][j], 0.01)
    m.box((0.2, 0.06, 0.02), (0.0, 0.85, 0.24), "paint_red")
    led(m, 0.3, 0.86, 0.24, "em_green", 0.03)


CABS = [c_medicine, c_dispense, c_fridge, c_autoclave, c_instr, c_cart]

WALLCAB = ["Wall First-Aid Station", "Glove and Mask Dispenser"]


@family("medcabinet", WALLCAB, mount="wall", tags=["medical", "storage"], solid=False, mount_y=1.4)
def medcabinet_wall(m, i, label, rng):
    lean(m)
    if i == 0:
        m.box((0.6, 0.7, 0.16), (0, 0, 0.08), "paint_white", 0.02)
        m.box((0.5, 0.6, 0.02), (0, 0, 0.17), "glass_green")
        m.box((0.3, 0.09, 0.03), (0, 0.0, 0.2), "paint_red")
        m.box((0.09, 0.3, 0.03), (0, 0.0, 0.2), "paint_red")
        for j in range(2):
            for k in range(3):
                m.box((0.12, 0.12, 0.09), (-0.15 + k * 0.15, -0.2 + j * 0.4, 0.13), ["paint_red", "md_bag", "hazard_yellow"][(j + k) % 3], 0.008)
        m.box((0.6, 0.05, 0.02), (0, 0.355, 0.17), "em_green")
        bolts(m, (-0.27, 0.27), (-0.32, 0.32), 0.165, 0.01)
    else:
        m.box((0.5, 0.36, 0.12), (0, 0.1, 0.06), "hull_light", 0.02)
        m.box((0.44, 0.1, 0.1), (0, 0.32, 0.06), "hull_dark", 0.01)
        for x, c in ((-0.12, "paint_blue"), (0.12, "paint_white")):
            m.box((0.2, 0.22, 0.05), (x, 0.1, 0.14), c, 0.01)
            m.box((0.1, 0.03, 0.02), (x, 0.0, 0.17), "black_metal")
        m.box((0.44, 0.04, 0.08), (0, -0.1, 0.14), "hull_dark", 0.006)
        m.box((0.36, 0.03, 0.02), (0, 0.24, 0.115), "em_green")
        led(m, 0.22, 0.32, 0.125, "em_green", 0.03)


# ================================================================ MEDTOOLS
TOOL = ["Hypospray Dock", "Medical Tricorder", "Surgical Instrument Tray", "Compact Microscope",
        "Syringe Rack", "Med-Kit Case", "Biohazard Bin", "Medical Shoulder Bag"]


@family("medtool", TOOL, mount="table", tags=["medical", "tool"], solid=False)
def medtool(m, i, label, rng):
    lean(m, 0.03)
    TOOLS[i](m, rng)


def t_hypo(m, rng):
    m.box((0.22, 0.05, 0.14), (0, 0.025, 0), "black_metal", 0.01)
    m.box((0.2, 0.06, 0.12), (0, 0.08, -0.01), "hull_dark", 0.01)
    m.box((0.2, 0.05, 0.03), (0, 0.16, -0.06), "hull_mid", 0.005)
    m.cyl(0.018, 0.14, (0, 0.14, 0.0), "chrome", axis="z", seg=8)
    m.cyl(0.024, 0.06, (0, 0.14, -0.03), "paint_teal", axis="z", seg=8)
    m.cyl(0.012, 0.04, (0, 0.14, 0.09), "steel", axis="z", seg=6, r2=0.004)
    m.cyl(0.014, 0.06, (0.0, 0.18, -0.02), "glass_blue", axis="z", seg=6)
    m.cyl(0.005, 0.06, (0.0, 0.18, -0.02), "em_cyan", axis="z", seg=4)
    led(m, 0.08, 0.115, 0.06, "em_green", 0.015)


def t_tricorder(m, rng):
    m.box((0.18, 0.05, 0.3), (0, 0.025, 0), "paint_grey", 0.012)
    m.box((0.16, 0.03, 0.28), (0, 0.06, 0), "black_metal", 0.008)
    m.quad((0.11, 0.09), (0, 0.077, 0.07), "screen:medical", rot=(-math.pi / 2, 0, 0))
    for k in range(3):
        m.cyl(0.014, 0.015, (-0.05 + k * 0.05, 0.078, -0.03), ["paint_red", "paint_teal", "em_amber"][k], seg=8)
    m.cyl(0.03, 0.02, (0, 0.078, -0.1), "chrome", seg=10)
    m.cyl(0.02, 0.02, (0, 0.085, -0.1), "em_cyan", seg=10)
    m.box((0.06, 0.03, 0.05), (0, 0.06, 0.16), "steel", 0.006)


def t_tray(m, rng):
    m.box((0.36, 0.015, 0.24), (0, 0.008, 0), "steel", 0.004)
    for x in (-1, 1):
        m.box((0.012, 0.03, 0.24), (x * 0.18, 0.02, 0), "steel")
    for z in (-1, 1):
        m.box((0.36, 0.03, 0.012), (0, 0.02, z * 0.12), "steel")
    for k in range(5):
        L = 0.14 + 0.02 * (k % 3)
        m.box((0.012, 0.008, L), (-0.12 + k * 0.05, 0.03, -0.02), "chrome")
        m.box((0.02, 0.01, 0.04), (-0.12 + k * 0.05, 0.03, -0.02 + L / 2), "chrome")
    m.sphere(0.02, (0.13, 0.04, 0.07), "chrome", seg=6, ring=4)
    m.box((0.05, 0.025, 0.05), (-0.13, 0.035, 0.07), "paint_teal", 0.005)
    m.cyl(0.008, 0.06, (0.03, 0.03, 0.08), "glass", axis="x", seg=5)


def t_microscope(m, rng):
    m.box((0.2, 0.03, 0.26), (0, 0.015, 0), "black_metal", 0.01)
    m.box((0.05, 0.3, 0.05), (0, 0.18, -0.08), "hull_light", 0.01)
    m.box((0.14, 0.02, 0.12), (0, 0.15, 0.03), "black_metal", 0.004)
    m.box((0.05, 0.005, 0.06), (0, 0.162, 0.03), "glass")
    m.cyl(0.02, 0.18, (0, 0.31, -0.02), "hull_light", seg=8, rot=(-0.55, 0, 0))
    m.cyl(0.025, 0.05, (0, 0.24, 0.05), "steel", seg=8)
    m.cyl(0.012, 0.06, (0, 0.2, 0.05), "chrome", seg=6)
    m.cyl(0.03, 0.03, (0.05, 0.1, -0.08), "steel", axis="x", seg=8)
    m.box((0.04, 0.02, 0.03), (0, 0.06, 0.08), "em_cyan")


def t_syringe(m, rng):
    m.box((0.3, 0.015, 0.14), (0, 0.008, 0), "black_metal", 0.004)
    m.box((0.3, 0.14, 0.02), (0, 0.08, -0.06), "plastic_black", 0.005)
    m.box((0.3, 0.02, 0.1), (0, 0.13, -0.02), "plastic_black", 0.004)
    for k in range(6):
        x = -0.125 + k * 0.05
        m.cyl(0.011, 0.11, (x, 0.09, -0.02), "glass", seg=6)
        m.cyl(0.004, 0.05, (x, 0.175, -0.02), "steel", seg=4)
        m.box((0.025, 0.006, 0.014), (x, 0.202, -0.02), "plastic_white")
        m.cyl(0.0085, 0.05, (x, 0.07, -0.02), ["em_cyan", "em_amber", "paint_red"][k % 3], seg=5)


def t_medkit(m, rng):
    m.box((0.34, 0.2, 0.14), (0, 0.1, 0), "paint_red", 0.02)
    m.box((0.36, 0.03, 0.16), (0, 0.19, 0), "paint_white", 0.008)
    m.box((0.12, 0.05, 0.005), (0, 0.1, 0.073), "paint_white")
    m.box((0.035, 0.12, 0.005), (0, 0.1, 0.073), "paint_white")
    m.link((-0.1, 0.22, 0.0), (0.1, 0.22, 0.0), 0.014, "black_metal", 6)
    for x in (-0.1, 0.1):
        m.box((0.02, 0.05, 0.03), (x, 0.205, 0.0), "black_metal")
    for x in (-0.11, 0.11):
        m.box((0.03, 0.05, 0.02), (x, 0.13, 0.078), "steel", 0.004)
    led(m, 0.11, 0.17, 0.075, "em_green", 0.02)


def t_biobin(m, rng):
    m.cyl(0.13, 0.34, (0, 0.17, 0), "md_biohaz", seg=12, r2=0.15)
    m.cyl(0.155, 0.04, (0, 0.36, 0), "paint_red", seg=12)
    m.box((0.1, 0.03, 0.05), (0.0, 0.395, 0.06), "black_metal", 0.004)
    # biohazard symbol as three discs + ring
    for k in range(3):
        a = k * 2.094 + 1.57
    m.torus(0.04, 0.008, (0, 0.2, 0.147), "hazard_yellow", axis="z", seg=10, tseg=4)
    m.cyl(0.012, 0.01, (0, 0.2, 0.145), "hazard_yellow", axis="z", seg=6)


def t_bag(m, rng):
    m.box((0.36, 0.22, 0.16), (0, 0.11, 0), "md_bag", 0.04)
    m.box((0.37, 0.09, 0.17), (0, 0.2, 0), "md_bag", 0.03)
    m.box((0.38, 0.015, 0.175), (0, 0.155, 0), "black_metal")
    m.link((-0.12, 0.24, 0), (-0.06, 0.32, 0), 0.01, "leather_black", 6)
    m.link((0.12, 0.24, 0), (0.06, 0.32, 0), 0.01, "leather_black", 6)
    m.link((-0.06, 0.32, 0), (0.06, 0.32, 0), 0.01, "leather_black", 6)
    m.box((0.2, 0.09, 0.02), (0, 0.09, 0.085), "hull_dark", 0.006)
    m.box((0.07, 0.02, 0.01), (0, 0.12, 0.098), "paint_white")
    m.box((0.02, 0.07, 0.01), (0, 0.12, 0.098), "paint_white")


TOOLS = [t_hypo, t_tricorder, t_tray, t_microscope, t_syringe, t_medkit, t_biobin, t_bag]


# ================================================================ SURGICAL
SURG = ["Surgical Robotic Arm Unit", "Anesthesia Machine", "Defibrillator Cart", "Ventilator Unit",
        "Dialysis Machine"]


@family("surgical", SURG, mount="floor", tags=["medical", "surgical"], solid=True)
def surgical(m, i, label, rng):
    lean(m)
    SURGS[i](m, rng)


def x_robot(m, rng):
    m.cyl(0.5, 0.25, (0, 0.13, 0), "hull_dark", seg=20)
    m.cyl(0.4, 0.25, (0, 0.37, 0), "hull_light", seg=20)
    m.torus(0.41, 0.02, (0, 0.5, 0), "em_cyan", seg=20, tseg=4)
    m.cyl(0.16, 0.6, (0, 0.85, -0.05), "hull_light", seg=12)
    m.sphere(0.2, (0, 1.2, -0.05), "hull_mid", seg=12, ring=6)
    m.link((0, 1.2, -0.05), (0.0, 1.9, 0.3), 0.09, "hull_light", 10)
    m.sphere(0.13, (0.0, 1.9, 0.3), "hull_mid", seg=12, ring=6)
    m.link((0.0, 1.9, 0.3), (0.0, 1.45, 0.8), 0.07, "hull_light", 10)
    m.sphere(0.1, (0.0, 1.45, 0.8), "black_metal", seg=10, ring=5)
    m.link((0.0, 1.45, 0.8), (0.0, 1.05, 0.85), 0.05, "steel", 8)
    for dx in (-0.04, 0.04):
        m.link((dx, 1.05, 0.85), (dx * 2, 0.85, 0.87), 0.012, "chrome", 5)
    m.torus(0.13, 0.014, (0.0, 1.9, 0.3), "em_cyan", axis="x", seg=14, tseg=4)
    m.torus(0.085, 0.012, (0.0, 1.45, 0.8), "em_cyan", axis="x", seg=12, tseg=4)
    led(m, 0.0, 0.4, 0.4, "em_green", 0.05)


def x_anes(m, rng):
    m.box((0.8, 0.06, 0.6), (0, 0.06, 0), "black_metal", 0.01)
    wheels(m, (-0.35, 0.35), (-0.25, 0.25), 0.06, 0.06)
    m.box((0.7, 0.9, 0.55), (0, 0.6, 0), "hull_light", 0.03)
    for k in range(3):
        m.box((0.6, 0.2, 0.03), (0, 0.32 + k * 0.26, 0.29), "hull_mid", 0.006)
        m.box((0.2, 0.03, 0.04), (0, 0.32 + k * 0.26, 0.32), "steel")
    m.box((0.8, 0.04, 0.6), (0, 1.09, 0), "steel", 0.008)
    m.box((0.5, 0.42, 0.14), (0.05, 1.32, -0.15), "black_metal", 0.02)
    m.screen((0.44, 0.34), (0.05, 1.32, -0.075), "vitals", bezel=0.0)
    m.cyl(0.08, 0.3, (-0.25, 1.28, 0.1), "glass", seg=10)
    m.cyl(0.085, 0.03, (-0.25, 1.15, 0.1), "steel", seg=10)
    m.cyl(0.085, 0.03, (-0.25, 1.42, 0.1), "steel", seg=10)
    for c, x in (("paint_green", 0.2), ("paint_blue", 0.32)):
        m.cyl(0.04, 0.28, (x, 1.25, 0.15), c, seg=8)
        m.cyl(0.03, 0.05, (x, 1.42, 0.15), "brass", seg=6)
    m.tube([(-0.25, 1.05, 0.15), (-0.45, 0.95, 0.3), (-0.4, 0.7, 0.35)], 0.02, "rubber")
    m.cyl(0.03, 0.22, (0.05, 1.63, -0.15), "steel", seg=8)


def x_defib(m, rng):
    m.box((0.7, 0.06, 0.55), (0, 0.32, 0), "steel", 0.008)
    wheels(m, (-0.3, 0.3), (-0.2, 0.2), 0.07, 0.08)
    m.box((0.5, 0.36, 0.34), (0, 0.54, 0.0), "paint_red", 0.03)
    m.box((0.44, 0.3, 0.1), (0, 0.95, -0.05), "paint_red", 0.03)
    m.screen((0.32, 0.2), (0, 0.98, 0.006), "lifesigns", bezel=0.012)
    m.cyl(0.05, 0.03, (-0.15, 0.82, 0.03), "paint_orange", axis="z", seg=10)
    m.cyl(0.04, 0.03, (0.05, 0.82, 0.03), "em_amber", axis="z", seg=10)
    m.cyl(0.03, 0.02, (0.15, 0.82, 0.03), "em_green", axis="z", seg=8)
    # paddles
    for s in (-1, 1):
        m.box((0.14, 0.03, 0.09), (s * 0.3, 0.73, 0.12), "black_metal", 0.008)
        m.box((0.05, 0.05, 0.08), (s * 0.3, 0.77, 0.08), "paint_grey", 0.01)
    m.box((0.14, 0.14, 0.02), (0.0, 0.54, 0.175), "paint_white", 0.004)
    m.box((0.1, 0.03, 0.01), (0.0, 0.54, 0.187), "paint_red")
    m.box((0.03, 0.1, 0.01), (0.0, 0.54, 0.187), "paint_red")


def x_vent(m, rng):
    m.cyl(0.3, 0.04, (0, 0.03, 0), "black_metal", seg=5)
    for k in range(5):
        a = k * 2 * math.pi / 5
        m.cyl(0.035, 0.06, (math.cos(a) * 0.29, 0.06, math.sin(a) * 0.29), "rubber", axis="x", seg=8)
    m.cyl(0.04, 0.8, (0, 0.45, 0), "steel", seg=8)
    m.box((0.54, 0.44, 0.44), (0, 1.0, 0), "hull_light", 0.04)
    m.screen((0.4, 0.26), (0, 1.06, 0.225), "lifesigns", bezel=0.012)
    for k in range(3):
        m.cyl(0.03, 0.03, (-0.16 + k * 0.16, 0.85, 0.23), ["paint_blue", "paint_white", "paint_red"][k], axis="z", seg=8)
    m.cyl(0.06, 0.1, (0.3, 0.95, 0.0), "steel", axis="x", seg=10)
    m.tube([(0.34, 0.95, 0.0), (0.5, 0.9, 0.2), (0.55, 0.6, 0.3), (0.4, 0.55, 0.4)], 0.03, "plastic_grey")
    m.box((0.14, 0.1, 0.12), (0.4, 0.5, 0.42), "paint_teal", 0.015)
    m.box((0.36, 0.03, 0.02), (0, 1.235, 0.22), "em_cyan")
    m.box((0.05, 0.16, 0.06), (-0.29, 1.1, 0.0), "black_metal", 0.006)


def x_dialysis(m, rng):
    m.box((0.7, 0.06, 0.6), (0, 0.06, 0), "black_metal", 0.01)
    wheels(m, (-0.3, 0.3), (-0.25, 0.25), 0.06, 0.06)
    m.box((0.6, 0.6, 0.5), (0, 0.42, 0), "hull_light", 0.03)
    m.box((0.5, 0.7, 0.5), (0, 1.1, -0.05), "hull_light", 0.03)
    m.screen((0.34, 0.26), (0, 1.32, 0.205), "power", bezel=0.012)
    # pump heads and cartridge
    for k in range(2):
        m.cyl(0.07, 0.05, (-0.14 + k * 0.28, 0.98, 0.26), "chrome", axis="z", seg=12)
        m.cyl(0.03, 0.03, (-0.14 + k * 0.28, 0.98, 0.29), "hull_dark", axis="z", seg=8)
    m.box((0.14, 0.32, 0.05), (0.0, 0.62, 0.28), "glass_blue", 0.008)
    m.box((0.08, 0.28, 0.02), (0.0, 0.62, 0.31), "md_blood")
    m.tube([(-0.14, 1.05, 0.28), (-0.25, 1.15, 0.35), (-0.3, 0.75, 0.4), (-0.06, 0.7, 0.32)], 0.012, "md_blood")
    m.tube([(0.14, 1.05, 0.28), (0.25, 1.15, 0.35), (0.3, 0.75, 0.4), (0.06, 0.7, 0.32)], 0.012, "water")
    m.box((0.2, 0.3, 0.16), (0.42, 1.0, -0.1), "paint_white", 0.03)  # dialysate bag
    m.cyl(0.015, 0.4, (0.42, 1.3, -0.1), "steel", seg=6)
    led(m, 0.22, 0.75, 0.255, "em_green", 0.03)


SURGS = [x_robot, x_anes, x_defib, x_vent, x_dialysis]


@family("surgical", ["Overhead Surgical Light Boom"], mount="ceiling", tags=["medical", "surgical"], solid=False)
def surgical_light(m, i, label, rng):
    lean(m)
    m.cyl(0.25, 0.08, (0, -0.04, 0), "hull_dark", seg=16)
    m.cyl(0.08, 0.5, (0, -0.33, 0), "steel", seg=10)
    m.sphere(0.09, (0, -0.6, 0), "hull_mid", seg=10, ring=6)
    m.link((0, -0.6, 0), (0.8, -0.65, 0.0), 0.05, "hull_light", 8)
    m.sphere(0.07, (0.8, -0.65, 0.0), "hull_mid", seg=10, ring=6)
    m.link((0, -0.6, 0), (-0.7, -0.62, 0.3), 0.05, "hull_light", 8)
    m.sphere(0.07, (-0.7, -0.62, 0.3), "hull_mid", seg=10, ring=6)
    for (x, y, z, r) in ((0.8, -0.65, 0.0, 0.32), (-0.7, -0.62, 0.3, 0.28)):
        m.cyl(0.03, 0.15, (x, y - 0.1, z), "steel", seg=6)
        m.cyl(r, 0.08, (x, y - 0.24, z), "hull_light", seg=20, r2=r * 0.9)
        m.cyl(r * 0.85, 0.02, (x, y - 0.29, z), "em_white", seg=20)
        m.cyl(r * 0.25, 0.03, (x, y - 0.3, z), "chrome", seg=10)
        m.torus(r * 0.92, 0.015, (x, y - 0.23, z), "steel", seg=20, tseg=4)


# ================================================================ CRYO
CRYO = ["Cryo-Stasis Pod", "Cryo Control Pillar", "Nutrient IV Tree", "Cryo Storage Tank"]


@family("cryo", CRYO, mount="floor", tags=["medical", "cryo"], solid=True)
def cryo(m, i, label, rng):
    lean(m)
    CR[i](m, rng)


def y_pod(m, rng):
    m.box((1.0, 0.3, 2.5), (0, 0.15, 0), "hull_dark", 0.04)  # plinth reaches the floor
    m.box((0.8, 0.6, 2.3), (0, 0.55, 0), "md_frost", 0.06)
    m.box((0.6, 0.08, 1.9), (0, 0.88, 0.0), "md_sheet", 0.03)
    # glass lid
    m.box((0.78, 0.4, 2.1), (0, 1.15, 0.0), "glass_blue", 0.12)
    m.box((0.05, 0.4, 2.1), (-0.4, 1.15, 0.0), "md_frost", 0.01)
    m.box((0.05, 0.4, 2.1), (0.4, 1.15, 0.0), "md_frost", 0.01)
    for z in (-1.05, 0.0, 1.05):
        m.box((0.85, 0.06, 0.06), (0, 1.35, z), "brushed_alu", 0.01)
    m.box((0.02, 0.05, 2.2), (0.41, 0.4, 0.0), "em_cyan")
    m.box((0.02, 0.05, 2.2), (-0.41, 0.4, 0.0), "em_cyan")
    m.box((0.5, 0.4, 0.2), (0, 0.5, 1.3), "hull_mid", 0.03)
    m.screen((0.34, 0.2), (0, 0.5, 1.405), "lifesigns", bezel=0.01)
    for s in (-1, 1):
        m.cyl(0.05, 0.25, (s * 0.3, 0.3, -1.3), "steel", seg=8, axis="z")
        m.cyl(0.06, 0.08, (s * 0.3, 0.3, -1.42), "chrome", seg=8, axis="z")
    # frost patches
    m.box((0.6, 0.02, 0.5), (0, 0.885, -0.5), "md_frost")


def y_ctrl(m, rng):
    m.box((0.7, 0.15, 0.7), (0, 0.075, 0), "hull_dark", 0.02)
    m.box((0.5, 1.7, 0.45), (0, 1.0, 0), "hull_light", 0.05)
    m.box((0.54, 0.12, 0.5), (0, 1.9, 0), "hull_dark", 0.02)
    m.screen((0.4, 0.3), (0, 1.5, 0.245), "vitals", bezel=0.015)
    m.box((0.36, 0.12, 0.1), (0, 1.15, 0.27), "hull_dark", 0.01, rot=(-0.3, 0, 0))
    for k in range(4):
        m.cyl(0.025, 0.02, (-0.12 + k * 0.08, 1.15, 0.31), ["em_cyan", "em_amber", "em_green", "em_red"][k], axis="z", seg=8)
    m.cyl(0.06, 0.05, (0, 0.8, 0.25), "paint_red", axis="z", seg=10)
    m.box((0.36, 0.3, 0.02), (0, 0.4, 0.235), "md_frost", 0.004)
    m.box((0.36, 0.02, 0.02), (0, 0.55, 0.245), "em_cyan")
    m.tube([(0.26, 1.85, -0.1), (0.42, 1.85, -0.1), (0.42, 0.25, -0.1), (0.7, 0.05, 0.1)], 0.03, "hull_mid")
    m.torus(0.22, 0.02, (0, 2.0, 0), "em_cyan", seg=16, tseg=4)


def y_iv(m, rng):
    m.cyl(0.32, 0.05, (0, 0.025, 0), "black_metal", seg=5)
    for k in range(5):
        a = k * 2 * math.pi / 5
        m.cyl(0.035, 0.06, (math.cos(a) * 0.3, 0.05, math.sin(a) * 0.3), "rubber", axis="x", seg=8)
    m.cyl(0.035, 2.0, (0, 1.0, 0), "steel", seg=8)
    for k, a in enumerate((0.0, 1.57, 3.14, 4.71)):
        L = 0.4
        ex, ez = math.cos(a) * L, math.sin(a) * L
        m.link((0, 2.0, 0), (ex, 2.05, ez), 0.015, "steel", 6)
        m.sphere(0.02, (ex, 2.05, ez), "steel", seg=5, ring=3)
        m.box((0.14, 0.24, 0.05), (ex, 1.88, ez), ["md_sheet", "glass_amber", "glass_green", "glass_blue"][k], 0.02, rot=(0, -a + 1.57, 0))
        m.tube([(ex, 1.76, ez), (ex * 0.4, 1.4 - k * 0.1, ez * 0.4 + 0.02), (0, 1.1 - k * 0.1, 0.06)], 0.008, "plastic_white")
    m.box((0.2, 0.22, 0.12), (0.0, 0.95, 0.09), "hull_light", 0.02)
    m.box((0.14, 0.08, 0.012), (0.0, 0.98, 0.156), "em_green")
    led(m, 0.0, 0.88, 0.156, "em_amber", 0.03)


def y_tank(m, rng):
    m.cyl(0.6, 0.15, (0, 0.075, 0), "hull_dark", seg=20)
    m.cyl(0.5, 1.7, (0, 1.0, 0), "md_frost", seg=20)
    m.cyl(0.52, 0.1, (0, 0.35, 0), "steel", seg=20)
    m.cyl(0.52, 0.1, (0, 1.65, 0), "steel", seg=20)
    m.sphere(0.5, (0, 1.85, 0), "md_frost", seg=20, ring=6, scale=(1, 0.4, 1))
    m.box((0.22, 1.2, 0.05), (0, 1.0, 0.5), "glass_blue")
    m.box((0.1, 1.1, 0.02), (0, 1.0, 0.53), "em_cyan")
    m.cyl(0.14, 0.14, (0, 2.1, 0), "steel", seg=12)
    m.cyl(0.16, 0.03, (0, 2.19, 0), "hazard_yellow", seg=12)
    m.cyl(0.05, 0.4, (0.0, 2.35, 0.0), "steel", seg=8)
    gauge(m, -0.25, 0.6, 0.5, 0.06, "em_cyan")
    gauge(m, 0.25, 0.6, 0.5, 0.06, "em_amber")
    m.torus(0.5, 0.02, (0, 1.0, 0), "chrome", seg=20, tseg=4)
    m.box((0.32, 0.1, 0.03), (0.0, 0.25, 0.5), "hull_dark", 0.006)
    m.box((0.2, 0.03, 0.02), (0.0, 0.25, 0.52), "em_blue")


CR = [y_pod, y_ctrl, y_iv, y_tank]


# ================================================================ MEDSUPPLY
SUP = ["Hover Stretcher", "IV Stand", "Linen Cart"]


@family("medsupply", SUP, mount="floor", tags=["medical", "supply"], solid=True)
def medsupply(m, i, label, rng):
    lean(m)
    SUPS[i](m, rng)


def p_hover(m, rng):
    m.box((0.8, 0.1, 2.0), (0, 0.3, 0), "hull_dark", 0.03)
    m.box((0.76, 0.02, 1.96), (0, 0.24, 0), "em_cyan")
    for x in (-0.3, 0.3):
        for z in (-0.7, 0.7):
            m.cyl(0.12, 0.06, (x, 0.2, z), "black_metal", seg=12)
            m.cyl(0.09, 0.02, (x, 0.165, z), "em_blue", seg=12)
    m.box((0.7, 0.1, 1.9), (0, 0.42, 0), "hull_light", 0.04)
    m.box((0.62, 0.08, 1.8), (0, 0.5, 0), "md_sheet", 0.03)
    m.box((0.5, 0.08, 0.3), (0, 0.6, -0.7), "plastic_white", 0.03)
    for s in (-1, 1):
        m.box((0.04, 0.05, 1.7), (s * 0.4, 0.58, 0.0), "steel", 0.008)
    m.box((0.6, 0.2, 0.06), (0, 0.65, 1.02), "hull_light", 0.02)
    m.box((0.4, 0.06, 0.02), (0, 0.66, 1.06), "em_cyan")
    m.box((0.6, 0.03, 0.06), (0, 0.56, 0.2), "fabric_red")
    m.box((0.6, 0.03, 0.06), (0, 0.56, 0.5), "fabric_red")
    led(m, 0.3, 0.66, 1.06, "em_green", 0.04)
    m.shift(dy=-0.105)  # hover height 0.05 m (was 0.155)


def p_ivstand(m, rng):
    m.cyl(0.03, 1.9, (0, 1.0, 0), "chrome", seg=8)
    m.cyl(0.32, 0.04, (0, 0.06, 0), "black_metal", seg=5)
    for k in range(5):
        a = k * 2 * math.pi / 5
        m.link((0, 0.1, 0), (math.cos(a) * 0.32, 0.06, math.sin(a) * 0.32), 0.02, "chrome", 6)
        m.cyl(0.035, 0.04, (math.cos(a) * 0.32, 0.035, math.sin(a) * 0.32), "rubber", axis="x", seg=8)
    m.cyl(0.05, 0.12, (0, 1.9, 0), "steel", seg=8)
    for a in (0.6, 2.7, 4.8):
        ex, ez = math.cos(a) * 0.22, math.sin(a) * 0.22
        m.link((0, 1.98, 0), (ex, 2.0, ez), 0.012, "chrome", 5)
    m.box((0.12, 0.22, 0.04), (0.21, 1.86, 0.1), "glass_blue", 0.01)
    m.box((0.1, 0.22, 0.04), (-0.18, 1.86, -0.12), "glass_amber", 0.01)
    # infusion pump
    m.box((0.2, 0.26, 0.14), (0.0, 1.35, 0.1), "hull_light", 0.02)
    m.box((0.16, 0.06, 0.01), (0.0, 1.42, 0.175), "em_green")
    m.box((0.16, 0.06, 0.01), (0.0, 1.3, 0.175), "black_metal")
    m.tube([(0.21, 1.74, 0.1), (0.15, 1.5, 0.15), (0.0, 1.35, 0.2), (0.1, 1.0, 0.25)], 0.007, "plastic_white")


def p_linen(m, rng):
    m.box((0.8, 0.06, 0.55), (0, 0.16, 0), "steel", 0.006)
    wheels(m, (-0.36, 0.36), (-0.22, 0.22), 0.06, 0.06)
    for x in (-0.38, 0.38):
        for z in (-0.25, 0.25):
            m.box((0.03, 1.1, 0.03), (x, 0.7, z), "steel")
    for y in (0.5, 0.95):
        m.box((0.8, 0.03, 0.55), (0, y, 0), "steel", 0.004)
    m.box((0.8, 0.03, 0.55), (0, 1.25, 0), "steel", 0.004)
    for y, ss in ((0.19, 0.29), (0.53, 0.31), (0.98, 0.3)):
        for j in range(3):
            c = ["md_sheet", "fabric_teal", "foam"][(j + int(y * 5)) % 3]
            m.box((0.22, 0.23, 0.44), (-0.25 + j * 0.25, y + 0.14, 0), c, 0.03)
    m.box((0.78, 0.4, 0.02), (0, 0.72, -0.27), "fabric_grey", 0.005)
    m.box((0.05, 0.03, 0.4), (0.42, 1.28, 0.0), "steel")
    label_plate(m, 0, 1.27, 0.29, 0.2, "em_cyan")


SUPS = [p_hover, p_ivstand, p_linen]

WALLSUP = ["Sharps Container", "Wall Patient Monitor"]


@family("medsupply", WALLSUP, mount="wall", tags=["medical", "supply"], solid=False, mount_y=1.3)
def medsupply_wall(m, i, label, rng):
    lean(m)
    if i == 0:
        m.box((0.3, 0.3, 0.02), (0, 0, 0.01), "black_metal", 0.004)
        m.box((0.24, 0.3, 0.16), (0, 0, 0.1), "md_biohaz", 0.02)
        m.box((0.26, 0.05, 0.18), (0, 0.16, 0.1), "paint_red", 0.008)
        m.box((0.16, 0.03, 0.08), (0, 0.1, 0.19), "black_metal", 0.006)
        m.torus(0.05, 0.008, (0, -0.02, 0.185), "hazard_yellow", axis="z", seg=10, tseg=4)
        m.box((0.16, 0.04, 0.02), (0, -0.12, 0.185), "hazard_yellow")
    else:
        m.box((0.7, 0.5, 0.08), (0, 0, 0.04), "hull_dark", 0.02)
        m.box((0.62, 0.42, 0.03), (0, 0, 0.095), "black_metal", 0.008)
        m.screen((0.56, 0.36), (0, 0, 0.115), "vitals", bezel=0.0)
        m.box((0.6, 0.02, 0.02), (0, -0.28, 0.09), "em_cyan")
        m.box((0.12, 0.05, 0.05), (0.0, 0.28, 0.06), "hull_mid", 0.008)
        led(m, 0.26, 0.28, 0.09, "em_green", 0.03)
        m.link((0.35, -0.25, 0.06), (0.5, -0.4, 0.12), 0.01, "rubber", 5)
        m.box((0.05, 0.06, 0.04), (0.5, -0.43, 0.12), "paint_teal", 0.006)
