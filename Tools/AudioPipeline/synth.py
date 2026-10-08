"""Procedural sound design for The Tester. Run `python3 synth.py` to regenerate every SFX and ambience clip as OGG.

Nothing here samples or imitates commercial music; all sounds are synthesised from scratch. The music cues come
from the client's soundtrack (see soundtrack.py); `build(with_music=True)` writes the synthesised fallback themes.
"""
import os, subprocess, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'Assets', 'TheTesterGame', 'Audio', 'Resources', 'Audio'))
R = np.random.default_rng(1234)


def t_(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return R.standard_normal(int(d * SR)).astype(np.float64)


def pink(d):
    n = int(d * SR)
    X = np.fft.rfft(R.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[1:] /= np.sqrt(f[1:])
    X[0] = 0
    y = np.fft.irfft(X, n)
    return y / (np.abs(y).max() + 1e-9)


def brown(d):
    y = np.cumsum(R.standard_normal(int(d * SR)))
    y = signal.lfilter([1, -1], [1, -0.995], y)
    return y / (np.abs(y).max() + 1e-9)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return signal.lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'low')
    return signal.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def env_ad(n, a, d, curve=4.0):
    na = max(1, int(a * SR))
    e = np.ones(n)
    e[:na] = np.linspace(0, 1, na)
    rest = n - na
    if rest > 0:
        e[na:] = np.exp(-curve * np.linspace(0, 1, rest) * (rest / SR) / max(d, 1e-4))
    return e


def norm(x, peak=0.9):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def reverb_ir(d=2.2, damp=3.2, stereo=True, seed=5):
    r = np.random.default_rng(seed)
    n = int(d * SR)
    tt = np.arange(n) / SR
    e = np.exp(-damp * tt)
    chans = []
    for c in range(2 if stereo else 1):
        x = r.standard_normal(n) * e
        x = lp(x, 6000) * 0.6 + lp(x, 2500) * 0.4
        x[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        chans.append(x / np.sqrt((x ** 2).sum()))
    return np.stack(chans, axis=1)


def reverb(x, wet=0.25, d=2.2, damp=3.2, seed=5):
    ir = reverb_ir(d, damp, seed=seed)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    out = np.zeros((x.shape[0] + ir.shape[0] - 1, 2))
    for c in range(2):
        out[:, c] = signal.fftconvolve(x[:, c], ir[:, c])
    dry = np.zeros_like(out)
    dry[:x.shape[0]] = x
    return dry * (1 - wet) + out * wet * 3.0


def loopify(x, xf=1.0):
    """Make a seamless loop by cross-fading the tail into the head."""
    n = int(xf * SR)
    head, tail = x[:n], x[-n:]
    w = np.linspace(0, 1, n)
    if x.ndim == 2:
        w = w[:, None]
    mixed = tail * (1 - w) + head * w
    return np.concatenate([mixed, x[n:-n]])


def write(name, x, quality=4, mono=False):
    path = os.path.join(OUT, name + '.ogg')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = np.asarray(x, np.float64)
    if mono and x.ndim == 2:
        x = x.mean(axis=1)
    x = np.clip(x, -1, 1)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wavfile.write(f.name, SR, (x * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f.name, '-c:a', 'libvorbis', '-q:a', str(quality), path], check=True)
        os.unlink(f.name)
    return path


# ============================================================================ instruments
def piano_note(freq, dur=3.0, vel=0.8, bright=1.0):
    tt = t_(dur)
    y = np.zeros_like(tt)
    B = 0.0004
    for k in range(1, 12):
        fk = freq * k * np.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        amp = (1.0 / k ** (1.2 / bright)) * vel
        dec = 0.6 + 2.2 * k / 8
        y += amp * np.sin(2 * np.pi * fk * tt + R.uniform(0, 6.28)) * np.exp(-dec * tt / (1 + 0.6 * (220 / freq)))
    ham = lp(noise(0.02), 3000) * env_ad(int(0.02 * SR), 0.0005, 0.01)
    y[:len(ham)] += ham * 0.05 * vel
    att = int(0.004 * SR)
    y[:att] *= np.linspace(0, 1, att)
    rel = int(0.25 * SR)
    y[-rel:] *= np.linspace(1, 0, rel)
    return y


def pad(freqs, dur, swell=2.0, bright=0.5):
    tt = t_(dur)
    y = np.zeros_like(tt)
    for f in freqs:
        for det in (-0.25, 0.0, 0.3):
            ph = R.uniform(0, 6.28)
            saw = signal.sawtooth(2 * np.pi * (f + det) * tt + ph)
            y += saw * 0.15
    y = lp(y, 900 + 1500 * bright, 2)
    e = np.minimum(1, tt / swell) * np.minimum(1, (dur - tt) / swell)
    return y * e


def pluck(freq, dur=1.2, bright=0.7):
    n = int(dur * SR)
    period = int(SR / freq)
    buf = R.uniform(-1, 1, period)
    buf = lp(buf, 2000 + 6000 * bright, 1)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = 0.5 * (buf[i % period] + buf[(i + 1) % period]) * 0.996
    return out


def marimba(freq, dur=1.2, vel=0.8):
    tt = t_(dur)
    y = np.sin(2 * np.pi * freq * tt) * np.exp(-5 * tt) + 0.3 * np.sin(2 * np.pi * freq * 3.93 * tt) * np.exp(-14 * tt) \
        + 0.12 * np.sin(2 * np.pi * freq * 9.2 * tt) * np.exp(-30 * tt)
    a = int(0.002 * SR)
    y[:a] *= np.linspace(0, 1, a)
    return y * vel


def metal(freqs, decays, dur=2.5, amp=None):
    tt = t_(dur)
    y = np.zeros_like(tt)
    amp = amp or [1.0] * len(freqs)
    for f, d, a in zip(freqs, decays, amp):
        y += a * np.sin(2 * np.pi * f * tt + R.uniform(0, 6.28)) * np.exp(-tt / d)
    click = hp(noise(0.006), 2000) * np.linspace(1, 0, int(0.006 * SR))
    y[:len(click)] += click * 0.4
    return y


def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if x.ndim == 2 and buf.ndim == 1:
        x = x.mean(axis=1)
    if x.ndim == 1 and buf.ndim == 2:
        buf[i:j] += (x[:j - i] * gain)[:, None]
    else:
        buf[i:j] += x[:j - i] * gain


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ============================================================================ ambiences
def amb_showroom(d=32):
    x = lp(pink(d + 2), 1200) * 0.25 + lp(brown(d + 2), 300) * 0.35
    tt = t_(d + 2)
    hum = 0.02 * np.sin(2 * np.pi * 59.5 * tt) + 0.01 * np.sin(2 * np.pi * 119 * tt)
    traffic = lp(brown(d + 2), 180) * (0.6 + 0.4 * np.sin(2 * np.pi * tt / 9.0)) * 0.35
    murmur = bp(noise(d + 2), 300, 1100) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 3.7) * np.sin(2 * np.pi * tt / 5.3)) * 0.04
    y = x + hum + traffic + murmur
    # a few distant soft chimes (elevator / door)
    for at in (6.0, 21.5):
        place(y, marimba(midi(84), 1.5, 0.05) + marimba(midi(79), 1.5, 0.04), at)
    st = reverb(norm(y, 0.5), wet=0.35, d=2.5)
    return loopify(norm(st[:int((d + 2) * SR)], 0.35), 1.5)


