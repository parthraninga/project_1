# c:\Users\Parth\Desktop\project_1\workflow_generator.py
from .jira_client import fetch_todo_issues_for_all_projects
from .implementor import move_issue_to_in_progress

def generate_workflow(issue_key, summary, description):
    # ... your OpenAI call and strict prompt here ...
    pass  # (put your OpenAI logic here)

def fetch_and_generate_workflows(jira):
    for project, issues in fetch_todo_issues_for_all_projects(jira):
        for issue in issues:
            summary = issue.fields.summary
            description = issue.fields.description or "No description provided."
            workflow = generate_workflow(issue.key, summary, description)
            # write workflow file:
            file_name = f"workflow_{issue.key}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(f"{issue.key}: {summary}\nDescription: {description}\n\nWorkflow:\n{workflow}\n")
            move_issue_to_in_progress(jira, issue)
            # You could call implement_issue_workflow_with_openai(issue.key) here if wanted