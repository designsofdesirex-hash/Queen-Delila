with open('gallery.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('href="https://fansly.com/queen_delila/posts"', 'href="https://linktr.ee/Fingoddessdelila"')
content = content.replace('Full content on Fansly →', 'Explore my world →')

with open('gallery.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Hover text updated successfully.")
