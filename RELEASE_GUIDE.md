# 🚀 Release Guide for Maintainers

## How to Create a New Release

### Step 1: Prepare the Release

1. **Test everything locally**
   ```bash
   uv run main.py
   # Make sure it works!
   ```

2. **Update version numbers** (if needed)
   - Update any version strings in code
   - Update CHANGELOG.md (if you have one)

3. **Commit all changes**
   ```bash
   git add .
   git commit -m "Prepare for release v1.0.0"
   git push
   ```

### Step 2: Create and Push a Tag

```bash
# Create a version tag
git tag v1.0.0

# Push the tag to GitHub
git push origin v1.0.0
```

**That's it!** GitHub Actions will automatically:
1. Build executables for Windows, macOS (Intel & ARM), and Linux
2. Create a new Release
3. Upload all executables to the Release

### Step 3: Wait for Build (5-10 minutes)

Go to your GitHub repository:
1. Click on "Actions" tab
2. You'll see "Build and Release Executables" running
3. Wait for all 4 builds to complete (green checkmarks)

### Step 4: Verify the Release

1. Go to "Releases" tab
2. You should see a new release `v1.0.0`
3. Check that all 4 files are attached:
   - ✅ `pokemon-card-generator-windows.exe`
   - ✅ `pokemon-card-generator-macos-intel`
   - ✅ `pokemon-card-generator-macos-arm`
   - ✅ `pokemon-card-generator-linux`

### Step 5: Test the Executables (Optional but Recommended)

Download each executable and test:
- Does it run?
- Can it generate cards?
- Are PDFs created correctly?

### Step 6: Announce the Release

Share on:
- Reddit: r/Pokemon, r/PokemonTCG
- Twitter/X
- Discord servers
- Your social media

---

## Troubleshooting Build Failures

### Build fails on Windows

**Common issue:** Missing icon file

**Solution:** Make sure `assets/icon.ico` exists, or remove `--icon` flag from workflow

### Build fails on macOS

**Common issue:** Permissions

**Solution:** Usually auto-resolved by GitHub Actions. If persists, check Python version compatibility.

### Executable is too large (>100MB)

**Solution:** This is normal! PyInstaller bundles Python + all dependencies.

To reduce size:
```yaml
# Add to pyinstaller command:
--exclude-module matplotlib
--exclude-module numpy
```

---

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- `v1.0.0` - Major release (big changes)
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)

Examples:
```bash
# First release
git tag v1.0.0

# Added new language support
git tag v1.1.0

# Fixed a bug
git tag v1.0.1
```

---

## Manual Build (if needed)

If you need to build locally:

### Windows
```bash
pip install pyinstaller
pyinstaller --onefile --name pokemon-card-generator main.py
```

### macOS / Linux
```bash
pip install pyinstaller
pyinstaller --onefile --name pokemon-card-generator main.py
```

Output will be in `dist/` folder.

---

## Rollback a Release

If you need to delete a bad release:

```bash
# Delete the tag locally
git tag -d v1.0.0

# Delete the tag on GitHub
git push origin :refs/tags/v1.0.0
```

Then manually delete the Release on GitHub:
1. Go to Releases
2. Click the bad release
3. Click "Delete"

---

## Pre-releases (Beta Testing)

To create a pre-release for testing:

```bash
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

The workflow will create a pre-release (marked with "Pre-release" label).

---

## Automated Release Notes

The workflow automatically generates release notes from your commits.

To make them better, use conventional commits:

```bash
git commit -m "feat: add support for Gen 9 Pokemon"
git commit -m "fix: correct DPI metadata handling"
git commit -m "docs: update README with new examples"
```

---

## Questions?

Open an issue on GitHub!
