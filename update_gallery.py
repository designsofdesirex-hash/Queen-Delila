import os
import random
import re

assets_dir = 'Assets'
files = os.listdir(assets_dir)

images = [f for f in files if 'galerie' in f and (f.endswith('.webp') or f.endswith('.jfif') or f.endswith('.jpg'))]
videos = [f for f in files if f.endswith('.mp4') and not f.endswith('.av1.mp4')]

gallery_items = []

for img in images:
    html = f"""
        <div class="gallery-tile" data-category="photo">
          <img src="assets/{img}" alt="Queen Delila Gallery" style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0;">
          <div class="gallery-tile-overlay">
            <a href="https://fansly.com/queen_delila/posts" target="_blank" rel="noopener" class="gallery-tile-caption">Full content on Fansly →</a>
          </div>
        </div>"""
    gallery_items.append(html)

for vid in videos:
    av1_vid = vid.replace('.mp4', '.av1.mp4')
    html = f"""
        <div class="gallery-tile gallery-tile--video" data-category="video">
          <video loop muted playsinline autoplay style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0;">
            <source src="assets/{av1_vid}" type="video/mp4; codecs=av01.0.05M.08">
            <source src="assets/{vid}" type="video/mp4">
          </video>
          <div class="gallery-tile-overlay">
            <a href="https://fansly.com/queen_delila/posts" target="_blank" rel="noopener" class="gallery-tile-caption">Full content on Fansly →</a>
          </div>
        </div>"""
    gallery_items.append(html)

random.shuffle(gallery_items)
gallery_html = '\n'.join(gallery_items)

with open('gallery.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_content = re.sub(r'(<div class="gallery-grid">).*?(</div>\s*<!-- /gallery-grid -->)', r'\g<1>\n' + gallery_html + r'\n\g<2>', content, flags=re.DOTALL)

with open('gallery.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Updated gallery.html with', len(gallery_items), 'items mixed.')
