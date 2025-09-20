import tkinter as tk
from tkinter import messagebox
import requests
from tkinter import ttk

def fetch_weather(latVal, lonVal, out_widget):
    out_widget.delete("1.0", "end")
    out_widget.insert("end", "Fetching weather data...\n")

    # Validate Latitude
    try:
        latVal = float(latVal)
        if latVal < -90 or latVal > 90:
            out_widget.insert("end", "Latitude values should be between -90 and 90.\n")
            return
    except ValueError:
        out_widget.insert("end", "Latitude value must be a valid number.\n")
        return

    # Validate Longitude
    try:
        lonVal = float(lonVal)
        if lonVal < -180 or lonVal > 180:
            out_widget.insert("end", "Longitude values should be between -180 and 180.\n")
            return
    except ValueError:
        out_widget.insert("end", "Longitude value must be a valid number.\n")
        return

    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latVal,
        "longitude": lonVal,
        "current": ["temperature_2m", "is_day", "precipitation", "rain", "showers", "snowfall"]
    }

    try:
        requestData = requests.get(api_url, params, timeout=10)
        requestData.raise_for_status()
        outputData = requestData.json()
    except requests.RequestException as e:
        out_widget.insert("end", f"Failed to fetch data: {e}\n")
        return

    current_units = outputData.get('current_units', {})
    current_data = outputData.get('current', {})
    tempText = f"The current temperature at the location is {current_data.get('temperature_2m', 'N/A')} {current_units.get('temperature_2m', '')}\n"
    precipitationText = f"There is {current_data.get('precipitation', 'N/A')} {current_units.get('precipitation', '')} of rainfall expected\n"
    snowfallText = f"There is {current_data.get('snowfall', 'N/A')} {current_units.get('snowfall', '')} of snow expected\n"

    out_widget.insert("end", tempText)
    out_widget.insert("end", precipitationText)
    out_widget.insert("end", snowfallText)

# Create main window
window = tk.Tk()
window.title("Weather data fetcher")
window.geometry("520x460")
window.resizable(False, False)

# Title
title_label = tk.Label(window, text="Weather data fetcher", font=("Arial", 14, "bold"))
title_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

# Notebook with two tabs
notebook = ttk.Notebook(window)
notebook.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

latlon_tab = ttk.Frame(notebook)
city_tab = ttk.Frame(notebook)
notebook.add(latlon_tab, text="Lat / Lon")
notebook.add(city_tab, text="City")

# -------------- Lat/Lon Tab --------------
tk.Label(latlon_tab, text="Enter a latitude:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
lat_entry = tk.Entry(latlon_tab)
lat_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(latlon_tab, text="Enter a longitude:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
lon_entry = tk.Entry(latlon_tab)
lon_entry.grid(row=1, column=1, padx=5, pady=5)

def on_fetch_latlon():
    fetch_weather(lat_entry.get(), lon_entry.get(), output_text_latlon)

fetch_button_latlon = tk.Button(latlon_tab, text="Get weather data", command=on_fetch_latlon)
fetch_button_latlon.grid(row=2, column=0, columnspan=2, pady=10)

output_text_latlon = tk.Text(latlon_tab, height=12, width=60, wrap="word")
output_text_latlon.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# -------------- City Tab --------------
tk.Label(city_tab, text="Enter a city:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
city_entry = tk.Entry(city_tab)
city_entry.grid(row=0, column=1, padx=5, pady=5)

def on_fetch_city():
    output_text_city.delete("1.0", "end")
    city_name = city_entry.get().strip()
    if not city_name:
        output_text_city.insert("end", "Please enter a city name.\n")
        return

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    try:
        resp = requests.get(geo_url, params=geo_params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        output_text_city.insert("end", f"Failed to fetch coordinates: {e}\n")
        return

    results = data.get("results") or []
    if not results:
        output_text_city.insert("end", f"No results found for '{city_name}'.\n")
        return

    latVal = results[0].get("latitude")
    lonVal = results[0].get("longitude")
    display_name_parts = [
        results[0].get("name"),
        results[0].get("admin1"),
        results[0].get("country"),
    ]
    display_name = ", ".join([p for p in display_name_parts if p])

    # Show the resolved coordinates prominently in the large output box
    output_text_city.insert("end", f"Found {display_name}\n")
    output_text_city.insert("end", f"Coordinates: {latVal:.4f}, {lonVal:.4f}\n")

    # Optionally sync entries in the Lat/Lon tab (helps users see/fine-tune values)
    try:
        lat_entry.delete(0, "end"); lat_entry.insert(0, f"{float(latVal):.6f}")
        lon_entry.delete(0, "end"); lon_entry.insert(0, f"{float(lonVal):.6f}")
    except Exception:
        pass

    fetch_weather(latVal, lonVal, output_text_city)

fetch_button_city = tk.Button(city_tab, text="Get weather data", command=on_fetch_city)
fetch_button_city.grid(row=1, column=0, columnspan=2, pady=10)

output_text_city = tk.Text(city_tab, height=12, width=60, wrap="word")
output_text_city.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Ensure the window is focused and on top when it opens
window.lift()
window.attributes('-topmost', True)
window.after(0, lambda: window.attributes('-topmost', False))
window.focus_force()

# Start the main loop
window.mainloop()