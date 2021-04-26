import requests
from dateutil import parser

interval = 1800
ORG = 'key4hep'
baseurl_wfl = "https://api.github.com/repos/{repo}/actions/workflows"
baseurl_wfr = "https://api.github.com/repos/{repo}/actions/runs"
baseurl_wf = "https://api.github.com/repos/{repo}/actions/runs/{run_id}"
baseurl_wfjl = "https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs"
baseurl_wfj = "https://api.github.com/repos/{repo}/actions/jobs/{job_id}"
baseurl_repo = "https://api.github.com/orgs/{org}/repos"

def Request(url):
  try:
    request = requests.get(url = url)
    data = request.json()
  except requests.exceptions.RequestException as e:
    print("Failed to request %s:" % url, e)
    raise SystemExit(e)
  return data

def send_run_report(run):
  if not run['conclusion']:
    status = run['status']
  else:
    status = run['conclusion']

  report = {
             'repository': run['repository']['name'],
             'branch': run['branch'],
             'workflow_id': run['workflow_id'],
             'run_id': run['id'],
             'name': run['name'],
             'status': status,
             'created_at:': run['created_at']
             'updated_at:': run['updated_at']
           }
  # send report
  return

if __name__ == "__main__":

  repos = []
  repos_data = Request(baseurl_repo.replace('{org}', ORG))
  for item in repos_data:
    repos.append(item['name'])

  for this_repo in repos:
    workflows = Request(baseurl_wfl.replace("{repo}", this_repo))
    runs = Request(baseurl_wfr.replace("{repo}", this_repo))
    #jobs = Request(baseurl_wfjl.replace("{repo}", this_repo))

    # Report all runs in the last interval
    for this_run in runs['workflow_runs']:
      if (datetime.now() - parser.parse(this_run['updated_at'])) <= datetime.timedelta(seconds=interval)):
        send_run_report(this_run)

    #loop over branches?
    for this_workflow in workflows['workflows']:
      latest_run = None
      workflowid = this_workflow['id']

      for this_run in runs['workflow_runs']:
        if this_run['workflow_id'] =! workflowid:
          continue
        if (not latest_run) or (parser.parse(this_run['updated_at']) - parser.parse(latest_run['updated_at']) >= datetime.timedelta(seconds=1)):
          latest_run = this_run
          continue

      if not latest_run:
        continue

      latest_run['branch'] = 'None'
      send_run_report(latest_run)
