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

## 🚀 Quick Start

### Download Executable (Recommended)

1. Go to [Releases](https://github.com/jasonma1127/ptcg-placeholder/releases/latest)
2. Download for your system:
   - 🪟 Windows: `pokemon-card-generator-windows.exe` → Double-click to run
   - 🍎 macOS: `pokemon-card-generator-macos-arm` → See macOS instructions below
   - 🐧 Linux: `pokemon-card-generator-linux` → Run in terminal with `chmod +x` first
3. Follow the on-screen prompts to generate cards!

#### macOS Setup

```bash
cd ~/Downloads
xattr -d com.apple.quarantine pokemon-card-generator-macos-arm
chmod +x pokemon-card-generator-macos-arm
./pokemon-card-generator-macos-arm
```

**Note:** macOS blocks unsigned apps by default. The `xattr` command removes this block (safe for open source software).

### Run from Source (Developers)

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/jasonma1127/ptcg-placeholder.git
cd ptcg-placeholder
uv sync
uv run main.py
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
