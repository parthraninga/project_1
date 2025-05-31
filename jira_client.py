# c:\Users\Parth\Desktop\project_1\jira_client.py
def fetch_todo_issues_for_all_projects(jira):
    """Yields (project, issues) for all projects with todo issues."""
    projects = jira.projects()
    for project in projects:
        jql = f'project = {project.key} AND status = "To Do" ORDER BY created DESC'
        issues = jira.search_issues(jql)
        if issues:
            yield project, issues