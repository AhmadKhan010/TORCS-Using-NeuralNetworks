import pandas as pd
import os

# Specify your directory path
directory = "C:\\Users\\Pc\\Downloads\\pyScrcClient-master\\pyScrcClient-master\\logs"

# Create an empty list to store dataframes
all_dataframes = []

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        # Read each CSV file and append to the list
        file_path = os.path.join(directory, filename)
        df = pd.read_csv(file_path)
        all_dataframes.append(df)

# Concatenate all dataframes
combined_df = pd.concat(all_dataframes, ignore_index=True)

# Save to a new CSV file
combined_df.to_csv('combined_output.csv', index=False)