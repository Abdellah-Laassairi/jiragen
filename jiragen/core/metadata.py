from enum import Enum
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from .generator import LiteLLMClient, LLMConfig


class IssueType(str, Enum):
    STORY = "Story"
    BUG = "Bug"
    TASK = "Task"
    EPIC = "Epic"
    SUBTASK = "Sub-task"


class IssuePriority(str, Enum):
    HIGHEST = "Highest"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    LOWEST = "Lowest"


class IssueMetadata(BaseModel):
    """Represents the metadata extracted from an issue's content."""

    issue_type: IssueType = Field(..., description="Type of the issue")
    priority: IssuePriority = Field(
        ..., description="Priority level of the issue"
    )
    labels: List[str] = Field(
        default_factory=list, description="Labels/tags for the issue"
    )
    story_points: Optional[int] = Field(
        None, description="Story points estimation"
    )
    components: List[str] = Field(
        default_factory=list, description="Affected components/modules"
    )
    description: Optional[str] = Field(
        None, description="Issue description in markdown format"
    )


class IssueMetadataExtractor:
    """Extracts metadata from issue content using LLM analysis."""

    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        logger.info("Initialized IssueMetadataExtractor")

    def _create_analysis_prompt(self, content: str) -> str:
        """Creates a structured prompt for the LLM to analyze JIRA issue content."""

        return """You are an expert in analyzing JIRA issues and extracting structured metadata.
            Follow these rules for consistent output:
            - Use JSON format.
            - Ensure values strictly follow the predefined options.
            - Only provide the valid json format, no other text.
            - If uncertain, make the best reasonable guess based on the context.

            Extract the following metadata:
        - issue_type: One of ["Story", "Bug", "Task", "Epic", "Sub-task"]
        - priority: One of ["Highest", "High", "Medium", "Low", "Lowest"]
        - labels: List of relevant technical tags (e.g., "frontend", "backend", "database").
        - story_points: Integer in Fibonacci sequence (1, 2, 3, 5, 8, 13) or null if not applicable.
        - components: List of affected system components or modules.
        - description: Issue description in markdown format.

        ### Example 1:
        Issue Content:
        'A new feature request to add dark mode to the UI. Should be implemented using Tailwind CSS.'

        Expected JSON Response:
        {
        "issue_type": "Story",
        "priority": "Medium",
        "labels": ["frontend", "UI", "TailwindCSS"],
        "story_points": 3,
        "components": ["UI"],
        "description": "Add dark mode to the UI using Tailwind CSS."
        }

        ### Example 2:
        Issue Content:
        'A critical bug causing 500 errors in the API when users submit forms.'

        Expected JSON Response:
        {
        "issue_type": "Bug",
        "priority": "Highest",
        "labels": ["backend", "API", "bug"],
        "story_points": null,
        "components": ["Form Submission", "API"],
        "description": "Fix critical bug causing 500 errors in the API."
        }

        Now, analyze the following issue and return a JSON response.

        Issue Content:
        {content}

        JSON Response:
        """.strip()

    def extract_metadata(self, content: str) -> IssueMetadata:
        """
        Analyzes the issue content and extracts relevant metadata.

        Args:
            content: The generated issue content to analyze

        Returns:
            IssueMetadata object containing the extracted metadata
        """
        logger.info("Extracting metadata from issue content")

        try:
            # Generate analysis using LLM with structured output
            prompt = self._create_analysis_prompt(content)
            logger.debug(f"Created analysis prompt of length: {len(prompt)}")
            with LiteLLMClient(self.llm_config) as llm:
                metadata = llm.generate(
                    prompt, response_format=IssueMetadata, temperature=0.3
                )

                logger.info(f"Successfully extracted metadata: {metadata}")
                logger.info(f"Metadata type: {type(metadata)}")
                return metadata

        except Exception as e:
            logger.error("Failed to extract metadata", exc_info=True)
            raise RuntimeError(f"Metadata extraction failed: {e}") from e
