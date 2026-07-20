import os

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
old_text = '<!-- PHOTO PLACEHOLDER -->'
new_text = '<img src=\"assets/mon-mot-cle-footer-1-01-2.jpg\" alt=\"Queen Delila\" class=\"footer-image\" style=\"width: 100%; height: 100%; object-fit: cover; border-radius: inherit;\">'

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
