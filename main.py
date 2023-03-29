import flask
import openai
import os
import requests
import subprocess
import time
import tomli

app = flask.Flask(__name__)

target_folder = '/opt/project'

def clone_repository(repo_url, target_folder):
    if not os.path.exists(target_folder):
        subprocess.run(['git', 'clone', repo_url, target_folder], check=True)

def get_env_var(name, default=None):
    value = os.getenv(name, default)
    if not value:
        raise ValueError(f"Error: {name} environment variable not set.")
    return value

def get_version_from_pyproject_toml():
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pyproject.toml"), "rb") as f:
        pyproject_toml = tomli.load(f)

    return pyproject_toml["tool"]["poetry"]["version"]

version = get_version_from_pyproject_toml()

def _get_file_tree(file, path, indent='', is_last=False):
    items = [item for item in os.listdir(path) if item != '.git']
    items_count = len(items)

    for index, item in enumerate(items):
        item_path = os.path.join(path, item)
        if index + 1 == items_count:
            print(f"{indent}└── {item}", end='/\n' if os.path.isdir(item_path) else '\n', file=file)
            new_indent = indent + '    '
        else:
            print(f"{indent}├── {item}", end='/\n' if os.path.isdir(item_path) else '\n', file=file)
            new_indent = indent + '│   '

        if os.path.isdir(item_path):
            _get_file_tree(item_path, new_indent)

def get_file_tree(path):
    import io
    project_tree = io.StringIO()
    _get_file_tree(project_tree, path)
    return project_tree.getvalue()

class GitHubAPI:
    def __init__(self, api_key, repo_url):
        self.api_key = api_key
        self.owner, self.repo = self.parse_repository_url(repo_url)

    def get_headers(self):
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def call_api(self, path, method="GET", **kwargs):
        url = f"https://api.github.com{path}"
        response = requests.request(method, url, headers=self.get_headers(), **kwargs)
        response.raise_for_status()
        return response.json()

    def parse_repository_url(self, url):
        path = url.replace("https://github.com/", "").rstrip(".git")
        owner, repo = path.split("/", 1)
        return owner, repo

    def get_repo_issues(self, state='open', assignee=None):
        path = f"/repos/{self.owner}/{self.repo}/issues"
        params = {'state': state}
        if assignee:
            params['assignee'] = assignee
        return self.call_api(path, params=params)

    def get_issue_comments(self, issue_number):
        path = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        return self.call_api(path)

    def create_issue_comment(self, issue_number, comment_body):
        path = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        data = {"body": comment_body}
        return self.call_api(path, method="POST", json=data)

class OpenAIClient:
    def __init__(self, api_key, user):
        self.api_key = api_key
        openai.api_key = api_key
        self.user = user
        self.context = {}
        self.rules = None
        try:
            with open('rules.txt', 'r') as f:
                self.rules = f.readlines()
        except FileNotFoundError:
            print("Info: 'rules.txt' file not found. Using an empty rules list.")
            self.rules = []

    def process_issue(self, issue, comments):
        title = issue['title']
        body = issue['body']

        messages=[]

        for rule in self.rules:
            if not rule:
                continue
            role, content = rule.split(':', maxsplit=1)
            messages.append({"role": role.strip(), "content": content.strip()})

        messages.append({"role": "system", "content": f'This is project structure:\n{get_file_tree(target_folder)}'})
        messages.append({"role": "system", "content": f'- Task title: {title}\n- Task description: {body}'})

        if comments:
            for comment in comments:
                comment_author = comment['user']['login']
                comment_body = comment['body']

                if comment_author == self.user:
                    messages.append({"role": "assistant", "content": f'{comment_body}'})
                else:
                    messages.append({"role": "user", "content": f'@{comment_author}: {comment_body}'})

        print('\nRequest:')
        for message in messages:
            print(message['role'], message['content'])

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        content = response.choices[0].message.content.strip()

        print('Response:', content)

        return content

class TaskProcessor:
    def __init__(self, github_api_key, repo_url, user, openai_api_key):
        self.github_api = GitHubAPI(github_api_key, repo_url)
        self.user= user
        self.openai_client = OpenAIClient(openai_api_key, self.user)

    def process_tasks(self):
        assigned_issues = self.github_api.get_repo_issues(assignee=self.user)

        for issue in assigned_issues:
            issue_number = issue["number"]
            comments = self.github_api.get_issue_comments(issue_number)
            if comments and comments[-1]['user']['login'] == self.user:
                continue

            comment = self.openai_client.process_issue(issue, comments)
            self.github_api.create_issue_comment(issue_number, comment)

@app.route('/')
def home():
    return flask.jsonify({"version": version}), 200

@app.route('/api/notify')
def notify():
    task_processor.process_tasks()
    return flask.jsonify({"status": "Success"}), 200

def main():
    github_api_key = get_env_var('PROJECT_ACCOUNT_API_KEY')
    repo_url = get_env_var('PROJECT_REPOSITORY')
    user_login = get_env_var('PROJECT_USER', 'JinnyAssistant')
    openai_api_key = get_env_var('OPENAI_API_KEY')

    clone_repository(repo_url, target_folder)

    os.chdir(target_folder)

    print(f"File tree for {target_folder}:")
    print(get_file_tree(target_folder))

    global task_processor
    task_processor = TaskProcessor(github_api_key, repo_url, user_login, openai_api_key)

    if 'LISTEN_PORT_FOR_EVENTS' in os.environ:
        app.run(debug=True, host='0.0.0.0', port=int(os.environ['LISTEN_PORT_FOR_EVENTS']))
    else:
        polling_time = int(os.environ.get('POLLING_TIME', 5)) * 60
        while True:
            task_processor.process_tasks()
            time.sleep(polling_time)

if __name__ == "__main__":
    main()
