import tkinter as tk
from tkinter import messagebox
import requests
from tkinter import ttk

def fetch_weather(latVal, lonVal):
    # Validate inputs
    try:
        lat = float(latVal)
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
    except Exception as e:
        return {"error": str(e)}
    try:
        lon = float(lonVal)
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
    except Exception as e:
        return {"error": str(e)}

    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "dew_point_2m",
            "is_day",
            "precipitation",
            "rain",
            "showers",
            "snowfall",
            "cloud_cover",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m",
            "visibility",
            "uv_index"
        ],
        "hourly": ["temperature_2m"],
        "daily": ["temperature_2m_max","temperature_2m_min"],
        "timezone": "auto"
    }
    try:
        resp = requests.get(api_url, params=params, timeout=7)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch data: {e}"}

    return {
        "lat": lat,
        "lon": lon,
        "current": data.get("current", {}),
        "current_units": data.get("current_units", {}),
        "hourly": data.get("hourly", {}),
        "hourly_units": data.get("hourly_units", {}),
        "daily": data.get("daily", {}),
        "daily_units": data.get("daily_units", {}),
    }


# Create main window
window = tk.Tk()
window.title("JWeather")
window.geometry("860x600")
window.resizable(True, True)

# Theme: Light mode, mobile-friendly spacing
style = ttk.Style()
try:
    style.theme_use('clam')
except Exception:
    pass
# Light colors
primary_bg = "#f7f7fa"   # light neutral background
surface_bg = "#ffffff"    # cards
border_color = "#dcdde1"
accent = "#007aff"        # iOS blue
text_color = "#1c1c1e"
subtle_text = "#6b7280"
accent_text = "#ffffff"

window.configure(bg=primary_bg)

style.configure('TFrame', background=primary_bg)
style.configure('Header.TLabel', background=primary_bg, foreground=text_color, font=("SF Pro Text", 18, "bold"))
style.configure('SubHeader.TLabel', background=primary_bg, foreground=subtle_text, font=("SF Pro Text", 11))
style.configure('TLabel', background=primary_bg, foreground=text_color)
# Card
style.configure('Card.TFrame', background=surface_bg, relief='solid', bordercolor=border_color, borderwidth=1)
style.configure('Card.TLabel', background=surface_bg, foreground=text_color)
# Buttons
style.configure('Accent.TButton', background=accent, foreground=accent_text, borderwidth=0, padding=8)
style.map('Accent.TButton', background=[('active', '#0a84ff')])

# Layout: single-column (header, sidebar, content stacked)
root_frame = ttk.Frame(window)
root_frame.grid(row=0, column=0, sticky="nsew")
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
root_frame.grid_rowconfigure(2, weight=1)
root_frame.grid_columnconfigure(0, weight=1)

header = ttk.Frame(root_frame, style='TFrame')
header.grid(row=0, column=0, sticky='ew', padx=12, pady=(8, 6))
app_title = ttk.Label(header, text="JWeather", style='Header.TLabel')
app_title.pack(side='left')
subtitle = ttk.Label(header, text="Current • Hourly • Daily", style='SubHeader.TLabel')
subtitle.pack(side='left', padx=8)

sidebar = ttk.Frame(root_frame, style='TFrame')
content = ttk.Frame(root_frame, style='TFrame')

# single column layout
sidebar.grid(row=1, column=0, sticky='ew', padx=12, pady=(0,8))
content.grid(row=2, column=0, sticky='nsew', padx=12, pady=(0,12))
# Make content scrollable so nothing is cut off on small screens
content_canvas = tk.Canvas(content, bg=primary_bg, highlightthickness=0, takefocus=True)
content_scroll = tk.Scrollbar(content, orient='vertical', command=content_canvas.yview)
content_scroll._visible = False
content_inner = ttk.Frame(content, style='TFrame')
# Update scrollregion whenever size of inner changes
def _update_scroll_metrics(event=None):
    # Update scrollregion and toggle scrollbar visibility based on content height vs canvas height
    try:
        content_canvas.configure(scrollregion=content_canvas.bbox('all'))
        # Determine if vertical scroll is needed
        bbox = content_canvas.bbox('all')
        need_scroll = False
        if bbox is not None:
            total_height = bbox[3] - bbox[1]
            visible_height = content_canvas.winfo_height()
            need_scroll = total_height > visible_height + 1
        # Show or hide scrollbar based on need
        if need_scroll:
            if not getattr(content_scroll, '_visible', False):
                content_scroll.grid(row=0, column=1, sticky='ns')
                content_scroll._visible = True
        else:
            if getattr(content_scroll, '_visible', False):
                content_scroll.grid_forget()
                content_scroll._visible = False
    except Exception:
        pass

