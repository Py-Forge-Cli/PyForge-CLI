# PyForge CLI Icon Usage Guide

This guide explains how to use the PyForge CLI icons across different platforms and documentation.

## 📁 Available Icon Files

### Main Icon
- **`icon_pyforge_forge.svg`** - Primary icon (256x256) for general use

### GitHub-Specific Assets
- **`github/icon_512x512.svg`** - Repository icon (512x512) for GitHub settings
- **`github/social-preview.svg`** - Social sharing image (1280x640) for GitHub

## 🔧 GitHub Repository Setup

### 1. Repository Icon
1. Go to your GitHub repository settings
2. Navigate to **General** settings
3. Scroll to **Repository details**
4. Click **Choose an image** next to the repository name
5. Upload `assets/github/icon_512x512.svg`

### 2. Social Preview Image
1. In repository settings, go to **General**
2. Scroll to **Social preview**
3. Click **Upload an image**
4. Upload `assets/github/social-preview.svg`
5. This will be used when the repository is shared on social media

## 📚 Documentation Usage

### MkDocs/Material (Current Setup)
The icon is already configured in:
- **README.md**: Shows at top of repository
- **docs/index.md**: Shows at top of documentation site

```markdown
<div align="center">
  <img src="../assets/icon_pyforge_forge.svg" alt="PyForge CLI" width="128" height="128">
</div>
```

### GitHub Pages
The icon will automatically appear on your GitHub Pages documentation site at:
`https://py-forge-cli.github.io/PyForge-CLI/`

## 🎨 Icon Design Details

### Color Scheme
- **Background**: Purple-to-blue gradient (#667eea → #764ba2)
- **Text**: Pure white (#ffffff) with off-white accent (#f8f9fa)
- **Style**: Modern, clean typography with Montserrat font

### Typography
- **Font**: Montserrat (2024's Font of the Year)
- **Weight**: 800 (Extra Bold) for main text
- **Spacing**: Tight letter spacing (-2px) for contemporary look
- **Size**: Optimized for each use case (48px-120px range)

### Technical Specs
- **Format**: SVG (scalable vector graphics)
- **Background**: Gradient with rounded corners
- **Text Effects**: Subtle drop shadow for depth
- **Responsive**: Scales perfectly at any size

## 📱 Platform Compatibility

### ✅ Supported Platforms
- **GitHub**: Repository icon, social preview, README display
- **Documentation Sites**: MkDocs, GitBook, Sphinx, etc.
- **Package Managers**: PyPI, conda-forge (as project logo)
- **Social Media**: Twitter, LinkedIn, GitHub social sharing
- **App Stores**: If creating desktop/mobile apps

### 💡 Usage Tips
- Use 128px size for documentation headers
- Use 512px size for repository/app icons  
- Use 1280x640 size for social media previews
- Always maintain aspect ratio when resizing
- SVG format ensures crisp display on all screen densities

## 🔄 Future Updates

To update the icon across all platforms:
1. Update the source SVG files in `/assets/`
2. Commit changes to the repository
3. GitHub Pages will automatically update documentation
4. Manually update repository icon in GitHub settings if needed
5. Social preview updates automatically with new commits

---

*The PyForge CLI icon uses modern design principles and professional typography to represent the tool's focus on powerful, clean data conversion.*