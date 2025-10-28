import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import database
import weather_api
import numpy as np  # Add this import

# Configure the page
st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide"
)

# Initialize components
db = database.WeatherDatabase()
weather = weather_api.WeatherAPI(use_mock=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🌤️ Weather Dashboard")
st.sidebar.markdown("---")

# Database operations
st.sidebar.subheader("Database Operations")
if st.sidebar.button("🗃️ Generate Sample Data"):
    with st.spinner("Generating sample data... This may take a few seconds."):
        db.generate_sample_data(days=30, records_per_day=3)
    st.sidebar.success("Sample data generated successfully!")

if st.sidebar.button("🧹 Clean Old Data"):
    deleted_count = db.delete_old_data(days_old=60)
    st.sidebar.success(f"Deleted {deleted_count} old records")

# Database statistics
db_stats = db.get_database_stats()
if db_stats:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Database Stats")
    st.sidebar.write(f"Total Records: {db_stats['total_records']}")
    st.sidebar.write(f"Cities: {db_stats['total_cities']}")

# City selection
cities = db.get_all_cities()
if not cities:
    st.error("❌ No weather data available. Please generate sample data first.")
    st.stop()

selected_city = st.sidebar.selectbox("📍 Select City", cities)

# Date range selection
days = st.sidebar.slider("📅 Historical Data Days", 1, 90, 7)

# Real API toggle
use_real_api = st.sidebar.checkbox("Use Real Weather API", value=False)
if use_real_api:
    api_key = st.sidebar.text_input("OpenWeatherMap API Key", type="password")
    if api_key:
        weather = weather_api.WeatherAPI(use_mock=False, api_key=api_key)
    else:
        st.sidebar.warning("Please enter your API key")

# Main content
st.markdown(f'<div class="main-header">Weather Dashboard - {selected_city}</div>', unsafe_allow_html=True)
st.markdown("---")

# Get current weather
try:
    current_weather = weather.get_current_weather(selected_city)

    # Display current weather in cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="🌡️ Temperature",
            value=f"{current_weather['temperature']}°C",
            delta=f"{random.choice(['-2°C', '-1°C', '+1°C', '+2°C'])} from yesterday"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💧 Humidity",
            value=f"{current_weather['humidity']}%"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="📊 Pressure",
            value=f"{current_weather['pressure']} hPa"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💨 Wind Speed",
            value=f"{current_weather['wind_speed']} m/s"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Weather description with emoji
    weather_emojis = {
        "Clear": "☀️",
        "Cloudy": "☁️",
        "Rain": "🌧️",
        "Snow": "❄️",
        "Fog": "🌫️",
        "Thunderstorm": "⛈️"
    }
    emoji = weather_emojis.get(current_weather['description'], "🌤️")

    st.subheader(f"{emoji} Current Conditions: {current_weather['description']}")

    # Store current weather in database
    db.insert_weather_data(
        current_weather['city'],
        current_weather['temperature'],
        current_weather['humidity'],
        current_weather['pressure'],
        current_weather['wind_speed'],
        current_weather['description']
    )

except Exception as e:
    st.error(f"Error fetching current weather: {e}")

# Get historical data
historical_data = db.get_historical_data(selected_city, days)

if not historical_data.empty:
    # Convert timestamp to datetime
    historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])

    # Create visualizations
    st.subheader(f"📈 Historical Data - Last {days} Days")

    # Create multiple tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["📊 Temperature Analysis", "🌧️ Weather Patterns", "📋 Raw Data"])

    with tab1:
        # Temperature chart with trend line
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Temperature plot
        ax1.plot(historical_data['timestamp'], historical_data['temperature'],
                 marker='o', linewidth=2, color='red', alpha=0.7, label='Temperature')

        # Add trend line (only if we have enough data points)
        if len(historical_data) > 1:
            try:
                z = np.polyfit(range(len(historical_data)), historical_data['temperature'], 1)
                p = np.poly1d(z)
                ax1.plot(historical_data['timestamp'], p(range(len(historical_data))),
                        '--', color='darkred', linewidth=1, label='Trend')
            except Exception as e:
                print(f"Could not create trend line: {e}")

        ax1.set_title(f'Temperature Trend - {selected_city}')
        ax1.set_ylabel('Temperature (°C)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        # Humidity and Pressure subplot
        ax2b = ax2.twinx()
        ax2.plot(historical_data['timestamp'], historical_data['humidity'],
                marker='s', linewidth=2, color='blue', alpha=0.7, label='Humidity')
        ax2b.plot(historical_data['timestamp'], historical_data['pressure'],
                 marker='^', linewidth=2, color='green', alpha=0.7, label='Pressure')

        ax2.set_xlabel('Date')
        ax2.set_ylabel('Humidity (%)', color='blue')
        ax2b.set_ylabel('Pressure (hPa)', color='green')
        ax2.legend(loc='upper left')
        ax2b.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

        plt.tight_layout()
        st.pyplot(fig)

    with tab2:
        # Weather patterns analysis
        col1, col2 = st.columns(2)

        with col1:
            # Weather condition distribution
            weather_counts = historical_data['description'].value_counts()
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            weather_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax2)
            ax2.set_title('Weather Condition Distribution')
            st.pyplot(fig2)

        with col2:
            # Wind speed distribution
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            ax3.hist(historical_data['wind_speed'], bins=10, alpha=0.7, color='orange')
            ax3.set_title('Wind Speed Distribution')
            ax3.set_xlabel('Wind Speed (m/s)')
            ax3.set_ylabel('Frequency')
            ax3.grid(True, alpha=0.3)
            st.pyplot(fig3)

    with tab3:
        # Statistics
        city_stats = db.get_city_statistics(selected_city)
        if city_stats:
            st.subheader("📊 City Statistics")
            cols = st.columns(4)
            stats_to_show = [
                ('avg_temperature', '🌡️ Avg Temp', '°C'),
                ('max_temperature', '🔥 Max Temp', '°C'),
                ('min_temperature', '❄️ Min Temp', '°C'),
                ('avg_humidity', '💧 Avg Humidity', '%')
            ]

            for (stat_key, stat_label, unit), col in zip(stats_to_show, cols):
                with col:
                    st.metric(stat_label, f"{city_stats.get(stat_key, 0)}{unit}")

        # Raw data table
        st.subheader("📋 Raw Data")
        display_data = historical_data[['timestamp', 'temperature', 'humidity',
                                      'pressure', 'wind_speed', 'description']].copy()
        display_data['timestamp'] = display_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(display_data, use_container_width=True)

        # Download data
        csv = historical_data.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"weather_data_{selected_city}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    st.info("ℹ️ No historical data available for the selected period.")

# Footer
st.markdown("---")
st.markdown("### 🚀 Weather Dashboard POC")
st.markdown("Built with Python, Streamlit, Pandas, Matplotlib, and SQLite")
st.markdown("**Features:** Real-time data • Historical analysis • Data visualization • CSV export")