content_inner.bind('<Configure>', _update_scroll_metrics)
# Create window for inner frame and keep its ID to sync widths
_inner_window = content_canvas.create_window((0,0), window=content_inner, anchor='nw')
# Keep inner frame width equal to the visible canvas width (no horizontal scroll)
def _on_canvas_configure(event=None):
    try:
        content_canvas.itemconfig(_inner_window, width=content_canvas.winfo_width())
        _update_scroll_metrics()
    except Exception:
        pass
content_canvas.bind('<Configure>', _on_canvas_configure)
content_canvas.configure(yscrollcommand=content_scroll.set)
content_canvas.grid(row=0, column=0, sticky='nsew')
# Scrollbar starts hidden; will be shown only when needed
# content_scroll.grid(row=0, column=1, sticky='ns')
content.grid_rowconfigure(0, weight=1)
content.grid_columnconfigure(0, weight=1)

# Cross-platform mouse wheel/trackpad scrolling

def _on_mousewheel(event):
    try:
        delta = event.delta
        if delta is None:
            return
        # Normalize delta across platforms: on Windows typically +/-120 per notch,
        # on macOS it can be small multiples. Scale to reasonable step count.
        if delta != 0:
            steps = -int(round(delta / 120))
        else:
            steps = 0
        # Use scroll_by amount to make trackpads feel smoother
        if steps == 0:
            # Fallback minimal movement based on sign
            steps = -1 if delta > 0 else (1 if delta < 0 else 0)
        if steps:
            # Scroll by number of mouse wheel notches, but use "pages" for large deltas to feel smoother
            granularity = 'units'
            if abs(steps) >= 3:
                granularity = 'pages'
            content_canvas.yview_scroll(steps, granularity)
    except Exception:
        pass


def _on_mousewheel_linux(event):
    try:
        if event.num == 4:
            content_canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            content_canvas.yview_scroll(1, 'units')
    except Exception:
        pass


def _bind_to_mousewheel():
    try:
        # Bind directly to canvas and inner only, avoid global bind_all to reduce side effects
        content_canvas.bind('<MouseWheel>', _on_mousewheel)
        # Linux
        content_canvas.bind('<Button-4>', _on_mousewheel_linux)
        content_canvas.bind('<Button-5>', _on_mousewheel_linux)
    except Exception:
        pass


def _unbind_from_mousewheel():
    try:
        content_canvas.unbind('<MouseWheel>')
        content_inner.unbind('<MouseWheel>')
        # Linux
        content_canvas.unbind('<Button-4>')
        content_canvas.unbind('<Button-5>')
    except Exception:
        pass

def _enter_scroll_area(event=None):
    try:
        _bind_to_mousewheel()
        content_canvas.focus_set()
        # Ensure wheel events bubble to the canvas by making canvas first bindtag
        def apply_bindtags(widget):
            try:
                tags = list(widget.bindtags())
                if content_canvas not in tags:
                    widget.bindtags((content_canvas,) + tuple(t for t in tags if t is not content_canvas))
            except Exception:
                pass
            for child in getattr(widget, 'winfo_children', lambda: [])():
                apply_bindtags(child)
        apply_bindtags(content_inner)
    except Exception:
        pass

def _leave_scroll_area(event=None):
    try:
        _unbind_from_mousewheel()
    except Exception:
        pass

for w in (content_canvas, content_inner):
    w.bind('<Enter>', _enter_scroll_area)
    w.bind('<Leave>', _leave_scroll_area)

# Reassign sections to content_inner instead of content

# Input notebook
notebook = ttk.Notebook(sidebar)
notebook.grid(row=0, column=0, sticky='ew', padx=0, pady=0)
sidebar.grid_columnconfigure(0, weight=1)
latlon_tab = ttk.Frame(notebook)
city_tab = ttk.Frame(notebook)
notebook.add(latlon_tab, text="Lat/Lon")
notebook.add(city_tab, text="City")
# Make City the default tab
try:
    notebook.select(city_tab)
