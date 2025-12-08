# 🎮 Pokemon Card Generator

A simple and easy-to-use Pokemon card generator that fetches data from PokeAPI to create high-quality printable Pokemon cards.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Key Features

- 🔍 **Flexible Search**: Search by generation or Pokemon ID
- 🌏 **Multi-language Support**: English, Traditional Chinese, Japanese (can be combined)
- 🎨 **High-Quality Design**: 300 DPI, standard trading card size (63×88mm)
- 📄 **PDF Output**: A4 pages, 9 cards per page, print-ready
- ⚡ **Smart Caching**: Automatically downloads and caches Pokemon images

## 🚀 Quick Start

### Installation

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the project
git clone <your-repository-url>
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

Issues and Pull Requests are welcome!

---

**Start creating your Pokemon cards!** 🎴✨