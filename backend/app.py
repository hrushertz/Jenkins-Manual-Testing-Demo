from flask import Flask, request, jsonify
import os
import json
import requests
import pandas as pd
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import datetime
import threading

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Directory setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File where test cases & test results are stored
TEST_CASES_FILE = os.path.join(UPLOAD_FOLDER, "test_cases.json")
TEST_RESULT_FILE = os.path.join(UPLOAD_FOLDER, "test_result.json")

# Jenkins Configuration
JENKINS_URL = os.getenv("JENKINS_URL", "http://localhost:8080/job/testing/")
JENKINS_USER = os.getenv("JENKINS_USER", "your-jenkins-username")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "your-jenkins-api-token")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Thread Lock for JSON File Safety
file_lock = threading.Lock()

# Reset test result at startup
def reset_test_result():
    with file_lock:
        with open(TEST_RESULT_FILE, "w") as f:
            json.dump({"test_result": "Pending"}, f)
    logging.info("🔄 Test result initialized to 'Pending'.")

reset_test_result()

@app.route("/")
def home():
    return jsonify({"message": "Manual Testing Dashboard API is running"}), 200


# 🟢 Notify Dashboard When Testing Starts
@app.route("/testing_started", methods=["POST"])
def testing_started():
    data = request.get_json()
    logging.info(f"📢 Testing Started: {data}")
    
    # Auto-reset test result at each new run
    reset_test_result()
    
    return jsonify({"message": "Testing started notification received"}), 200


# 🟢 Modify the Upload API to Reset Before New Upload
@app.route("/upload_test_cases", methods=["POST"])
def upload_test_cases():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "Only .xlsx files are allowed"}), 400

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(UPLOAD_FOLDER, f"test_cases_{timestamp}.xlsx")
    file.save(file_path)

    try:
        df = pd.read_excel(file_path, skiprows=1)
        expected_columns = ["id", "description", "status"]

        if len(df.columns) >= 3:
            df = df.iloc[:, :3]
            df.columns = expected_columns
        else:
            return jsonify({"error": "Invalid file format. Ensure at least three columns: id, description, status."}), 400

        test_cases = df.to_dict(orient="records")

        with file_lock:
            # 🚨 Reset test_cases.json before saving new test cases
            with open(TEST_CASES_FILE, "w") as f:
                json.dump([], f)  # Empty the file before writing new test cases

            with open(TEST_CASES_FILE, "w") as f:
                json.dump(test_cases, f, indent=4)

        logging.info("✅ Test cases updated successfully")

        return jsonify({"message": "File uploaded and test cases updated successfully!", "test_cases": test_cases}), 200

    except Exception as e:
        logging.error(f"❌ Error processing file: {str(e)}")
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

# 🟢 Fetch Test Cases (For React Dashboard)
@app.route("/get_test_cases", methods=["GET"])
def get_test_cases():
    # 🚨 Ensure test cases file resets on startup or refresh
    if not os.path.exists(TEST_CASES_FILE):
        return jsonify([])  # ✅ Return empty list if file does not exist

    try:
        with file_lock:
            with open(TEST_CASES_FILE, "r") as f:
                test_cases = json.load(f)

            # ✅ If file exists but is empty, return an empty list
            if not test_cases:
                return jsonify([])

        return jsonify(test_cases), 200
    except Exception as e:
        logging.error(f"❌ Error reading test_cases.json: {str(e)}")
        return jsonify({"error": "Failed to read test cases"}), 500


# 🟢 Submit Test Results (Pass/Fail) & Store for Jenkins Polling
@app.route("/submit_result", methods=["POST"])
def submit_result():
    try:
        data = request.get_json()
        logging.info(f"📩 Received Test Result: {data}")

        if not data or "test_result" not in data:
            logging.error("❌ Error: Missing 'test_result' in request payload")
            return jsonify({"error": "Invalid request. 'test_result' is required"}), 400

        test_result = data.get("test_result").capitalize()
        
        if test_result not in ["Pass", "Fail"]:
            logging.error("❌ Error: Invalid test result value")
            return jsonify({"error": "Invalid test result value. Use 'Pass' or 'Fail'"}), 400

        with file_lock:
            with open(TEST_RESULT_FILE, "w") as f:
                json.dump({"test_result": test_result}, f)

        logging.info(f"✅ Test result stored successfully: {test_result}")

        return jsonify({"message": "✅ Test result stored successfully"}), 200

    except Exception as e:
        logging.error(f"❌ Server Error: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


# 🟢 Jenkins will Poll this API for Test Results
@app.route("/get_test_result", methods=["GET"])
def get_test_result():
    if not os.path.exists(TEST_RESULT_FILE):
        return jsonify({"test_result": "Pending"})

    try:
        with file_lock:
            with open(TEST_RESULT_FILE, "r") as f:
                result = json.load(f)

            # 🚀 Send the result to Jenkins
            logging.info(f"📤 Sent Test Result to Jenkins: {result}")

            # 🚨 Reset test result immediately after Jenkins fetches it
            with open(TEST_RESULT_FILE, "w") as f:
                json.dump({"test_result": "Pending"}, f)

        return jsonify(result), 200

    except Exception as e:
        logging.error(f"❌ Error reading test result: {str(e)}")
        return jsonify({"error": "Failed to read test result"}), 500
    

# ✅ API to reset the test result (Use this if Jenkins keeps getting old values)
@app.route("/reset_test_result", methods=["POST"])
def reset_test_result():
    global test_result
    test_result = "Pending"
    logging.info("🔄 Test result reset to 'Pending'")
    
    return jsonify({"message": "Test result reset to 'Pending'"}), 200


# 🟢 Send Notification to Developer on Failure
@app.route("/send_notification", methods=["POST"])
def send_notification():
    data = request.get_json()
    message = data.get("message", "No message provided")
    logging.info(f"📢 Developer Notification: {message}")
    return jsonify({"message": "Developer notified"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)