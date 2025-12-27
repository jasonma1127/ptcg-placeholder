# 🎴 PTCG Placeholder

A tool for Pokemon card collectors to generate placeholder cards for organizing their binders while building their collection.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Key Features

- 🔍 **Flexible Search**: Find cards by generation or Pokemon ID for your collection
- 🗂️ **Binder Organization**: Create placeholders to keep your card binder organized
- 🌏 **Multi-language Support**: English, Traditional Chinese, Japanese (perfect for international collecting)
- 🎨 **Authentic Design**: Standard trading card size (63×88mm) to fit perfectly in binders
- 📄 **Print-Ready**: A4 pages with 9 cards each, optimized for home printing
- ⚡ **Collection Planning**: Visual reference while hunting for specific cards

## 🚀 Quick Start

### Option 1: Download Executable (Easiest - No Installation Required!)

**For non-technical users:**

1. Go to [Releases](https://github.com/jasonma1127/ptcg-placeholder/releases/latest)
2. Download the file for your operating system:
   - 🪟 Windows: `pokemon-card-generator-windows.exe`
   - 🍎 macOS: `pokemon-card-generator-macos-arm` (see note below)
   - 🐧 Linux: `pokemon-card-generator-linux`
3. Double-click to run (macOS/Linux: may need to run `chmod +x` first)
4. Follow the on-screen prompts!

**macOS Users:** You may see a security warning. Right-click the file → "Open" → "Open" to bypass. See [USAGE_GUIDE.md](USAGE_GUIDE.md) for details.

### Option 2: Run from Source (For Developers)

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the project
git clone https://github.com/jasonma1127/ptcg-placeholder.git
cd ptcg-placeholder

# 3. Install dependencies
uv sync

# 4. Run the application
uv run main.py
```

### How to Use

1. **Choose Search Method**
   - By Generation: `1` (e.g., `1-3` for first three generations)
   - By ID: `2` (e.g., `1,25,150` for Bulbasaur, Pikachu, Mewtwo)

2. **Select Language(s)**
   - Single language: `1` (English), `2` (Chinese), `3` (Japanese)
   - Multiple languages: `1,2` (English + Chinese)

3. **Generate PDF**
   - The program automatically downloads images, generates cards, and creates a PDF
   - Output files are saved in the `data/output/` directory

## 📋 System Requirements

- Python 3.9+
- 2GB+ RAM (for large batches)
- Internet connection (for initial image downloads)

## 🛠️ Tech Stack

- **Frontend UI**: Rich (terminal interface)
- **Image Processing**: Pillow
- **PDF Generation**: ReportLab
- **API Client**: aiohttp (async downloads)
- **Package Management**: uv

## 📁 Project Structure

```
ptcg-placeholder/
├── main.py                 # Application entry point
├── src/                   # Source code
│   ├── api/              # PokeAPI integration
│   ├── card/             # Card design
│   ├── ui/               # User interface
│   └── pdf/              # PDF generation
├── config/               # Configuration files
└── data/                 # Output and cache (auto-generated)
```

## 🎯 Usage Examples

```bash
# Generate all Generation 1 Pokemon cards (English + Chinese)
uv run main.py
# Select: 1 → 1 → 1,2 → y

# Generate Pikachu card (Japanese)
uv run main.py
# Select: 2 → 25 → 3 → y
```

## 📄 Legal Notice

This project is for **educational and personal use only**. Pokemon-related content is copyrighted by The Pokemon Company.

## 🤝 Contributing

**Feature Requests & Bug Reports:**
- Please open an [Issue](https://github.com/jasonma1127/ptcg-placeholder/issues)
- Describe your use case or the problem you're facing

**Note:** This is a personal project maintained by a single developer. Pull requests are not currently accepted, but all feature requests and bug reports are welcome via Issues!

---

**Start organizing your Pokemon card collection!** 🎴✨
