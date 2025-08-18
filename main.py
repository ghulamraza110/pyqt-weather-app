# Import necessary modules
import sys                          # Provides access to system-specific parameters and functions
import requests                     # Allows sending HTTP requests to APIs
from PyQt5.QtWidgets import (        # Import PyQt5 GUI components
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtCore import Qt         # Provides alignment constants and other core features

# Your OpenWeatherMap API key (used to authenticate API requests)
API_KEY = "749d4afd316de7f04d7c7b1699a4fdc5"

# Main application class
class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()          # Call the parent QWidget constructor
        self.unit = "F"             # Default temperature unit is Fahrenheit
        self.initUI()               # Call function to set up the User Interface

    def initUI(self):
        # Set window title and minimum size
        self.setWindowTitle("Weather App")  # Title of the app window
        self.setMinimumSize(400, 500)       # Minimum size of the window (width x height)

        # Create UI elements
        self.city_label = QLabel("Enter city name:")   # Label for city input
        self.city_label.setObjectName("city_label")    # Assigns a CSS-style ID for styling

        self.city_input = QLineEdit()                  # Text box for user to input city
        self.get_weather_button = QPushButton("Get Weather")  # Button to fetch weather
        self.unit_toggle = QPushButton("Switch to °C")        # Button to switch units

        self.temperature_label = QLabel()              # Label to display temperature
        self.temperature_label.setObjectName("temperature_label")

        self.emoji_label = QLabel()                    # Label to display weather emoji
        self.emoji_label.setObjectName("emoji_label")

        self.description_label = QLabel()              # Label to display weather description
        self.description_label.setObjectName("description_label")

        # Arrange widgets vertically in a column layout
        layout = QVBoxLayout()
        layout.setSpacing(20)                          # Space between widgets
        layout.addWidget(self.city_label)              # Add "Enter city name" label
        layout.addWidget(self.city_input)              # Add input field
        layout.addWidget(self.get_weather_button)      # Add weather button
        layout.addWidget(self.unit_toggle)             # Add unit toggle button
        layout.addWidget(self.temperature_label)       # Add temperature label
        layout.addWidget(self.emoji_label)             # Add emoji label
        layout.addWidget(self.description_label)       # Add description label
        self.setLayout(layout)                         # Apply layout to window

        # Center-align key widgets
        for widget in [self.city_label, self.city_input,
                       self.temperature_label, self.emoji_label,
                       self.description_label]:
            widget.setAlignment(Qt.AlignCenter)        # Align all widgets center horizontally

        # Apply custom styling using CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;  /* Light gray background */
            }
            QLabel {
                font-family: Calibri;      /* Font for all labels */
                color: #333;               /* Dark gray text */
            }
            QLabel#city_label {
                font-size: 22px;           /* Bigger font for city input label */
                font-weight: bold;
            }
            QLineEdit {
                font-size: 18px;           /* Input field text size */
                padding: 6px;              /* Padding inside input box */
                border: 1px solid #ccc;    /* Gray border */
                border-radius: 4px;        /* Rounded corners */
            }
            QPushButton {
                font-size: 18px;           /* Button text size */
                padding: 8px;              /* Button padding */
                background-color: #0078D7; /* Blue button */
                color: white;              /* White text */
                border-radius: 5px;        /* Rounded button */
            }
            QPushButton:hover {
                background-color: #005a9e; /* Darker blue when hovered */
            }
            QLabel#temperature_label {
                font-size: 90px;           /* Big font for temperature */
                font-weight: bold;
            }
            QLabel#emoji_label {
                font-size: 70px;           /* Large emoji size */
                font-family: Segoe UI Emoji; /* Emoji font */
            }
            QLabel#description_label {
                font-size: 40px;           /* Large italic text for description */
                font-style: italic;
            }
        """)

        # Connect buttons to their respective functions
        self.get_weather_button.clicked.connect(self.get_weather)  # Fetch weather on click
        self.unit_toggle.clicked.connect(self.toggle_unit)         # Toggle unit on click

    def toggle_unit(self):
        # Toggle between Celsius and Fahrenheit
        self.unit = "C" if self.unit == "F" else "F"   # Switch unit
        self.unit_toggle.setText(f"Switch to °{'F' if self.unit == 'C' else 'C'}")  # Update button text
        self.get_weather()                             # Refresh weather with new unit

    def get_weather(self):
        # Get city name from input field
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"

        try:
            # Make API request
            response = requests.get(url)               # Send GET request to API
            response.raise_for_status()                # Raise error if status code != 200
            data = response.json()                     # Parse JSON response

            # If city is found, display weather data
            if data["cod"] == 200:
                self.display_weather(data)
            else:
                self.display_error("City not found.")  # Show error if invalid city
        except requests.exceptions.HTTPError as http_error:
            self.display_error(f"HTTP Error: {http_error}")   # Handle HTTP errors
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error: Check your internet connection.") # Handle no internet
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error: The request timed out.")             # Handle timeout
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error: {req_error}")  # Handle other request errors

    def display_error(self, message):
        # Show error message in red font
        self.temperature_label.setStyleSheet("font-size: 30px; color: red;")
        self.temperature_label.setText(message)   # Display error message
        self.emoji_label.clear()                  # Clear emoji
        self.description_label.clear()            # Clear description

    def display_weather(self, data):
        # Convert temperature from Kelvin to selected unit
        temp_k = data["main"]["temp"]            # Extract temp in Kelvin
        temp = (temp_k - 273.15) if self.unit == "C" else (temp_k * 9/5) - 459.67  # Convert to C or F
        unit_symbol = "°C" if self.unit == "C" else "°F"   # Select correct unit symbol

        # Extract weather info
        weather_id = data["weather"][0]["id"]    # Weather condition code
        description = data["weather"][0]["description"]   # Weather description (text)

        # Update UI with weather data
        self.temperature_label.setText(f"{temp:.0f}{unit_symbol}") # Show rounded temperature
        self.emoji_label.setText(self.get_weather_emoji(weather_id))  # Show emoji
        self.description_label.setText(description.capitalize())      # Capitalize description

    @staticmethod
    def get_weather_emoji(weather_id):
        # Map weather condition codes to emojis
        if 200 <= weather_id <= 232:
            return "⛈"   # Thunderstorm
        elif 300 <= weather_id <= 321:
            return "🌦"   # Drizzle
        elif 500 <= weather_id <= 531:
            return "🌧"   # Rain
        elif 600 <= weather_id <= 622:
            return "❄"   # Snow
        elif 701 <= weather_id <= 741:
            return "🌫"   # Fog/mist
        elif weather_id == 762:
            return "🌋"   # Volcanic ash
        elif weather_id == 771:
            return "💨"   # Strong wind
        elif weather_id == 781:
            return "🌪"   # Tornado
        elif weather_id == 800:
            return "☀"    # Clear sky
        elif 801 <= weather_id <= 804:
            return "☁"    # Clouds
        else:
            return "🌈"   # Default (miscellaneous)

# Launch the application
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create QApplication instance
    weather_app = WeatherApp()    # Create an instance of WeatherApp
    weather_app.show()            # Show the app window
    sys.exit(app.exec_())         # Start event loop, exit cleanly when closed
