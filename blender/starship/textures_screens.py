"""Additional 256x256 emissive display textures (UI looks) for the ship's screens.

They reuse the drawing helpers of textures.py and are appended to textures.SCREENS (so make_screens writes them
with the same CRT scanline / posterise pass).  `screen_families.py` maps the generic screen names used by the
models onto these variants.
"""
import math

import numpy as np

from . import textures as T

S = T.S
_canvas, _grid_lines, _circle, _fill_circle = T._canvas, T._grid_lines, T._circle, T._fill_circle
_rect, _text_lines, _header, _line = T._rect, T._text_lines, T._header, T._line


def _arr(c, k=1.0):
    return np.array(c, np.float32) * k


def _gauge(img, cx, cy, r, val, c, warn=0.8):
    _circle(img, cx, cy, r, _arr(c, .5), 3)
    for k in range(11):
        a = math.pi * (1.0 + k / 10 * 1.0)
        _line(img, cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a), c, 1)
    a = math.pi * (1.0 + val)
    _line(img, cx, cy, cx + (r - 6) * math.cos(a), cy + (r - 6) * math.sin(a), (1, .3, .2) if val > warn else (1, 1, 1), 2)


def _hbar(img, x0, y0, x1, h, val, c, bg=.15):
    _rect(img, x0, y0, x1, y0 + h, _arr(c, bg))
    _rect(img, x0, y0, x0 + (x1 - x0) * val, y0 + h, c)


def _plot(img, ys, x0, x1, ybase, amp, c, w=1):
    xs = np.linspace(x0, x1, len(ys)).astype(int)
    for k in range(len(xs) - 1):
        _line(img, xs[k], ybase - ys[k] * amp, xs[k + 1], ybase - ys[k + 1] * amp, c, w)


def _poly(img, pts, c, w=1, close=True):
    for a, b in zip(pts, pts[1:] + ([pts[0]] if close else [])):
        _line(img, a[0], a[1], b[0], b[1], c, w)


def scr_reactor_core(rng):
    img = _canvas((.02, .01, .05)); c = (.5, .6, 1.)
    for r, k in ((100, .25), (78, .4), (56, .6), (34, .8)):
        _circle(img, 128, 132, r, _arr(c, k), 3)
    for i in range(12):
        th = i / 12 * 6.283
        _line(img, 128 + 34 * math.cos(th), 132 + 34 * math.sin(th), 128 + 100 * math.cos(th), 132 + 100 * math.sin(th), _arr(c, .35))
    _fill_circle(img, 128, 132, 22, (.9, .95, 1)); _fill_circle(img, 128, 132, 12, (1, 1, 1))
    _header(img, c); return img


def scr_warp_coils(rng):
    img = _canvas((.03, .0, .05)); c = (1., .4, .9)
    for sx in (60, 196):
        for k in range(8):
            _rect(img, sx - 22, 36 + k * 26, sx + 22, 52 + k * 26, _arr(c, rng.uniform(.3, 1)))
    xs = np.arange(60, 196)
    _plot(img, np.sin(xs / 9.0) * .5, 80, 176, 140, 40, (1, 1, 1), 2)
    _rect(img, 90, 200, 166, 206, _arr(c, .6)); _header(img, c); return img


def scr_star_chart(rng):
    img = _canvas((.0, .01, .04)); c = (.5, .7, 1.)
    for _ in range(90):
        _fill_circle(img, rng.uniform(4, 252), rng.uniform(20, 252), rng.choice([1, 1, 1.5, 2]), _arr((1, .95, .85), rng.uniform(.4, 1)))
    for cx in (60, 130, 200):
        _circle(img, cx, 140 + rng.uniform(-40, 40), 20, _arr(c, .7), 1)
    _grid_lines(img, c, 64, .3); _header(img, c); return img


