import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

navbar_insta_pattern = r'<a href=\"https://www\.instagram\.com/[^\"]+\" target=\"_blank\" rel=\"noopener\" class=\"nav-social\" aria-label=\"Instagram\">'
navbar_insta_replace = '<a href=\"https://www.instagram.com/realdelila?igsh=MXRybHloNXlvdGY2Nw==\" target=\"_blank\" rel=\"noopener\" class=\"nav-social\" aria-label=\"Instagram\">'

navbar_tg_pattern = r'<a href=\"#telegram-placeholder\" target=\"_blank\" rel=\"noopener\" class=\"nav-social\" aria-label=\"Telegram\">'
navbar_tg_replace = '<a href=\"https://t.me/Goddessdelila\" target=\"_blank\" rel=\"noopener\" class=\"nav-social\" aria-label=\"Telegram\">'

footer_socials_pattern = r'<div class=\"footer-socials\">.*?</div>'
footer_socials_replace = '''<div class=\"footer-socials\">
        <a href=\"https://linktr.ee/Fingoddessdelila\" target=\"_blank\" rel=\"noopener\">Linktree</a>
        <a href=\"https://fansly.com/queen_delila/posts\" target=\"_blank\" rel=\"noopener\">Fansly</a>
        <a href=\"https://throne.com/goddess_delila\" target=\"_blank\" rel=\"noopener\">Throne</a>
        <a href=\"https://www.instagram.com/realdelila?igsh=MXRybHloNXlvdGY2Nw==\" target=\"_blank\" rel=\"noopener\">Instagram</a>
        <a href=\"https://x.com/onTheFloor4D?t=G6OQuRqxacyJcYz1mPgnAg&s=09\" target=\"_blank\" rel=\"noopener\">X (Twitter)</a>
        <a href=\"https://www.snapchat.com/@goddessdelila?share_id=OcYJYYbYtxg&locale=en-US\" target=\"_blank\" rel=\"noopener\">Snapchat</a>
        <a href=\"https://whatsapp.com/channel/0029VbCAX733gvWXa1D86C2Z\" target=\"_blank\" rel=\"noopener\">WhatsApp Comm</a>
        <a href=\"https://t.me/+Jb6YXyabZN9lZmQ0\" target=\"_blank\" rel=\"noopener\">Telegram Comm</a>
        <a href=\"https://t.me/Goddessdelila\" target=\"_blank\" rel=\"noopener\">Telegram Private</a>
        <button class=\"nav-social theme-toggle\" id=\"themeToggle\" aria-label=\"Toggle Theme\" style=\"background:none; border:none; cursor:pointer;\" title=\"Switch Theme\">
          <svg width=\"18\" height=\"18\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\">
            <circle cx=\"12\" cy=\"12\" r=\"5\"></circle>
            <line x1=\"12\" y1=\"1\" x2=\"12\" y2=\"3\"></line>
            <line x1=\"12\" y1=\"21\" x2=\"12\" y2=\"23\"></line>
            <line x1=\"4.22\" y1=\"4.22\" x2=\"5.64\" y2=\"5.64\"></line>
            <line x1=\"18.36\" y1=\"18.36\" x2=\"19.78\" y2=\"19.78\"></line>
            <line x1=\"1\" y1=\"12\" x2=\"3\" y2=\"12\"></line>
            <line x1=\"21\" y1=\"12\" x2=\"23\" y2=\"12\"></line>
            <line x1=\"4.22\" y1=\"19.78\" x2=\"5.64\" y2=\"18.36\"></line>
            <line x1=\"18.36\" y1=\"5.64\" x2=\"19.78\" y2=\"4.22\"></line>
          </svg>
        </button>
      </div>'''

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update navbar
    content = re.sub(navbar_insta_pattern, navbar_insta_replace, content)
    content = re.sub(navbar_tg_pattern, navbar_tg_replace, content)
    
    # Update footer
    content = re.sub(footer_socials_pattern, footer_socials_replace, content, flags=re.DOTALL)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated links in HTML files.')
