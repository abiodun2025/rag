#!/usr/bin/env python3
"""
Real Jira Integration for Task/Project Agent
Connects to actual Jira instances and manages real projects in real-time.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class JiraConfig:
    """Jira connection configuration."""
    base_url: str
    username: str
    api_token: str
    project_key: str
    verify_ssl: bool = True

class RealJiraIntegration:
    """Real-time Jira integration for actual projects."""
    
    def __init__(self, config: JiraConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=config.verify_ssl,
            auth=(config.username, config.api_token)
        )
        self.base_url = config.base_url.rstrip('/')
        self.api_url = f"{self.base_url}/rest/api/3"
        
        logger.info(f"Real Jira integration initialized for {config.base_url}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Jira instance."""
        try:
            response = await self.client.get(f"{self.api_url}/myself")
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "Connected to Jira successfully",
                    "user": user_data.get("displayName"),
                    "account_id": user_data.get("accountId"),
                    "email": user_data.get("emailAddress")
                }
            else:
                return {
                    "success": False,
                    "error": f"Connection failed: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    async def get_project_info(self, project_key: str = None) -> Dict[str, Any]:
        """Get real project information from Jira."""
        try:
            project_key = project_key or self.config.project_key
            response = await self.client.get(f"{self.api_url}/project/{project_key}")
            
            if response.status_code == 200:
                project_data = response.json()
                return {
                    "success": True,
                    "project": {
                        "key": project_data.get("key"),
                        "name": project_data.get("name"),
                        "description": project_data.get("description"),
                        "lead": project_data.get("lead", {}).get("displayName"),
                        "category": project_data.get("projectCategory", {}).get("name"),
                        "project_type": project_data.get("projectTypeKey"),
                        "simplified": project_data.get("simplified"),
                        "style": project_data.get("style"),
                        "is_private": project_data.get("isPrivate")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get project: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting project info: {str(e)}"
            }
    
    async def create_real_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a real issue in Jira."""
        try:
            # Prepare issue payload
            payload = {
                "fields": {
                    "project": {"key": issue_data.get("project_key", self.config.project_key)},
                    "summary": issue_data.get("summary", ""),
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": issue_data.get("description", "")
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": issue_data.get("issue_type", "Task")}
                }
            }
            
            # Add optional fields
            if issue_data.get("priority"):
                payload["fields"]["priority"] = {"name": issue_data["priority"]}
            
            if issue_data.get("assignee"):
                payload["fields"]["assignee"] = {"accountId": issue_data["assignee"]}
            
            if issue_data.get("labels"):
                payload["fields"]["labels"] = issue_data["labels"]
            
            if issue_data.get("components"):
                payload["fields"]["components"] = [{"name": comp} for comp in issue_data["components"]]
            
            response = await self.client.post(
                f"{self.api_url}/issue",
                json=payload
            )
            
            if response.status_code == 201:
                issue_response = response.json()
                return {
                    "success": True,
                    "issue": {
                        "id": issue_response.get("id"),
                        "key": issue_response.get("key"),
                        "self": issue_response.get("self")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create issue: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error creating issue: {str(e)}"
            }
    
    async def get_real_issues(self, project_key: str = None, jql: str = None) -> Dict[str, Any]:
        """Get real issues from Jira using JQL or project key."""
        try:
            if jql:
                # Use custom JQL query
                search_url = f"{self.api_url}/search"
                payload = {
                    "jql": jql,
                    "maxResults": 100,
                    "fields": ["summary", "status", "assignee", "priority", "created", "updated"]
                }
            else:
                # Use project key
                project_key = project_key or self.config.project_key
                search_url = f"{self.api_url}/search"
                payload = {
                    "jql": f"project = {project_key} ORDER BY created DESC",
                    "maxResults": 100,
                    "fields": ["summary", "status", "assignee", "priority", "created", "updated"]
                }
            
            response = await self.client.post(search_url, json=payload)
            
            if response.status_code == 200:
                search_data = response.json()
                issues = []
                
                for issue in search_data.get("issues", []):
                    fields = issue.get("fields", {})
                    issues.append({
                        "id": issue.get("id"),
                        "key": issue.get("key"),
                        "summary": fields.get("summary"),
                        "status": fields.get("status", {}).get("name"),
                        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
                        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else "No Priority",
                        "created": fields.get("created"),
                        "updated": fields.get("updated")
                    })
                
                return {
                    "success": True,
                    "total": search_data.get("total"),
                    "issues": issues
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get issues: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting issues: {str(e)}"
            }
    
    async def update_real_issue(self, issue_key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a real issue in Jira."""
        try:
            # Prepare update payload
            payload = {"fields": {}}
            
            if "summary" in updates:
                payload["fields"]["summary"] = updates["summary"]
            
            if "description" in updates:
                payload["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": updates["description"]
                                }
                            ]
                        }
                    ]
                }
            
            if "priority" in updates:
                payload["fields"]["priority"] = {"name": updates["priority"]}
            
            if "assignee" in updates:
                payload["fields"]["assignee"] = {"accountId": updates["assignee"]}
            
            if "labels" in updates:
                payload["fields"]["labels"] = updates["labels"]
            
            if "components" in updates:
                payload["fields"]["components"] = [{"name": comp} for comp in updates["components"]]
            
            # Handle status transitions
            if "status" in updates:
                # Get available transitions first
                transitions_response = await self.client.get(
                    f"{self.api_url}/issue/{issue_key}/transitions"
                )
                
                if transitions_response.status_code == 200:
                    transitions_data = transitions_response.json()
                    target_status = updates["status"]
                    
                    # Find the transition ID for the target status
                    transition_id = None
                    for transition in transitions_data.get("transitions", []):
                        if transition.get("to", {}).get("name") == target_status:
                            transition_id = transition.get("id")
                            break
                    
                    if transition_id:
                        # Perform the transition
                        transition_payload = {"transition": {"id": transition_id}}
                        transition_response = await self.client.post(
                            f"{self.api_url}/issue/{issue_key}/transitions",
                            json=transition_payload
                        )
                        
                        if transition_response.status_code != 204:
                            logger.warning(f"Status transition failed: {transition_response.status_code}")
            
            # Update other fields
            if len(payload["fields"]) > 0:
                response = await self.client.put(
                    f"{self.api_url}/issue/{issue_key}",
                    json=payload
                )
                
                if response.status_code == 204:
                    return {
                        "success": True,
                        "message": f"Issue {issue_key} updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to update issue: HTTP {response.status_code}",
                        "details": response.text
                    }
            else:
                return {
                    "success": True,
                    "message": f"Issue {issue_key} updated successfully (status only)"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating issue: {str(e)}"
            }
    
    async def get_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific issue."""
        try:
            response = await self.client.get(
                f"{self.api_url}/issue/{issue_key}",
                params={"expand": "changelog,comments,attachments"}
            )
            
            if response.status_code == 200:
                issue_data = response.json()
                fields = issue_data.get("fields", {})
                
                return {
                    "success": True,
                    "issue": {
                        "id": issue_data.get("id"),
                        "key": issue_data.get("key"),
                        "summary": fields.get("summary"),
                        "description": fields.get("description"),
                        "status": fields.get("status", {}).get("name"),
                        "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "Unassigned",
                        "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else "Unknown",
                        "priority": fields.get("priority", {}).get("name") if fields.get("priority") else "No Priority",
                        "created": fields.get("created"),
                        "updated": fields.get("updated"),
                        "labels": fields.get("labels", []),
                        "components": [comp.get("name") for comp in fields.get("components", [])],
                        "comments_count": fields.get("comment", {}).get("total", 0),
                        "attachments_count": len(fields.get("attachment", [])),
                        "changelog_entries": len(issue_data.get("changelog", {}).get("histories", []))
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get issue details: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting issue details: {str(e)}"
            }
    
    async def get_project_workflow(self, project_key: str = None) -> Dict[str, Any]:
        """Get workflow information for a project."""
        try:
            project_key = project_key or self.config.project_key
            
            # Get project statuses
            response = await self.client.get(f"{self.api_url}/project/{project_key}/statuses")
            
            if response.status_code == 200:
                statuses_data = response.json()
                workflows = {}
                
                for status_info in statuses_data:
                    issue_type = status_info.get("name", "Unknown")
                    statuses = []
                    
                    for status in status_info.get("statuses", []):
                        statuses.append({
                            "id": status.get("id"),
                            "name": status.get("name"),
                            "description": status.get("description"),
                            "category": status.get("statusCategory", {}).get("name")
                        })
                    
                    workflows[issue_type] = statuses
                
                return {
                    "success": True,
                    "project_key": project_key,
                    "workflows": workflows
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get workflows: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting workflows: {str(e)}"
            }
    
    async def search_issues_advanced(self, jql: str, fields: List[str] = None, max_results: int = 100) -> Dict[str, Any]:
        """Advanced issue search with custom JQL and fields."""
        try:
            payload = {
                "jql": jql,
                "maxResults": max_results,
                "fields": fields or ["summary", "status", "assignee", "priority", "created", "updated"]
            }
            
            response = await self.client.post(f"{self.api_url}/search", json=payload)
            
            if response.status_code == 200:
                search_data = response.json()
                return {
                    "success": True,
                    "total": search_data.get("total"),
                    "max_results": search_data.get("maxResults"),
                    "start_at": search_data.get("startAt"),
                    "issues": search_data.get("issues", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Search failed: HTTP {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching issues: {str(e)}"
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Example usage and configuration
async def main():
    """Example usage of real Jira integration."""
    
    # Configuration (you would load this from environment variables or config file)
    config = JiraConfig(
        base_url="https://your-domain.atlassian.net",
        username="your-email@example.com",
        api_token="your-api-token",
        project_key="PROJ"
    )
    
    jira = RealJiraIntegration(config)
    
    try:
        # Test connection
        print("Testing Jira connection...")
        connection = await jira.test_connection()
        print(f"Connection: {connection}")
        
        if connection['success']:
            # Get project info
            print("\nGetting project information...")
            project = await jira.get_project_info()
            print(f"Project: {project}")
            
            # Get recent issues
            print("\nGetting recent issues...")
            issues = await jira.get_real_issues()
            print(f"Issues: {issues}")
            
            # Get workflow information
            print("\nGetting workflow information...")
            workflow = await jira.get_project_workflow()
            print(f"Workflow: {workflow}")
    
    finally:
        await jira.close()

if __name__ == "__main__":
    print("🔗 Real Jira Integration Module")
    print("=" * 50)
    print("This module provides real-time integration with actual Jira instances.")
    print("Configure your Jira credentials to use it.")
    print()
    
    # Don't run main() without proper configuration
    print("⚠️  Configure Jira credentials before running integration tests")
