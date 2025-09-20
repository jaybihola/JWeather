# JWeather — Simple GUI Weather App (Tkinter + Open‑Meteo)

JWeather is a lightweight desktop application built with Python's Tkinter that lets you quickly check current weather for a location by either:
- Entering latitude and longitude, or
- Typing a city name (which is geocoded to coordinates)

The app uses the free Open‑Meteo APIs for both weather and geocoding.


## Features
- Two-tab interface:
  - Lat/Lon tab: manually input coordinates.
  - City tab: search by city name (auto-resolves to coordinates).
- Shows current:
  - Temperature (°C by default from the API)
  - Precipitation
  - Snowfall
- Input validation for latitude (−90…90) and longitude (−180…180).
- Clear status messages and error handling (network timeouts, invalid inputs, no search results).

## Requirements
- Python 3.8 or newer (tested with Python 3.10+)
- Internet connection (to call Open‑Meteo APIs)

Python libraries used:
- tkinter (standard library GUI toolkit, included with most CPython installations)
- requests

Note: On some Linux distributions, you may need to install Tk support separately (e.g., `sudo apt-get install python3-tk`).


## Installation
1. Clone or download this repository.

2. (Recommended) Create and activate a virtual environment:
   - macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     py -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If you don't have a requirements.txt, install `requests` directly:
   ```bash
   pip install requests
   ```


## Running the App
From the project root:
```bash
python main.py
```
The main window titled "Weather data fetcher" will open.


## How to Use
- Lat / Lon tab:
  1. Enter a latitude (−90 to 90) and longitude (−180 to 180).
  2. Click "Get weather data".
  3. The output box shows current temperature, precipitation, and snowfall.

- City tab:
  1. Enter a city name (e.g., "Paris").
  2. Click "Get weather data".
  3. The app queries Open‑Meteo's geocoding API to find coordinates, displays the resolved place name and coordinates, then fetches the current weather for those coordinates.


## APIs Used
- Weather: https://api.open-meteo.com/v1/forecast
  - Current fields requested: `temperature_2m`, `is_day`, `precipitation`, `rain`, `showers`, `snowfall`
- Geocoding: https://geocoding-api.open-meteo.com/v1/search
  - Parameters include `name`, `count=1`, `language=en`, `format=json`

Both APIs are free and do not require an API key at the time of writing.


## Network and Timeouts
- Network requests use a 10-second timeout.
- Errors (e.g., connection failure, non-200 responses) are displayed in the output box.


## Project Structure
```
JWeather/
├── main.py        # Tkinter GUI and logic
└── README.md      # This file
```


## Code Overview
- `fetch_weather(latVal, lonVal, out_widget)`: Validates inputs, calls Open‑Meteo weather API, and writes results to the provided text widget.
- City tab flow:
  - Calls Open‑Meteo geocoding API to resolve the city to coordinates.
  - Displays resolved place name and coordinates.
  - Calls `fetch_weather` with those coordinates.


## Troubleshooting
- Tkinter not found on Linux: install `python3-tk` (Debian/Ubuntu) or your distro's Tk package.
- SSL/Certificates issues on macOS: run `Install Certificates.command` inside your Python framework folder, or update Python.
- No results for city: Try a more specific query (e.g., include state/country), or check your internet connection.
- Timeouts: The app uses a 10s timeout. Check connectivity or try again.


## Development
- Single-file app (`main.py`) for simplicity.
- Consider refactoring into modules if you plan to extend functionality (e.g., services/api.py, ui/...).
- To run with live reload, consider tools like `watchdog` to auto-restart on changes (not included).


## License
This project is provided as-is without warranty. You can adapt it for personal use. If you plan to publish or distribute, consider adding a LICENSE file with your preferred license (e.g., MIT, Apache-2.0). Acknowledgments to Open‑Meteo for their free APIs.


## Acknowledgments
- Open‑Meteo: https://open-meteo.com/
- Tkinter documentation: https://docs.python.org/3/library/tkinter.html
