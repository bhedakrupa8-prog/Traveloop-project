import re

def simple_markdown_to_html(text):
    """
    Very basic markdown-like formatting for notes.
    Supports:
    **bold** -> <strong>bold</strong>
    *italic* -> <em>italic</em>
    - list item -> <li>list item</li>
    """
    if not text:
        return ""
        
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Simple lines to paragraphs
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if stripped:
                html_lines.append(f'{stripped}<br>')
                
    if in_list:
        html_lines.append('</ul>')
        
    return ''.join(html_lines)