except Exception:
    pass

# Lat/Lon inputs
ttk.Label(latlon_tab, text="Latitude").grid(row=0, column=0, padx=6, pady=6, sticky='w')
lat_entry = ttk.Entry(latlon_tab)
latlon_tab.grid_columnconfigure(1, weight=1)
lat_entry.grid(row=0, column=1, padx=6, pady=6, sticky='ew')

ttk.Label(latlon_tab, text="Longitude").grid(row=1, column=0, padx=6, pady=6, sticky='w')
lon_entry = ttk.Entry(latlon_tab)
lon_entry.grid(row=1, column=1, padx=6, pady=6, sticky='ew')

status_var = tk.StringVar(value="Enter coordinates or city and click Fetch")
status_label = ttk.Label(sidebar, textvariable=status_var, style='SubHeader.TLabel')
status_label.grid(row=2, column=0, sticky='w', pady=(12,0))

# Content sections
current_card = ttk.Frame(content_inner, padding=12, style='Card.TFrame')
current_card.grid(row=0, column=0, sticky='ew')
content_inner.grid_columnconfigure(0, weight=1)
current_card.grid_columnconfigure(1, weight=1)

# Current section widgets
current_icon = ttk.Label(current_card, text="☀", style='Card.TLabel', font=("Segoe UI Emoji", 32))
current_icon.grid(row=0, column=0, rowspan=2, padx=(0,12))
current_temp = ttk.Label(current_card, text="--°", style='Card.TLabel', font=("Segoe UI", 28, 'bold'))
current_temp.grid(row=0, column=1, sticky='w')
current_desc = ttk.Label(current_card, text="", style='Card.TLabel')
current_desc.grid(row=1, column=1, sticky='w')
current_meta = ttk.Label(current_card, text="", style='Card.TLabel')
current_meta.grid(row=0, column=2, rowspan=2, sticky='e')

# Click for details on current section
current_card_tip = tk.StringVar(value="Click for more current details…")

def show_current_details(event=None):
    try:
        # Build a simple popup with more granular metrics
        top = tk.Toplevel(window)
        top.title("Current Details")
        top.configure(bg=surface_bg)
        ttk.Label(top, text="Current Conditions", style='Header.TLabel').grid(row=0, column=0, padx=12, pady=(12,6), sticky='w')
        desc = current_desc.cget('text')
        meta = current_meta.cget('text')
        ttk.Label(top, text=desc, style='TLabel').grid(row=1, column=0, padx=12, pady=4, sticky='w')
        ttk.Label(top, text=meta, style='TLabel').grid(row=2, column=0, padx=12, pady=(0,12), sticky='w')
        ttk.Button(top, text="Close", style='Accent.TButton', command=top.destroy).grid(row=3, column=0, padx=12, pady=(0,12), sticky='e')
    except Exception:
        pass

for w in (current_card, current_icon, current_temp, current_desc):
    w.bind('<Button-1>', show_current_details)
    w.configure(cursor='hand2')

# Hourly chart
hourly_frame = ttk.Frame(content_inner, padding=12, style='Card.TFrame')
hourly_frame.grid(row=1, column=0, sticky='ew', pady=(8,0))
hourly_label = ttk.Label(hourly_frame, text="Next 24h", style='Card.TLabel')
hourly_label.grid(row=0, column=0, sticky='w')
hourly_canvas = tk.Canvas(hourly_frame, height=160, bg=surface_bg, highlightthickness=0)
hourly_canvas.grid(row=1, column=0, sticky='ew', pady=(6,0))
hourly_frame.grid_columnconfigure(0, weight=1)

def show_hourly_details(event=None):
    try:
        top = tk.Toplevel(window)
        top.title("Hourly Details")
        top.configure(bg=surface_bg)
        ttk.Label(top, text="Hourly Forecast — Next 24h", style='Header.TLabel').grid(row=0, column=0, padx=12, pady=(12,6), sticky='w')
        # Reuse the canvas snapshot by drawing a smaller legend
        ttk.Label(top, text="Tap anywhere to close", style='SubHeader.TLabel').grid(row=1, column=0, padx=12, pady=(0,12), sticky='w')
        top.bind('<Button-1>', lambda e: top.destroy())
    except Exception:
        pass

