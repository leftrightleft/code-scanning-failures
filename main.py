import requests
import time
import sys
import os
from collections import defaultdict

# Constants
GITHUB_API_VERSION = "2022-11-28"
BASE_URL = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": GITHUB_API_VERSION
}

# Check if the org name is provided as an argument
if len(sys.argv) < 2:
    print("Usage: python script.py <org_name>")
    sys.exit(1)

ORG_NAME = sys.argv[1]
PAT = os.getenv('GITHUB_PAT')

if not PAT:
    print("Error: GITHUB_PAT environment variable is not set.")
    sys.exit(1)

HEADERS["Authorization"] = f"Bearer {PAT}"

def make_request(url, method="GET"):
    """Make an API request and handle rate limiting."""
    while True:
        response = requests.request(method, url, headers=HEADERS)
        if response.status_code == 403:
            remaining = response.headers.get("X-Ratelimit-Remaining")
            reset = response.headers.get("X-Ratelimit-Reset")
            if remaining == "0" and reset:
                reset_time = int(reset)
                current_time = int(time.time())
                wait_time = reset_time - current_time
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)
                continue  # Retry the request after waiting
        return response

def get_rate_limit_reset_time(repo):
    """Get the rate limit reset time for a repository."""
    url = f"{BASE_URL}/repos/{repo}/code-scanning/analyses"
    response = make_request(url, method="HEAD")
    remaining = response.headers.get("X-Ratelimit-Remaining")
    reset = response.headers.get("X-Ratelimit-Reset")

    if remaining is None or reset is None:
        raise RuntimeError(f"Unable to retrieve rate limit information for repository: {repo}")

    return int(remaining), int(reset)

def get_repos(org_name):
    """Get the list of repositories for an organization."""
    url = f"{BASE_URL}/orgs/{org_name}/repos"
    repos = []
    while url:
        response = make_request(url)
        if response.status_code != 200:
            raise RuntimeError(f"Unable to retrieve repositories for organization: {org_name}")
        repos.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return [repo['full_name'] for repo in repos]

def get_analyses(repo):
    """Get the list of code scanning analyses for a repository."""
    url = f"{BASE_URL}/repos/{repo}/code-scanning/analyses"
    analyses = []
    while url:
        response = make_request(url)
        if response.status_code == 404:
            return []
        elif response.status_code == 403:
            error_message = response.json().get("message", "")
            if "Advanced Security must be enabled" in error_message:
                print(f"Repository: {repo} - {error_message}")
                return []
            remaining = response.headers.get("X-Ratelimit-Remaining")
            reset = response.headers.get("X-Ratelimit-Reset")
            if remaining == "0" and reset:
                reset_time = int(reset)
                current_time = int(time.time())
                wait_time = reset_time - current_time
                print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)
                continue  # Retry the request after waiting
            else:
                print(f"Error: 403 Forbidden for repository: {repo}")
                return []
        elif response.status_code != 200:
            raise RuntimeError(f"Invalid response for repository: {repo}")
        analyses.extend(response.json())
        url = response.links.get('next', {}).get('url')
    return analyses

def main():
    repos = get_repos(ORG_NAME)

    for repo in repos:
        remaining, reset = get_rate_limit_reset_time(repo)

        if remaining == 0:
            current_time = int(time.time())
            wait_time = reset - current_time
            print(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time)

        analyses = get_analyses(repo)

        if not isinstance(analyses, list):
            print(f"Analyses is not an array for repository: {repo}")
            continue

        total_analyses = len(analyses)
        analyses_with_errors = [analysis for analysis in analyses if analysis.get('error')]

        if total_analyses > 0:
            print(f"Repository: {repo}")
            print(f"Total Analyses: {total_analyses}")
            print(f"Analyses with Errors: {len(analyses_with_errors)}")

            if analyses_with_errors:
                error_counts_by_category = defaultdict(int)
                for analysis in analyses_with_errors:
                    category = analysis.get('category', 'Unknown')
                    error_counts_by_category[category] += 1

                print("Error Counts by Category:")
                for category, count in error_counts_by_category.items():
                    print(f"{category}: {count}")

            print()  # Add a new line after each repository

if __name__ == "__main__":
    main()