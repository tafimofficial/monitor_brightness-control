from PIL import Image
import shutil
import os

# Source path (artifact)
# Note: I'll need to fill this in dynamically or use the path I know.
# I will use the path returned by generate_image in the previous step.
# C:/Users/Tafim/.gemini/antigravity/brain/db4e95dc-e531-4134-914f-ce0b5fbd68de/app_icon_1768902286162.png
source_path = r"C:/Users/Tafim/.gemini/antigravity/brain/db4e95dc-e531-4134-914f-ce0b5fbd68de/app_icon_1768902286162.png"
dest_dir = r"d:\monitorian\assets"
dest_png = os.path.join(dest_dir, "icon.png")
dest_ico = os.path.join(dest_dir, "icon.ico")

# Ensure assets dir exists
os.makedirs(dest_dir, exist_ok=True)

# Copy/Overwrite png
shutil.copy(source_path, dest_png)
print(f"Copied PNG to {dest_png}")

# Convert to ICO
img = Image.open(dest_png)
# Windows 10/11 likes specific sizes.
icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img.save(dest_ico, format='ICO', sizes=icon_sizes)
print(f"Created ICO at {dest_ico}")
