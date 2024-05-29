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
    exclude_languages = {'Ruby', 'Objective-C'}  # Set of languages to exclude

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
        for repo in org.get_repos(type='all'):
            contributors = repo.get_contributors()
            for contributor in contributors:
                if contributor.login == username:
                    repo_languages = repo.get_languages()
                    for language in repo_languages.keys():
                        if language not in exclude_languages:
                            languages.add(language)

    return len(languages), languages

def create_svg(contributions, languages_count, languages):
    svg_content = f"""
    <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="white"/>
        <text x="10" y="20" font-family="Arial" font-size="20" fill="black">GitHub Contributions</text>
        <text x="10" y="50" font-family="Arial" font-size="14" fill="black">Contributions in the last 7 days:</text>
        <text x="10" y="70" font-family="Arial" font-size="14" fill="black">{len(contributions)}</text>
        <text x="10" y="100" font-family="Arial" font-size="20" fill="black">Programming Languages Used</text>
        <text x="10" y="130" font-family="Arial" font-size="14" fill="black">Total Languages:</text>
        <text x="10" y="150" font-family="Arial" font-size="14" fill="black">{languages_count}</text>
        <text x="10" y="180" font-family="Arial" font-size="14" fill="black">Languages:</text>
        <text x="10" y="200" font-family="Arial" font-size="14" fill="black">{", ".join(languages)}</text>
    </svg>
    """
    with open("contributions.svg", "w") as svg_file:
        svg_file.write(svg_content)

def update_readme():
    with open("README.md", "r") as file:
        lines = file.readlines()

    with open("README.md", "w") as file:
        in_marker = False
        for line in lines:
            if line.strip() == "<!-- START CONTRIBUTIONS -->":
                in_marker = True
                file.write(line)
                file.write("\n![Contributions](contributions.png)\n")
                file.write("\n![Contributions](contributions.svg)\n")
            elif line.strip() == "<!-- END CONTRIBUTIONS -->":
                in_marker = False
            elif not in_marker:
                file.write(line)

if __name__ == "__main__":
    username = os.getenv('USERNAME')
    token = os.getenv('PAT_TOKEN')
    organization = 'sinov8'

    if not username or not token:
        raise ValueError("USERNAME and PAT_TOKEN must be set as environment variables.")

    contributions = get_contributions(username, token)
    plot_contributions(contributions)
    
    languages_count, languages = count_languages(username, token, organization)
    create_svg(contributions, languages_count, languages)
    update_readme()
