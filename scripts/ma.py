#!/usr/bin/env python3
"""
Article Management Script (ma.py)
Generates and updates HTML pages for the chugakujukenpasssite using OpenAI API.
Processes article.md files to create modular HTML content with categories, tags, and references.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Install with: pip install openai")
    sys.exit(1)


class ArticleManager:
    """Manages article generation and HTML page updates using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ArticleManager with OpenAI API key."""
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.script_dir = Path(__file__).parent
        self.root_dir = self.script_dir.parent
        self.templates_dir = self.script_dir / 'templates'
        
    def read_article(self, article_path: Path) -> str:
        """Read the article markdown content."""
        if not article_path.exists():
            raise FileNotFoundError(f"Article not found: {article_path}")
        
        with open(article_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_metadata(self, content: str) -> Dict:
        """Extract metadata from markdown frontmatter."""
        metadata = {
            'title': '',
            'description': '',
            'category': '',
            'tags': [],
            'references': []
        }
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'title':
                            metadata['title'] = value.strip('"\'')
                        elif key == 'description':
                            metadata['description'] = value.strip('"\'')
                        elif key == 'category':
                            metadata['category'] = value.strip('"\'')
                        elif key == 'tags':
                            # Parse tags as list
                            tags_str = value.strip('[]')
                            metadata['tags'] = [t.strip().strip('"\'') for t in tags_str.split(',')]
                        elif key == 'references':
                            # Parse references as list
                            refs_str = value.strip('[]')
                            metadata['references'] = [r.strip().strip('"\'') for r in refs_str.split(',')]
        
        return metadata
    
    def generate_html_content(self, markdown_content: str, metadata: Dict) -> str:
        """Generate HTML content from markdown using OpenAI API."""
        prompt = f"""Convert the following markdown article into well-structured HTML content for a Japanese middle school entrance exam preparation website.

The article metadata:
- Title: {metadata.get('title', 'Untitled')}
- Category: {metadata.get('category', 'General')}
- Tags: {', '.join(metadata.get('tags', []))}

