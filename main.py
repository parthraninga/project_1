from dotenv import load_dotenv
import shutil
load_dotenv()
import os
import subprocess
import openai
from jira import JIRA
from getpass import getpass
from git_automation import automate_git_for_issues

def get_credentials():
    """Load Jira credentials from environment or prompt user."""
    server = os.getenv('JIRA_SERVER')
    email = os.getenv('JIRA_EMAIL')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    api_token = os.getenv('JIRA_API_TOKEN')
    return server, email, api_token

def connect_to_jira(server, email, api_token):
    """Connect to Jira and return a Jira instance."""
    try:
        jira = JIRA(server=server, basic_auth=(email, api_token))
        return jira
    except Exception as e:
        print(f"Failed to connect to Jira: {e}")
        exit(1)

def fetch_todo_issues_for_all_projects(jira):
    """Fetch and print 'To Do' issues for all accessible projects."""
    projects = jira.projects()
    for project in projects:
        project_key = project.key
        print(f'\n--- "To Do" Issues in Project {project_key}: {project.name} ---')

        jql_query = f'project = {project_key} AND status = "To Do" ORDER BY created DESC'
        try:
            issues = jira.search_issues(jql_query)
            if not issues:
                print("No 'To Do' issues found.")
            else:
                for issue in issues:
                    print(f"{issue.key}: {issue.fields.summary}")
        except Exception as e:
            print(f"Failed to retrieve issues for project {project_key}: {e}")


def fetch_todo_issues_for_all_projects(jira):
    """Fetch and print 'To Do' issues with descriptions for all accessible projects."""
    projects = jira.projects()
    for project in projects:
        project_key = project.key
        print(f'\n--- "To Do" Issues in Project {project_key}: {project.name} ---')

        jql_query = f'project = {project_key} AND status = "To Do" ORDER BY created DESC'
        try:
            issues = jira.search_issues(jql_query)
            if not issues:
                print("No 'To Do' issues found.")
            else:
                for issue in issues:
                    summary = issue.fields.summary
                    description = issue.fields.description or "No description provided."
                    print(f"\n{issue.key}: {summary}\nDescription: {description}")
        except Exception as e:
            print(f"Failed to retrieve issues for project {project_key}: {e}")


# Generate task workflow using OpenAI
# Generate detailed, numbered workflow using OpenAI
def generate_workflow(issue_key, summary, description):
    prompt = f"""You are a senior developer and team lead. Based on the following Jira issue, generate a step-by-step implementation plan in the following strict format:

- Use *numbered sections* and *subsections* (e.g., 1.1, 1.2).
- Describe whether a *function, **API call, or **UI component* is being created or used.
- Include *logical details* and *state handling*.
- Use *clear formatting* with section titles like "User Input Phase", "Frontend Sends Request", etc.
- If API calls are required, show the exact *OpenWeatherMap API endpoint structure*.
- Add *examples* in parentheses where relevant (e.g., "Delhi, Tokyo, Paris").
- Maintain clarity for *UX logic, **refresh, and **sorting*.
- DO NOT use emojis.
- DO NOT use bullets or vague steps. Only use the strict format shown below.

Format Example:
1. User Input Phase  
1.1. Provide a form or input field for the user to enter 3 or more city names.  
1.2. Accept input as a comma-separated list (e.g., Delhi, Tokyo, Paris).  
1.3. Add a "Compare Weather" button that triggers the fetching process.  
...

Here is the Jira issue:

Issue Key: {issue_key}  
Title: {summary}  
Description: {description}

Now generate the detailed numbered workflow below:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",  # Use gpt-4.1 for better instruction following
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating workflow for {issue_key}: {e}"



def fetch_and_generate_workflows(jira):
    """Generate workflows for each issue's 'To Do' and write to a separate file per issue."""
    projects = jira.projects()

    for project in projects:
        project_key = project.key
        project_name = project.name.replace(" ", "_")
        jql_query = f'project = {project_key} AND status = "To Do" ORDER BY created DESC'

        try:
            issues = jira.search_issues(jql_query)
            if not issues:
                continue

            for issue in issues:
                summary = issue.fields.summary
                description = issue.fields.description or "No description provided."
                print(f"Generating workflow for {issue.key} in {project_name}...")
                workflow = generate_workflow(issue.key, summary, description)

                # Write workflow to its own file per issue
                file_name = f"workflow_{issue.key}.txt"
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(f"{issue.key}: {summary}\nDescription: {description}\n\nWorkflow:\n{workflow}\n")
                print(f"✅ Workflow for {issue.key} written to {file_name}")

                # Move issue to In Progress
                move_issue_to_in_progress(jira, issue)

                # Implement code and folder structure for the issue using the workflow file
                implement_issue_workflow_with_openai(issue.key)

        except Exception as e:
            print(f"Error fetching issues for {project_key}: {e}")

