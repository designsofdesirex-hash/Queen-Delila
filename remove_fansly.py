import os
import re
import glob

html_files = glob.glob('*.html')

nav_pattern = r'\s*<a href="https://fansly\.com/queen_delila/posts"[^>]*class="nav-social"[^>]*>.*?</a>'
footer_pattern = r'\s*<a href="https://fansly\.com/queen_delila/posts"[^>]*>Fansly</a>'
feature_pattern = r'<a href="https://fansly\.com/queen_delila/posts"([^>]*)>View on Fansly →</a>'

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove Nav Fansly
    content = re.sub(nav_pattern, '', content, flags=re.DOTALL)
    
    # Remove Footer Fansly
    content = re.sub(footer_pattern, '', content)
    
    # Replace feature links
    content = re.sub(feature_pattern, r'<a href="https://linktr.ee/Fingoddessdelila"\1>Explore Links →</a>', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fansly links removed successfully.")
