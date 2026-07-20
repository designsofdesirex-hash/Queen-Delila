import re

# 1. Update styles.css
with open("css/styles.css", "r", encoding="utf-8") as f:
    css_content = f.read()

# Replace masonry grid with standard grid
css_content = re.sub(
    r'\.gallery-grid\s*\{.*?\bgap:\s*4px;\s*\}',
    '.gallery-grid {\n  display: grid;\n  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));\n  gap: 4px;\n}',
    css_content,
    flags=re.DOTALL
)
css_content = re.sub(r'@media\s*\([^)]+\)\s*\{\s*\.gallery-grid\s*\{\s*column-count:\s*\d+;\s*\}\s*\}', '', css_content)

# Update gallery-tile to have a standard aspect ratio (e.g., 3/4)
css_content = re.sub(
    r'\.gallery-tile\s*\{.*?aspect-ratio:\s*auto\s*!important;\s*\}',
    '.gallery-tile {\n  position: relative;\n  overflow: hidden;\n  background: var(--gunmetal);\n  cursor: pointer;\n  aspect-ratio: 3 / 4;\n}',
    css_content,
    flags=re.DOTALL
)

with open("css/styles.css", "w", encoding="utf-8") as f:
    f.write(css_content)

# 2. Update gallery.html
with open("gallery.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace inline styles for img and video to ensure they cover the frame
html_content = html_content.replace('style="width:100%; height:auto; display:block; border-radius:inherit;"', 'style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; border-radius:inherit;"')

with open("gallery.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Standardized grid applied successfully.")
