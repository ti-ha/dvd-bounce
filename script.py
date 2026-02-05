from PIL import Image, ImageOps
import math
import os
import random

FILENAME = "img.png"
EXPORT_FILENAME = "bounce.gif"
SCALE = 0.1

# Feature flag: cycle random colours over the image
COLOUR_CYCLE = True

COLOURS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 128, 0),
    (128, 0, 255),
]


def apply_colour_tint(image, colour):
    """Apply a colour tint that is visible even on black pixels."""
    _, _, _, a = image.split()
    grayscale = image.convert("L")
    tinted = ImageOps.colorize(grayscale, black=colour, white=(255, 255, 255))
    tinted = tinted.convert("RGBA")
    tinted.putalpha(a)
    return tinted

img_path = os.path.join(os.path.dirname(__file__), FILENAME)
original = Image.open(img_path).convert("RGBA")

# Resize image
scale = SCALE
new_size = (int(original.width * scale), int(original.height * scale))
bouncing_img = original.resize(new_size, Image.LANCZOS)
img_w, img_h = bouncing_img.size



vx, vy = 6, 5  # Asymmetric velocities


h_travel = vx * 60
v_travel = vy * 50 

canvas_width = h_travel + img_w
canvas_height = v_travel + img_h


h_period = 2 * h_travel // vx
v_period = 2 * v_travel // vy


def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

loop_frames = lcm(h_period, v_period)

max_frames = loop_frames

x, y = 0.0, 0.0
curr_vx, curr_vy = float(vx), float(vy)

frames = []
current_colour = random.choice(COLOURS)

for frame in range(max_frames):
    frame_img = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    if COLOUR_CYCLE:
        tinted = apply_colour_tint(bouncing_img, current_colour)
        frame_img.paste(tinted, (int(x), int(y)), tinted)
    else:
        frame_img.paste(bouncing_img, (int(x), int(y)), bouncing_img)

    frame_p = frame_img.convert("P", palette=Image.ADAPTIVE, colors=255)

    mask = Image.new("L", frame_img.size, 255)
    alpha = frame_img.split()[3]
    mask.paste(alpha, (0, 0))

    frames.append((frame_p, mask))

    # Update position
    x += curr_vx
    y += curr_vy

    if x <= 0 or x >= h_travel:
        curr_vx = -curr_vx
        x = max(0, min(x, h_travel))
        if COLOUR_CYCLE:
            current_colour = random.choice([c for c in COLOURS if c != current_colour])
    if y <= 0 or y >= v_travel:
        curr_vy = -curr_vy
        y = max(0, min(y, v_travel))
        if COLOUR_CYCLE:
            current_colour = random.choice([c for c in COLOURS if c != current_colour])

output_path = os.path.join(os.path.dirname(__file__), EXPORT_FILENAME)

frame_images = [f[0] for f in frames]
masks = [f[1] for f in frames]

frame_images[0].save(
    output_path,
    save_all=True,
    append_images=frame_images[1:],
    duration=35,
    loop=0,
    transparency=0,
    disposal=2 
)

duration_sec = len(frames) * 35 / 1000
print(f"\nGIF saved!")
print(f"Frames: {len(frames)}")
print(f"Duration: {duration_sec:.1f} seconds")