def amb_studio(d=32):
    tt = t_(d + 2)
    y = lp(brown(d + 2), 250) * 0.4 + lp(pink(d + 2), 700) * 0.12
    y += 0.015 * np.sin(2 * np.pi * 120 * tt) + 0.006 * np.sin(2 * np.pi * 240 * tt)
    fan = bp(noise(d + 2), 2500, 6000) * 0.008
    y += fan
    st = reverb(norm(y, 0.5), wet=0.3, d=1.6)
    return loopify(norm(st[:int((d + 2) * SR)], 0.28), 1.5)


def amb_city(d=32):
    tt = t_(d + 2)
    traffic = lp(brown(d + 2), 400) * (0.7 + 0.3 * np.sin(2 * np.pi * tt / 6.0)) * 0.6
    wash = bp(pink(d + 2), 200, 2500) * 0.2
    y = traffic + wash
    for at in R.uniform(1, d, 10):  # birds
        n = int(0.18 * SR)
        f0 = R.uniform(2800, 4200)
        tw = np.arange(n) / SR
        chirp = np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * 18 * tw)) * tw) * env_ad(n, 0.01, 0.08)
        place(y, chirp * 0.05, at)
    st = reverb(norm(y, 0.6), wet=0.15, d=1.2)
    return loopify(norm(st[:int((d + 2) * SR)], 0.4), 1.5)