for w in (hourly_frame, hourly_canvas, hourly_label):
    w.bind('<Button-1>', show_hourly_details)
    try:
        w.configure(cursor='hand2')
    except Exception:
        pass

# Daily grid
daily_frame = ttk.Frame(content_inner, padding=12, style='Card.TFrame')
# Ensure daily frame is visible initially by giving it some minimum height via padding and letting content expand
# Also place it before binding resize so initial geometry is computed
daily_frame.grid(row=2, column=0, sticky='ew', pady=(8,0))
daily_label = ttk.Label(daily_frame, text="This Week — Min/Max and Trend", style='Card.TLabel')
daily_label.grid(row=0, column=0, sticky='w')
daily_rows = []
for i in range(1, 7):
    row = ttk.Frame(daily_frame, style='Card.TFrame')
    row.grid(row=i, column=0, sticky='ew', pady=2)
    icon = ttk.Label(row, text="—", style='Card.TLabel', width=2)
    day = ttk.Label(row, text="", style='Card.TLabel', width=10)
    bar = tk.Canvas(row, height=10, bg=surface_bg, highlightthickness=0)
    bar.pack(side='left', padx=6, fill='x', expand=True)
    hi = ttk.Label(row, text="", style='Card.TLabel', width=6)
    lo = ttk.Label(row, text="", style='Card.TLabel', width=6)
    icon.pack(side='left'); day.pack(side='left', padx=6)
    hi.pack(side='left'); lo.pack(side='left')
    def on_daily_click_factory(index):
        def handler(event=None):
            try:
                data = last_bundle.get('data') or {}
                daily = data.get('daily') or {}
                hourly = data.get('hourly') or {}
                daily_units = data.get('daily_units') or {}
                cur_units = data.get('hourly_units') or {}
                tmax = (daily.get('temperature_2m_max') or [])
                tmin = (daily.get('temperature_2m_min') or [])
                times = (daily.get('time') or [])
                # Basic header
                title = f"Day {index+1} Details"
                iso = None
                if 0 <= index < len(times):
                    iso = times[index]
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(iso)
                        title = dt.strftime('%A, %b %d')
                    except Exception:
                        pass
                top = tk.Toplevel(window)
                top.title(title)
                top.configure(bg=surface_bg)
                ttk.Label(top, text=title, style='Header.TLabel').grid(row=0, column=0, padx=12, pady=(12,6), sticky='w')
                # Hi/Lo
                hi_val = (tmax[index] if 0 <= index < len(tmax) else None)
                lo_val = (tmin[index] if 0 <= index < len(tmin) else None)
                hi_unit = daily_units.get('temperature_2m_max', '°')
                lo_unit = daily_units.get('temperature_2m_min', '°')
                ttk.Label(top, text=f"High: {round(hi_val) if hi_val is not None else '—'}{hi_unit}", style='TLabel').grid(row=1, column=0, padx=12, pady=(0,4), sticky='w')
                ttk.Label(top, text=f"Low:  {round(lo_val) if lo_val is not None else '—'}{lo_unit}", style='TLabel').grid(row=2, column=0, padx=12, pady=(0,8), sticky='w')
                # Derive details from hourly for the selected date
                details_lines = []
                try:
                    h_times = hourly.get('time') or []
                    h_t = hourly.get('temperature_2m') or []
                    if iso and h_times and h_t and len(h_times) == len(h_t):
                        # Select entries matching the iso date (YYYY-MM-DD prefix)
                        day_idx = [i for i, t in enumerate(h_times) if isinstance(t, str) and t.startswith(iso)]
                        vals = [h_t[i] for i in day_idx]
                        if vals:
                            import math
                            hmin = min(vals); hmax = max(vals)
                            havg = sum(vals)/len(vals)
                            unit = cur_units.get('temperature_2m', '°')
                            details_lines.append(f"Hourly min/max: {round(hmin)}{unit}/{round(hmax)}{unit}")
                            details_lines.append(f"Hourly average: {round(havg)}{unit}")
                            # Morning (06-12), Afternoon (12-18), Evening (18-24)
                            def bucket_range(start_h, end_h):
                                bucket = [h_t[i] for i in day_idx if start_h <= int(h_times[i][11:13]) < end_h]
                                return (round(sum(bucket)/len(bucket)) if bucket else '—')
                            morn = bucket_range(6,12)
                            aft = bucket_range(12,18)
                            eve = bucket_range(18,24)
                            details_lines.append(f"Morning/Afternoon/Evening avg: {morn}{unit} / {aft}{unit} / {eve}{unit}")
                    else:
                        details_lines.append("No hourly breakdown available for this day.")
                except Exception:
                    details_lines.append("No hourly breakdown available for this day.")
                # Present details
                row_i = 3
                for ln in details_lines:
                    ttk.Label(top, text=ln, style='TLabel').grid(row=row_i, column=0, padx=12, pady=(0,4), sticky='w')
                    row_i += 1
                ttk.Button(top, text="Close", style='Accent.TButton', command=top.destroy).grid(row=row_i, column=0, padx=12, pady=(8,12), sticky='e')
            except Exception:
                pass
        return handler
    for bindw in (row, icon, day, bar, hi, lo):
        bindw.bind('<Button-1>', on_daily_click_factory(i-1))
        try:
            bindw.configure(cursor='hand2')
        except Exception:
            pass
    daily_rows.append((icon, day, bar, hi, lo))

