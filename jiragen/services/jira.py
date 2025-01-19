"""
JIRA Service module for fetching and processing JIRA data.
Handles epics, tickets, and components with comprehensive error handling and logging.
"""


import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from jira import JIRA
from loguru import logger
from pydantic import BaseModel, ConfigDict

FILTER_CUSTOM_FIELD_LENGTH = 5  # Minimum length for custom field content


class JiraConfig(BaseModel):
    """Configuration for JIRA connection and defaults."""

    url: str
    username: str
    api_token: str
    default_project: str

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @classmethod
    def from_config_manager(cls, config_manager):
        """Create JiraConfig from ConfigManager instance."""
        config = config_manager.config
        if not config.has_section("JIRA"):
            raise ValueError("JIRA configuration section not found")

        return cls(
            url=config["JIRA"]["url"],
            username=config["JIRA"]["username"],
            api_token=config["JIRA"]["api_token"],
            default_project=config["JIRA"].get("default_project", "DEMO"),
        )


class JiraFetchConfig(BaseModel):
    """Configuration for JIRA data fetching."""

    output_dir: Path
    data_types: List[str]
    batch_size: int = 100
    max_results: int = 1000

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JiraDataFetcher(ABC):
    """Abstract base class for JIRA data fetchers."""

    def __init__(self, jira: JIRA, project_key: str):
        self.jira = jira
        self.project_key = project_key
        logger.debug(
            f"Initialized {self.__class__.__name__} for project: {project_key}"
        )

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch data from JIRA."""
        pass

    @abstractmethod
    def to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert data to markdown format."""
        pass


