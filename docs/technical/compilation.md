# Compilation Guide

This guide covers building standalone executables for the Graph Centrality Analysis application.

## Manual Compilation

### Prerequisites
- Python 3.7+ installed
- All dependencies from `requirements.txt`
- PyInstaller package

### Install Build Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Build Executable

#### Linux/macOS
```bash
pyinstaller --onefile src/application/main.py \
  --hidden-import=matplotlib.backends.backend_svg \
  --hidden-import=PIL._tkinter_finder \
  --paths=.
```

#### Windows
```cmd
pyinstaller --onefile src\application\main.py ^
  --hidden-import=matplotlib.backends.backend_svg ^
  --hidden-import=PIL._tkinter_finder ^
  --paths=.
```

### PyInstaller Options Explained
- `--onefile`: Creates a single executable file
- `--hidden-import=matplotlib.backends.backend_svg`: Includes SVG backend for matplotlib
- `--hidden-import=PIL._tkinter_finder`: Ensures PIL/Pillow works with Tkinter
- `--paths=.`: Adds current directory to Python path for imports

### Run Compiled Executable

#### Linux/macOS
```bash
chmod +x dist/main  # Set executable permissions
./dist/main         # Run the application
```

#### Windows
```cmd
dist\main.exe       # Run the application
```

## Automated Builds (GitHub Actions)

The repository includes automated build workflows that create executables for both Linux and Windows platforms.

### Workflow Files
- `.github/workflows/release-linux.yml` - Linux builds
- `.github/workflows/release-windows.yml` - Windows builds

### Build Process
1. **Trigger**: Automatically runs on pushes to `main` branch
2. **Environment**: Uses Python 3.11 on respective OS runners
3. **Dependencies**: Installs requirements and PyInstaller
4. **Build**: Creates platform-specific executables
5. **Release**: Publishes executables as GitHub releases

