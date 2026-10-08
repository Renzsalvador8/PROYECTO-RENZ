"""Background keying for the illustrated reference sheets (paper / flat backgrounds)."""
import numpy as np
from scipy import ndimage
from common import *


def estimate_bg(a, box, ring=6):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1, :3]
    border = np.concatenate([sub[:ring].reshape(-1, 3), sub[-ring:].reshape(-1, 3),
                             sub[:, :ring].reshape(-1, 3), sub[:, -ring:].reshape(-1, 3)])
    return np.median(border, axis=0)


def key_region(a, box, bg=None, t_bg=24.0, t_fg=70.0, local_bg=True, decontam=True):
    """Return RGBA float array (crop of box) with background removed.

    Background = pixels close to bg color AND connected to the crop border.
    Edge alpha is derived from colour distance so anti-aliasing survives.
    """
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1, :3].copy()
    if bg is None:
        bg = estimate_bg(a, box)
    if local_bg:
        # smooth local background estimate (handles paper gradients)
        bgimg = np.empty_like(sub)
        for c in range(3):
            bgimg[:, :, c] = bg[c]
        near = np.linalg.norm(sub - bg, axis=2) < t_bg * 1.2
        for c in range(3):
            ch = np.where(near, sub[:, :, c], np.nan)
            # nan-aware blur via normalized convolution
            v = np.nan_to_num(ch)
            w = (~np.isnan(ch)).astype(np.float32)
            vb = ndimage.gaussian_filter(v, 12)
            wb = ndimage.gaussian_filter(w, 12)
            bgimg[:, :, c] = np.where(wb > 1e-3, vb / np.maximum(wb, 1e-3), bg[c])
    else:
        bgimg = np.broadcast_to(bg, sub.shape)
    d = np.linalg.norm(sub - bgimg, axis=2)
    cand = d < t_bg
    lab, n = ndimage.label(cand)
    border_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgmask = np.isin(lab, list(border_labels))
    # alpha: 0 in background core, ramps on edges
    alpha = np.ones(d.shape, np.float32)
    ramp = smoothstep(t_bg * 0.5, t_fg, d)
    edge_zone = ndimage.binary_dilation(~bgmask, iterations=2) & bgmask
    alpha[bgmask] = 0.0
    alpha[edge_zone] = ramp[edge_zone]
    # pixels outside bg but still very close to bg colour right at the boundary: soften
    fg_edge = (~bgmask) & ndimage.binary_dilation(bgmask, iterations=1)
    alpha[fg_edge] = np.maximum(ramp[fg_edge], 0.35)
    rgb = sub
    if decontam:
        aa = np.clip(alpha, 1e-3, 1)[:, :, None]
        rgb = np.where(alpha[:, :, None] < 0.999, (sub - (1 - aa) * bgimg) / aa, sub)
        rgb = np.clip(rgb, 0, 255)
    out = np.dstack([rgb, alpha * 255.0])
    return out


def composite_check(rgba, bgcol=(255, 0, 255)):
    a = rgba[:, :, 3:4] / 255.0
    rgb = rgba[:, :, :3] * a + np.array(bgcol, np.float32) * (1 - a)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), 'RGB')