class EpicFetcher(JiraDataFetcher):
    """Fetches and processes JIRA epics."""

    def fetch(self) -> List[Dict[str, Any]]:
        excluded_statuses = ["Product team Backlog", "Epic Done"]
        status_list = '", "'.join(excluded_statuses)
        jql_query = f'project = "{self.project_key}" AND issuetype = Epic AND status NOT IN ("{status_list}")'

        logger.info(f"Fetching epics with JQL: {jql_query}")
        try:
            epics = self.jira.search_issues(
                jql_query,
                maxResults=1000,
                expand="changelog,renderedFields,names,schema,transitions,editmeta,changelog",
            )
            logger.success(f"Successfully fetched {len(epics)} epics")
            return [self._process_epic(epic) for epic in epics]
        except Exception as e:
            logger.error(f"Error fetching epics: {str(e)}")
            raise

    def _process_epic(self, epic) -> Dict[str, Any]:
        """Process a single epic with full metadata."""
        logger.debug(f"Processing epic: {epic.key}")
        try:
            # Get all linked issues
            links = self.jira.remote_links(epic)
            # TODO : implementation of linked issues by epic
            logger.warning(f"Links not taken into account: {links}")
            linked_issues = []
            for link in (
                epic.fields.issuelinks
                if hasattr(epic.fields, "issuelinks")
                else []
            ):
                if hasattr(link, "outwardIssue"):
                    linked_issues.append(
                        {
                            "key": link.outwardIssue.key,
                            "type": link.type.outward,
                            "direction": "outward",
                        }
                    )
                if hasattr(link, "inwardIssue"):
                    linked_issues.append(
                        {
                            "key": link.inwardIssue.key,
                            "type": link.type.inward,
                            "direction": "inward",
                        }
                    )

            # Get all comments
            comments = []
            if hasattr(epic.fields, "comment"):
                for comment in epic.fields.comment.comments:
                    comments.append(
                        {
                            "author": comment.author.displayName,
                            "created": comment.created,
                            "body": comment.body,
                        }
                    )

            # Get all attachments
            attachments = []
            if hasattr(epic.fields, "attachment"):
                for attachment in epic.fields.attachment:
                    attachments.append(
                        {
                            "filename": attachment.filename,
                            "created": attachment.created,
                            "size": attachment.size,
                            "mimeType": attachment.mimeType,
                            "content": attachment.content
                            if hasattr(attachment, "content")
                            else None,
                        }
                    )

            # Get all custom fields
            custom_fields = {}
            for field_name in dir(epic.fields):
                if field_name.startswith("customfield_"):
                    value = getattr(epic.fields, field_name)
                    if value is not None:
                        str_value = str(value)
                        if len(str_value.strip()) > FILTER_CUSTOM_FIELD_LENGTH:
                            custom_fields[field_name] = str_value

            return {
                "key": epic.key,
                "summary": epic.fields.summary,
                "description": epic.fields.description or "",
                "status": epic.fields.status.name,
                "created": epic.fields.created,
                "updated": epic.fields.updated,
                "assignee": epic.fields.assignee.displayName
                if epic.fields.assignee
                else "Unassigned",
                "reporter": epic.fields.reporter.displayName
                if epic.fields.reporter
                else "Unknown",
                "priority": epic.fields.priority.name
                if hasattr(epic.fields.priority, "name")
                else "None",
                "labels": epic.fields.labels,
                "components": [comp.name for comp in epic.fields.components]
                if hasattr(epic.fields, "components")
                else [],
                "comments": comments,
                "attachments": attachments,
                "linked_issues": linked_issues,
                "custom_fields": custom_fields,
            }
        except Exception as e:
            logger.error(f"Error processing epic {epic.key}: {str(e)}")
            raise

    def to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert epic data to markdown format."""
        logger.debug(f"Converting epic {data['key']} to markdown")
        md_parts = [
            f"# {data['key']}: {data['summary']}\n",
            "## Basic Information",
            f"**Status:** {data['status']}  ",
            f"**Priority:** {data['priority']}  ",
            f"**Assignee:** {data['assignee']}  ",
            f"**Reporter:** {data['reporter']}  ",
            f"**Created:** {data['created']}  ",
            f"**Updated:** {data['updated']}\n",
            "## Description",
            data["description"] or "No description provided.\n",
        ]

        if data["labels"]:
            md_parts.extend(["## Labels", ", ".join(data["labels"]) + "\n"])

        if data["components"]:
            md_parts.extend(
                [
                    "## Components",
                    "\n".join(f"- {comp}" for comp in data["components"])
                    + "\n",
                ]
            )

        if data["linked_issues"]:
            md_parts.extend(
                [
                    "## Linked Issues",
                    "\n".join(
                        f"- {link['key']} ({link['type']}, {link['direction']})"
                        for link in data["linked_issues"]
                    )
                    + "\n",
                ]
            )

        if data["comments"]:
            md_parts.extend(
                [
                    "## Comments",
                    "\n".join(
                        f"### {comment['author']} - {comment['created']}\n{comment['body']}\n"
                        for comment in data["comments"]
                    )
                    + "\n",
                ]
            )

        if data["attachments"]:
            md_parts.extend(
                [
                    "## Attachments",
                    "\n".join(
                        f"- {att['filename']} ({att['size']} bytes, {att['mimeType']})"
                        for att in data["attachments"]
                    )
                    + "\n",
                ]
            )

        if data["custom_fields"]:
            md_parts.extend(
                [
                    "## Custom Fields",
                    "\n".join(
                        f"### {field}\n{value}\n"
                        for field, value in data["custom_fields"].items()
                    )
                    + "\n",
                ]
            )

        return "\n".join(md_parts)


class TicketFetcher(JiraDataFetcher):
    """Fetches and processes JIRA tickets with comprehensive metadata."""

    def fetch(self) -> List[Dict[str, Any]]:
        jql_query = f'project = "{self.project_key}" AND issuetype = Story'

        logger.info(f"Fetching tickets with JQL: {jql_query}")
        try:
            tickets = self.jira.search_issues(
                jql_query,
                maxResults=1000,
                expand="changelog,renderedFields,names,schema,transitions,editmeta,changelog",
            )
            logger.success(f"Successfully fetched {len(tickets)} tickets")
            return [self._process_ticket(ticket) for ticket in tickets]
        except Exception as e:
            logger.error(f"Error fetching tickets: {str(e)}")
            raise

    def _process_ticket(self, ticket) -> Dict[str, Any]:
        """Process a single ticket with full metadata."""
        logger.debug(f"Processing ticket: {ticket.key}")
        try:
            # Get all linked issues
            linked_issues = []
            for link in (
                ticket.fields.issuelinks
                if hasattr(ticket.fields, "issuelinks")
                else []
            ):
                if hasattr(link, "outwardIssue"):
                    linked_issues.append(
                        {
                            "key": link.outwardIssue.key,
                            "type": link.type.outward,
                            "direction": "outward",
                        }
                    )
                if hasattr(link, "inwardIssue"):
                    linked_issues.append(
                        {
                            "key": link.inwardIssue.key,
                            "type": link.type.inward,
                            "direction": "inward",
                        }
                    )

            # Get all comments
            comments = []
            if hasattr(ticket.fields, "comment"):
                for comment in ticket.fields.comment.comments:
                    comments.append(
                        {
                            "author": comment.author.displayName,
                            "created": comment.created,
                            "body": comment.body,
                        }
                    )

            # Get all attachments
            attachments = []
            if hasattr(ticket.fields, "attachment"):
                for attachment in ticket.fields.attachment:
                    attachments.append(
                        {
                            "filename": attachment.filename,
                            "created": attachment.created,
                            "size": attachment.size,
                            "mimeType": attachment.mimeType,
                            "content": attachment.content
                            if hasattr(attachment, "content")
                            else None,
                        }
                    )

            # Get all custom fields
            custom_fields = {}
            for field_name in dir(ticket.fields):
                if field_name.startswith("customfield_"):
                    value = getattr(ticket.fields, field_name)
                    if value is not None:
                        str_value = str(value)
                        if len(str_value.strip()) > FILTER_CUSTOM_FIELD_LENGTH:
                            custom_fields[field_name] = str_value

            # Get sprint information if available
            sprint_info = None
            sprint_field = next(
                (
                    f
                    for f in dir(ticket.fields)
                    if f.lower().endswith("sprint")
                ),
                None,
            )
            if sprint_field:
                sprint_value = getattr(ticket.fields, sprint_field)
                if sprint_value:
                    sprint_info = {
                        "name": getattr(sprint_value[0], "name", "Unknown"),
                        "state": getattr(sprint_value[0], "state", "Unknown"),
                        "startDate": getattr(
                            sprint_value[0], "startDate", None
                        ),
                        "endDate": getattr(sprint_value[0], "endDate", None),
                    }

            return {
                "key": ticket.key,
                "summary": ticket.fields.summary,
                "description": ticket.fields.description or "",
                "status": ticket.fields.status.name,
                "created": ticket.fields.created,
                "updated": ticket.fields.updated,
                "assignee": ticket.fields.assignee.displayName
                if ticket.fields.assignee
                else "Unassigned",
                "reporter": ticket.fields.reporter.displayName
                if ticket.fields.reporter
                else "Unknown",
                "priority": ticket.fields.priority.name
                if hasattr(ticket.fields.priority, "name")
                else "None",
                "labels": ticket.fields.labels,
                "components": [comp.name for comp in ticket.fields.components]
                if hasattr(ticket.fields, "components")
                else [],
                "story_points": getattr(
                    ticket.fields, "customfield_10002", None
                ),  # Adjust field ID as needed
                "epic_link": getattr(
                    ticket.fields, "customfield_10014", None
                ),  # Adjust field ID as needed
                "sprint": sprint_info,
                "comments": comments,
                "attachments": attachments,
                "linked_issues": linked_issues,
                "custom_fields": custom_fields,
                "resolution": ticket.fields.resolution.name
                if ticket.fields.resolution
                else None,
                "watchers": [
                    w.displayName for w in self.jira.watchers(ticket).watchers
                ]
                if hasattr(ticket, "watchers")
                else [],
            }
        except Exception as e:
            logger.error(f"Error processing ticket {ticket.key}: {str(e)}")
            raise

    def to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert ticket data to markdown format."""
        logger.debug(f"Converting ticket {data['key']} to markdown")
        md_parts = [
            f"# {data['key']}: {data['summary']}\n",
            "## Basic Information",
            f"**Status:** {data['status']}  ",
            f"**Priority:** {data['priority']}  ",
            f"**Assignee:** {data['assignee']}  ",
            f"**Reporter:** {data['reporter']}  ",
            f"**Created:** {data['created']}  ",
            f"**Updated:** {data['updated']}  ",
            f"**Resolution:** {data['resolution'] or 'Unresolved'}\n",
            "## Description",
            data["description"] or "No description provided.\n",
        ]

        if data["story_points"] is not None:
            md_parts.extend(["## Story Points", f"{data['story_points']}\n"])

        if data["epic_link"]:
            md_parts.extend(["## Epic Link", f"{data['epic_link']}\n"])

        if data["sprint"]:
            md_parts.extend(
                [
                    "## Sprint Information",
                    f"**Name:** {data['sprint']['name']}  ",
                    f"**State:** {data['sprint']['state']}  ",
                    f"**Start Date:** {data['sprint']['startDate']}  ",
                    f"**End Date:** {data['sprint']['endDate']}\n",
                ]
            )

        if data["labels"]:
            md_parts.extend(["## Labels", ", ".join(data["labels"]) + "\n"])

        if data["components"]:
            md_parts.extend(
                [
                    "## Components",
                    "\n".join(f"- {comp}" for comp in data["components"])
                    + "\n",
                ]
            )

        if data["linked_issues"]:
            md_parts.extend(
                [
                    "## Linked Issues",
                    "\n".join(
                        f"- {link['key']} ({link['type']}, {link['direction']})"
                        for link in data["linked_issues"]
                    )
                    + "\n",
                ]
            )

        if data["comments"]:
            md_parts.extend(
                [
                    "## Comments",
                    "\n".join(
                        f"### {comment['author']} - {comment['created']}\n{comment['body']}\n"
                        for comment in data["comments"]
                    )
                    + "\n",
                ]
            )

        if data["attachments"]:
            md_parts.extend(
                [
                    "## Attachments",
                    "\n".join(
                        f"- {att['filename']} ({att['size']} bytes, {att['mimeType']})"
                        for att in data["attachments"]
                    )
                    + "\n",
                ]
            )

        if data["watchers"]:
            md_parts.extend(
                [
                    "## Watchers",
                    "\n".join(f"- {watcher}" for watcher in data["watchers"])
                    + "\n",
                ]
            )

        if data["custom_fields"]:
            md_parts.extend(
                [
                    "## Custom Fields",
                    "\n".join(
                        f"### {field}\n{value}\n"
                        for field, value in data["custom_fields"].items()
                    )
                    + "\n",
                ]
            )

        return "\n".join(md_parts)


