import re

with open("css/styles.css", "r", encoding="utf-8") as f:
    content = f.read()

css_patch = """
.gallery-grid {
  column-count: 1;
  column-gap: 4px;
}
@media (min-width: 600px) {
  .gallery-grid {
    column-count: 2;
  }
}
@media (min-width: 900px) {
  .gallery-grid {
    column-count: 3;
  }
}
@media (min-width: 1200px) {
  .gallery-grid {
    column-count: 4;
  }
}
"""

content = re.sub(r'\.gallery-grid\s*\{.*?\bgap:\s*4px;\s*\}', css_patch.strip(), content, flags=re.DOTALL)

content = re.sub(r'\.gallery-tile\s*\{.*?cursor:\s*pointer;\s*\}', """.gallery-tile {
  position: relative;
  overflow: hidden;
  background: var(--gunmetal);
  cursor: pointer;
  break-inside: avoid;
  margin-bottom: 4px;
  aspect-ratio: auto !important;
}""", content, flags=re.DOTALL)

content = re.sub(r'\.gallery-tile:nth-child\(3n\+2\)\s*\{.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'\.gallery-tile:nth-child\(5n\+3\)\s*\{.*?\}', '', content, flags=re.DOTALL)

# Modify placeholder to remove absolute positioning
content = re.sub(r'\.gallery-tile-placeholder\s*\{.*?color:\s*var\(--white-faint\);\s*\}', """.gallery-tile-placeholder {
  background: linear-gradient(135deg, var(--gunmetal) 0%, var(--black-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: var(--white-faint);
}""", content, flags=re.DOTALL)


with open("css/styles.css", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated styles.css with masonry layout.")
