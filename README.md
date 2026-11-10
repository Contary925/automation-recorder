# Magento Search Video Recorder

A Python automation script that uses Playwright to perform a search for Magento developers and record the browser session as a WebM video.

The script reads company and location data from a CSV file, opens the specified search engine, enters a search query, opens the first result, and saves the recorded session.

## Features

- Automated browser interaction using Playwright (Sync API).
- CSV input with support for multiple companies.
- Search queries generated using the city specified in the input data.
- Character-by-character text input to simulate typing.
- Custom animated cursor with a highlight circle and click ripple effects.
- On-screen callouts to indicate the current stage of the automation.
- Browser session recording in WebM format.
- Separate video file for each company.
- Basic error handling and diagnostic information when a recording fails.

## Project structure

```text
recorder/
├── qscript.py          # Main automation logic
├── capture_video.py    # CSV processing and execution entry point
├── input.csv           # Input data
├── requirements.txt    # Python dependencies
└── video/              # Generated recordings
```

The `video/` directory is created automatically if it does not exist.

## Requirements

- Python 3.9 or newer.
- Playwright for Python.
- Chromium browser installed through Playwright.

The project uses Python standard-library modules for CSV processing and file management. No additional third-party Python packages are required.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Contary925/automation-recorder/
cd recorder
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Chromium

```bash
playwright install chromium
```

## Running the project

### Linux with a graphical environment

If a graphical display is available, run:

```bash
python3 capture_video.py
```

### WSL2 without a graphical environment

When running under WSL2 without an X server or another graphical display, use Xvfb:

```bash
sudo apt update
sudo apt install xvfb
```

Then start the script with:

```bash
xvfb-run -a python3 capture_video.py
```

**Why is Xvfb needed?**

The browser is launched in headed mode (`headless=False`) to produce a visible browser session in the recording. WSL2 installations without a graphical environment do not provide a display by default.

Xvfb creates a temporary virtual display, allowing Chromium to run in headed mode without requiring a physical monitor or a separate X server.

## Input CSV

The script reads input data from `input.csv`.

The file must use:

- UTF-8 encoding.
- Semicolon (`;`) as the delimiter.
- Double quotes (`"`) as the quote character.
- The exact column names listed below.

### CSV format

```csv
URL;Company Name;Language;Country;Postcode;City;Street;HouseNo
https://www.bing.com/;Example Company;English;Belarus;220000;Minsk;Independence Avenue;1
https://www.bing.com/;Another Company;English;Belarus;246000;Gomel;Sovetskaya Street;10
```

### Column description

| Column | Description |
|---|---|
| `URL