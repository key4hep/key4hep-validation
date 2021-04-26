import requests
from dateutil import parser

ORG = 'key4hep'
baseurl_wfl = "https://api.github.com/repos/{repo}/actions/workflows"
baseurl_repo = "https://api.github.com/orgs/{org}/repos"

def Request(url):
  try:
    request = requests.get(url = url)
    data = request.json()
  except requests.exceptions.RequestException as e:
    print("Failed to request %s:" % url, e)
    raise SystemExit(e)
  return data


if __name__ == "__main__":

  repos = []
  repos_data = Request(baseurl_repo.replace('{org}', ORG))
  for item in repos_data:
    repos.append(item['name'])

  repo_badges = {}
  for this_repo in repos:
    badges = []
    workflows = Request(baseurl_wfl.replace("{repo}", ORG + '/' + this_repo))
    print(workflows)
    for this_workflow in workflows['workflows']:
      name = this_workflow['name']
      badge = this_workflow['badge_url']
      badges.append(badge)

    repo_badges[this_repo] = badges

  for k,v in repo_badges.items():
    print("### %s\n" %k)
    for badge in v:
      print("![badge](%s)\n" %badge )
