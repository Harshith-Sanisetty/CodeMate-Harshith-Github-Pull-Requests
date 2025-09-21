import os
import requests
from dotenv import load_dotenv
from .base_connector import BaseConnector
from typing import List, Dict

class GitHubConnector(BaseConnector):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GITHUB_API_KEY")
        if not self.api_key:
            raise ValueError("GITHUB_API_KEY not found in .env file")
        
        self.headers = {
            "Authorization": f"token {self.api_key}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_base_url = "https://api.github.com"

    def _parse_pr_url(self, pr_url: str) -> dict:
        try:
            parts = pr_url.replace("https://github.com/", "").split("/")
            owner, repo, _, pr_number = parts[0], parts[1], parts[2], parts[3]
            return {"owner": owner, "repo": repo, "pr_number": pr_number}
        except IndexError:
            raise ValueError("Invalid GitHub PR URL format.")

    def get_pr_metadata(self, pr_url: str) -> dict:
        url_parts = self._parse_pr_url(pr_url)
        api_url = f"{self.api_base_url}/repos/{url_parts['owner']}/{url_parts['repo']}/pulls/{url_parts['pr_number']}"
        response = requests.get(api_url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return {"title": data.get("title", ""), "description": data.get("body", "")}

    def get_pr_diff(self, pr_url: str) -> str:
        url_parts = self._parse_pr_url(pr_url)
        api_url = f"{self.api_base_url}/repos/{url_parts['owner']}/{url_parts['repo']}/pulls/{url_parts['pr_number']}"
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        response = requests.get(api_url, headers=diff_headers)
        response.raise_for_status()
        return response.text
        
    def post_comment(self, pr_url: str, comment: str):
        print("--- Posting comment to GitHub ---")
        url_parts = self._parse_pr_url(pr_url)
        api_url = f"{self.api_base_url}/repos/{url_parts['owner']}/{url_parts['repo']}/issues/{url_parts['pr_number']}/comments"
        payload = {"body": comment}
        response = requests.post(api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        print("--- Comment posted successfully ---")

    def get_pr_comments(self, pr_url: str) -> List[Dict]:
        """Fetches all comments from a given PR URL."""
        print("--- Fetching PR comments from GitHub ---")
        url_parts = self._parse_pr_url(pr_url)
        api_url = f"{self.api_base_url}/repos/{url_parts['owner']}/{url_parts['repo']}/issues/{url_parts['pr_number']}/comments"
        response = requests.get(api_url, headers=self.headers)
        response.raise_for_status()
        return response.json()