from PIL import Image, ImageFilter, ImageEnhance
import os, glob, numpy as np

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frames = sorted(glob.glob(os.path.join(root, "ref", "frame-*.jpg")))
arrs = [np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) for p in frames]
med = np.median(np.stack(arrs, axis=0), axis=0).astype(np.uint8)
im = Image.fromarray(med, "RGB")
im = ImageEnhance.Color(im).enhance(1.08)
im = ImageEnhance.Contrast(im).enhance(1.04)
im = ImageEnhance.Sharpness(im).enhance(1.1)
big = im.resize((1920, 1195), Image.Resampling.LANCZOS)
big = big.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
dest = os.path.join(root, "assets", "pond-garden.jpg")
os.makedirs(os.path.dirname(dest), exist_ok=True)
big.save(dest, "JPEG", quality=92, optimize=True)
print("wrote", dest, big.size)
