import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random  # Add this import
import numpy as np  # Add this import

class WeatherDatabase:
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)

    def init_database(self):
        """Initialize database and create tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity INTEGER NOT NULL,
                pressure INTEGER NOT NULL,
                wind_speed REAL NOT NULL,
                description TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_city_timestamp
            ON weather_data(city, timestamp)
        ''')

        conn.commit()
        conn.close()
        print("Database initialized successfully!")

    def insert_weather_data(self, city, temperature, humidity, pressure, wind_speed, description):
        """Insert weather data into database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO weather_data (city, temperature, humidity, pressure, wind_speed, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (city, temperature, humidity, pressure, wind_speed, description))

            conn.commit()
            print(f"Weather data inserted for {city}")

        except Exception as e:
            print(f"Error inserting weather data: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_historical_data(self, city, days=7):
        """Get historical weather data for a city"""
        conn = self.get_connection()

        try:
            # FIXED: Use parameter substitution correctly
            query = '''
                SELECT * FROM weather_data
                WHERE city = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp
            '''

            df = pd.read_sql_query(query, conn, params=(city, days))

            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            return df

        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_all_cities(self):
        """Get list of all cities in database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT DISTINCT city FROM weather_data ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            return cities

        except Exception as e:
            print(f"Error fetching cities: {e}")
            return []
        finally:
            conn.close()

    def get_city_statistics(self, city):
        """Get statistical summary for a city"""
        conn = self.get_connection()

        try:
            query = '''
                SELECT
                    COUNT(*) as total_records,
                    AVG(temperature) as avg_temp,
                    MAX(temperature) as max_temp,
                    MIN(temperature) as min_temp,
                    AVG(humidity) as avg_humidity,
                    AVG(pressure) as avg_pressure,
                    AVG(wind_speed) as avg_wind_speed,
                    MAX(timestamp) as last_update
                FROM weather_data
                WHERE city = ?
            '''

            cursor = conn.cursor()
            cursor.execute(query, (city,))
            result = cursor.fetchone()

            if result:
                stats = {
                    'total_records': result[0],
                    'avg_temperature': round(result[1], 1) if result[1] else 0,
                    'max_temperature': round(result[2], 1) if result[2] else 0,
                    'min_temperature': round(result[3], 1) if result[3] else 0,
                    'avg_humidity': round(result[4], 1) if result[4] else 0,
                    'avg_pressure': round(result[5], 1) if result[5] else 0,
                    'avg_wind_speed': round(result[6], 1) if result[6] else 0,
                    'last_update': result[7]
                }
                return stats
            return {}

        except Exception as e:
            print(f"Error fetching city statistics: {e}")
            return {}
        finally:
            conn.close()

    def delete_old_data(self, days_old=30):
        """Delete data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                DELETE FROM weather_data
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days_old,))

            deleted_rows = cursor.rowcount
            conn.commit()
            print(f"Deleted {deleted_rows} old records")
            return deleted_rows

        except Exception as e:
            print(f"Error deleting old data: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def generate_sample_data(self, days=30, records_per_day=3):
        """Generate comprehensive sample weather data"""
        cities = ["New York", "London", "Tokyo", "Sydney", "Paris", "Berlin", "Mumbai"]

        # Clear existing data
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weather_data")
        conn.commit()
        conn.close()

        print(f"Generating {days} days of sample data for {len(cities)} cities...")

        # Generate sample data
        for day in range(days):
            current_date = datetime.now() - timedelta(days=days-day-1)

            for city in cities:
                # Generate multiple records per day to simulate different times
                for record in range(records_per_day):
                    # Simulate daily temperature variation (colder at night)
                    if record == 0:  # Morning
                        temp_adjust = -2
                    elif record == 1:  # Afternoon
                        temp_adjust = 5
                    else:  # Evening
                        temp_adjust = -1

                    # Get base mock data
                    from weather_api import WeatherAPI
                    weather_api = WeatherAPI(use_mock=True)
                    weather_data = weather_api._get_mock_weather_data(city)

                    # Adjust temperature for time of day
                    weather_data['temperature'] += temp_adjust

                    # Create specific timestamp
                    specific_time = current_date.replace(
                        hour=8 + record * 6,  # 8AM, 2PM, 8PM
                        minute=random.randint(0, 59)
                    )

                    # Insert with specific timestamp
                    self._insert_with_timestamp(
                        weather_data['city'],
                        weather_data['temperature'],
                        weather_data['humidity'],
                        weather_data['pressure'],
                        weather_data['wind_speed'],
                        weather_data['description'],
                        specific_time
                    )

        print("Sample data generation completed!")

    def _insert_with_timestamp(self, city, temperature, humidity, pressure, wind_speed, description, timestamp):
        """Insert data with specific timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO weather_data (city, temperature, humidity, pressure, wind_speed, description, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (city, temperature, humidity, pressure, wind_speed, description, timestamp))

        conn.commit()
        conn.close()

    def get_database_stats(self):
        """Get overall database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            total_records = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_data")
            total_cities = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM weather_data")
            date_range = cursor.fetchone()

            return {
                'total_records': total_records,
                'total_cities': total_cities,
                'date_range': date_range
            }

        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
        finally:
            conn.close()