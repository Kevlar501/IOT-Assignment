#!/bin/bash

# 1. Move into the data folder and reset files
cd data
rm -f latest.jpg
rm -f sensor_log.csv
echo "timestamp, temperature, humidity, pressure" > sensor_log.csv

# 2. Move into the images folder and delete everything
cd images
rm -f *

# 3. Move into the sensor folder and clear pycache
cd ../../sensor/__pycache__
rm -rf *

echo "Cleanup complete!"