# Actions
fetch_btn = ttk.Button(sidebar, text="Fetch", style='Accent.TButton')
fetch_btn.grid(row=1, column=0, pady=(12,0), sticky='ew')

# Single-column layout: keep chart width responsive to content width

def on_resize(event=None):
    try:
        avail = max(260, min(820, content.winfo_width() - 24))
        hourly_canvas.config(width=avail)
    except Exception:
        pass

window.bind('<Configure>', on_resize)
# Apply once at start
window.after(50, on_resize)

# Utility: map basic icon based on simple current conditions

def icon_for(current):
    cc = current.get('cloud_cover')
    rain = current.get('rain') or 0
    snow = current.get('snowfall') or 0
    is_day = current.get('is_day', 1)
    if snow and snow > 0:
        return '🌨'
    if rain and rain > 0:
        return '🌧'
    if cc is None:
        return '☀' if is_day else '🌙'
    try:
        cc = float(cc)
    except Exception:
        cc = 0
    if cc < 20:
        return '☀' if is_day else '🌙'
    if cc < 60:
        return '⛅'
    return '☁'

# Render functions

def render_current(bundle):
    cur = bundle.get('current', {})
    units = bundle.get('current_units', {})
    t = cur.get('temperature_2m')
    app = cur.get('apparent_temperature')
    rh = cur.get('relative_humidity_2m')
    wind = cur.get('wind_speed_10m')
    gust = cur.get('wind_gusts_10m')
    uv = cur.get('uv_index')
    icon = icon_for(cur)
    current_icon.config(text=icon)
    if t is not None:
        current_temp.config(text=f"{round(t)}{units.get('temperature_2m','°C')}")
    else:
        current_temp.config(text="--°")
    parts = []
    if rh is not None: parts.append(f"Humidity {rh}{units.get('relative_humidity_2m','%')}")
    if wind is not None: parts.append(f"Wind {wind}{units.get('wind_speed_10m',' m/s')}")
    if gust is not None: parts.append(f"Gust {gust}{units.get('wind_gusts_10m',' m/s')}")
    if uv is not None: parts.append(f"UV {uv}")
    current_desc.config(text=" • ".join(parts))
    if app is not None and t is not None:
        current_meta.config(text=f"Feels like {round(app)}{units.get('apparent_temperature','°C')}  |  Cloud {cur.get('cloud_cover','—')}{units.get('cloud_cover','%')}")
    else:
        current_meta.config(text=f"Cloud {cur.get('cloud_cover','—')}{units.get('cloud_cover','%')}")