# ============================================================================ sfx
def footstep(seed):
    r = np.random.default_rng(seed)
    n = int(0.22 * SR)
    heel = hp(r.standard_normal(n), 900) * env_ad(n, 0.0005, 0.012)
    body = lp(r.standard_normal(n), 300) * env_ad(n, 0.001, 0.04) * 0.8
    tone = np.sin(2 * np.pi * r.uniform(150, 190) * np.arange(n) / SR) * env_ad(n, 0.001, 0.03) * 0.4
    y = heel * 0.6 + body + tone
    return norm(reverb(norm(y), wet=0.12, d=0.8)[: int(0.5 * SR)], 0.7)


def cloth(seed, d=0.45):
    r = np.random.default_rng(seed)
    n = int(d * SR)
    x = bp(r.standard_normal(n), 900, 5000)
    e = np.convolve(np.abs(r.standard_normal(n)), np.ones(800) / 800, 'same')
    e *= np.sin(np.linspace(0, np.pi, n))
    return norm(x * e, 0.5)


def glint(base=1800, d=1.8, gain=1.0):
    y = metal([base, base * 2.76, base * 5.4, base * 1.5], [0.6, 0.35, 0.18, 0.4], d, [1, 0.5, 0.25, 0.3])
    wh = bp(noise(0.35), 1500, 7000) * np.sin(np.linspace(0, np.pi, int(0.35 * SR))) * 0.15
    out = np.zeros(int(d * SR))
    place(out, wh, 0.0)
    place(out, y * 0.35, 0.12)
    return norm(reverb(out, wet=0.25, d=1.4), 0.6 * gain)


def whoosh(d=0.6, lo=300, hi=4000):
    n = int(d * SR)
    x = noise(d)
    tt = np.linspace(0, 1, n)
    y = np.zeros(n)
    # sweeping band
    for k in range(6):
        seg = slice(k * n // 6, (k + 1) * n // 6)
        f = lo + (hi - lo) * (k / 6)
        y[seg] = bp(x, f * 0.7, min(f * 1.4, 18000))[seg]
    return norm(y * np.sin(np.pi * tt) ** 1.5, 0.45)


def tick():
    y = marimba(midi(91), 0.4, 0.6) + marimba(midi(98), 0.4, 0.3)
    return norm(reverb(y, wet=0.2, d=0.9), 0.5)


def found():
    out = np.zeros(int(2.0 * SR))
    place(out, marimba(midi(79), 1.4, 0.7), 0.0)
    place(out, marimba(midi(86), 1.4, 0.6), 0.11)
    place(out, piano_note(midi(91), 1.6, 0.3), 0.11)
    return norm(reverb(out, wet=0.3, d=1.8), 0.55)


def wrong():
    n = int(0.35 * SR)
    tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * 140 * tt) * np.exp(-14 * tt) + lp(noise(0.35), 600) * np.exp(-30 * tt) * 0.3
    return norm(reverb(y, wet=0.15, d=0.6), 0.45)


def scribble(d=0.9):
    n = int(d * SR)
    x = bp(noise(d), 2000, 7000)
    e = np.zeros(n)
    k = 0
    while k < n:
        L = int(R.uniform(0.04, 0.12) * SR)
        e[k:k + L] = np.sin(np.linspace(0, np.pi, len(e[k:k + L]))) * R.uniform(0.4, 1.0)
        k += L + int(R.uniform(0.0, 0.05) * SR)
    return norm(x * e, 0.3)


