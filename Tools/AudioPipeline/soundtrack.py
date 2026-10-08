"""The game's music, cut from the client's soundtrack (source/zenith_theme_master.ogg, generated with Suno).

Run `python3 soundtrack.py [path/to/master.wav|ogg]` to rebuild the four music cues. The tempo drifts a little
(about 114-118 BPM), so loop lengths were measured, not computed: each loop starts on a beat and ends where the
onset pattern best matches its start (cross-correlation of onset envelopes), so the groove carries across the
seam. Each cue is level-matched to the cue it replaced so every call-site volume in the game keeps working:

  music_title     intro section (0.79-33.464 s), seamless loop   menu, arrival, showroom bed, Zenith Studio
  music_drive     main groove (47.711-80.744 s), seamless loop   test drive (under the motor and road noise)
  sting_complete  re-entry hit after the breakdown (102.56 s)   "PRUEBAS COMPLETADAS"
  music_finale    climax and natural ending (102.56-158.82 s)   awards finale and end screen

synth.py no longer writes these four files.
"""
import os, re, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

from synth import OUT, SR, write

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, 'source', 'zenith_theme_master.ogg')

# name: (start s, end s, crossfade s for loops or None, target integrated loudness LUFS, fade-out s)
CUES = {
    'Music/music_title': (0.79, 33.464, 2.0, -19.1, 0.0),
    'Music/music_drive': (47.711, 80.744, 1.5, -17.5, 0.0),
    'Music/sting_complete': (102.56, 107.06, None, -18.4, 1.5),
    'Music/music_finale': (102.56, 158.82, None, -18.7, 0.4),
}


def load(path):
    """Decode any audio file with ffmpeg to float stereo at SR."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp = f.name
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', tmp],
                   check=True)
    sr, x = wavfile.read(tmp)
    os.unlink(tmp)
    assert sr == SR
    return x.astype(np.float64)


def lufs(x):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        wavfile.write(f.name, SR, np.clip(x, -1, 1).astype(np.float32))
        tmp = f.name
    r = subprocess.run(['ffmpeg', '-nostats', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True)
    os.unlink(tmp)
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)
    return float(m[-1])


def loop_equal_power(x, xf):
    """Seamless loop: the xf seconds after the loop end are blended (equal power) into the loop start."""
    n = int(xf * SR)
    body, tail = x[:-n], x[-n:]
    t = np.linspace(0, np.pi / 2, n)[:, None]
    head = body[:n] * np.sin(t) + tail * np.cos(t)
    return np.concatenate([head, body[n:]])


def cut(x, start, end, xf, fade_out):
    a = int(round(start * SR))
    b = int(round((end + (xf or 0)) * SR))
    y = x[a:b].copy()
    if xf:
        y = loop_equal_power(y, xf)
    else:
        k = int(0.01 * SR)                       # 10 ms de-click at the cut
        y[:k] *= np.linspace(0, 1, k)[:, None]
        if fade_out > 0:
            k = int(fade_out * SR)
            y[-k:] *= (np.cos(np.linspace(0, np.pi / 2, k)) ** 2)[:, None]
    return y


def build(master=MASTER):
    x = load(master)
    for name, (start, end, xf, target, fade) in CUES.items():
        y = cut(x, start, end, xf, fade)
        gain = 10 ** ((target - lufs(y)) / 20)
        y = y * gain
        peak = np.abs(y).max()
        p = write(name, y, quality=5)
        print(f'{name}: {len(y) / SR:.2f} s, gain {20 * np.log10(gain):+.1f} dB, peak {20 * np.log10(peak):.1f} dBFS, '
              f'{os.path.getsize(p) // 1024} KB')


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else MASTER)
