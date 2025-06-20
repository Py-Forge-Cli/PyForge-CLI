# Your First Conversion

Step-by-step walkthrough of your first file conversion with PyForge CLI.

## What You'll Learn

In this detailed tutorial, you'll learn:
- How to prepare files for conversion
- Understanding command options
- Reading output and results
- Handling common issues

## Prerequisites

- PyForge CLI installed ([Installation Guide](installation.md))
- A sample file to convert (PDF, Excel, MDB, or DBF)

## Step 1: Choose Your File

For this tutorial, we'll use a PDF file. If you don't have one, you can:
- Download a sample PDF from the internet
- Create a simple PDF from any document

## Step 2: Basic Conversion

```bash
# Convert PDF to text
pyforge convert document.pdf
```

This will create `document.txt` in the same directory.

## Step 3: Examine the Output

```bash
# View the converted text
cat document.txt

# Or open in your text editor
open document.txt  # macOS
notepad document.txt  # Windows
```

## What's Next?

- Explore [Converter Options](../converters/index.md)
- Try [Batch Processing](../tutorials/index.md)
- Read the [CLI Reference](../reference/cli-reference.md)