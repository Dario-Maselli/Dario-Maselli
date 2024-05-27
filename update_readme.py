import requests
from datetime import datetime

GITHUB_USERNAME = "your_username"
README_FILE = "README.md"

def fetch_contributions(username):
    response = requests.get(f"https://api.github.com/users/{username}/events/public")
    events = response.json()
    contributions = 0
    for event in events:
        if event['type'] in ['PushEvent', 'PullRequestEvent']:
            contributions += 1
    return contributions

def fetch_languages(username):
    response = requests.get(f"https://api.github.com/users/{username}/repos")
    repos = response.json()
    languages = {}
    for repo in repos:
        lang_response = requests.get(repo['languages_url'])
        repo_languages = lang_response.json()
        for lang, bytes_count in repo_languages.items():
            if lang in languages:
                languages[lang] += bytes_count
            else:
                languages[lang] = bytes_count
    return languages

def update_readme(contributions, languages):
    with open(README_FILE, "r") as file:
        readme_content = file.readlines()

    new_content = []
    for line in readme_content:
        if line.startswith("<!-- CONTRIBUTIONS:"):
            new_content.append(f"<!-- CONTRIBUTIONS: {contributions} -->\n")
        elif line.startswith("<!-- LANGUAGES:"):
            lang_str = ', '.join([f"{lang}: {count}" for lang, count in languages.items()])
            new_content.append(f"<!-- LANGUAGES: {lang_str} -->\n")
        else:
            new_content.append(line)

    with open(README_FILE, "w") as file:
        file.writelines(new_content)

if __name__ == "__main__":
    contributions = fetch_contributions(GITHUB_USERNAME)
    languages = fetch_languages(GITHUB_USERNAME)
    update_readme(contributions, languages)
