"""
convert_md_to_html.py
Converte un file Markdown in HTML standalone con stile integrato.
Uso: python convert_md_to_html.py input.md [output.html]
"""

import sys
import re
import os


def md_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_table = False
    in_blockquote = False
    in_ul = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return ''
        out = ['<div class="table-wrap"><table>']
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip('|').split('|')]
            if i == 0:
                out.append('<thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead><tbody>')
            elif i == 1 and all(re.match(r'^[-: ]+$', c) for c in cells):
                continue
            else:
                out.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
        out.append('</tbody></table></div>')
        table_rows = []
        return '\n'.join(out)

    def flush_ul():
        return '</ul>' if in_ul else ''

    def inline(text):
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        # Code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
        # Strikethrough
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if re.match(r'^---+$', line.strip()):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_table:
                html_lines.append(flush_table())
                in_table = False
            html_lines.append('<hr>')
            i += 1
            continue

        # Table
        if '|' in line and line.strip().startswith('|'):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            in_table = True
            table_rows.append(line)
            i += 1
            continue
        else:
            if in_table:
                html_lines.append(flush_table())
                in_table = False

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            level = len(m.group(1))
            text = inline(m.group(2))
            html_lines.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Blockquote
        if line.startswith('>'):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            text = inline(line.lstrip('> ').strip())
            html_lines.append(f'<blockquote>{text}</blockquote>')
            i += 1
            continue

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', line)
        if m:
            if not in_ul:
                html_lines.append('<ul>')
                in_ul = True
            html_lines.append(f'<li>{inline(m.group(1))}</li>')
            i += 1
            continue
        else:
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False

        # Empty line
        if line.strip() == '':
            html_lines.append('')
            i += 1
            continue

        # Paragraph
        html_lines.append(f'<p>{inline(line)}</p>')
        i += 1

    if in_ul:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append(flush_table())

    return '\n'.join(html_lines)


def wrap_in_page(body_html, title='Caso Studio'):
    return f'''<!DOCTYPE html>
<html lang="it" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Work+Sans:wght@300..700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #faf7f2; --surface: #f5f0e8; --border: #d4c9b6;
      --text: #2a2018; --muted: #7a6e5e; --faint: #b8ac9a;
      --primary: #b84c1a; --green: #3d6e3a; --green-bg: #eaf2e9;
      --font-display: 'Playfair Display', Georgia, serif;
      --font-body: 'Work Sans', sans-serif;
    }}
    [data-theme="dark"] {{
      --bg: #1a1510; --surface: #211c15; --border: #3d3428;
      --text: #e8ddd0; --muted: #9a8e7e; --faint: #6a6050;
      --primary: #e06830; --green: #6aac60; --green-bg: #1a2e18;
    }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }}
    body {{ font-family: var(--font-body); font-size: 1rem; color: var(--text); background: var(--bg); line-height: 1.7; padding: 2rem 1rem 4rem; }}
    .page {{ max-width: 760px; margin-inline: auto; }}
    h1 {{ font-family: var(--font-display); font-size: clamp(1.8rem,4vw,3rem); font-weight: 700; margin-bottom: 0.5rem; }}
    h2 {{ font-family: var(--font-display); font-size: clamp(1.3rem,2.5vw,1.9rem); margin-top: 2.5rem; margin-bottom: 0.75rem; color: var(--text); }}
    h3 {{ font-family: var(--font-body); font-size: 1.1rem; font-weight: 700; margin-top: 1.5rem; margin-bottom: 0.5rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }}
    p {{ margin-bottom: 1rem; max-width: 68ch; }}
    ul {{ padding-left: 1.5rem; margin-bottom: 1rem; list-style: disc; }}
    li {{ margin-bottom: 0.4rem; }}
    blockquote {{
      border-left: 3px solid var(--primary); padding: 0.75rem 1.25rem;
      margin: 1.25rem 0; background: var(--surface); border-radius: 0 0.5rem 0.5rem 0;
      color: var(--muted); font-style: italic;
    }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
    .table-wrap {{ overflow-x: auto; margin: 1.5rem 0; border-radius: 0.75rem; border: 1px solid var(--border); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: var(--surface); padding: 0.75rem 1rem; text-align: left; font-size: 0.85rem; font-weight: 700; color: var(--muted); border-bottom: 1px solid var(--border); }}
    td {{ padding: 0.7rem 1rem; font-size: 0.9rem; border-bottom: 1px solid var(--border); }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: var(--surface); padding: 0.1em 0.4em; border-radius: 0.25rem; font-size: 0.9em; }}
    strong {{ font-weight: 700; color: var(--text); }}
    a {{ color: var(--primary); }}
    .nav {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:2.5rem; padding-bottom:1rem; border-bottom:1px solid var(--border); }}
    .nav-title {{ font-family:var(--font-display); font-size:1rem; font-weight:700; color:var(--text); }}
    .toggle {{ cursor:pointer; background:none; border:1px solid var(--border); border-radius:999px; padding:0.3rem 0.75rem; font-size:0.8rem; color:var(--muted); }}
    .toggle:hover {{ color:var(--primary); border-color:var(--primary); }}
  </style>
</head>
<body>
<div class="page">
  <div class="nav">
    <span class="nav-title">Anita Brau — Portfolio</span>
    <button class="toggle" data-theme-toggle>🌙 Dark</button>
  </div>
  {body_html}
</div>
<script>
(function(){{
  const t=document.querySelector('[data-theme-toggle]'),r=document.documentElement;
  let d=matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';
  r.setAttribute('data-theme',d);
  t&&t.addEventListener('click',()=>{{
    d=d==='dark'?'light':'dark';
    r.setAttribute('data-theme',d);
    t.textContent=d==='dark'?'☀️ Light':'🌙 Dark';
  }});
}})();
</script>
</body>
</html>'''


def convert(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"Errore: file '{input_path}' non trovato.")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Titolo dalla prima riga H1
    title_match = re.search(r'^#\s+(.+)', md_text, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(input_path)

    body = md_to_html(md_text)
    full_html = wrap_in_page(body, title)

    if not output_path:
        output_path = os.path.splitext(input_path)[0] + '.html'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"✅ Convertito: {input_path} → {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python convert_md_to_html.py input.md [output.html]")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    convert(input_file, output_file)
