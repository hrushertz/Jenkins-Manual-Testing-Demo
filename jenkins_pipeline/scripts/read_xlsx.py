import pandas as pd
import json
import requests

# Read the Excel File
df = pd.read_excel("test_cases.xlsx")

# Convert to JSON
test_cases = df.to_dict(orient="records")

# Send Data to Dashboard
dashboard_url = "http://your-dashboard-url/upload_test_cases"
response = requests.post(dashboard_url, json={"test_cases": test_cases})

if response.status_code == 200:
    print("Test cases successfully sent to dashboard ✅")
else:
    print("Failed to send test cases ❌")