def render_hourly(bundle):
    hourly = bundle.get('hourly', {})
    temps = hourly.get('temperature_2m') or []
    hours = hourly.get('time') or []
    n = min(24, len(temps))
    hourly_canvas.delete('all')
    if n == 0:
        w = max(240, hourly_canvas.winfo_width() or 320)
        h = hourly_canvas.winfo_height() or 160
        hourly_canvas.create_text(w/2, h/2, text="No hourly data", fill=subtle_text)
        return
    vals = temps[:n]
    tmin, tmax = min(vals), max(vals)
    pad = 24
    w = max(240, hourly_canvas.winfo_width() or 320)
    h = hourly_canvas.winfo_height() or 160
    # axes
    hourly_canvas.create_line(pad, h-pad, w-pad, h-pad, fill=border_color)
    hourly_canvas.create_line(pad, pad, pad, h-pad, fill=border_color)
    # scale
    def y(v):
        if tmax == tmin:
            return h/2
        return h - pad - (v - tmin) * (h - 2*pad) / (tmax - tmin)
    step = (w - 2*pad) / max(1, (n-1))
    hourly_canvas.config(width=int(w), height=int(h))
    pts = []
    for i, v in enumerate(vals):
        x = pad + i*step
        yv = y(v)
        pts.append((x, yv))
    # draw polyline
    for i in range(1, len(pts)):
        hourly_canvas.create_line(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1], fill=accent, width=2)
    # dots and labels every 3 hours
    for i, (x, yv) in enumerate(pts):
        hourly_canvas.create_oval(x-3, yv-3, x+3, yv+3, fill="#7bd3ff", outline="")
        if i % 3 == 0:
            label = f"{round(vals[i])}°"
            hourly_canvas.create_text(x, yv-12, text=label, fill=text_color, font=("Segoe UI", 9))


def render_daily(bundle):
    daily = bundle.get('daily', {})
    tmax = daily.get('temperature_2m_max') or []
    tmin = daily.get('temperature_2m_min') or []
    time = daily.get('time') or []
    if not tmax or not tmin:
        for icon, day, bar, hi, lo in daily_rows:
            day.config(text="")
            bar.delete('all')
            hi.config(text="")
            lo.config(text="")
        daily_label.config(text="This Week — No data")
        return
    overall_min = min(tmin)
    overall_max = max(tmax)
    # Add a small weekly insight
    trend = "stable"
    try:
        if len(tmax) >= 2:
            delta = tmax[min(5,len(tmax)-1)] - tmax[0]
            if delta > 2:
                trend = "warming"
            elif delta < -2:
                trend = "cooling"
    except Exception:
        pass
    weekly_range = f"{round(overall_min)}–{round(overall_max)}°"
    daily_label.config(text=f"This Week — {weekly_range}, {trend}")

    def scale(v):
        if overall_max == overall_min:
            return 0
        return (v - overall_min) / (overall_max - overall_min)
    for idx in range(min(6, len(time))):
        icon, day, bar, hi, lo = daily_rows[idx]
        # day label from ISO date
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(time[idx])
            day_str = dt.strftime('%a')
        except Exception:
            day_str = f"D{idx+1}"
        day.config(text=day_str)
        bar.delete('all')
        w = max(60, bar.winfo_width() or 420)
        h = 10
        x0 = scale(tmin[idx]) * w
        x1 = scale(tmax[idx]) * w
        # glassy bar with subtle border
        bar.create_rectangle(x0, 0, x1, h, fill="#5ac8fa", outline="")
        hi.config(text=f"{round(tmax[idx])}°")
        lo.config(text=f"{round(tmin[idx])}°")
        # crude icon from temps range
        icon.config(text='🔥' if tmax[idx] >= 30 else ('❄' if tmax[idx] <= 0 else '⛅'))

# Controller

# Keep the latest fetched bundle for detail popups
last_bundle = {
    'data': None
}

def perform_fetch(lat, lon):
    status_var.set("Fetching…")
    window.update_idletasks()
    data = fetch_weather(lat, lon)
    if 'error' in data:
        status_var.set(data['error'])
        messagebox.showerror("Error", data['error'])
        return
    render_current(data)
    render_hourly(data)
    render_daily(data)
    last_bundle['data'] = data
    status_var.set(f"Updated • {round(data['lat'],4)}, {round(data['lon'],4)}")


def on_fetch_latlon():
    perform_fetch(lat_entry.get().strip(), lon_entry.get().strip())


ttk.Label(city_tab, text="City name").grid(row=0, column=0, padx=6, pady=6, sticky='w')
city_entry = ttk.Entry(city_tab)
city_tab.grid_columnconfigure(1, weight=1)
city_entry.grid(row=0, column=1, padx=6, pady=6, sticky='ew')


