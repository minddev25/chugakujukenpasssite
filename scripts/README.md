# Article Management Scripts

This folder contains private content management tools for the chugakujukenpasssite. These scripts use OpenAI API to generate and update HTML pages from markdown articles.

⚠️ **This folder is excluded from git via `.gitignore` to keep content management tools private.**

## Files

- **ma.sh** - Shell script wrapper for easy command-line usage
- **ma.py** - Python script with OpenAI API integration for HTML generation
- **article.md** - Example article template in markdown format
- **README.md** - This documentation file

## Prerequisites

1. **Python 3.7+** installed on your system
2. **OpenAI API key** - Get one from https://platform.openai.com/api-keys
3. **openai Python package** - Install with `pip install openai`

## Setup

1. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. Install required Python packages:
   ```bash
   pip install openai
   ```

## Usage

### Basic Usage

Generate an HTML page from the default `article.md`:
```bash
./ma.sh
```

Or use the Python script directly:
```bash
python3 ma.py
```

### Creating a New Article

Create a new article template:
```bash
./ma.sh -n "記事のタイトル"
```

This creates `article.md` with proper frontmatter structure.

### Processing Specific Articles

Process a specific markdown file:
```bash
./ma.sh my-article.md
```

Specify output filename:
```bash
./ma.sh article.md -o custom-page.html
```

### Updating Existing Pages

Update an existing HTML page:
```bash
./ma.sh -u article.md
```

### Listing Articles

List all markdown articles in the scripts folder:
```bash
./ma.sh -l
```

### Validating Articles

Validate article format before processing:
```bash
./ma.sh -v article.md
```

## Article Format

Articles should be written in Markdown with YAML frontmatter:

```markdown
---
title: Article Title
description: Brief description for meta tags
category: 算数|国語|理科|社会|コツ・勉強法
tags: [tag1, tag2, tag3]
references: [related-page1.html, related-page2.html]
---

# Main Heading

Your content here in Markdown format...

## Section Heading

More content...
```

### Frontmatter Fields

- **title** (required): Page title
- **description** (optional): Meta description for SEO
- **category** (optional): Main category - if not provided, AI will suggest one
- **tags** (optional): List of tags - if not provided, AI will generate them
- **references** (optional): Related pages to link to

### Markdown Features

The content supports standard Markdown:
- Headers (H1-H6)
- Lists (ordered and unordered)
- Bold and italic text
- Links and images
- Tables
- Code blocks
- Blockquotes

The Python script will convert these to appropriate HTML with the site's CSS classes.

## How It Works

1. **Read Article**: Reads the markdown file and extracts frontmatter metadata
2. **Generate Metadata**: If categories/tags are missing, uses OpenAI to suggest them based on content
3. **Generate HTML**: Uses OpenAI GPT-4 to convert markdown to well-structured HTML
4. **Create Full Page**: Wraps the content in the site's header, navigation, and footer structure
5. **Write File**: Saves the complete HTML file to the repository root

## Generated HTML Structure

The scripts generate HTML pages that match the existing site structure:
- DOCTYPE and HTML5 semantic tags
- Site header with navigation
- Breadcrumb navigation
- Main content area with proper CSS classes
- Footer with copyright notice
- Responsive design classes

## Features

### Intelligent Content Generation
- Converts markdown to semantic HTML
- Applies appropriate CSS classes from the site
- Creates proper Japanese typography
- Generates internal links to related pages

### Metadata Management
- Automatic category suggestion based on content
- AI-generated tags from article analysis
- Related page recommendations
- SEO-friendly meta descriptions

### Quality Assurance
- Validates article format before processing
- Checks for required metadata
- Ensures proper HTML structure
- Maintains consistency with existing pages

## Command Reference

### ma.sh Options

```
-h, --help          Show help message
-o, --output FILE   Specify output HTML filename
-u, --update        Update existing HTML page
-l, --list          List all article markdown files
-n, --new TITLE     Create new article.md template
-v, --validate      Validate article.md format
```

### ma.py Options

```
article             Path to article markdown file (default: article.md)
-o, --output        Output HTML filename
-u, --update        Update existing HTML page
-k, --api-key       OpenAI API key (or use OPENAI_API_KEY env var)
-l, --list          List all article files
```

## Examples

### Create and Process New Article

```bash
# Create new article
./ma.sh -n "効果的な時間管理術"

# Edit article.md with your content

# Validate format
./ma.sh -v article.md

# Generate HTML page
./ma.sh article.md -o time-management.html
```

### Update Existing Page

```bash
# Update article content in article.md

# Update the corresponding HTML page
./ma.sh -u article.md
```

### Batch Processing

```bash
# Process multiple articles
for article in *.md; do
    ./ma.sh "$article"
done
```

## Tips

1. **API Costs**: GPT-4 API calls have costs. Review your usage on OpenAI dashboard.
2. **Quality Review**: Always review generated HTML before committing to ensure quality.
3. **Metadata**: Providing good metadata (category, tags) improves output quality.
4. **Consistency**: Use existing categories to maintain site structure.
5. **References**: Add related page references to create internal linking structure.

## Troubleshooting

### "OpenAI API key not provided"
Set the OPENAI_API_KEY environment variable:
```bash
export OPENAI_API_KEY='your-key'
```

### "openai package not installed"
Install the package:
```bash
pip install openai
```

### "Article file not found"
Make sure you're in the scripts directory or provide full path to article file.

### Generated HTML doesn't match site style
The script uses GPT-4 to generate HTML based on existing site patterns. Review and adjust the prompt in ma.py if needed.

## Security Notes

⚠️ **Important Security Considerations:**

1. This folder is gitignored to keep content management tools private
2. Never commit your OpenAI API key to the repository
3. Use environment variables for sensitive data
4. Review generated content before publishing
5. Keep this folder secure on your local machine

## Future Enhancements

Potential improvements:
- Support for multiple article formats (reStructuredText, AsciiDoc)
- Batch processing with progress tracking
- Preview mode before writing files
- Automatic image optimization
- Content calendar integration
- Version control for articles
- A/B testing support
- Analytics integration

## Support

For issues or questions about these scripts:
1. Check this README first
2. Review error messages carefully
3. Verify API key and dependencies
4. Test with the example article.md

---

**Remember**: This folder and its contents are private and excluded from version control.
