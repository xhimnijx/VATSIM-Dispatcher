import pandas as pd
import json
import re
from typing import List, Dict

def create_controller_summary_csv(json_file_path: str, output_csv_path: str):
    """
    Processes VATSIM controller data from a JSON file, extracts area codes and
    controller types, and generates a CSV summary.

    This function reads a JSON file containing a list of online VATSIM controllers.
    It uses a robust regular expression to parse each controller's callsign,
    identifying the airspace area (e.g., 'EGLL', 'LON') and the type of control
    service (e.g., 'TWR', 'GND'). The data is then aggregated into a pandas
    DataFrame, pivoted to create a summary table, and saved as a CSV file.

    Args:
        json_file_path (str): The path to the input JSON file containing VATSIM data.
        output_csv_path (str): The path where the output CSV file will be saved.
    """
    try:
        # Load the JSON data from the provided file path
        with open(json_file_path, 'r') as f:
            data: List[Dict] = json.load(f)

        # Convert the list of dictionaries to a pandas DataFrame
        df = pd.DataFrame(data)

        # Define a function to extract the area code and controller type
        def extract_info_with_lon(callsign: str) -> pd.Series:
            """
            Extracts a three or four-letter area code and controller type from a callsign.
            
            Args:
                callsign (str): The VATSIM controller callsign (e.g., 'LON_N_CTR').
            
            Returns:
                pd.Series: A pandas Series containing the extracted area code and controller type.
            """
            # Regex to find a 3 or 4-letter prefix at the start of the callsign
            area_match = re.search(r'^(\w{3,4})_', callsign)
            area_code = area_match.group(1).upper() if area_match else 'UNKNOWN'

            # Regex to find the controller type at the end of the callsign
            type_match = re.search(r'_(APP|TWR|GND|CTR|DEL|DEP)', callsign)
            controller_type = type_match.group(1) if type_match else 'OTHER'

            return pd.Series([area_code, controller_type])

        # Apply the extraction function to the 'callsign' column of the DataFrame
        df[['area_code', 'controller_type']] = df['callsign'].apply(extract_info_with_lon)

        # Filter out entries that could not be parsed or are not standard controller types
        filtered_df = df[(df['area_code'] != 'UNKNOWN') & (df['controller_type'] != 'OTHER')]

        # Group the data by area code and controller type, then count the occurrences
        controller_counts = filtered_df.groupby(['area_code', 'controller_type']).size().reset_index(name='count')

        # Pivot the table to create the summary, with area codes as rows and controller types as columns
        summary_df = controller_counts.pivot_table(index='area_code', columns='controller_type', values='count', fill_value=0)

        # Calculate a total score for each area by summing the controller counts
        summary_df['Total_Score'] = summary_df.sum(axis=1)

        # Sort the DataFrame in descending order based on the total score
        summary_df = summary_df.sort_values(by='Total_Score', ascending=False)

        # Save the final summary DataFrame to a new CSV file
        summary_df.to_csv(output_csv_path)

        print(f"CSV file '{output_csv_path}' generated successfully.")

    except FileNotFoundError:
        print(f"Error: The file '{json_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Specify the input and output file names
input_file = 'heatmap generator/current_vatsim_data.json'
output_file = 'heatmap generator/vatsim_controller_summary_updated.csv'

# Run the function to generate the CSV file
create_controller_summary_csv(input_file, output_file)