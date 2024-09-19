import pyodbc
from components.ChatGPTConversation import ChatGPTConversation
from components.DatabaseSchemaFetcher import DatabaseSchemaFetcher

class ChatGPTManager:
    """
    Class responsible for managing multiple ChatGPT conversations based on project_key and connection_string.
    """
    def __init__(self, api_key, projects_connection_string):
        self.api_key = api_key
        self.projects_connection_string = projects_connection_string
        self.conversations = {}
        self.projects = self.fetch_projects()
        print("Init Complete")
        print(self.projects)

    def fetch_projects(self):
        """
        Fetch the project_key and connection_string from the projects table.
        """
        try:
            connection = pyodbc.connect(self.projects_connection_string)
            cursor = connection.cursor()

            # Fetch project keys and corresponding database connection strings
            cursor.execute("SELECT jira_key, connection_string, description FROM projects")
            projects = cursor.fetchall()

            cursor.close()
            connection.close()

            # Convert the result into a dictionary for easier lookup
            return {project[0]: project[1] for project in projects}

        except Exception as e:
            print(f"Error fetching projects: {e}")
            return {}

    def start_conversation(self, project_key):
        print("Starting Conversation with chatGPT for project " + project_key)
        print(self.projects)
        """
        Initialize a new conversation for a project_key if it hasn't been started yet.
        """
        if project_key in self.conversations:
            return f"Conversation for project {project_key} is already started."

        if project_key not in self.projects:
            return f"Project with key {project_key} does not exist."

        # Get the database connection string for the project
        connection_string = self.projects[project_key]
        schema_fetcher = DatabaseSchemaFetcher(connection_string)

        # Fetch schema for the project
        print("Fetching schema")
        schema = schema_fetcher.fetch_schema()
        # print(f"Schema for project {project_key}:\n{schema}")
        print("Schema Fetched")

        # Start a new conversation for the project key
        self.conversations[project_key] = ChatGPTConversation(self.api_key, schema, "")
        return f"Conversation for project {project_key} started."

    def query_conversation(self, project_key, summary, description):
        """
        Send a query to an existing conversation based on the project key.
        """
        if project_key not in self.conversations:
            init_message = self.start_conversation(project_key)
            if "does not exist" in init_message:
                return init_message

        print("Getting Conversation")
        conversation = self.conversations.get(project_key)
        print("Conversation Received")
        if conversation:
            user_query = f"""JIRA Ticket information:
            Summary: {summary}
            Desciption: {description}"""
            return conversation.query(user_query)
        else:
            return f"Error: Unable to initialize conversation for project {project_key}."