def scr_nav_course(rng):
    img = _canvas((.01, .03, .04)); c = (.3, 1., .8)
    _grid_lines(img, c, 32, .14)
    pts = [(24, 220), (70, 190), (110, 200), (150, 130), (190, 140), (230, 50)]
    for a, b in zip(pts, pts[1:]):
        _line(img, *a, *b, c, 2)
    for p in pts:
        _circle(img, *p, 6, (1, 1, 1), 2)
    _rect(img, 12, 28, 100, 34, _arr(c, .6)); _header(img, c); return img


def scr_body_scan(rng):
    img = _canvas((.0, .04, .05)); c = (.4, 1., 1.)
    _fill_circle(img, 128, 52, 16, _arr(c, .35))
    _rect(img, 108, 72, 148, 150, _arr(c, .3)); _rect(img, 108, 150, 122, 230, _arr(c, .3)); _rect(img, 134, 150, 148, 230, _arr(c, .3))
    _rect(img, 82, 76, 106, 150, _arr(c, .25)); _rect(img, 150, 76, 174, 150, _arr(c, .25))
    for y in range(80, 150, 10):
        _line(img, 112, y, 144, y, c)
    _line(img, 20, 110, 236, 110, (1, 1, .6), 1)
    _text_lines(img, 190, 40, 5, 54, c, rng, 12); _header(img, c); return img


def scr_cargo_manifest(rng):
    img = _canvas((.04, .03, .01)); c = (1., .75, .25)
    for r in range(11):
        y = 26 + r * 20
        _rect(img, 8, y, 8 + rng.uniform(30, 60), y + 8, c)
        _rect(img, 80, y, 80 + rng.uniform(40, 110), y + 8, _arr(c, .6))
        _rect(img, 204, y, 204 + rng.uniform(10, 40), y + 8, (.4, 1, .5) if r % 3 else (1, .3, .2))
    _header(img, c); return img


def scr_security_grid(rng):
    img = _canvas((.01, .02, .01)); c = (.3, 1., .4)
    for r in range(3):
        for k in range(3):
            x0, y0 = 6 + k * 83, 22 + r * 78
            _rect(img, x0, y0, x0 + 78, y0 + 72, _arr(c, rng.uniform(.04, .16)))
            _rect(img, x0, y0, x0 + 78, y0 + 2, c); _rect(img, x0, y0 + 70, x0 + 78, y0 + 72, c)
            _fill_circle(img, x0 + 20 + rng.uniform(0, 40), y0 + 40 + rng.uniform(-10, 14), 4, (1, 1, .8))
            _rect(img, x0 + 4, y0 + 6, x0 + 10, y0 + 12, (1, .2, .2))
    _header(img, c); return img


def scr_comms_spectrum(rng):
    img = _canvas((.01, .02, .05)); c = (.4, .8, 1.)
    _grid_lines(img, c, 32, .12)
    base = np.abs(np.convolve(rng.normal(size=100), np.ones(3) / 3, "same")) * .3
    for _ in range(5):
        p = rng.integers(10, 90); base[p - 2:p + 3] += rng.uniform(.4, 1) * np.array([.3, .7, 1, .7, .3])
    _plot(img, base, 10, 246, 220, 140, c, 2); _header(img, c); return img


def scr_hydro_status(rng):
    img = _canvas((.01, .04, .02)); c = (.4, 1., .4)
    for i in range(8):
        x = 18 + i * 29
        h = rng.uniform(40, 150)
        _rect(img, x, 220 - h, x + 18, 220, _arr(c, .7))
        _fill_circle(img, x + 9, 220 - h, 11, c)
        _rect(img, x + 6, 222, x + 12, 236, (.5, .35, .2))
    _header(img, c); return img


