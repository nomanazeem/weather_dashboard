import database

# Test database creation
db = database.WeatherDatabase()

# Generate sample data
db.generate_sample_data(days=7, records_per_day=2)

# Check if cities are available
cities = db.get_all_cities()
print("Available cities:", cities)

# Check database stats
stats = db.get_database_stats()
print("Database stats:", stats)