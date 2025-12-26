# 📖 Pokemon Card Generator - Usage Guide

## For Non-Technical Users

### Step 1: Download

1. Visit the [Releases page](https://github.com/jasonma1127/ptcg-placeholder/releases/latest)
2. Download the correct file for your computer:

| Your Computer | Download This |
|---------------|---------------|
| Windows PC | `pokemon-card-generator-windows.exe` |
| Mac (M1/M2/M3/M4) | `pokemon-card-generator-macos-arm` |
| Linux | `pokemon-card-generator-linux` |

**Note for older Intel Mac users:** Please use Option 2 (Run from Source) as pre-built Intel executables are no longer provided.

### Step 2: First Time Setup

#### Windows
1. Double-click the `.exe` file
2. If Windows shows a security warning, click "More info" → "Run anyway"
3. That's it!

#### macOS

**Important:** macOS will show a security warning because this app is not signed with an Apple Developer certificate (costs $99/year). This is normal for free open-source software.

**Method 1: Right-click to Open (Easiest)**
1. Right-click (or Control-click) the downloaded file
2. Select "Open" from the menu
3. Click "Open" in the security dialog that appears
4. You only need to do this once!

**Method 2: Remove Quarantine Flag**
1. Open Terminal (Applications → Utilities → Terminal)
2. Run this command (replace path if needed):
   ```bash
   xattr -d com.apple.quarantine ~/Downloads/pokemon-card-generator-macos-arm
   chmod +x ~/Downloads/pokemon-card-generator-macos-arm
   ~/Downloads/pokemon-card-generator-macos-arm
   ```

**Method 3: System Settings**
1. Try to open the file (it will be blocked)
2. Open System Settings → Privacy & Security
3. Scroll down to see "pokemon-card-generator-macos-arm was blocked"
4. Click "Open Anyway"

#### Linux
```bash
chmod +x pokemon-card-generator-linux
./pokemon-card-generator-linux
```

### Step 3: Using the Tool

When you run the program, you'll see a menu:

```
🎴 Pokemon Card Generator

How would you like to select Pokemon?
1. By Generation (e.g., all Gen 1 Pokemon)
2. By ID (e.g., specific Pokemon like Pikachu)
```

**Option 1: Generate by Generation**
```
Enter your choice: 1
Enter generation number(s) (1-9): 1

This will generate all 151 Pokemon from Generation 1!
```

**Option 2: Generate specific Pokemon**
```
Enter your choice: 2
Enter Pokemon ID(s) (comma-separated): 1,4,7,25,150

This will generate:
- Bulbasaur (#1)
- Charmander (#4)
- Squirtle (#7)
- Pikachu (#25)
- Mewtwo (#150)
```

### Step 4: Choose Languages

```
Select language(s):
1. English
2. Traditional Chinese
3. Japanese

Enter your choice (comma-separated for multiple): 1,2

This will show both English and Chinese names on the cards!
```

### Step 5: Wait for Generation

```
Downloading Pokemon images... ⏳
Generating cards... 🎨
Creating PDF... 📄

✅ Success!
PDF saved to: data/output/pokemon_cards_gen1_20251222_123456.pdf
```

### Step 6: Find Your PDF

The PDF will be saved in a folder called `data/output/` next to the program.

**Finding the file:**
- **Windows**: Right-click the program → "Open file location" → look for `data/output` folder
- **macOS**: Right-click the program → "Show in Finder" → look for `data/output` folder
- **Linux**: The PDF is in `./data/output/`

### Step 7: Print Your Cards

1. Open the PDF
2. Print settings:
   - ✅ Select "Actual Size" or "100%" (NOT "Fit to Page")
   - ✅ Use thick paper (200gsm+ recommended)
   - ✅ Color printing
3. Cut out the cards along the borders
4. Insert into card binder!

---

## Troubleshooting

### "The program won't open" / "Malicious software" warning (macOS)

This is macOS Gatekeeper blocking unsigned apps. **This is normal and safe** - the app is open source and you can review the code.

**Quick Fix:**
1. Right-click the file → "Open"
2. Click "Open" in the dialog

See "Step 2: First Time Setup → macOS" above for detailed instructions with 3 different methods.

### "Missing python39.dll" (Windows)

This shouldn't happen with the compiled executable. If it does:
1. Download the latest release again
2. Or use Option 2 (run from source) from README

### "No internet connection" error

The tool needs internet to download Pokemon images (only first time).
- Check your internet connection
- Try again later

### Cards are the wrong size when printed

Make sure to:
1. Select "Actual Size" or "100%" in print settings
2. **Do NOT** select "Fit to Page" or "Shrink to Fit"

### Generation takes a long time

This is normal! Depending on how many Pokemon:
- 10 Pokemon: ~30 seconds
- 50 Pokemon: ~2 minutes
- 151 Pokemon: ~5 minutes

The images are cached, so next time will be faster!

---

## Tips & Tricks

### Fastest Way to Generate Popular Pokemon

Create a favorites list:
```
Starters: 1,4,7 (Bulbasaur, Charmander, Squirtle)
Legendary Birds: 144,145,146 (Articuno, Zapdos, Moltres)
Mewtwo & Mew: 150,151
Popular: 25,6,9,94,131 (Pikachu, Charizard, Blastoise, Gengar, Lapras)
```

### Multiple Language Cards

Perfect for language learning or international collecting!
```
Select: 1,2,3 (English, Chinese, Japanese)
```

The card will show all three names stacked.

### Organizing Your Binder

1. Generate one generation at a time
2. Print each generation on different colored paper
3. Use the cards as placeholders while hunting for real cards
4. Replace with actual cards as you collect them!

---

## FAQ

**Q: Is this legal?**
A: Yes for personal use! Do NOT sell these cards or claim they're official.

**Q: Can I customize the cards?**
A: Not yet, but it's planned for future versions!

**Q: Do I need to download Pokemon images every time?**
A: No! They're cached in `data/pokemon_images/`. Delete this folder to re-download.

**Q: How much disk space do I need?**
A: About 50-200 MB depending on how many Pokemon you generate.

**Q: Can I use this offline?**
A: After first run (images downloaded), you can use it offline!

**Q: What paper should I use?**
A: Recommended: 200-300gsm card stock for durability.

---

## Support

- 🐛 Report bugs: [GitHub Issues](https://github.com/jasonma1127/ptcg-placeholder/issues)
- ⭐ Like this tool? Star the repo!
- 💬 Questions? Open a discussion on GitHub

---

**Happy Collecting! 🎴✨**
