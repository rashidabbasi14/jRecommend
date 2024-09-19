import os
import importlib
import pkgutil
import requests
import json


from requests.auth import HTTPBasicAuth
from flask import Flask, request, jsonify
from dotenv import load_dotenv
 

# Define the package path (adjust as needed)
package_name = 'components'
package_path = os.path.join(os.path.dirname(__file__), package_name)

# Iterate through the package and sub-packages
for module_info in pkgutil.walk_packages([package_path], package_name + "."):
    # Import the module
    module = importlib.import_module(module_info.name)


from components.common.helper import Helper
from components.ChatGPTManager import ChatGPTManager

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Initialize the ChatGPT Manager using environment variables
api_key = os.getenv("OPENAI_API_KEY")

manager = ChatGPTManager(api_key, Helper.fetch_connection_string())

@app.route('/query', methods=['POST'])
def query():
    """
    API endpoint to handle ChatGPT queries for a specific project_key.
    Expects JSON input with 'project_key' and 'query' fields.
    """

    print("API Called")
    print(request.json)

    data = request.json["issue"]
    fields = request.json["issue"]["fields"]
    project = request.json["issue"]["fields"]["project"]

    project_key = project.get('id')
    issue_key = data.get('key')
    summary = fields.get('summary')
    description = fields.get('description')

    print(project_key)
    print(issue_key)
    print(summary)
    print(description)
    
    if not project_key or not description or not summary:
        return jsonify({'error': 'Project key and query are required fields'}), 400

    aiResponse = manager.query_conversation(project_key, summary, description)

    print("AI Response received")
    # print(aiResponse)

    if(Helper.is_valid_json(aiResponse)):
        content = json.loads(aiResponse)["content"]
    else:
        content = json.loads(f"""
            [
                {{
                    "type": "paragraph",
                    "content": [
                        {{
                            "type": "text",
                            "text": "{aiResponse}"
                        }}
                    ]
                }}
            ]
            """)

    JIRA_URL = os.getenv("JIRA_URL")
    EMAIL = os.getenv("JIRA_EMAIL")
    API_TOKEN = os.getenv("JIRA_API_TOKEN")
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "customfield_10037": {
                "type": "doc",
                "version": 1,
                "content": content
            }
        }
    }

    print(payload)
    print("Updating JIRA Ticket")
    response = requests.put(
        url,
        json=payload,
        headers=headers,
        auth=HTTPBasicAuth(EMAIL, API_TOKEN)
    )
    print("JIRA Ticket udpated. Response = ")
    print(response)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
