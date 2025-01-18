"""Upload command for jiragen CLI."""

import configparser
from pathlib import Path
from typing import Any, Dict, Optional

from jira import JIRA
from loguru import logger
from rich.console import Console

from jiragen.core.config import ConfigManager

console = Console()


def read_config(config_path: Path) -> Dict[str, str]:
    """Read Jira configuration from config file."""
    config = configparser.ConfigParser()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    config.read(str(config_path))
    return config["JIRA"]


def get_project_key(jira: JIRA, project_name: str) -> Optional[str]:
    """Get project key from project name."""
    projects = jira.projects()
    for project in projects:
        if project.name.lower() == project_name.lower():
            return project.key
        elif project_name.lower() in project.name.lower():
            return project.key
    return None


def validate_component(
    jira: JIRA, project_key: str, component_name: Optional[str]
) -> Optional[str]:
    """Validate component exists and return its ID."""
    if not component_name:
        return None

    components = jira.project_components(project_key)
    for component in components:
        if component.name.lower() == component_name.lower():
            return component.id
    logger.warning(f"Component '{component_name}' not found in project")
    return None


def validate_epic(
    jira: JIRA, project_key: str, epic_key: Optional[str]
) -> Optional[str]:
    """Validate epic exists and return its key."""
    if not epic_key:
        return None

    try:
        epic = jira.issue(epic_key)
        if epic.fields.issuetype.name.lower() != "epic":
            logger.warning(f"Issue '{epic_key}' is not an epic")
            return None
        if epic.fields.project.key != project_key:
            logger.warning(
                f"Epic '{epic_key}' does not belong to project '{project_key}'"
            )
            return None
        return epic_key
    except Exception:
        logger.warning(f"Epic '{epic_key}' not found")
        return None


def validate_priority(
    jira: JIRA, priority_name: Optional[str]
) -> Optional[str]:
    """Validate priority exists and return its name."""
    if not priority_name:
        return None

    try:
        priorities = jira.priorities()
        for priority in priorities:
            if priority.name.lower() == priority_name.lower():
                return priority.name
        logger.warning(f"Priority '{priority_name}' not found")
        return None
    except Exception:
        logger.warning("Error validating priority")
        return None


def validate_labels(labels: Optional[str]) -> list:
    """Validate and format labels."""
    if not labels:
        return []
    return [label.strip() for label in labels.split(",") if label.strip()]


def convert_md_to_jira(md_text: Optional[str]) -> str:
    """Convert markdown text to Jira markup."""
    if not md_text:
        return ""

    # Headers
    md_text = md_text.replace("### ", "h3. ")
    md_text = md_text.replace("## ", "h2. ")
    md_text = md_text.replace("# ", "h1. ")

    # Lists
    lines = md_text.split("\n")
    converted_lines = []
    for line in lines:
        if line.strip().startswith("- "):
            line = "* " + line.strip()[2:]
        elif line.strip().startswith("* "):
            line = "* " + line.strip()[2:]
        elif line.strip().startswith("1. "):
            line = "# " + line.strip()[3:]
        converted_lines.append(line)

    md_text = "\n".join(converted_lines)

    # Task lists
    md_text = md_text.replace("- [ ]", "(x)")
    md_text = md_text.replace("- [x]", "(/) ")

    # Code blocks
    md_text = md_text.replace("```", "{code}")

    # Bold and Italic
    md_text = md_text.replace("**", "*")
    md_text = md_text.replace("__", "_")

    return md_text


def upload_command(
    title: str,
    description: Optional[str] = None,
    issue_type: str = "Story",
    epic_key: Optional[str] = None,
    component_name: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[str] = None,
    assignee: Optional[str] = None,
    reporter: Optional[str] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Upload a Jira issue with the provided content and options.

    Args:
        title: Issue summary/title
        description: Issue description (can be in markdown format)
        issue_type: Type of issue (Story, Bug, Task, Epic, etc.)
        epic_key: Key of the epic to link the issue to (not applicable for epics)
        component_name: Name of the component to assign
        priority: Priority level (Highest, High, Medium, Low, Lowest)
        labels: Comma-separated list of labels
        assignee: Username of the assignee
        reporter: Username of the reporter
        custom_fields: Dictionary of custom field IDs and values

    Returns:
        str: The key of the created issue, or None if creation failed
    """
    try:
        # Get config manager
        config_manager = ConfigManager()

        # Read Jira configuration
        config = read_config(config_manager.config_path)
        jira_url = config["url"]
        username = config["username"]
        api_token = config["api_token"]
        default_project = config.get("default_project", "DEMO")

        # Initialize Jira client
        jira = JIRA(server=jira_url, basic_auth=(username, api_token))

        # Get project key
        project_key = get_project_key(jira, default_project)
        if not project_key:
            logger.error(f"Could not find project '{default_project}'")
            return None

        # Convert description from markdown to Jira markup
        jira_description = convert_md_to_jira(description)

        # Validate inputs
        component_id = validate_component(jira, project_key, component_name)
        validated_priority = validate_priority(jira, priority)
        validated_labels = validate_labels(labels)

        # Find assignee and reporter users
        assignee_account = None
        reporter_account = None

        if assignee:
            users = jira.search_users(query=assignee)
            if users:
                assignee_account = users[0].accountId
            else:
                logger.warning(f"Assignee '{assignee}' not found")

        if reporter:
            users = jira.search_users(query=reporter)
            if users:
                reporter_account = users[0].accountId
            else:
                logger.warning(f"Reporter '{reporter}' not found")

        # Prepare issue fields
        issue_dict = {
            "project": project_key,
            "summary": title,
            "description": jira_description,
            "issuetype": {"name": issue_type},
        }

        if assignee_account:
            issue_dict["assignee"] = {"accountId": assignee_account}

        if reporter_account:
            issue_dict["reporter"] = {"accountId": reporter_account}

        if component_id:
            issue_dict["components"] = [{"id": component_id}]

        # Only add epic link if the issue type is not an epic
        if issue_type.lower() != "epic" and epic_key:
            validated_epic_key = validate_epic(jira, project_key, epic_key)
            if validated_epic_key:
                issue_dict[
                    "customfield_10014"
                ] = validated_epic_key  # Epic Link field

        if validated_priority:
            issue_dict["priority"] = {"name": validated_priority}

        if validated_labels:
            issue_dict["labels"] = validated_labels

        # Add custom fields if provided
        if custom_fields:
            issue_dict.update(custom_fields)

        # Create issue
        new_issue = jira.create_issue(**issue_dict)
        console.print(
            f"✓ Successfully created Jira issue: {jira_url}/browse/{new_issue.key}",
            style="green",
        )
        return new_issue.key

    except Exception as e:
        logger.error(f"Error creating Jira issue: {str(e)}")
        return None
