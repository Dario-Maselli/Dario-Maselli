import matplotlib.pyplot as plt
from github import Github
import datetime
import os

def get_contributions(username, token):
    g = Github(token)
    user = g.get_user(username)
    events = user.get_events()
    contributions = []

    for event in events:
        if event.created_at.date() > datetime.datetime.now().date() - datetime.timedelta(days=7):
            contributions.append(event.created_at)

    return contributions

def plot_contributions(contributions):
    dates = [c.date() for c in contributions]
    dates_count = {date: dates.count(date) for date in set(dates)}

    fig, ax = plt.subplots()
    ax.bar(dates_count.keys(), dates_count.values())

    plt.xlabel('Date')
    plt.ylabel('Contributions')
    plt.title('GitHub Contributions in the Last 7 Days')

    plt.savefig('contributions.png')

def count_languages(username, token, organization=None):
    g = Github(token)
    languages = set()
    exclude_languages = {'Ruby', 'Objective-C', 'Blade', 'C'}  # Set of languages to exclude

    # Include user repositories
    user = g.get_user(username)
    repos = user.get_repos()

    for repo in repos:
        repo_languages = repo.get_languages()
        for language in repo_languages.keys():
            if language not in exclude_languages:
                languages.add(language)

    # Include organization repositories if specified
    if organization:
        org = g.get_organization(organization)
        print("Organization Repositories:")
        for repo in org.get_repos(type='all'):
            print(repo.name)
            contributors = repo.get_contributors()
            for contributor in contributors:
                if contributor.login == username:
                    repo_languages = repo.get_languages()
                    for language in repo_languages.keys():
                        if language not in exclude_languages:
                            languages.add(language)

    return len(languages), languages

def update_readme(languages_count, languages):
    with open("README.md", "r") as file:
        lines = file.readlines()

    with open("README.md", "w") as file:
        in_marker = False
        for line in lines:
            if line.strip() == "<!-- START CONTRIBUTIONS -->":
                in_marker = True
                file.write(line)
                file.write("## This is a 'Work In Progress'\n")
                file.write("\n![Contributions](contributions.png)\n")
                file.write(f"\nTotal Programming Languages Used: {languages_count}\n")
                file.write("\nLanguages: " + ", ".join(languages) + "\n")
            elif line.strip() == "<!-- END CONTRIBUTIONS -->":
                in_marker = False
            elif not in_marker:
                file.write(line)
        file.write("<!-- END CONTRIBUTIONS -->")

if __name__ == "__main__":
    username = os.getenv('USERNAME')
    token = os.getenv('PAT_TOKEN')
    organization = 'sinov8'

    if not username or not token:
        raise ValueError("USERNAME and PAT_TOKEN must be set as environment variables.")

    contributions = get_contributions(username, token)
    plot_contributions(contributions)
    
    languages_count, languages = count_languages(username, token, organization)
    update_readme(languages_count, languages)
