import re

html_content = """
        <div class="service-card reveal" style="display:flex; flex-direction:column; justify-content:center;">
          <h3 class="service-card-title" style="margin-bottom:20px; font-size:1.5rem; text-transform:none; letter-spacing:normal;">Packs</h3>
          <div style="display:flex; flex-direction:column; gap:16px; width:100%; font-size:1.1rem; color:var(--white-faint);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Standard</span><span style="font-weight:600; color:var(--white);">20 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>VIP</span><span style="font-weight:600; color:var(--white);">40 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Premium</span><span style="font-weight:600; color:var(--white);">60 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>PremiumPlus</span><span style="font-weight:600; color:var(--white);">80 €</span>
            </div>
          </div>
        </div>

        <div class="service-card reveal" style="display:flex; flex-direction:column; justify-content:center;">
          <h3 class="service-card-title" style="margin-bottom:20px; font-size:1.5rem; text-transform:none; letter-spacing:normal;">Groups</h3>
          <div style="display:flex; flex-direction:column; gap:16px; width:100%; font-size:1.1rem; color:var(--white-faint);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>VIP</span><span style="font-weight:600; color:var(--white);">20 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Premium</span><span style="font-weight:600; color:var(--white);">60 €</span>
            </div>
          </div>
        </div>

        <div class="service-card reveal" style="display:flex; flex-direction:column; justify-content:center;">
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:20px; flex-wrap:wrap; gap:8px;">
            <h3 class="service-card-title" style="font-size:1.5rem; text-transform:none; letter-spacing:normal; margin:0;">Personalised</h3>
            <span style="color:var(--red); font-size:0.9rem; font-weight:600;">starting from €€</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:16px; width:100%; font-size:1.1rem; color:var(--white-faint);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Vocals</span><span style="font-weight:600; color:var(--white);">10 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Pictures</span><span style="font-weight:600; color:var(--white);">20 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Videos</span><span style="font-weight:600; color:var(--white);">35 €</span>
            </div>
          </div>
        </div>

        <div class="service-card reveal" style="display:flex; flex-direction:column; justify-content:center;">
          <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:20px; flex-wrap:wrap; gap:8px;">
            <h3 class="service-card-title" style="font-size:1.5rem; text-transform:none; letter-spacing:normal; margin:0;">Sessions</h3>
            <span style="color:var(--red); font-size:0.9rem; font-weight:600;">starting from €€</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:16px; width:100%; font-size:1.1rem; color:var(--white-faint);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Texting</span><span style="font-weight:600; color:var(--white);">10 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Vocal call</span><span style="font-weight:600; color:var(--white);">25 €</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span>Video call</span><span style="font-weight:600; color:var(--white);">40 €</span>
            </div>
          </div>
        </div>
"""

with open("rules.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace everything inside <div class="services-grid"> ... </div>
new_content = re.sub(r'(<div class="services-grid">).*?(      </div>\s*</section>)', r'\g<1>\n' + html_content + r'\n\g<2>', content, flags=re.DOTALL)

with open("rules.html", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Services updated.")