def on_fetch_city():
    name = city_entry.get().strip()
    if not name:
        status_var.set("Enter a city name")
        return
    status_var.set("Locating…")
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": name, "count": 1, "language": "en", "format": "json"}
    try:
        resp = requests.get(geo_url, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch coordinates: {e}")
        status_var.set("Geocoding error")
        return
    results = data.get('results') or []
    if not results:
        status_var.set(f"No results for '{name}'")
        return
    lat = results[0]['latitude']
    lon = results[0]['longitude']
    # sync fields
    try:
        lat_entry.delete(0, 'end'); lat_entry.insert(0, f"{float(lat):.6f}")
        lon_entry.delete(0, 'end'); lon_entry.insert(0, f"{float(lon):.6f}")
    except Exception:
        pass
    perform_fetch(lat, lon)

# Default to City tab for fetch routing as well
fetch_btn.configure(command=lambda: (on_fetch_latlon() if notebook.index('current') == 0 else on_fetch_city()))

# Ensure the window is focused and on top when it opens
window.lift()
window.attributes('-topmost', True)
window.after(0, lambda: window.attributes('-topmost', False))
window.focus_force()

# Attempt to auto-detect user city via IP and fetch on startup

def try_auto_locate_and_fetch():
    # Run auto-locate off the UI thread to avoid freezing and reduce perceived slowness
    import threading, time

    def normalize_ip_info(info: dict):
        city = (info.get('city') or info.get('city_name') or '').strip()
        lat = info.get('latitude') or info.get('lat')
        lon = info.get('longitude') or info.get('lon')
        # Some providers use strings
        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
        except Exception:
            lat, lon = None, None
        return city, lat, lon

    def ip_provider_calls(results: list, done_flag: dict):
        # Query multiple IP geolocation providers concurrently, take the first success
        providers = [
            ("https://ipapi.co/json/", None),
            ("https://ipinfo.io/json", None),
            ("https://ifconfig.co/json", None),
            ("https://ipwho.is/", None),
        ]
        def call(url, params=None):
            try:
                r = requests.get(url, params=params, timeout=3.5)
                if r.status_code == 200:
                    info = r.json() or {}
                    # ipinfo may return loc as "lat,lon"
                    if 'loc' in info and (not info.get('latitude') or not info.get('longitude')):
                        try:
                            parts = str(info['loc']).split(',')
                            if len(parts) == 2:
                                info['latitude'] = float(parts[0])
                                info['longitude'] = float(parts[1])
                        except Exception:
                            pass
                    if 'success' in info and not info.get('success', True):
                        return
                    if not done_flag.get('done'):
                        results.append(info)
                        done_flag['done'] = True
            except Exception:
                return
        threads = []
        for url, params in providers:
            t = threading.Thread(target=call, args=(url, params), daemon=True)
            threads.append(t)
            t.start()
        # Wait a short budget for first success
        start = time.time()
        while time.time() - start < 4.0 and not done_flag.get('done'):
            time.sleep(0.02)
        # No need to join; threads are daemonic

    def worker():
        try:
            window.after(0, lambda: (status_var.set("Locating your city…"), window.update_idletasks()))
            results = []
            done_flag = {'done': False}
            ip_provider_calls(results, done_flag)
            if results:
                city, lat, lon = normalize_ip_info(results[0])
                # Prefer direct lat/lon (fast path)
                if lat is not None and lon is not None:
                    def do_fetch_coords():
                        try:
                            lat_entry.delete(0, 'end'); lat_entry.insert(0, f"{lat:.6f}")
                            lon_entry.delete(0, 'end'); lon_entry.insert(0, f"{lon:.6f}")
                        except Exception:
                            pass
                        status_var.set("Fetching weather…")
                        perform_fetch(lat, lon)
                    window.after(0, do_fetch_coords)
                    return
                # Fallback to city geocoding if we only have city
                if city:
                    def do_city():
                        try:
                            city_entry.delete(0, 'end'); city_entry.insert(0, city)
                        except Exception:
                            pass
                        status_var.set("Finding coordinates…")
                        on_fetch_city()
                    window.after(0, do_city)
                    return
            # If no IP result, just reset status
            window.after(0, lambda: status_var.set("Enter a city or coordinates and click Fetch"))
        except Exception:
            window.after(0, lambda: status_var.set("Enter a city or coordinates and click Fetch"))

    threading.Thread(target=worker, daemon=True).start()

# Kick off auto-locate shortly after UI initializes
window.after(400, try_auto_locate_and_fetch)

# Start the main loop
window.mainloop()