def car_door(close=True):
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    thunk = lp(noise(0.9), 220) * np.exp(-18 * tt) * 1.2 + np.sin(2 * np.pi * 70 * tt) * np.exp(-12 * tt)
    latch = hp(noise(0.9), 1500) * np.exp(-90 * tt) * 0.5
    y = thunk + latch if close else (latch * 0.8 + lp(noise(0.9), 500) * np.exp(-25 * tt) * 0.4)
    return norm(reverb(y, wet=0.15, d=1.0), 0.7)


def ev_motor(d=4.0):
    tt = t_(d)
    f0 = 210.0
    y = 0.5 * np.sin(2 * np.pi * f0 * tt) + 0.25 * np.sin(2 * np.pi * f0 * 2 * tt) + 0.12 * np.sin(2 * np.pi * f0 * 3.02 * tt) \
        + 0.08 * np.sin(2 * np.pi * 1450 * tt) + 0.05 * bp(noise(d), 300, 1200)
    y *= 1 + 0.03 * np.sin(2 * np.pi * 7 * tt)
    return norm(y, 0.45)


def road_noise(d=4.0):
    y = lp(brown(d), 500) * 0.7 + bp(pink(d), 300, 2500) * 0.3
    return loopify(norm(y, 0.5), 0.5)


def horn():
    tt = t_(0.32)
    y = (np.sign(np.sin(2 * np.pi * 420 * tt)) * 0.5 + np.sin(2 * np.pi * 525 * tt)) * env_ad(len(tt), 0.01, 0.25)
    return norm(lp(y, 2500), 0.4)


def indicator():
    out = np.zeros(int(0.5 * SR))
    for at, f in ((0.0, 2400), (0.25, 1900)):
        n = int(0.02 * SR)
        place(out, hp(noise(0.02), f) * np.linspace(1, 0, n), at)
    return norm(out, 0.35)


def ui_tick():
    return norm(marimba(midi(96), 0.25, 0.4), 0.3)


def ui_confirm():
    out = np.zeros(int(0.8 * SR))
    place(out, marimba(midi(84), 0.7, 0.5), 0)
    place(out, marimba(midi(91), 0.7, 0.4), 0.07)
    return norm(reverb(out, wet=0.2, d=0.8), 0.4)


def trophy(kind):
    if kind == 'lux':     # black ceramic/glass: higher, glassy
        y = metal([1320, 2410, 3780, 5210], [0.9, 0.5, 0.3, 0.2], 2.4, [1, 0.6, 0.4, 0.25])
    else:                  # bronze: lower, heavier
        y = metal([520, 1190, 2050, 3120], [1.4, 0.8, 0.5, 0.3], 2.8, [1, 0.7, 0.4, 0.2])
    thump = lp(noise(0.2), 300) * env_ad(int(0.2 * SR), 0.001, 0.03)
    out = np.zeros(len(y))
    place(out, thump, 0)
    out += y * 0.5
    return norm(reverb(out, wet=0.25, d=1.6), 0.6)


def applause(d=5.0, people=7):
    out = np.zeros(int(d * SR))
    for p in range(people):
        rate = R.uniform(3.2, 4.6)
        start = R.uniform(0.0, 0.6)
        stop = d - R.uniform(0.6, 1.6)
        tcur = start
        f = R.uniform(900, 1800)
        while tcur < stop:
            n = int(0.03 * SR)
            clap = bp(noise(0.03), f * 0.6, f * 2.2) * env_ad(n, 0.0005, 0.008)
            g = min(1, (tcur - start) / 0.5) * min(1, (stop - tcur) / 0.8)
            place(out, clap * g * R.uniform(0.6, 1.0), tcur)
            tcur += 1 / rate + R.uniform(-0.03, 0.03)
    return norm(reverb(out, wet=0.35, d=1.8), 0.4)


def stache():
    n = int(0.25 * SR)
    x = bp(noise(0.25), 3000, 9000) * np.sin(np.linspace(0, np.pi, n)) ** 2
    return norm(x, 0.25)


