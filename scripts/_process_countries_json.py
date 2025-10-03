import json
import os

script_path = os.path.dirname(os.path.abspath(__file__))

input_file = os.path.join(script_path, '../static', 'regions.json')

output_file = os.path.join(script_path, '../static', 'regions_output.json')

# Load JSON
with open(input_file, "r", encoding="utf-8") as f:
    countries = json.load(f)

# Transform: Country -> List of states
country_states = {
    country["name"]: [state["name"] for state in country.get("states", [])]
    for country in countries
}

# Save result back to JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(country_states, f, indent=4, ensure_ascii=False)

print(f"✅ File saved to: {output_file}")