def scr_life_support(rng):
    img = _canvas((.01, .04, .05)); c = (.4, .95, 1.)
    for i, v in enumerate((.82, .45, .6, .3)):
        _gauge(img, 64 + (i % 2) * 128, 100 + (i // 2) * 100, 44, v, c)
    _header(img, c); return img


def scr_power_grid(rng):
    img = _canvas((.04, .03, .0)); c = (1., .8, .2)
    nodes = [(rng.uniform(24, 232), rng.uniform(40, 236)) for _ in range(14)]
    for i in range(14):
        j = (i * 5 + 3) % 14
        _line(img, *nodes[i], *nodes[j], _arr(c, .45))
    for p in nodes:
        _fill_circle(img, *p, 5, c if rng.random() > .2 else (1, .25, .2))
    _header(img, c); return img


def scr_damage_control(rng):
    img = _canvas((.04, .01, .01)); c = (1., .5, .3)
    hull = [(20, 130), (70, 90), (190, 90), (236, 130), (190, 170), (70, 170)]
    _poly(img, hull, c, 2)
    for k in range(5):
        x0 = 50 + k * 30
        _rect(img, x0, 105, x0 + 24, 155, _arr((1, .2, .15) if k in (1, 3) else (.2, .8, .3), .5))
    _line(img, 20, 130, 236, 130, _arr(c, .4))
    _text_lines(img, 12, 196, 4, 150, c, rng, 12); _header(img, c); return img


def scr_atmosphere(rng):
    img = _canvas((.01, .03, .04)); c = (.5, .9, 1.)
    for r in range(4):
        for k in range(5):
            v = rng.uniform(.3, 1)
            _rect(img, 10 + k * 48, 26 + r * 56, 52 + k * 48, 74 + r * 56, _arr(c, .12 + .5 * v) if v > .45 else (.8, .2, .2))
    _header(img, c); return img


def scr_deck_map(rng):
    img = _canvas((.01, .03, .05)); c = (.3, .8, 1.)
    _rect(img, 12, 40, 244, 232, _arr(c, .08)); _poly(img, [(12, 40), (244, 40), (244, 232), (12, 232)], c, 2)
    xs = [12, 80, 150, 244]
    ys = [40, 110, 170, 232]
    for x in xs[1:-1]:
        _line(img, x, 40, x, 232, _arr(c, .7), 2)
    for y in ys[1:-1]:
        _line(img, 12, y, 244, y, _arr(c, .7), 2)
    _fill_circle(img, 90 + rng.uniform(0, 100), 120 + rng.uniform(0, 60), 5, (1, .4, .2)); _header(img, c); return img


def scr_shield_status(rng):
    img = _canvas((.0, .02, .06)); c = (.4, .7, 1.)
    for r in (96, 80, 64):
        _circle(img, 128, 136, r, _arr(c, .8 - (96 - r) / 100), 4)
    _poly(img, [(128, 100), (150, 172), (128, 156), (106, 172)], (1, 1, 1), 2)
    for k in range(6):
        _rect(img, 12 + k * 40, 238, 44 + k * 40, 246, _arr(c, rng.uniform(.4, 1)))
    _header(img, c); return img


def scr_weapons(rng):
    img = _canvas((.05, .01, .01)); c = (1., .3, .2)
    _circle(img, 128, 132, 60, c, 2); _circle(img, 128, 132, 90, _arr(c, .6), 1)
    _line(img, 128, 30, 128, 234, _arr(c, .6)); _line(img, 20, 132, 236, 132, _arr(c, .6))
    _rect(img, 114, 118, 142, 146, (1, 1, 1))
    for k in range(4):
        _hbar(img, 10, 210 + k * 9, 100, 6, rng.uniform(.3, 1), c)
    _header(img, c); return img


def scr_sensor_sweep(rng):
    img = _canvas((.0, .05, .04)); c = (.3, 1., .7)
    for r in (40, 80, 120):
        _circle(img, 128, 236, r, _arr(c, .6), 1)
    for k in range(40):
        a = math.pi * (0.1 + 0.8 * k / 40)
        _line(img, 128, 236, 128 + 130 * math.cos(a), 236 - 130 * math.sin(a), _arr(c, .04 + .5 * (k / 40) ** 3))
    for _ in range(6):
        r = rng.uniform(25, 110); a = rng.uniform(.3, 2.8)
        _fill_circle(img, 128 + r * math.cos(a), 236 - r * math.sin(a), 3, (1, 1, .6))
    _header(img, c); return img


def scr_docking(rng):
    img = _canvas((.01, .03, .03)); c = (.4, 1., .8)
    for s in (30, 60, 90):
        _rect(img, 128 - s, 132 - s, 128 + s, 132 + s, _arr(c, .08))
        _poly(img, [(128 - s, 132 - s), (128 + s, 132 - s), (128 + s, 132 + s), (128 - s, 132 + s)], _arr(c, .7), 1)
    _line(img, 128, 30, 128, 234, c); _line(img, 20, 132, 236, 132, c)
    _fill_circle(img, 128 + rng.uniform(-14, 14), 132 + rng.uniform(-14, 14), 6, (1, .5, .2))
    _text_lines(img, 12, 22, 2, 70, c, rng); _header(img, c); return img


def scr_engine_temp(rng):
    img = _canvas((.04, .01, .0)); c = (1., .5, .15)
    for k in range(10):
        h = rng.uniform(30, 170)
        col = (1, .2, .1) if h > 130 else (1, .65, .15) if h > 80 else (.3, .8, .4)
        _rect(img, 12 + k * 24, 232 - h, 30 + k * 24, 232, col)
    _line(img, 10, 100, 246, 100, (1, .2, .1)); _header(img, c); return img


def scr_coolant_flow(rng):
    img = _canvas((.0, .03, .05)); c = (.3, .85, 1.)
    for y in (60, 120, 180):
        _rect(img, 20, y, 236, y + 14, _arr(c, .15))
        for x in range(24, 230, 28):
            _poly(img, [(x, y + 2), (x + 14, y + 7), (x, y + 12)], c, 1, False)
    for x in (70, 160):
        _rect(img, x, 40, x + 14, 200, _arr(c, .15))
    _fill_circle(img, 70, 120, 14, (.2, .6, 1)); _header(img, c); return img


def scr_fuel_status(rng):
    img = _canvas((.02, .03, .0)); c = (.8, 1., .3)
    for k in range(4):
        x0 = 20 + k * 58
        _rect(img, x0, 40, x0 + 40, 220, _arr(c, .12)); _poly(img, [(x0, 40), (x0 + 40, 40), (x0 + 40, 220), (x0, 220)], c, 1)
        v = rng.uniform(.2, 1.0)
        _rect(img, x0 + 3, 220 - 176 * v, x0 + 37, 218, c if v > .35 else (1, .3, .2))
    _header(img, c); return img


def scr_crew_roster(rng):
    img = _canvas((.02, .03, .05)); c = (.6, .85, 1.)
    for r in range(8):
        y = 26 + r * 28
        _fill_circle(img, 22, y + 10, 9, _arr(c, .5))
        _rect(img, 40, y + 2, 40 + rng.uniform(50, 120), y + 8, c)
        _rect(img, 40, y + 14, 40 + rng.uniform(30, 90), y + 18, _arr(c, .5))
        _fill_circle(img, 230, y + 10, 5, (.3, 1, .4) if rng.random() > .2 else (1, .6, .2))
    _header(img, c); return img


def scr_schedule(rng):
    img = _canvas((.02, .03, .04)); c = (.7, .9, 1.)
    for r in range(8):
        for k in range(5):
            if rng.random() > .3:
                _rect(img, 12 + k * 48, 24 + r * 28, 56 + k * 48, 46 + r * 28, _arr(c, rng.uniform(.15, .6)))
    _header(img, c); return img


def scr_ecg_multi(rng):
    img = _canvas((.0, .04, .02)); c = (.3, 1., .5)
    for r in range(4):
        y = 50 + r * 52
        xs = np.arange(0, 100)
        per = 20 + r * 3
        sig = np.where((xs % per) < 3, 1.0, 0.0) * np.sin((xs % per) / 3 * math.pi) - np.where(((xs - 4) % per) < 2, .3, 0) + np.sin(xs / 3.0) * .03
        _plot(img, sig, 10, 246, y, 24, c if r != 2 else (1, .4, .3))
    _header(img, c); return img


def scr_dna(rng):
    img = _canvas((.02, .0, .05)); c = (.8, .5, 1.)
    ys = np.arange(24, 244)
    for k, y in enumerate(ys):
        x1 = 128 + 55 * math.sin(y / 14.0)
        x2 = 128 - 55 * math.sin(y / 14.0)
        _fill_circle(img, x1, y, 2.2, c); _fill_circle(img, x2, y, 2.2, (.4, .8, 1))
        if k % 9 == 0:
            _line(img, x1, y, x2, y, _arr(c, .5))
    _header(img, c); return img


def scr_lissajous(rng):
    img = _canvas((.0, .03, .0)); c = (.4, 1., .4)
    _grid_lines(img, c, 32, .15)
    t = np.linspace(0, 6.283, 400)
    a, b = rng.integers(1, 4), rng.integers(2, 5)
    xs = 128 + 90 * np.sin(a * t + .5); ys = 140 + 80 * np.sin(b * t)
    for k in range(len(t) - 1):
        _line(img, xs[k], ys[k], xs[k + 1], ys[k + 1], c, 1)
    _header(img, c); return img


def scr_waterfall(rng):
    img = _canvas((.0, .0, .04)); c = (.5, .8, 1.)
    for r in range(20):
        row = np.abs(np.convolve(rng.normal(size=64), np.ones(3) / 3, "same"))
        for k, v in enumerate(row):
            img[22 + r * 11:32 + r * 11, k * 4:k * 4 + 4] = _arr((v * .4, v * .7 + .05, min(1, v + .2)))
    _header(img, c); return img


def scr_planet_survey(rng):
    img = _canvas((.0, .02, .04)); c = (.4, .9, .6)
    _fill_circle(img, 128, 132, 84, (.05, .15, .12))
    for k in range(-4, 5):
        _line(img, 128 - 84 * math.cos(k / 5), 132 + k * 16, 128 + 84 * math.cos(k / 5), 132 + k * 16, _arr(c, .35))
        _circle(img, 128, 132, 84 - abs(k) * 6, _arr(c, .2))
    _circle(img, 128, 132, 84, c, 2)
    _fill_circle(img, 150, 110, 5, (1, .4, .2)); _header(img, c); return img


def scr_asteroids(rng):
    img = _canvas((.0, .0, .03)); c = (.8, .8, .9)
    for _ in range(14):
        x, y, r = rng.uniform(20, 236), rng.uniform(34, 240), rng.uniform(6, 22)
        pts = [(x + r * math.cos(a) * rng.uniform(.7, 1.1), y + r * math.sin(a) * rng.uniform(.7, 1.1)) for a in np.linspace(0, 6.28, 8, endpoint=False)]
        _poly(img, pts, _arr(c, rng.uniform(.4, 1)), 1)
    _poly(img, [(118, 130), (128, 108), (138, 130)], (.3, 1, .5), 2); _header(img, (.5, .6, 1.)); return img


def scr_orbits(rng):
    img = _canvas((.0, .01, .04)); c = (.5, .8, 1.)
    _fill_circle(img, 128, 132, 10, (1, .85, .4))
    for k, r in enumerate((26, 44, 66, 90, 116)):
        _circle(img, 128, 132, r, _arr(c, .45), 1)
        a = rng.uniform(0, 6.28)
        _fill_circle(img, 128 + r * math.cos(a), 132 + r * math.sin(a), 3 + k * .4, c)
    _header(img, c); return img


def scr_inventory_grid(rng):
    img = _canvas((.03, .03, .02)); c = (.9, .9, .5)
    for r in range(6):
        for k in range(8):
            x0, y0 = 10 + k * 30, 26 + r * 36
            _poly(img, [(x0, y0), (x0 + 26, y0), (x0 + 26, y0 + 32), (x0, y0 + 32)], _arr(c, .45), 1)
            if rng.random() > .35:
                _rect(img, x0 + 4, y0 + 6, x0 + 22, y0 + 26, _arr(c, rng.uniform(.2, .7)))
    _header(img, c); return img


def scr_floor_indicator(rng):
    img = _canvas((.02, .02, .03)); c = (1., .7, .2)
    _rect(img, 70, 40, 186, 216, (0, 0, 0))
    _text_lines(img, 90, 70, 1, 70, c, rng, 12)
    _poly(img, [(128, 60), (160, 100), (96, 100)], c, 2)
    _rect(img, 100, 130, 156, 190, _arr(c, .85)); _rect(img, 112, 142, 144, 150, (0, 0, 0)); _rect(img, 112, 160, 144, 168, (0, 0, 0))
    _header(img, c); return img


def scr_airlock_cycle(rng):
    img = _canvas((.05, .03, .0)); c = (1., .75, .2)
    _hbar(img, 20, 100, 236, 30, .62, c)
    for k in range(4):
        _fill_circle(img, 50 + k * 52, 170, 14, (.3, 1, .4) if k < 2 else (1, .3, .2) if k == 2 else _arr(c, .3))
    _rect(img, 20, 210, 130, 216, c); _header(img, c); return img


def scr_assay(rng):
    img = _canvas((.02, .02, .04)); c = (.8, .6, 1.)
    _grid_lines(img, c, 32, .1)
    xs = np.linspace(0, 1, 200); y = np.zeros(200)
    for _ in range(5):
        p = rng.uniform(.1, .9); y += rng.uniform(.3, 1) * np.exp(-((xs - p) / .02) ** 2)
    _plot(img, y, 10, 246, 224, 150, c, 2); _header(img, c); return img


def scr_thermal(rng):
    img = _canvas((.0, .0, .05))
    yy, xx = np.mgrid[0:S, 0:S]
    v = np.zeros((S, S), np.float32)
    for _ in range(5):
        cx, cy, r = rng.uniform(30, 226), rng.uniform(50, 226), rng.uniform(25, 60)
        v += np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    v = np.clip(v, 0, 1)
    img[:] = np.stack([np.clip(v * 2, 0, 1), np.clip(v * 2 - .6, 0, 1), np.clip(.4 - v + v * v * .1, 0, 1)], 2) * .85
    _header(img, (1., .6, .3)); return img


def scr_radiation(rng):
    img = _canvas((.04, .04, .0)); c = (1., .9, .2)
    _fill_circle(img, 128, 110, 40, _arr(c, .2))
    for k in range(3):
        a = k * 2.094
        pts = [(128, 110), (128 + 40 * math.cos(a), 110 + 40 * math.sin(a)), (128 + 40 * math.cos(a + 1.05), 110 + 40 * math.sin(a + 1.05))]
        _poly(img, pts, c, 1)
        _fill_circle(img, 128, 110, 6, c)
    for k in range(20):
        h = rng.uniform(4, 40) * (1 + k / 20)
        _rect(img, 14 + k * 11, 236 - h, 22 + k * 11, 236, c)
    _header(img, c); return img


def scr_uplink(rng):
    img = _canvas((.0, .02, .05)); c = (.5, .85, 1.)
    _poly(img, [(128, 150), (80, 100), (176, 100)], c, 2)
    _circle(img, 128, 96, 50, _arr(c, .5), 2)
    for r in (26, 38, 52):
        _circle(img, 128, 36, r, _arr(c, .5), 1)
    _hbar(img, 20, 210, 236, 12, .74, c); _header(img, c); return img


def scr_terminal(rng):
    img = _canvas((.0, .03, .0)); c = (.3, 1., .3)
    for r in range(16):
        w = rng.choice([0, 0, 30, 90, 150, 200])
        if w:
            _rect(img, 10, 24 + r * 14, 10 + w * rng.uniform(.6, 1), 31 + r * 14, _arr(c, .8))
    _rect(img, 10, 240, 20, 250, c); _header(img, c); return img


def scr_radar_sector(rng):
    img = _canvas((.01, .04, .03)); c = (.3, 1., .5)
    for r in (40, 80, 120):
        for a in np.linspace(math.pi * 1.15, math.pi * 1.85, 40):
            _fill_circle(img, 128 + r * math.cos(a), 240 + r * math.sin(a), 1, _arr(c, .6))
    for a in (1.15, 1.5, 1.85):
        _line(img, 128, 240, 128 + 125 * math.cos(math.pi * a), 240 + 125 * math.sin(math.pi * a), _arr(c, .6))
    for _ in range(5):
        r = rng.uniform(20, 115); a = rng.uniform(math.pi * 1.2, math.pi * 1.8)
        _fill_circle(img, 128 + r * math.cos(a), 240 + r * math.sin(a), 3, (1, 1, .6))
    _header(img, c); return img


def scr_graph_lines(rng):
    img = _canvas((.02, .02, .04)); c = (1., .75, .3)
    _grid_lines(img, c, 32, .12)
    for k, col in enumerate((c, (.4, .9, 1.), (.5, 1., .5))):
        ys = np.cumsum(rng.normal(size=40)) * .06
        _plot(img, ys - ys.min(), 10, 246, 230 - k * 8, 100, col, 2)
    _header(img, c); return img


def scr_log_list(rng):
    img = _canvas((.01, .02, .04)); c = (.6, .85, 1.)
    for r in range(17):
        y = 24 + r * 13
        _rect(img, 8, y, 38, y + 6, _arr(c, .5))
        _rect(img, 46, y, 46 + rng.uniform(40, 190), y + 6, _arr(c, .85 if r % 5 else 1.0) if r % 7 else (1, .4, .3))
    _header(img, c); return img


NEW_SCREENS = {
    "reactor_core": scr_reactor_core, "warp_coils": scr_warp_coils, "star_chart": scr_star_chart,
    "nav_course": scr_nav_course, "body_scan": scr_body_scan, "cargo_manifest": scr_cargo_manifest,
    "security_grid": scr_security_grid, "comms_spectrum": scr_comms_spectrum, "hydro_status": scr_hydro_status,
    "life_support": scr_life_support, "power_grid": scr_power_grid, "damage_control": scr_damage_control,
    "atmosphere": scr_atmosphere, "deck_map": scr_deck_map, "shield_status": scr_shield_status,
    "weapons": scr_weapons, "sensor_sweep": scr_sensor_sweep, "docking": scr_docking,
    "engine_temp": scr_engine_temp, "coolant_flow": scr_coolant_flow, "fuel_status": scr_fuel_status,
    "crew_roster": scr_crew_roster, "schedule": scr_schedule, "ecg_multi": scr_ecg_multi, "dna": scr_dna,
    "lissajous": scr_lissajous, "waterfall": scr_waterfall, "planet_survey": scr_planet_survey,
    "asteroids": scr_asteroids, "orbits": scr_orbits, "inventory_grid": scr_inventory_grid,
    "floor_indicator": scr_floor_indicator, "airlock_cycle": scr_airlock_cycle, "assay": scr_assay,
    "thermal": scr_thermal, "radiation": scr_radiation, "uplink": scr_uplink, "terminal": scr_terminal,
    "radar_sector": scr_radar_sector, "graph_lines": scr_graph_lines, "log_list": scr_log_list,
}
