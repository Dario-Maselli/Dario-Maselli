import matplotlib.pyplot as plt
from github import Github
import datetime
import os
from collections import defaultdict
from math import cos, sin, radians, pi
import random

# Define a mapping of file extensions to programming languages
extension_to_language = {
    'py': 'Python',
    'js': 'JavaScript',
    'java': 'Java',
    'rb': 'Ruby',
    'php': 'PHP',
    'cpp': 'C++',
    'c': 'C',
    'cs': 'C#',
    'html': 'HTML',
    'css': 'CSS',
    'swift': 'Swift',
    'go': 'Go',
    'ts': 'TypeScript',
    'kt': 'Kotlin',
    'dart': 'Dart'
}

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
    languages = defaultdict(int)
    exclude_languages = {'Ruby', 'Objective-C'}  # Set of languages to exclude

    # Include user repositories
    user = g.get_user(username)
    repos = user.get_repos()

    for repo in repos:
        try:
            commits = repo.get_commits(author=username)
            for commit in commits:
                files = commit.files
                for file in files:
                    extension = file.filename.split('.')[-1]
                    language = extension_to_language.get(extension)
                    if language and language not in exclude_languages:
                        languages[language] += file.additions + file.deletions
        except Exception as e:
            print(f"Skipping repository {repo.name} due to error: {e}")

    # Include organization repositories if specified
    if organization:
        org = g.get_organization(organization)
        print("Organization Repositories:")
        for repo in org.get_repos(type='all'):
            print(repo.name)
            try:
                commits = repo.get_commits(author=username)
                for commit in commits:
                    files = commit.files
                    for file in files:
                        extension = file.filename.split('.')[-1]
                        language = extension_to_language.get(extension)
                        if language and language not in exclude_languages:
                            languages[language] += file.additions + file.deletions
            except Exception as e:
                print(f"Skipping repository {repo.name} due to error: {e}")

    # Get the top 5 languages by lines of code changed
    sorted_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:5]
    top_languages = {language: lines for language, lines in sorted_languages}

    return len(top_languages), top_languages

def generate_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def create_3d_contrib_graph(contributions):
    dates = [c.date() for c in contributions]
    dates_count = {date: dates.count(date) for date in set(dates)}
    max_contrib = max(dates_count.values(), default=1)
    days = sorted(dates_count.keys())

    graph_elements = []
    for i, day in enumerate(days):
        height = (dates_count[day] / max_contrib) * 100
        graph_elements.append(f'<rect x="{i*5}" y="{100-height}" width="4" height="{height}" fill="#66b3ff"/>')
    
    return "\n".join(graph_elements)

def create_svg(contributions, languages_count, languages):
    # Define colors for the pie chart
    colors = ["#ff9999","#66b3ff","#99ff99","#ffcc99","#c2c2f0","#ffb3e6","#c2f0c2","#ff6666"]
    while len(colors) < languages_count:
        colors.append(generate_color())
    
    # Calculate the pie chart data
    total = sum(languages.values())
    angles = [(value / total) * 360 for value in languages.values()]
    
    # Create the 3D contribution graph
    contrib_graph = create_3d_contrib_graph(contributions)
    
    # Create the SVG content
    svg_content = f"""
    <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="rgb(10, 10, 30)"/>
        <text x="10" y="20" font-family="Arial" font-size="20" fill="white">GitHub Contributions</text>
        <text x="10" y="50" font-family="Arial" font-size="14" fill="white">Contributions in the last 7 days:</text>
        <text x="10" y="70" font-family="Arial" font-size="14" fill="white">{len(contributions)}</text>
        <text x="10" y="100" font-family="Arial" font-size="20" fill="white">Programming Languages Used</text>
        <text x="10" y="130" font-family="Arial" font-size="14" fill="white">Total Languages:</text>
        <text x="10" y="150" font-family="Arial" font-size="14" fill="white">{languages_count}</text>
        <g transform="translate(300, 200)">
    """

    start_angle = 0
    for i, (language, angle) in enumerate(zip(languages.keys(), angles)):
        end_angle = start_angle + angle
        x1 = 100 * cos(radians(start_angle))
        y1 = 100 * sin(radians(start_angle))
        x2 = 100 * cos(radians(end_angle))
        y2 = 100 * sin(radians(end_angle))
        large_arc_flag = 1 if angle > 180 else 0

        path_d = f"M0,0 L{x1},{y1} A100,100 0 {large_arc_flag},1 {x2},{y2} Z"
        mid_angle = start_angle + (angle / 2)
        label_x = 120 * cos(radians(mid_angle))
        label_y = 120 * sin(radians(mid_angle))
        
        svg_content += f"""
        <path d="{path_d}" fill="{colors[i]}" opacity="0">
            <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{i * 0.5}s" fill="freeze"/>
        </path>
        <text x="{label_x}" y="{label_y}" font-family="Arial" font-size="14" fill="white" text-anchor="middle" alignment-baseline="middle">{language}</text>
        """
        start_angle += angle
    
    svg_content += "</g>"
    svg_content += f"""
        <g transform="translate(100, 350)">
            {contrib_graph}
        </g>
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
                file.write("## This is a 'Work In Progress'\n")
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
