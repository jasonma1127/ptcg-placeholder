# 🎴 PTCG Placeholder

A tool for Pokemon card collectors to generate placeholder cards for organizing their binders while building their collection.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🔍 Search by generation or Pokemon ID
- 🌏 Multi-language support (English, Traditional Chinese, Japanese)
- 🎨 Standard trading card size (63×88mm)
- 📄 A4-optimized PDF output (9 cards per page, 300 DPI)
- ⚡ Fast async image downloading with caching

## 🚀 Installation

### Prerequisites

- Python 3.9 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install and Run

```bash
# Clone the repository
git clone https://github.com/jasonma1127/ptcg-placeholder.git
cd ptcg-placeholder

# Install dependencies
uv sync

# Run the application
uv run main.py
```

**Quick one-liner:**
```bash
git clone https://github.com/jasonma1127/ptcg-placeholder.git && cd ptcg-placeholder && uv sync && uv run main.py
```

## 📖 How to Use

1. **Select search method**: Generation (1-9) or specific Pokemon IDs
2. **Choose language(s)**: English, Chinese, Japanese, or multiple
3. **Choose output location**: Desktop, Downloads, Documents, or custom path
4. **Wait for generation**: Images download once, then cached
5. **Print your cards**: Use "Actual Size" (100%) print setting

**Popular Pokemon IDs:**
- Starters: `1,4,7` (Bulbasaur, Charmander, Squirtle)
- Pikachu: `25`
- Eevee evolutions: `133-136`
- Legendary birds: `144-146`
- Mewtwo & Mew: `150,151`

## 🖨️ Printing Tips

- Use 200-300gsm card stock for durability
- Print at "Actual Size" or "100%" (NOT "Fit to Page")
- Color printing recommended
- Cut along borders and insert into binder

## ⚙️ Technical Details

- **Language**: Python 3.9+
- **UI**: Rich (terminal)
- **PDF**: ReportLab (300 DPI)
- **Images**: Pillow + PokeAPI
- **Async**: aiohttp for fast downloads

## 📄 Legal Notice

For **personal use only**. Pokemon is copyrighted by The Pokemon Company, Nintendo, and Game Freak.

## 🤝 Contributing

- **Bug reports & feature requests**: Open an [Issue](https://github.com/jasonma1127/ptcg-placeholder/issues)
- **Pull requests**: Not currently accepted (personal project)
- All suggestions are welcome!

## 📜 License

MIT License - see [LICENSE](LICENSE) file

---

**Start organizing your Pokemon card collection!** 🎴✨
