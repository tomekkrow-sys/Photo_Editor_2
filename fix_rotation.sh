#!/bin/bash
set -e

echo "=== Photo Editor 2 - Naprawa obrotu ==="
echo ""

# Backupy z timestampem
TS=$(date +%s)
cp core/pipeline.py "core/pipeline.py.bak.$TS"
cp ui/canvas.py "ui/canvas.py.bak.$TS"
cp ui/main_window.py "ui/main_window.py.bak.$TS"

python3 << 'PYEOF'
import re

# ─── 1. NAPRAWA GŁÓWNA: core/pipeline.py (brak bytesPerLine w QImage) ───
with open('core/pipeline.py', 'r') as f:
    content = f.read()

changes = 0

# RGBA8888: dodaj 4. argument = szerokość * 4 bajty
old = "QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)"
new = "QImage(data, pil_img.width, pil_img.height, pil_img.width * 4, QImage.Format.Format_RGBA8888)"
if old in content:
    content = content.replace(old, new)
    changes += 1
    print("  [FIX] core/pipeline.py: dodano bytesPerLine dla RGBA8888")

# RGB888: dodaj 4. argument = szerokość * 3 bajty
old = "QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)"
new = "QImage(data, pil_img.width, pil_img.height, pil_img.width * 3, QImage.Format.Format_RGB888)"
if old in content:
    content = content.replace(old, new)
    changes += 1
    print("  [FIX] core/pipeline.py: dodano bytesPerLine dla RGB888")

with open('core/pipeline.py', 'w') as f:
    f.write(content)

# ─── 2. NAPRAWA CANVAS: ui/canvas.py (wymuszanie repaint po zmianie pixmapy) ───
with open('ui/canvas.py', 'r') as f:
    lines = f.readlines()

# Szukamy miejsc gdzie _pixmap jest przypisywane i nie ma potem update()
i = 0
while i < len(lines):
    line = lines[i]
    if 'self._pixmap' in line and '=' in line and 'update()' not in line:
        # Sprawdź czy w następnych 3 liniach jest już update() lub repaint()
        has_update = False
        for j in range(i+1, min(i+4, len(lines))):
            if 'update()' in lines[j] or 'repaint()' in lines[j]:
                has_update = True
                break
        if not has_update:
            indent = len(line) - len(line.lstrip())
            lines.insert(i+1, ' ' * indent + "self.update()\n")
            print(f"  [FIX] ui/canvas.py: linia {i+1} - dodano self.update() po zmianie _pixmap")
    i += 1

with open('ui/canvas.py', 'w') as f:
    f.writelines(lines)

# ─── 3. NAPRAWA MAIN WINDOW: ui/main_window.py (odświeżenie canvas po obrocie) ───
with open('ui/main_window.py', 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'Obrocono:' in line and 'showMessage' in line:
        # Sprawdź czy następna linia już aktualizuje canvas
        if i+1 < len(lines) and 'canvas' not in lines[i+1]:
            indent = len(line) - len(line.lstrip())
            lines.insert(i+1, ' ' * indent + "if hasattr(self, 'canvas'):\n")
            lines.insert(i+2, ' ' * indent + "    self.canvas.update()\n")
            print("  [FIX] ui/main_window.py: dodano odświeżenie canvas po obrocie")
        break

with open('ui/main_window.py', 'w') as f:
    f.writelines(lines)

print("")
print("=== BACKUPY ===")
print("  core/pipeline.py.bak." + str(TS))
print("  ui/canvas.py.bak." + str(TS))
print("  ui/main_window.py.bak." + str(TS))
PYEOF

echo ""
echo "=== DIFF core/pipeline.py ==="
diff "core/pipeline.py.bak.$TS" core/pipeline.py || true

echo ""
echo "=== GOTOWE ==="
echo "Uruchom aplikację i sprawdź obrót."
echo "Jeśli nadal są problemy, przywróć backupy: cp core/pipeline.py.bak.$TS core/pipeline.py"
