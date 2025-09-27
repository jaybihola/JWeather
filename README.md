# JWeather — Rich Weather App (Tkinter + Open‑Meteo)

JWeather is a lightweight desktop application built with Python's Tkinter that lets you quickly check current weather for a location by either:
- Entering latitude and longitude, or
- Typing a city name (which is geocoded to coordinates)

The app uses the free Open‑Meteo APIs for both weather and geocoding.


## Features
- Light mode theme with clean cards and iOS-blue accents.
- Responsive layout: resizable window with mobile-style stacked layout when narrow.
- Sidebar with two input modes in a Notebook:
  - Lat/Lon: manually input coordinates
  - City: search by city name (default tab; auto-detects your city via IP on launch when possible)
- Current section: big temperature, condition icon, humidity, wind, cloud cover, UV.
- Hourly section: embedded line chart (Canvas) for next 24h temperatures; click to open quick details.
- Daily section: 6-day min/max bars with icons, plus a weekly insight (range and warming/cooling trend). Click any day to see a full breakdown (hi/low, hourly min/max/average, and morning/afternoon/evening averages).
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
The main window titled "JWeather" will open with a light theme in a single-column layout (sidebar on top, content below). By default, the City tab is selected and the app attempts to auto-detect your city via your IP address; if successful, it fetches weather automatically. The window is resizable; charts expand with the available width. Use the sidebar to enter a city or coordinates, then click Fetch to populate the Current, Hourly, and Daily sections. You can click the Current, Hourly, or any day in the This Week section for quick details.


## How to Use
- Lat / Lon tab:
  1. Enter a latitude (−90 to 90) and longitude (−180 to 180).
  2. Click "Fetch".
  3. The Current, Hourly, and Daily sections will update.

- City tab:
  1. Enter a city name (e.g., "Paris").
  2. Click "Fetch".
  3. The app geocodes the city to coordinates, syncs the Lat/Lon fields, and updates all sections.


## APIs Used
- Weather: https://api.open-meteo.com/v1/forecast
  - Current fields: temperature_2m, apparent_temperature, relative_humidity_2m, dew_point_2m, is_day, precipitation, rain, showers, snowfall, cloud_cover, pressure_msl, surface_pressure, wind_speed_10m, wind_gusts_10m, wind_direction_10m, visibility, uv_index
  - Hourly: temperature_2m (next 24h charted)
  - Daily: temperature_2m_max, temperature_2m_min (6-day bars)
- Geocoding: https://geocoding-api.open-meteo.com/v1/search
  - Parameters include `name`, `count=1`, `language=en`, `format=json`

Both APIs are free and do not require an API key at the time of writing.


## Network and Timeouts
- Auto-detect and weather fetch run off the UI thread to keep the app responsive.
- IP geolocation uses multiple providers in parallel with ~3.5s per-provider timeouts and picks the first successful result.
- Geocoding requests use a 6-second timeout; weather requests use a 7-second timeout.
- Errors (e.g., connection failure, non-200 responses) are shown via a dialog and in the status text in the sidebar.


## Project Structure
```
JWeather/
├── main.py        # Tkinter GUI and logic
└── README.md      # This file
```


## Code Overview
- `fetch_weather(latVal, lonVal)`: Validates inputs, calls Open‑Meteo weather API (current, hourly, daily), and returns a structured dict.
- Controller updates three sections: Current card, Hourly chart (Canvas), Daily grid.
- City tab flow:
  - Calls Open‑Meteo geocoding API to resolve the city to coordinates.
  - Syncs the Lat/Lon fields and triggers fetch.


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