def sigh():
    n = int(1.4 * SR)
    tt = np.linspace(0, 1, n)
    x = bp(noise(1.4), 400, 1800) * (np.sin(np.pi * tt) ** 2) * (1 - 0.5 * tt)
    x = lp(x, 1500)
    return norm(x, 0.18)


def big_magnifier():
    out = np.zeros(int(2.2 * SR))
    place(out, whoosh(0.5, 150, 1500) * 0.8, 0)
    tt = t_(0.5)
    thud = np.sin(2 * np.pi * (90 - 40 * tt) * tt) * np.exp(-8 * tt)
    place(out, thud * 0.6, 0.35)
    place(out, glint(1100, 1.6, 0.8), 0.4)
    return norm(out, 0.6)


def tl_beep():
    return norm(np.sin(2 * np.pi * 880 * t_(0.12)) * env_ad(int(0.12 * SR), 0.005, 0.06), 0.2)


# ============================================================================ music
def music_title():
    bpm = 62
    beat = 60 / bpm
    d = 32 * beat
    out = np.zeros((int((d + 4) * SR), 2))
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [43, 50, 55, 58], [45, 52, 57, 61]]   # Dm  Bb  Gm  A
    for i, ch in enumerate(chords * 2):
        place(out, pad([midi(m) for m in ch], 4 * beat + 1.5, swell=1.6, bright=0.3)[:, None] * np.array([0.9, 1.0]) * 0.22, i * 4 * beat)
    melody = [(0, 69, 1.5), (2, 72, 1), (3, 74, 2), (6, 72, 1), (7, 70, 1), (8, 70, 2.5), (11, 69, 1), (12, 67, 3),
              (16, 69, 1.5), (18, 72, 1), (19, 77, 2), (22, 76, 1), (23, 74, 1), (24, 73, 3), (28, 69, 3)]
    for b, m, L in melody:
        place(out, piano_note(midi(m), L * beat + 2.0, 0.45, 0.9), b * beat)
    for b in range(0, 32, 2):
        place(out, piano_note(midi(chords[(b // 4) % 4][0] - 12), 2.5, 0.25, 0.6), b * beat)
    st = reverb(out, wet=0.38, d=3.2, damp=1.8)
    return loopify(norm(st[:int((d + 2) * SR)], 0.5), 2.0)


def music_drive():
    bpm = 104
    beat = 60 / bpm
    d = 32 * beat
    out = np.zeros((int((d + 3) * SR), 2))
    prog = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64]]   # D  Bm  G  A
    for bar in range(8):
        ch = prog[bar % 4]
        place(out, pad([midi(m - 12) for m in ch], 4 * beat + 0.8, swell=0.6, bright=0.45)[:, None] * 0.16, bar * 4 * beat)
        for s in range(8):
            m = ch[s % 3] + (12 if s in (3, 7) else 0)
            pan = np.array([0.7, 1.0]) if s % 2 else np.array([1.0, 0.7])
            place(out, marimba(midi(m), 0.6, 0.35)[:, None] * pan, (bar * 4 + s * 0.5) * beat)
        place(out, piano_note(midi(ch[0] - 24), 2.0, 0.5, 0.5), bar * 4 * beat)
        for s in range(4):  # soft pulse
            n = int(0.05 * SR)
            k = lp(noise(0.05), 120) * env_ad(n, 0.001, 0.02)
            place(out, k * 0.5, (bar * 4 + s) * beat)
    st = reverb(out, wet=0.22, d=1.8)
    return loopify(norm(st[:int((d + 1.5) * SR)], 0.45), 1.0)


def music_finale():
    bpm = 66
    beat = 60 / bpm
    d = 24 * beat
    out = np.zeros((int((d + 5) * SR), 2))
    prog = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59], [48, 55, 60, 64], [53, 57, 60, 65]]
    for i, ch in enumerate(prog):
        place(out, pad([midi(m) for m in ch], 4 * beat + 2, swell=1.8, bright=0.4)[:, None] * 0.2, i * 4 * beat)
        place(out, piano_note(midi(ch[0] - 12), 3.5, 0.35, 0.6), i * 4 * beat)
    mel = [(0, 76, 2), (2, 79, 2), (4, 77, 1.5), (6, 76, 1), (7, 74, 1), (8, 72, 3), (12, 74, 1), (13, 76, 1), (14, 79, 2),
           (16, 84, 3), (20, 81, 2), (22, 79, 2)]
    for b, m, L in mel:
        place(out, piano_note(midi(m), L * beat + 2.5, 0.4, 1.0), b * beat)
    st = reverb(out, wet=0.4, d=3.5, damp=1.6)
    st = st[:int((d + 5) * SR)]
    fade = int(3 * SR)
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return norm(st, 0.5)


def sting_complete():
    out = np.zeros((int(4.0 * SR), 2))
    for m, at in ((62, 0), (66, 0.06), (69, 0.12), (74, 0.18)):
        place(out, piano_note(midi(m), 3.5, 0.4, 0.9), at)
    place(out, pad([midi(50), midi(57), midi(62)], 3.8, swell=0.8, bright=0.4)[:, None] * 0.25, 0)
    return norm(reverb(out, wet=0.35, d=2.6)[: int(4.0 * SR)], 0.5)


def build(with_music=False):
    clips = {
        'Ambience/amb_showroom': (amb_showroom, 3, True), 'Ambience/amb_studio': (amb_studio, 3, True),
        'Ambience/amb_city': (amb_city, 3, True),
        'Sfx/footstep_1': (lambda: footstep(1), 4, True), 'Sfx/footstep_2': (lambda: footstep(2), 4, True),
        'Sfx/footstep_3': (lambda: footstep(3), 4, True), 'Sfx/footstep_4': (lambda: footstep(4), 4, True),
        'Sfx/cloth_1': (lambda: cloth(5), 4, True), 'Sfx/cloth_2': (lambda: cloth(6, 0.6), 4, True),
        'Sfx/magnifier_up': (glint, 4, True), 'Sfx/magnifier_down': (lambda: whoosh(0.4, 200, 2500), 4, True),
        'Sfx/inspect_tick': (tick, 4, True), 'Sfx/inspect_found': (found, 4, True), 'Sfx/wrong': (wrong, 4, True),
        'Sfx/scribble': (scribble, 4, True), 'Sfx/door_open': (lambda: car_door(False), 4, True),
        'Sfx/door_close': (lambda: car_door(True), 4, True), 'Sfx/ev_motor': (ev_motor, 4, True),
        'Sfx/road_noise': (road_noise, 4, True), 'Sfx/horn': (horn, 4, True), 'Sfx/indicator': (indicator, 4, True),
        'Sfx/ui_tick': (ui_tick, 4, True), 'Sfx/ui_confirm': (ui_confirm, 4, True),
        'Sfx/trophy_lux': (lambda: trophy('lux'), 4, True), 'Sfx/trophy_effie': (lambda: trophy('effie'), 4, True),
        'Sfx/applause': (applause, 4, True), 'Sfx/stache': (stache, 4, True), 'Sfx/sigh': (sigh, 4, True),
        'Sfx/big_magnifier': (big_magnifier, 4, True), 'Sfx/whoosh': (whoosh, 4, True), 'Sfx/traffic_beep': (tl_beep, 4, True),
        # Music/* now comes from the client's soundtrack (soundtrack.py). The synthesised themes below are kept
        # as an offline fallback: build(with_music=True) writes them instead.
    }
    if with_music:
        clips.update({
            'Music/music_title': (music_title, 4, False), 'Music/music_drive': (music_drive, 4, False),
            'Music/music_finale': (music_finale, 4, False), 'Music/sting_complete': (sting_complete, 4, False),
        })
    for name, (fn, q, mono) in clips.items():
        x = fn()
        p = write(name, x, q, mono)
        print(name, round(len(x) / SR, 2), 's', os.path.getsize(p) // 1024, 'KB')


if __name__ == '__main__':
    build()
