"""Brand marks supplied by the client, cleaned into crisp alpha masks.

Sources (Assets/References):
  ref_hyundai_logo.jpg        black emblem + HYUNDAI wordmark on white (431x350)
  ref_zenith_logo_cream.png   cream "Z." circle mark on transparent (1890x1890)

The sources are small/compressed, so each mark is upsampled, re-thresholded with a
narrow smoothstep (removes JPEG ringing, keeps an anti-aliased edge) and cached.
Everything else in the pipeline asks for a mark at a pixel height and colour.
"""
import numpy as np
from PIL import Image, ImageFilter

from common import ref, smoothstep

_CACHE = {}

# Ink bounding boxes inside ref_hyundai_logo.jpg (rows/cols, inclusive), measured once.
_HY_EMBLEM = (85, 215, 88, 342)
_HY_WORDMARK = (240, 287, 51, 379)
_UPSAMPLE = 8


def _clean_mask(gray_ink, up):
    """gray_ink: float 0..1 (1 = ink). Returns an upsampled, re-edged float mask."""
    h, w = gray_ink.shape
    im = Image.fromarray((gray_ink * 255).astype(np.uint8), 'L')
    im = im.resize((w * up, h * up), Image.BICUBIC).filter(ImageFilter.GaussianBlur(up * 0.6))
    a = np.asarray(im).astype(np.float32) / 255.0
    # Narrow ramp around the 50% iso-line: crisp but still anti-aliased after downsampling.
    return smoothstep(0.38, 0.62, a)


def _hyundai_masks():
    if 'hy' in _CACHE:
        return _CACHE['hy']
    g = np.asarray(Image.open(ref('ref_hyundai_logo.jpg')).convert('L')).astype(np.float32) / 255.0
    ink = 1.0 - g
    out = {}
    pad = 3
    for key, (r0, r1, c0, c1) in (('emblem', _HY_EMBLEM), ('wordmark', _HY_WORDMARK)):
        crop = ink[r0 - pad:r1 + 1 + pad, c0 - pad:c1 + 1 + pad]
        out[key] = _clean_mask(crop, _UPSAMPLE)
    # Stacked lockup exactly as supplied (emblem over wordmark).
    r0, r1 = _HY_EMBLEM[0] - pad, _HY_WORDMARK[1] + 1 + pad
    c0, c1 = min(_HY_EMBLEM[2], _HY_WORDMARK[2]) - pad, max(_HY_EMBLEM[3], _HY_WORDMARK[3]) + 1 + pad
    out['stacked'] = _clean_mask(ink[r0:r1, c0:c1], _UPSAMPLE)
    _CACHE['hy'] = out
    return out


def _zenith_mask():
    if 'z' in _CACHE:
        return _CACHE['z']
    a = np.asarray(Image.open(ref('ref_zenith_logo_cream.png')).convert('RGBA'))[..., 3].astype(np.float32) / 255.0
    ys, xs = np.where(a > 0.08)
    pad = 12
    crop = a[ys.min() - pad:ys.max() + 1 + pad, xs.min() - pad:xs.max() + 1 + pad]
    m = smoothstep(0.3, 0.7, crop)
    _CACHE['z'] = m
    return m


def _mask(kind):
    if kind == 'zenith':
        return _zenith_mask()
    return _hyundai_masks()[kind]


def mark(kind, height, color, alpha=1.0):
    """Render a mark as an RGBA PIL image `height` pixels tall.

    kind: 'emblem' | 'wordmark' | 'stacked' (Hyundai) or 'zenith' (Z. circle mark).
    color: (r, g, b). Width follows the mark's aspect ratio.
    """
    m = _mask(kind)
    h, w = m.shape
    th = max(1, int(round(height)))
    tw = max(1, int(round(w * th / h)))
    mi = Image.fromarray((m * 255).astype(np.uint8), 'L').resize((tw, th), Image.LANCZOS)
    a = np.asarray(mi).astype(np.float32) / 255.0 * alpha
    out = np.zeros((th, tw, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = color
    out[..., 3] = a * 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def aspect(kind):
    m = _mask(kind)
    return m.shape[1] / m.shape[0]


def lockup_h(height, color, gap=0.42, word_scale=0.36, alpha=1.0):
    """Horizontal dealer-sign lockup: emblem on the left, wordmark to its right.

    height: emblem height in px. The wordmark cap height is height*word_scale.
    """
    em = mark('emblem', height, color, alpha)
    wm = mark('wordmark', height * word_scale, color, alpha)
    gx = int(round(height * gap))
    W = em.width + gx + wm.width
    out = Image.new('RGBA', (W, em.height), (0, 0, 0, 0))
    out.alpha_composite(em, (0, 0))
    out.alpha_composite(wm, (em.width + gx, (em.height - wm.height) // 2))
    return out


def paste_center(dst, img, cx, cy):
    """Alpha-composite img onto PIL RGBA dst centred at (cx, cy) (pixel coords)."""
    x = int(round(cx - img.width / 2))
    y = int(round(cy - img.height / 2))
    dst.alpha_composite(img, (max(0, x), max(0, y)),
                        (max(0, -x), max(0, -y)))
    return dst


if __name__ == '__main__':
    import os
    from common import SCRATCH
    bg = Image.new('RGBA', (1400, 900), (24, 40, 56, 255))
    paste_center(bg, mark('stacked', 300, (236, 232, 222)), 350, 250)
    paste_center(bg, lockup_h(140, (236, 232, 222)), 950, 250)
    paste_center(bg, mark('zenith', 360, (255, 255, 235)), 350, 650)
    paste_center(bg, mark('emblem', 40, (210, 210, 214)), 950, 650)
    p = os.path.join(SCRATCH, 'logos_test.png')
    bg.save(p)
    print(p)