class ComponentFetcher(JiraDataFetcher):
    """Fetches and processes JIRA components."""

    def fetch(self) -> List[Dict[str, Any]]:
        logger.info(f"Fetching components for project: {self.project_key}")
        try:
            components = self.jira.project_components(self.project_key)
            logger.success(
                f"Successfully fetched {len(components)} components"
            )
            return [
                self._process_component(component) for component in components
            ]
        except Exception as e:
            logger.error(f"Error fetching components: {str(e)}")
            raise

    def _process_component(self, component) -> Dict[str, Any]:
        """Process a single component."""
        logger.debug(f"Processing component: {component.name}")
        return {
            "name": component.name,
            "description": getattr(component, "description", ""),
            "lead": getattr(component.lead, "displayName", "")
            if hasattr(component, "lead")
            else "",
        }

    def to_markdown(self, data: Dict[str, Any]) -> str:
        """Convert component data to markdown format."""
        logger.debug(f"Converting component {data['name']} to markdown")
        md_parts = [f"# Component: {data['name']}\n"]

        if data["lead"]:
            md_parts.append(f"**Lead:** {data['lead']}\n")

        if data["description"]:
            md_parts.extend(["## Description", data["description"]])
        else:
            md_parts.append("No description provided.")

        return "\n".join(md_parts)