def main():
     server, email, api_token = get_credentials()
     jira = connect_to_jira(server, email, api_token)
     fetch_todo_issues_for_all_projects(jira)
     # fetch_and_generate_workflows(jira)
     automate_git_for_issues(jira)

def move_issue_to_in_progress(jira, issue):
    """
    Transitions the given issue to 'In Progress' if a valid transition exists.
    """
    try:
        transitions = jira.transitions(issue)
        # Find the transition id for "In Progress"
        in_progress_transition = next(
            (t for t in transitions if t['name'].lower() == 'in progress'),
            None
        )
        if in_progress_transition:
            jira.transition_issue(issue, in_progress_transition['id'])
            print(f"Moved {issue.key} to In Progress.")
        else:
            print(f"No 'In Progress' transition available for {issue.key}.")
    except Exception as e:
        print(f"Failed to transition {issue.key} to In Progress: {e}")


def implement_issue_workflow_with_openai(issue_key):
    """
    Reads the workflow file for the given issue, creates a folder for the issue,
    and uses OpenAI to generate project files/folders as suggested by the workflow.
    """
    workflow_filename = f"workflow_{issue_key}.txt"
    issue_folder = issue_key

    # Check if file exists
    if not os.path.exists(workflow_filename):
        print(f"Workflow file {workflow_filename} not found.")
        return

    # Read workflow
    with open(workflow_filename, "r", encoding="utf-8") as wf:
        workflow_content = wf.read()

    # Optionally refresh: Delete existing issue folder
    if os.path.exists(issue_folder):
        shutil.rmtree(issue_folder)
    
    os.makedirs(issue_folder, exist_ok=True)

    # Ask OpenAI for the code to implement
    prompt = f"""Read this workflow for a Jira issue below.
For each step, provide a JavaScript-only (not TypeScript!) version with React if UI is needed.
*For each and every workflow (WEAT), you MUST create a new React Vite project (with npm create vite@latest), using JavaScript (JSx) only. Do NOT use TypeScript. This includes the full folder structure, npm dependencies, package.json, and all source files.*
Always use correct Windows folder/file syntax and *never start file paths with a '/' or '\\'*.
Every code file you create must be in JSX. Use npm libraries as needed.
Document each file with: javascript [relative/path/filename.jsx]
...

Workflow:
{workflow_content}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response['choices'][0]['message']['content']
        parse_and_write_ai_files(content, issue_folder)
        print(f"✅ Files generated for {issue_key} inside ./{issue_folder}/")
    except Exception as e:
        print(f"OpenAI error for {issue_key}: {e}")


def parse_and_write_ai_files(ai_content, issue_folder):
    """
    Scans OpenAI's answer for Markdown code blocks with filenames, and writes those to files in the issue folder.
    Handles both bracket [filename] and plain filename formats.
    Logs actual file-writing so you can confirm.
    """
    import re
    import os

    # Regex matches: javascript [path/to/file.js] ... 
    # AND           javascript path/to/file.js ... 
    code_block_pattern = (
        r"(?P<lang>\w+)?(?:\s+\[?(?P<filename>[^\]\n\r]+)\]?)?[\r\n]+(?P<code>[\s\S]+?)```"
    )
    matches = re.findall(code_block_pattern, ai_content)
    written_any = False

    def clean_filename(filename):
        if not filename:
            return None
        filename = filename.strip().replace("\\", "/")
        while filename.startswith("/") or filename.startswith("\\"):
            filename = filename[1:]
        if filename.startswith("./"):
            filename = filename[2:]
        filename = filename.replace("..", "")
        filename = filename.rstrip("/\\")  # remove trailing slash which would indicate dir
        return filename

    for lang, filename, code in matches:
        safe_filename = clean_filename(filename)
        if not safe_filename or not code.strip():
            continue
        path = os.path.join(issue_folder, safe_filename)
        dir_path = os.path.dirname(path)
        abspath = os.path.abspath(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        if not safe_filename.endswith("/") and not safe_filename.endswith("\\"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(code.strip())
            print(f"  - Created {abspath}")
            written_any = True

    if not written_any:
        debugfile = os.path.join(issue_folder, 'ai_debug_output_not_written.txt')
        os.makedirs(issue_folder, exist_ok=True)
        with open(debugfile, "w", encoding="utf-8") as df:
            df.write(ai_content)
        print(f"[Warning] No files written for {issue_folder}! LLM output dumped to: {os.path.abspath(debugfile)}")


        
def implement_all_issue_folders(jira):
    projects = jira.projects()
    for project in projects:
        project_key = project.key
        jql_query = f'project = {project_key} AND status = "In Progress" ORDER BY created DESC'
        try:
            issues = jira.search_issues(jql_query)
            for issue in issues:
                implement_issue_workflow_with_openai(issue.key)
        except Exception as e:
            print(f"Error reading issues for {project_key}: {e}")

if __name__ == "__main__":
    main()
