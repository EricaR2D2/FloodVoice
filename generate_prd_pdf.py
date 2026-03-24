"""
Generate HTML from FloodVoice PRD Markdown file
Creates a print-ready HTML that can be converted to PDF via browser
"""

import os
import re

def simple_markdown_to_html(md_content):
    """Simple markdown to HTML converter"""

    # Convert headers
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', md_content, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

    # Convert horizontal rules
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)

    # Convert lists (simple version)
    lines = html.split('\n')
    in_list = False
    result = []

    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item = line.strip()[2:]
            result.append(f'<li>{item}</li>')
        elif line.strip().startswith(tuple(f'{i}. ' for i in range(10))):
            if not in_list:
                result.append('<ol>')
                in_list = 'ol'
            item = re.sub(r'^\d+\.\s+', '', line.strip())
            result.append(f'<li>{item}</li>')
        else:
            if in_list:
                if in_list == 'ol':
                    result.append('</ol>')
                else:
                    result.append('</ul>')
                in_list = False
            if line.strip():
                result.append(f'<p>{line}</p>')
            else:
                result.append('<br>')

    if in_list:
        if in_list == 'ol':
            result.append('</ol>')
        else:
            result.append('</ul>')

    html = '\n'.join(result)
    return html

def markdown_to_html(md_file):
    """Convert markdown to HTML with styling"""

    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = simple_markdown_to_html(md_content)
    
    # Add professional styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>FloodVoice - Product Requirements Document</title>
        <style>
            @page {{
                size: letter;
                margin: 1in;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #666;
                }}
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 100%;
                margin: 0;
                padding: 0;
            }}
            
            h1 {{
                color: #1e3a8a;
                border-bottom: 3px solid #3b82f6;
                padding-bottom: 10px;
                margin-top: 30px;
                font-size: 28pt;
                page-break-before: avoid;
            }}
            
            h2 {{
                color: #1e40af;
                border-bottom: 2px solid #60a5fa;
                padding-bottom: 8px;
                margin-top: 25px;
                font-size: 20pt;
                page-break-after: avoid;
            }}
            
            h3 {{
                color: #1e40af;
                margin-top: 20px;
                font-size: 16pt;
                page-break-after: avoid;
            }}
            
            h4 {{
                color: #2563eb;
                margin-top: 15px;
                font-size: 13pt;
            }}
            
            p {{
                margin: 10px 0;
                text-align: justify;
            }}
            
            ul, ol {{
                margin: 10px 0;
                padding-left: 30px;
            }}
            
            li {{
                margin: 5px 0;
            }}
            
            strong {{
                color: #1e40af;
                font-weight: 600;
            }}
            
            code {{
                background-color: #f3f4f6;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            
            pre {{
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #3b82f6;
                overflow-x: auto;
                page-break-inside: avoid;
            }}
            
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
                page-break-inside: avoid;
            }}
            
            th, td {{
                border: 1px solid #d1d5db;
                padding: 10px;
                text-align: left;
            }}
            
            th {{
                background-color: #3b82f6;
                color: white;
                font-weight: 600;
            }}
            
            tr:nth-child(even) {{
                background-color: #f9fafb;
            }}
            
            hr {{
                border: none;
                border-top: 2px solid #e5e7eb;
                margin: 30px 0;
            }}
            
            blockquote {{
                border-left: 4px solid #3b82f6;
                padding-left: 20px;
                margin: 20px 0;
                color: #4b5563;
                font-style: italic;
                background-color: #f9fafb;
                padding: 15px 20px;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
            
            /* Header styling */
            .document-header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 20px;
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                border-radius: 8px;
            }}
            
            .document-header h1 {{
                color: white;
                border: none;
                margin: 0;
                font-size: 32pt;
            }}
            
            .document-subtitle {{
                font-size: 14pt;
                margin-top: 10px;
                opacity: 0.9;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return styled_html

def save_html(html_content, output_file):
    """Save HTML to file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ HTML saved: {output_file}")

def open_in_browser(html_file):
    """Open HTML file in default browser for printing to PDF"""
    import webbrowser
    file_path = os.path.abspath(html_file)
    webbrowser.open(f'file:///{file_path}')
    print(f"✅ Opening in browser: {file_path}")
    print("\n📌 To save as PDF:")
    print("   1. Press Ctrl+P (or Cmd+P on Mac)")
    print("   2. Select 'Save as PDF' or 'Microsoft Print to PDF'")
    print("   3. Click 'Save'")
    return True

def main():
    """Main function to generate PDF"""
    
    # File paths
    md_file = "FLOODVOICE_PRD.md"
    html_file = "FLOODVOICE_PRD.html"
    pdf_file = "FLOODVOICE_PRD.pdf"
    
    # Check if markdown file exists
    if not os.path.exists(md_file):
        print(f"❌ Error: {md_file} not found")
        return
    
    print("🌊 FloodVoice PRD PDF Generator")
    print("=" * 50)
    
    # Step 1: Convert Markdown to HTML
    print("\n📄 Converting Markdown to HTML...")
    html_content = markdown_to_html(md_file)
    save_html(html_content, html_file)
    
    # Step 2: Open HTML in browser for PDF printing
    print("\n📑 Opening HTML for PDF conversion...")
    open_in_browser(html_file)

    print("\n✨ Success! HTML file ready for PDF conversion")
    print(f"📍 HTML Location: {os.path.abspath(html_file)}")
    print(f"📍 Save PDF as: {os.path.abspath(pdf_file)}")

if __name__ == "__main__":
    main()

