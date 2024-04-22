import requests
from fpdf import FPDF
from datetime import datetime

# Jira credentials and URL
JIRA_URL = "https://example.net/"
USERNAME = "username"  # Change this to your username
API_TOKEN = "api_token"
# ^^^ change API token to your API token

# JQL query to search for issues with the #implem tag, ordered by updated date descending
jql_query = 'JQL_query'

# API endpoint for searching issues
api_url = f"{JIRA_URL}/rest/api/3/search"

# Headers for API request
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Authentication
auth = (USERNAME, API_TOKEN)

# Parameters for the JIRA search
params = {
    "jql": jql_query,
    "maxResults": 100,
    "fields": "key,summary,assignee,reporter,status,resolution,created,updated,duedate,project,issuetype,priority"
}

def generate_pdf(data):
    pdf = FPDF(orientation='L')  # Set orientation to landscape
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=10)

    # Group issues by project
    projects = {}
    for issue in data:
        project_name = issue['fields']['project']['name']
        if project_name not in projects:
            projects[project_name] = []
        projects[project_name].append(issue)

    # Add page before the loop starts
    pdf.add_page()

    # Iterate over projects
    for project_name, project_issues in projects.items():
        # Header for the project
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Project: {project_name}", ln=True, align='C')
        pdf.set_font("Arial", size=10)

        # Headers for the table
        headers = ["Type", "Key", "Summary", "Assignee", "Reporter", "Priority", "Status", "Created", "Updated", "Due Date"]
        col_widths = [20, 35, 90, 22, 22, 16, 20, 18, 18, 18]  # Adjusted column widths
        for header, width in zip(headers, col_widths):
            pdf.cell(width, 10, header, 1, 0, 'C')
        pdf.ln()

        # Data rows
        for issue in project_issues:
            print(issue['fields'].keys())
            for field, width in zip(
                    [
                        issue["fields"]["issuetype"]["name"],
                        issue['key'],
                        (issue['fields']['summary'][:43] + '...') if len(issue['fields']['summary']) > 25 else
                        issue['fields']['summary'],
                        (issue['fields']['assignee']['displayName'][:9] + '...') if issue['fields']['assignee'] else "",
                        (issue['fields']['reporter']['displayName'][:9] + '...') if issue['fields']['reporter'] else "",
                        issue['fields']['priority']['name'],
                        issue['fields']['status']['name'],
                        datetime.strptime(issue['fields']['created'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d/%b/%y'),
                        datetime.strptime(issue['fields']['updated'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d/%b/%y'),
                        datetime.strptime(issue['fields'].get('duedate', '')[:10], '%Y-%m-%d').strftime('%d/%b/%y') if issue['fields'].get('duedate', '') else "--"
                    ],
                    col_widths
            ):

                if field == issue['key']:
                    pdf.set_text_color(0, 0, 255)
                    pdf.set_font("Arial", style='U')
                    pdf.cell(width, 10, field, 1, 0, 'C', link=JIRA_URL + "browse/" + field)
                    pdf.set_text_color(0)
                    pdf.set_font("Arial", size=10)
                else:
                    pdf.cell(width, 10, field, 1, 0, 'C')
            pdf.ln()

    pdf.output("jira_issues.pdf")

# Send request to JIRA API
response = requests.get(api_url, headers=headers, params=params, auth=auth)

if response.status_code == 200:
    # Generate PDF if data is successfully fetched
    data = response.json().get('issues', [])
    generate_pdf(data)
    print("PDF generated successfully!")
else:
    print(f"Failed to fetch data: {response.status_code} - {response.text}")
