import glob

html_files = glob.glob('*.html')

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace motto
    content = content.replace('I have puppets all over the world', 'Your eternal addiction')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Motto updated successfully.")
