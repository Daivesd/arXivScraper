# arXiv Scraper
This thing finds papers on arXiv for given keywords and saves them do SQLite database. The script can run in background (minimized to systray) and notiy you if it finds new papers - and automatically adds them to the database.

## Dependencies
- PySide6
- arxiv
- sqlite3
- pandas
  
Maybe something else :)

## How to run
You can either:
- Suggested: Run the script directly -> <code>pythonw main.py</code> to run the script unlinked with respect to the terminal
  - Please note: You can create a venv with conda using <code>conda env create -f environment.yml</code>

- Run the executable builds (Windows only) - **TODO**

- Build an executable yourself

## Build instructions
You can build your own executable usint pyinstaller:

<code>pip install pyinstaller</code>

### Windows
1. Open terminal and cd to the directory where the code sits
2. run <code>pyinstaller --onefile --windowed main.py</code>
3. The executable is in the dist folder
4. Optional: To use an icon: <code>pyinstaller --onefile --icon=your_icon.ico your_script.py</code>
### Linux
1. Open terminal and cd to the directory where the code sits
2. run <code>pyinstaller --onefile main.py</code> (I don't know if --windowed works)
### MacOS
1. Open terminal and cd to the directory where the code sits
2. Run <code>pyinstaller --onefile --windowed --icon=your_icon.ico your_script.py</code> (MacOS doesn't like png, you **need** an .ico file here)
3. Grant execute permissions <code>chmod +x dist/main</code>

## Check Database
- Use the built-in viewer
- Use https://github.com/sqlitebrowser/sqlitebrowser. It's pretty cool.

## Pictures
This is what the main program looks like:
![image](https://github.com/user-attachments/assets/fda4207e-6a5e-44de-a81c-21d5cf88afab)

This is the built-in database viewer:
![image](https://github.com/user-attachments/assets/8f656153-c090-442b-bcaa-b6ad3773f923)


