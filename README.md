# Jira Project Issue Fetcher

This Python script connects to a Jira Cloud instance and fetches all "To Do" issues for a selected project.

## Features
- Secure connection to Jira using API token and email.
- Lists all accessible projects.
- Fetches and displays “To Do” issues for a specified project.

## Setup

1. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

2. Export your Jira details as environment variables (recommended):
   
   On Windows:
   ```sh
   set JIRA_SERVER=https://your-domain.atlassian.net/
   set JIRA_EMAIL=your-email@example.com
   set JIRA_API_TOKEN=your-api-token
   ```

3. Run the script:

   ```sh
   python main.py
   ```

   Or, enter your credentials when prompted.

## Security
Do NOT hardcode sensitive information. Always use environment variables or prompt input for credentials.