class JiraDataManager:
    """Manages JIRA data fetching and storage."""

    def __init__(self, jira_config: JiraConfig, fetch_config: JiraFetchConfig):
        """Initialize the JIRA data manager with configuration."""
        logger.info("Initializing JiraDataManager")
        try:
            self.jira = JIRA(
                server=jira_config.url,
                basic_auth=(jira_config.username, jira_config.api_token),
            )
            logger.success("Successfully connected to JIRA")
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {str(e)}")
            raise

        # Get project key using the helper function
        project_key = get_project_key(self.jira, jira_config.default_project)
        if not project_key:
            raise ValueError(
                f"Could not find project: {jira_config.default_project}"
            )

        self.project_key = project_key
        self.config = fetch_config

        # Initialize fetchers
        self.fetchers = {
            "epics": EpicFetcher(self.jira, self.project_key),
            "tickets": TicketFetcher(self.jira, self.project_key),
            "components": ComponentFetcher(self.jira, self.project_key),
        }
        logger.debug(
            f"Initialized fetchers for types: {list(self.fetchers.keys())}"
        )

    def _ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure a directory exists and create it if it doesn't.

        Args:
            directory: Directory path as string or Path object

        Returns:
            Path: Path object of the ensured directory
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.debug(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def _save_json(self, data: Dict[str, Any], filepath: Path) -> None:
        """
        Save data as JSON with proper error handling.

        Args:
            data: Dictionary to save
            filepath: Path where to save the JSON file
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Successfully saved JSON to {filepath}")
        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {str(e)}")
            raise

    def _save_markdown(self, content: str, filepath: Path) -> None:
        """
        Save content as markdown with proper error handling.

        Args:
            content: Markdown content to save
            filepath: Path where to save the markdown file
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.debug(f"Successfully saved markdown to {filepath}")
        except Exception as e:
            logger.error(f"Error saving markdown to {filepath}: {str(e)}")
            raise

    def fetch_data(self, vector_store=None) -> Dict[str, int]:
        """
        Fetch and store JIRA data.

        Args:
            vector_store: Optional vector store instance for storing processed data

        Returns:
            Dict[str, int]: Count of processed items for each data type
        """
        logger.info("Starting data fetch process")
        data_types = (
            ["epics", "tickets", "components"]
            if "all" in self.config.data_types
            else self.config.data_types
        )
        logger.debug(f"Processing data types: {data_types}")

        results = {}
        progress_callback = getattr(self, "progress_callback", None)

        for data_type in data_types:
            if data_type not in self.fetchers:
                logger.warning(f"Skipping unknown data type: {data_type}")
                continue

            logger.info(f"Processing {data_type}")
            fetcher = self.fetchers[data_type]

            try:
                # Fetch items from JIRA
                items = list(
                    fetcher.fetch()
                )  # Convert to list to get total count
                total_items = len(items)

                # Prepare output directory
                data_dir = self._ensure_directory(
                    self.config.output_dir / data_type
                )
                processed_count = 0

                for item in items:
                    item_id = item.get("key", item.get("name"))
                    logger.debug(f"Processing {data_type} item: {item_id}")

                    try:
                        # Save raw JSON
                        json_path = data_dir / f"{item_id}.json"
                        self._save_json(item, json_path)

                        # Convert to markdown and save
                        markdown = fetcher.to_markdown(item)
                        md_path = data_dir / f"{item_id}.md"
                        self._save_markdown(markdown, md_path)

                        # Add to vector store if provided
                        if vector_store is not None:
                            vector_store.add_files([md_path])

                        processed_count += 1

                        # Update progress if callback is provided
                        if progress_callback:
                            progress = (processed_count / total_items) * 100
                            progress_callback(
                                data_type,
                                progress,
                                processed_count,
                                total_items,
                            )

                    except Exception as e:
                        logger.error(
                            f"Error processing {data_type} item {item_id}: {str(e)}"
                        )
                        continue

                results[data_type] = processed_count
                logger.success(
                    f"Successfully processed {processed_count} {data_type}"
                )

            except Exception as e:
                logger.error(f"Error processing {data_type}: {str(e)}")
                results[data_type] = 0
                continue

        return results

    def bulk_fetch(
        self, vector_store, batch_size: int = None
    ) -> Dict[str, int]:
        """
        Fetch data in batches to handle large datasets.

        Args:
            vector_store: Vector store instance for storing processed data
            batch_size: Optional batch size for processing

        Returns:
            Dict[str, int]: Count of processed items for each data type
        """
        if batch_size is None:
            batch_size = self.config.batch_size

        logger.info(f"Starting bulk fetch with batch size {batch_size}")

        try:
            results = self.fetch_data(vector_store)
            logger.success("Bulk fetch completed successfully")
            return results
        except Exception as e:
            logger.error(f"Error during bulk fetch: {str(e)}")
            raise

    def validate_fetched_data(self, results: Dict[str, int]) -> bool:
        """
        Validate the fetched data against expected counts.

        Args:
            results: Dictionary containing counts of processed items

        Returns:
            bool: True if validation passes, False otherwise
        """
        logger.info("Validating fetched data")

        try:
            for data_type, count in results.items():
                if count == 0:
                    logger.warning(f"No items processed for {data_type}")
                    return False

                data_dir = self.config.output_dir / data_type
                json_files = list(data_dir.glob("*.json"))
                md_files = list(data_dir.glob("*.md"))

                if len(json_files) != count or len(md_files) != count:
                    logger.error(f"Mismatch in file counts for {data_type}")
                    return False

            logger.success("Data validation passed")
            return True

        except Exception as e:
            logger.error(f"Error during data validation: {str(e)}")
            return False


def get_project_key(jira: JIRA, project_name: str) -> Optional[str]:
    """
    Get project key from project name using case-insensitive matching.
    Supports both exact and partial matches.
    """
    logger.info(f"Getting project key for project: {project_name}")
    projects = jira.projects()
    for project in projects:
        if project.name.lower() == project_name.lower():
            logger.info(f"Found exact match project key: {project.key}")
            return project.key
        elif project_name.lower() in project.name.lower():
            logger.info(f"Found partial match project key: {project.key}")
            return project.key
    logger.warning(f"No project key found for project name: {project_name}")
    return None
