# c:\Users\Parth\Desktop\project_1\config.py
from dotenv import load_dotenv
import os
from jira import JIRA
import openai

load_dotenv()

def get_jira():
    server = os.getenv('JIRA_SERVER')
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if not (server and email and api_token):
        raise ValueError("Missing Jira credentials in environment.")
    return JIRA(server=server, basic_auth=(email, api_token))