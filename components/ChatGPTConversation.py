import openai

class ChatGPTConversation:
    """
    Class responsible for managing a conversation with ChatGPT.
    Each conversation is initialized with a different database schema.
    """
    def __init__(self, api_key, schema, project_description):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.schema = schema
        self.messages = [
            {
                "role": "system",
                "content": """**Output in ADF JSON format:**
                        - Only Return the technical specification document in Atlassian Document Format (ADF) JSON structure for proper rendering in JIRA.
                        - Ensure JSON Structure is in Atlassian Document Format and has no error such as INVALID_INPUT .
                    You are acting as a tech lead responsible for creating a technical specification document for JIRA tickets related to a specific application or bug. 
                    Given the application database schema and the project description below, create a tech spec document for below:
                    - **Database Schema Updates:**
                        - Analyze the current schema and propose any necessary database changes.
                        - Provide SQL queries for schema alterations such as creating/modifying tables or columns.
                        - Suggest adding or modifying indexes to optimize performance.
                        
                    - **Code Level Changes:**
                        - Based on the project description, outline potential changes needed in the codebase.
                        - Identify any specific methods, classes, or modules that need to be altered or added.
                        
                    - **Test Cases:**
                        - Propose detailed test cases that should be implemented to validate the changes, covering both unit and integration testing.
                        - Include edge cases, success/failure scenarios, and performance considerations.
                        """
            }
        ]
        # Now, split the schema into chunks if it's larger than a certain token limit
        max_schema_tokens = 2000  # Adjust this value as needed
        # print("Chunking Schema")
        schema_chunks = self.split_schema_into_chunks(self.schema, max_schema_tokens)
        print("Schema Chunks: " + str(len(schema_chunks)))
        # Add each chunk as a separate message
        for i, chunk in enumerate(schema_chunks):
            self.messages.append({
                "role": "assistant",
                "content": f"Schema chunk {i+1}:\n{chunk}"
            })
        # Optionally, let the assistant know that all schema chunks have been provided
        self.messages.append({
            "role": "assistant",
            "content": "All schema chunks have been provided. You can now answer queries based on the schema."
        })

        if project_description:
            self.messages.append({
                "role": "assistant",
                "content": f"Project Description: \n{project_description}"
            })

    def split_schema_into_chunks(self, schema_text, max_tokens):
        # print("Encoding")
        # encoding = tiktoken.encoding_for_model('gpt-4')  # or 'gpt-4' if using GPT-4
        print("Spliting")
        tables = schema_text.strip().split('\n\n')  # Assuming tables are separated by two newlines
        print("Tables: " + str(len(tables)))
        chunks = []
        current_chunk = ''
        current_tokens = 0
        counter = 0

        # print("Chunking..")
        for table in tables:
            counter += 1
            # print("CHUNKING ... " + str(counter))
            table = table.strip()
            if not table:
                continue
            # table_tokens = encoding.encode(table)
            table_tokens = len(table)
            num_table_tokens = (table_tokens)
            if current_tokens + num_table_tokens <= max_tokens:
                if current_chunk:
                    current_chunk += '\n\n' + table
                else:   
                    current_chunk = table
                current_tokens += num_table_tokens
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = table
                current_tokens = num_table_tokens
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def num_tokens_from_messages(self, messages):
        # encoding = tiktoken.encoding_for_model('gpt-4')  # or 'gpt-4' if using GPT-4
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Every message has a fixed overhead
            for key, value in message.items():
                num_tokens += len(value)
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        return num_tokens

    def query(self, user_query):
        print("Sending query to chatGPT.")
        # print(user_query)
        """
        Send a query to ChatGPT and return the response.
        """
        self.messages.append({"role": "user", "content": user_query})
        # Check if total tokens exceed the model's maximum token limit
        max_tokens = 8000  # For GPT-3.5-turbo; adjust accordingly for GPT-4
        num_tokens = self.num_tokens_from_messages(self.messages)
        if num_tokens > max_tokens:
            # Remove older messages (excluding the system prompt and initial schema messages)
            while num_tokens > max_tokens and len(self.messages) > 3:
                # Remove the second message after system prompt (schema chunks are next)
                removed_message = self.messages.pop(3)
                num_tokens = self.num_tokens_from_messages(self.messages)
            if num_tokens > max_tokens:
                return "Error: Message length exceeds the model's maximum token limit."

        print("Messages to CHATGPT:" + str(len(self.messages)))
        # print(self.messages)
        response = openai.chat.completions.create(
            model="gpt-4-turbo",  # or "gpt-4" if you have access
           messages=self.messages
        )
        reply = response.choices[0].message.content
        # Add the assistant's reply to the messages
        self.messages.append({"role": "assistant", "content": reply})
        return reply