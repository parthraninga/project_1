import os
import subprocess

def run_git_command(command, cwd="."):
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        raise

def format_branch_name(issue_key, summary):
    # Make a safe Git branch name
    safe_summary = summary.lower().replace(" ", "").replace("/", "")[:40]
    return f"{issue_key}_{safe_summary}"

def create_and_push_branch(base_branch, new_branch):
    run_git_command(["git", "checkout", base_branch])

    branches = subprocess.check_output(["git", "branch"], text=True)
    if new_branch in branches:
        run_git_command(["git", "checkout", new_branch])
    else:
        run_git_command(["git", "checkout", "-b", new_branch])
        run_git_command(["git", "push", "-u", "origin", new_branch])

def commit_and_push_changes(issue_key, file_path):
    run_git_command(["git", "add", file_path])
    run_git_command(["git", "commit", "-m", f"Add code for {issue_key}"])
    run_git_command(["git", "push"])

def automate_git_for_issues(jira, project_key="WEAT", base_branch="Weather", code_dir="generated"):
    jql = f'project = {project_key} AND status = "To Do" ORDER BY created ASC'
    issues = jira.search_issues(jql)

    # Ensure Weather branch exists
    run_git_command(["git", "checkout", "main"])

    # Check if branch exists
    branches = subprocess.check_output(["git", "branch"], text=True)
    if base_branch in branches:
        run_git_command(["git", "checkout", base_branch])
    else:
        run_git_command(["git", "checkout", "-b", base_branch])
        run_git_command(["git", "push", "-u", "origin", base_branch])

    for issue in issues:
        issue_key = issue.key
        summary = issue.fields.summary or "task"
        branch_name = format_branch_name(issue_key, summary)

        print(f"\n🔧 Processing: {branch_name}")
        try:
            create_and_push_branch(base_branch, branch_name)

            code_file = f"{code_dir}/{issue_key}.py"
            if os.path.exists(code_file):
                commit_and_push_changes(issue_key, code_file)
            else:
                print(f"⚠ Code file not found: {code_file}")
        except Exception as e:
            print(f"❌ Failed to process {branch_name}: {e}")