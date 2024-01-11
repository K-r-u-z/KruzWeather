import tkinter as tk
from tkinter import ttk, messagebox
import requests
import time
from PIL import Image, ImageTk, ImageFilter 
import io
import os
import sys
from dotenv import dotenv_values

# Before Git Hub:
# Export as EXE: python -m auto_py_to_exe
# Then export as --onefile and no terminal
# Drag and drop KruzWeather.exe from output folder into root folder and delete output folder.
# Update ReadMe
# Push/Commit

# Dark Color Palette
bg_color = "#202123"  # Dark background
primary_color = "#3498db"  # Blue
text_color = "#FFFFFF"  # White text
temp_color = "#FFFFFF"  # White text
button_color = "#3498db"  # Blue for button
hourly_text_color = "#3498db"  # Blue text for hourly forecast

# For py-to-exe/pyinstaller
def resource_path(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Define global variables
global city
secrets = dotenv_values(".env")
api_key = secrets["API_KEY"]
base_url = secrets["API_BASE_URL"]
path = resource_path(".env")
update_interval_ms = 60000  # 60 seconds
time_update_interval_ms = 1000  # 1 second

search_button_pressed = False  # Variable to track whether the search button has been pressed
hourly_frame = None
time_label = None
city_label = None
result_frame = None  # Initialize result_frame

# Functions
def apply_textured_background(root, image_path):
    try:
        # Load the background image
        original_bg_image = Image.open(image_path)

        # Resize the image to match the window size
        window_size = (root.winfo_screenwidth(), root.winfo_screenheight())
        original_bg_image = original_bg_image.resize(window_size, Image.LANCZOS)

        # Apply a blur effect to the image (optional)
        original_bg_image = original_bg_image.filter(ImageFilter.BLUR)

        # Create a PhotoImage object from the original image
        bg_photo = ImageTk.PhotoImage(original_bg_image)

        # Create a label to display the background image
        bg_label = tk.Label(root, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(relwidth=1, relheight=1)  # Set the label to cover the entire window

    except (IOError, OSError) as e:
        print(f"Error loading background image: {e}") # Prevent crash in filepath/image is not found.


def get_weather(api_key, city, units):
    endpoint = "/weather"
    params = {
        'q': city,
        'units': units,
        'APPID': api_key
    }

    try:
        response = requests.get(f"{base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    
def get_weather_and_display():
    global city, search_button_pressed

    if not search_button_pressed:
        return

    city = entry.get()
    units = unit_var.get()

    if not city:
        messagebox.showerror("Error", "City name cannot be empty.")
        return

    # Destroy the existing result_frame and hourly_frame if they exist
    for widget in main_frame.winfo_children():
        if isinstance(widget, tk.Frame) and widget != city_frame:
            widget.destroy()

    try:
        weather_data = get_weather(api_key, city, units)

        if weather_data:
            # Hide the title_frame only when the search is successful
            title_frame.pack_forget()
            
            # Rearrange widgets in the main frame
            city_frame.pack(side=tk.TOP, pady=10)  # Adjust the pady value as needed
            display_weather_results(weather_data, units)

            # Fetch and display hourly forecast
            hourly_data = get_hourly_forecast(api_key, city, units)
            if hourly_data:
                display_hourly_forecast(hourly_data, units)
            else:
                messagebox.showerror("Error", "Failed to retrieve hourly forecast.")
        else:
            messagebox.showerror("Error", "Failed to retrieve weather data.")

    except Exception as e:
        print(f"An exception occurred: {e}")
        messagebox.showerror("Error", "An error occurred. Please try again.")



def get_hourly_forecast(api_key, city, units):
    endpoint = "/forecast"
    params = {
        'q': city,
        'units': units,
        'APPID': api_key
    }

    try:
        response = requests.get(f"{base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hourly forecast: {e}")
        return None



def format_temperature(temperature, units):
    if units == 'metric':
        return f"{temperature}°C"
    elif units == 'imperial':
        return f"{temperature}°F"
    else:
        return f"{temperature}"

def create_label(parent, text, font=None, row=None, column=None, padx=0, pady=0, sticky=None, **kwargs):
    label = tk.Label(parent, text=text, font=font, bg=bg_color, **kwargs)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return label  # Return the created label widget


def display_weather_results(weather_data, units):
    global city, time_label, city_label, result_frame  # Include result_frame in global scope
    weather_description = weather_data['weather'][0]['description']
    temperature = round(weather_data['main']['temp'])
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    visibility = weather_data['visibility']
    temp_max = round(weather_data['main']['temp_max'])
    temp_min = round(weather_data['main']['temp_min'])

    # Create a new frame for weather results
    result_frame = tk.Frame(main_frame, bg=bg_color)
    result_frame.pack(expand=True, pady=(10, 10), side="top", anchor="n")  # Use pack manager

    # Display current time above the city name
    time_label = create_label(result_frame, "", font=("HelveticaNeue-Thin ", 16), fg=text_color, anchor='center')
    city_label = create_label(result_frame, city, font=("HelveticaNeue-Thin ", 24, "bold"), fg=text_color, pady=(80, 0), anchor='center')


    # Create a label for temperature with manual spacing
    temperature_label = create_label(result_frame, f"{format_temperature(temperature, units)}", font=("HelveticaNeue-Thin ", 60), fg=text_color, pady=(5,0), anchor='center')

    # Capitalize the first letter of each word in the description
    weather_description = ' '.join(word.capitalize() for word in weather_description.split())
    create_label(result_frame, weather_description, font=("HelveticaNeue-Thin ", 14), fg=text_color, pady=(5,0), anchor='center')

    # Create labels for "H:" and "L:" with manual spacing
    high_low_label = create_label(result_frame, f"H: {format_temperature(temp_max, units)}   L: {format_temperature(temp_min, units)}", font=("HelveticaNeue-Thin ", 12), fg=text_color, pady=5, anchor='center')

    # Add a separator under the high_low_label
    separator_high_low = ttk.Separator(result_frame, orient="horizontal")
    separator_high_low.grid(row=4, column=0, columnspan=10, sticky="ew", pady=(35, 0))

     # Use grid layout for description, high, and low labels with adjusted column values
    create_label(result_frame, f"Humidity: {humidity}%", font=("HelveticaNeue-Thin Neue-Thin", 14), fg=primary_color, pady=5, anchor='w')

    # Convert wind speed based on units
    if units == 'imperial':
        wind_speed_label = f"Wind Speed: {wind_speed} mph"
    else:
        # Convert wind speed from mph to km/h for metric units
        wind_speed_metric = round(wind_speed * 1.60934, 2)
        wind_speed_label = f"Wind: {wind_speed_metric} km/h"

    create_label(result_frame, wind_speed_label, font=("HelveticaNeue-Thin ", 14), fg=primary_color, pady=5, anchor='center')

    # Convert visibility based on units
    if units == 'imperial':
        visibility_converted = round(visibility * 0.000621371, 2)  # Convert meters to miles
        visibility_unit = 'miles'
    else:
        visibility_converted = visibility
        visibility_unit = 'meters'

    visibility_label = f"Visibility: {visibility_converted} {visibility_unit}"
    create_label(result_frame, visibility_label, font=("HelveticaNeue-Thin ", 14), fg=primary_color, pady=5, anchor='center')


    # Weather icon frame
    icon_frame = tk.Frame(main_frame, bg=bg_color)
    icon_frame.pack(expand=True, pady=(10, 10), side="top", anchor="n")  # Use pack manager


    # Create a label for the weather icon with a larger size using PIL
    icon_id = weather_data['weather'][0]['icon']
    icon_url = f"http://openweathermap.org/img/wn/{icon_id}.png"
    icon_data = requests.get(icon_url).content
    icon_image = Image.open(io.BytesIO(icon_data))

    # Adjust the size to improve image quality (e.g., 150x150)
    new_size = (100, 100)
    icon_image = icon_image.resize(new_size, Image.LANCZOS)

    # Create a PhotoImage object from the resized image
    icon = ImageTk.PhotoImage(icon_image)

    icon_label = tk.Label(icon_frame, image=icon, bg=bg_color)
    icon_label.image = icon
    icon_label.pack()

    update_time()



def format_hour(hour):
    # Convert hour to 12-hour format with AM/PM
    if hour == 0:
        return "12 AM"
    elif 1 <= hour <= 11:
        return f"{hour} AM"
    elif hour == 12:
        return "12 PM"
    else:
        return f"{hour-12} PM"

def display_hourly_forecast(hourly_data, units):
    # Create a new frame for hourly forecast
    global hourly_frame

    # Check if hourly_frame already exists
    if hourly_frame is not None:
        # Destroy the existing hourly_frame and create a new one
        hourly_frame.destroy()

    hourly_frame = tk.Frame(main_frame, bg=bg_color)
    
    # Create a canvas to enable horizontal scrolling
    canvas = tk.Canvas(hourly_frame, bg=bg_color, scrollregion=(0, 0, 2000, 100), height=60)
    canvas.pack(side="top", fill="both", expand=True)

    # Create a horizontal scrollbar for the canvas
    scrollbar_style = ttk.Style()
    scrollbar_style.configure("Horizontal.TScrollbar", troughcolor=bg_color, background=bg_color)
    scrollbar_x = ttk.Scrollbar(hourly_frame, orient="horizontal", command=canvas.xview, style="Horizontal.TScrollbar")
    scrollbar_x.pack(side="bottom", fill="x")

    # Move the scrollbar outside the visible area
    scrollbar_x.place(x=-1000, y=0)

    # Hide the entire column containing the scrollbar
    hourly_frame.grid_columnconfigure(1, weight=0, minsize=0)

    # Bind the MouseWheel event to the on_mouse_wheel function
    canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: on_mouse_wheel(event, canvas))

    # Configure the canvas to work with the horizontal scrollbar
    canvas.configure(xscrollcommand=scrollbar_x.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


    # Create another frame inside the canvas to hold the hourly forecast details
    inner_frame = tk.Frame(canvas, bg=bg_color, width=2000, height=100)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Display hourly forecast using Labels in a grid
    for i, entry in enumerate(hourly_data['list']):
        timestamp = entry['dt_txt']
        temperature = round(entry['main']['temp'])
        weather_icon = entry['weather'][0]['icon']
        hour = int(timestamp.split()[1][:2])  # Extract hour from timestamp

        # Display hourly forecast details in a grid layout
        col = i * 250  # Adjust the width based on your content
        create_label(inner_frame, format_hour(hour), font=("HelveticaNeue-Thin ", 12), row=0, column=col, padx=10, pady=5, sticky=tk.W, fg=hourly_text_color)
        create_label(inner_frame, f"{format_temperature(temperature, units)}", font=("HelveticaNeue-Thin ", 10), row=1, column=col, padx=10, pady=5, sticky=tk.W, fg=hourly_text_color)
        create_label(inner_frame, f"{weather_icon}", font=("HelveticaNeue-Thin ", 12), row=2, column=col, padx=10, pady=5, sticky=tk.W, fg=hourly_text_color)

    # Pack the hourly_frame inside the main_frame
    hourly_frame.pack(expand=True, pady=(10, 10), side="top", anchor="n")


def switch_units_and_refresh():
    global unit_text_var
    unit = 'metric' if unit_var.get() == 'imperial' else 'imperial'
    unit_var.set(unit)
    unit_text_var.set('Imperial' if unit == 'imperial' else 'Metric')
    get_weather_and_display()



# Function to fetch weather and update display
def update_weather_and_display():
    get_weather_and_display()
    root.after(update_interval_ms, update_weather_and_display)  # Schedule the function to run every 30000 milliseconds (5 seconds)



# Function to handle the search button press
def on_search_button_press():
    global search_button_pressed, canvas  # Make canvas global
    search_button_pressed = True
    get_weather_and_display()


def on_mouse_wheel(event, canvas):
    canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")


def update_time():
    global time_label, result_frame
    if time_label and result_frame:  # Check if both labels are not None
        current_time = time.strftime("%H:%M:%S")  # Format: H:MM:SS
        time_label.config(text=current_time)
        result_frame.after(time_update_interval_ms, update_time)  # Update every 1000 milliseconds (1 second)


# GUI setup
root = tk.Tk()
root.title("Kruz's Weather")
root.geometry("540x800")
root.configure(bg=bg_color)

# Apply textured background
background_image_path = resource_path("imgs/background.jpg")
apply_textured_background(root, background_image_path)

# Create unit_var after the root window is created
unit_var = tk.StringVar(value='imperial')  # Default unit is imperial
unit_text_var = tk.StringVar()
unit_text_var.set('Imperial' if unit_var.get() == 'imperial' else 'Metric')

# Title frame
title_frame = tk.Frame(root, bg=bg_color)
title_frame.pack(side=tk.TOP, fill=tk.X)

title_label = tk.Label(title_frame, text="Kruz's Weather", font=("HelveticaNeue-Thin ", 24, "bold"), fg=text_color, bg=bg_color)
title_label.pack(pady=300)

# Version label in the bottom left-hand corner
version_label = tk.Label(root, text="Build v.1.0.0", font=("HelveticaNeue-Thin ", 10), fg="black", bg="#94acd4")
version_label.place(relx=0.00, rely=0.975)

# Main frame
main_frame = tk.Frame(root, bg=bg_color)
main_frame.pack(expand=True, fill='both', pady=20)

# City frame
city_frame = tk.Frame(main_frame, bg=bg_color)
city_frame.pack(side=tk.TOP, pady=10)  # Adjust the pady value to bring it down

label = tk.Label(city_frame, text="Enter City:", font=("HelveticaNeue-Thin ", 14), fg=primary_color, bg=bg_color)
label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

entry = tk.Entry(city_frame, font=("HelveticaNeue-Thin ", 14))
entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Dynamic Search Button using grid
search_button = tk.Button(
    city_frame, text="Search", command=on_search_button_press,
    font=("HelveticaNeue-Thin ", 10, "bold"), bg=button_color, fg=text_color,
    borderwidth=2, relief="raised", pady=5, padx=10, bd=0, highlightthickness=0,
)
search_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

# Settings button to toggle units
settings_button = tk.Button(
    city_frame, textvariable=unit_text_var, command=switch_units_and_refresh,
    font=("HelveticaNeue-Thin", 10, "bold"), bg=button_color, fg=text_color,
    borderwidth=2, relief="raised", pady=5, padx=10, bd=0, highlightthickness=0,
)
settings_button.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

# Display weather details underneath the search mechanism
display_frame = tk.Frame(main_frame, bg=bg_color)
display_frame.pack(side=tk.TOP, pady=20)


update_weather_and_display()
update_time()
root.resizable(width=False, height=False)
root.mainloop()