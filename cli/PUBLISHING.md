# Publishing Sinth to PyPI

Guide for publishing the `sinth` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org
2. **Test PyPI Account** (optional): Create account at https://test.pypi.org
3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version

**Edit both files to keep version in sync:**

`pyproject.toml`:
```toml
version = "0.1.1"  # Increment version
```

`aim_cli/__init__.py`:
```python
__version__ = "0.1.1"
```

**Test the version:**
```bash
python3 -m aim_cli.cli --version
# Should output: sinth 0.1.1
```

### 2. Build Distribution

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build
```

This creates:
- `dist/sinth-0.1.0-py3-none-any.whl` (wheel)
- `dist/sinth-0.1.0.tar.gz` (source)

### 3. Test on Test PyPI (Optional)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ sinth

# Test it works
sinth --help
sinth fetch weather
```

### 4. Upload to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Enter your PyPI credentials when prompted
```

### 5. Verify Installation

```bash
# Uninstall test version
pip uninstall sinth

# Install from PyPI
pip install sinth

# Test
sinth --help
sinth fetch weather
```

## Using API Tokens (Recommended)

### Create API Token

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: `sinth`
5. Scope: Entire account (or specific project)
6. Copy the token (starts with `pypi-`)

### Configure token

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
```

Now you can upload without entering credentials:
```bash
python -m twine upload dist/*
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

Add `PYPI_TOKEN` secret to GitHub repo settings.

## Version Guidelines

Follow semantic versioning:
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features (backwards compatible)
- `1.0.0` - Stable release

## Checklist

Before publishing:
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `aim_cli/__init__.py`
- [ ] Update `CLI.md` with any new features
- [ ] Test locally: `pip install -e .`
- [ ] Run all commands to verify they work
- [ ] Build: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Upload to Test PyPI (optional)
- [ ] Upload to PyPI
- [ ] Create GitHub release with tag

## Package Information

- **Package name**: `sinth`
- **Command**: `sinth`
- **Description**: Sinth — the CLI for AIM. Synthesize intent into reality.
- **Homepage**: https://intentmodel.dev
- **Repository**: https://github.com/juicejs/application-intent-language
- **PyPI**: https://pypi.org/project/sinth/
