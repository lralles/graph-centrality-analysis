Compile 

pyinstaller --onefile src/application/main.py --hidden-import=matplotlib.backends.backend_svg --hidden-import=PIL._tkinter_finder --paths=.

run

python3 -m src.application.main