Requirements:
1. Generate clean HTML content (without <!DOCTYPE>, <html>, <head>, or <body> tags)
2. Use semantic HTML5 tags (article, section, h2, h3, etc.)
3. Apply existing CSS classes from the site: article-content, highlight-box, warning-box
4. Create proper Japanese typography and formatting
5. Include navigation breadcrumbs if appropriate
6. Add internal links to related pages if references are provided: {', '.join(metadata.get('references', []))}
7. Use tables with inline styles matching the existing site style (border-collapse:collapse, padding:0.5rem, border:1px solid #ddd)
8. Follow the structure pattern from existing pages (header, nav, main, article, footer)

Markdown content:
{markdown_content}

Generate the complete HTML page following the existing site structure."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert web developer specializing in educational content sites. You create clean, semantic HTML with proper Japanese language support."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def generate_categories_and_tags(self, markdown_content: str) -> Dict:
        """Use OpenAI to intelligently generate categories and tags from content."""
        prompt = f"""Analyze the following article content and suggest appropriate categories and tags for a Japanese middle school entrance exam preparation website.

Existing categories on the site:
- 算数 (Math)
- 国語 (Japanese)
- 理科 (Science)
- 社会 (Social Studies)
- コツ・勉強法 (Study Tips)

Article content:
{markdown_content[:1000]}...

Provide your response as JSON with the following structure:
{{
    "category": "suggested category (use one of the existing categories or suggest a new one in Japanese)",
    "tags": ["tag1", "tag2", "tag3"],
    "related_pages": ["page1.html", "page2.html"]
}}

Suggest 3-5 relevant tags in Japanese."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in educational content organization for Japanese middle school entrance exams."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Warning: Could not generate categories/tags: {str(e)}")
            return {"category": "General", "tags": [], "related_pages": []}
    
    def create_full_html_page(self, content: str, metadata: Dict, output_filename: str) -> str:
        """Create a complete HTML page with header, navigation, and footer."""
        title = metadata.get('title', 'Untitled')
        description = metadata.get('description', '')
        category = metadata.get('category', 'General')
        
        # Determine active nav link based on category
        nav_links = {
            'index.html': 'ホーム',
            'math.html': '算数',
            'japanese.html': '国語',
            'science.html': '理科',
            'social.html': '社会',
            'tips.html': 'コツ・勉強法'
        }
        
        category_to_file = {
            '算数': 'math.html',
            '国語': 'japanese.html',
            '理科': 'science.html',
            '社会': 'social.html',
            'コツ・勉強法': 'tips.html'
        }
        
        active_page = category_to_file.get(category, output_filename)
        
        # Build navigation HTML
        nav_html = []
        for file, label in nav_links.items():
            active_class = ' active' if file == active_page else ''
            nav_html.append(f'                    <li><a href="{file}" class="nav-link{active_class}">{label}</a></li>')
        
        # Build breadcrumb
        breadcrumb_html = f'''    <nav class="breadcrumb">
        <div class="container">
            <ol class="breadcrumb-list">
                <li><a href="index.html" class="breadcrumb-link">ホーム</a></li>
                <li class="breadcrumb-separator">></li>
                <li>{title}</li>
            </ol>
        </div>
    </nav>'''
        
        full_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 中学受験パス</title>
    <meta name="description" content="{description}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="logo">中学受験パス</h1>
            <nav class="nav">
                <ul class="nav-list">
{chr(10).join(nav_html)}
                </ul>
            </nav>
        </div>
    </header>

{breadcrumb_html}

    <main class="main">
        <div class="container">
{content}
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p class="footer-text">&copy; 2024 中学受験パス. 頑張る受験生を応援します。</p>
        </div>
    </footer>
</body>
</html>'''
        
        return full_html
    
    def process_article(self, article_path: Path, output_filename: Optional[str] = None, update_mode: bool = False) -> None:
        """Process an article markdown file and generate/update HTML page."""
        print(f"Processing article: {article_path}")
        
        # Read article content
        content = self.read_article(article_path)
        
        # Extract metadata
        metadata = self.extract_metadata(content)
        print(f"Metadata: {metadata}")
        
        # If no metadata provided, generate categories and tags
        if not metadata.get('category') or not metadata.get('tags'):
            print("Generating categories and tags from content...")
            generated = self.generate_categories_and_tags(content)
            if not metadata.get('category'):
                metadata['category'] = generated.get('category', 'General')
            if not metadata.get('tags'):
                metadata['tags'] = generated.get('tags', [])
            if not metadata.get('references'):
                metadata['references'] = generated.get('related_pages', [])
            print(f"Generated: {generated}")
        
        # Generate HTML content
        print("Generating HTML content using OpenAI...")
        html_content = self.generate_html_content(content, metadata)
        
        # Determine output filename
        if not output_filename:
            # Generate from title or use article filename
            if metadata.get('title'):
                base_name = re.sub(r'[^\w\s-]', '', metadata['title'])
                base_name = re.sub(r'[-\s]+', '-', base_name).lower()
                output_filename = f"{base_name}.html"
            else:
                output_filename = article_path.stem + ".html"
        
        output_path = self.root_dir / output_filename
        
        # Check if file exists for update mode
        if update_mode and not output_path.exists():
            print(f"Warning: Update mode specified but {output_filename} does not exist. Creating new file.")
        
        # Create full HTML page
        print("Creating complete HTML page...")
        full_html = self.create_full_html_page(html_content, metadata, output_filename)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✓ Successfully {'updated' if update_mode else 'created'} {output_path}")
        print(f"  Category: {metadata.get('category')}")
        print(f"  Tags: {', '.join(metadata.get('tags', []))}")
        
    def list_articles(self) -> List[Path]:
        """List all article.md files in the scripts directory."""
        articles = list(self.script_dir.glob('*.md'))
        return articles


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Article Management Script for chugakujukenpasssite'
    )
    parser.add_argument(
        'article',
        nargs='?',
        default='article.md',
        help='Path to article markdown file (default: article.md)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output HTML filename'
    )
    parser.add_argument(
        '-u', '--update',
        action='store_true',
        help='Update existing HTML page'
    )
    parser.add_argument(
        '-k', '--api-key',
        help='OpenAI API key (or set OPENAI_API_KEY environment variable)'
    )
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List all article files'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize manager
        manager = ArticleManager(api_key=args.api_key)
        
        if args.list:
            articles = manager.list_articles()
            print(f"Found {len(articles)} article(s):")
            for article in articles:
                print(f"  - {article.name}")
            return
        
        # Process article
        article_path = manager.script_dir / args.article
        manager.process_article(
            article_path,
            output_filename=args.output,
            update_mode=args.update
        )
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
