import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF

# Load the Excel data
file_path = 'Sammanställning Skellefteå.xlsx'
sheet_name = 'Blad1'
data = pd.read_excel(file_path, sheet_name=sheet_name)

# Select specific rows (5th, 52nd, 53rd, 54th, 55th in Excel; index starts at 0)
selected_rows = data.iloc[[4, 51, 52, 53, 54]]

# Define namespaces
BRICK = Namespace("https://brickschema.org/schema/1.1/Brick#")
EX = Namespace("http://example.org/building#")

# Initialize RDF graph
g = Graph()
g.bind("brick", BRICK)
g.bind("ex", EX)

# Iterate over rows and build RDF triples
for index, row in selected_rows.iterrows():
    # Skip rows without a valid building name
    if pd.isna(row[0]) or "fastigheter" in str(row[0]) or "Beteckning" in str(row[0]) or "Energideklarationer" in str(row[0]):
        continue

    # Extract data from the row
    building_name = row[0]  # Building name
    address = row[1]        # Address
    activity_type = row[2]  # Type of activity
    energy_class = row[3]   # Energy class
    total_energy = row[4]   # Total energy consumption (kWh)
    year_built = row[15]    # Construction year
    floor_area = row[18]    # Floor area (m²)

    # Create building entity
    building_uri = EX[building_name.replace(" ", "_")]
    g.add((building_uri, RDF.type, BRICK.Building))
    g.add((building_uri, BRICK.hasAddress, Literal(address)))
    g.add((building_uri, BRICK.hasActivityType, Literal(activity_type)))
    g.add((building_uri, BRICK.energyClass, Literal(energy_class)))

    # Safely handle construction year and floor area
    if not pd.isna(year_built):
        try:
            g.add((building_uri, BRICK.yearBuilt, Literal(int(year_built))))
        except ValueError:
            print(f"Invalid construction year '{year_built}' for building '{building_name}'. Skipping this field.")

    if not pd.isna(floor_area):
        try:
            g.add((building_uri, BRICK.hasFloorArea, Literal(float(floor_area))))
        except ValueError:
            print(f"Invalid floor area '{floor_area}' for building '{building_name}'. Skipping this field.")

    # Add energy consumption data
    if not pd.isna(total_energy):
        energy_usage_uri = EX[f"{building_name.replace(' ', '_')}_EnergyUsage"]
        g.add((energy_usage_uri, RDF.type, BRICK.Energy_Usage))
        g.add((energy_usage_uri, BRICK.totalEnergy, Literal(float(total_energy))))  # Total energy in kWh
        g.add((building_uri, BRICK.hasPart, energy_usage_uri))
    else:
        print(f"Missing energy consumption data for building '{building_name}'. Skipping energy usage entity.")

# Serialize the graph to an RDF file
output_file = "buildings_energy.ttl"
g.serialize(destination=output_file, format="turtle")
print(f"RDF data has been written to {output_file}")
