import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from litellm import completion
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, model_validator

from jiragen.core.client import VectorStoreClient, VectorStoreConfig


class LLMConfig(BaseModel):
    model: str = "openai/gpt-4o-mini"  # Default model name
    api_base: Optional[str] = Field(
        default=None
    )  # API endpoint, set based on model
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.95

    model_config = ConfigDict(
        arbitrary_types_allowed=True, extra="allow", validate_assignment=True
    )

    @model_validator(mode="after")
    def set_api_base(self) -> "LLMConfig":
        """Proper V2 validator for api_base"""
        if "/" in self.model:
            provider = self.model.split("/")[0]
            if provider == "ollama":
                self.api_base = "http://localhost:11434"
        return self

    def to_request_params(self) -> Dict[str, Any]:
        params = self.model_dump()
        params.pop("api_base", None)
        logger.debug(f"LLM parameters: {params}")
        return params


class GeneratorConfig(BaseModel):
    template_path: Path
    llm_config: LLMConfig
    max_context_length: int = 128000

    model_config = ConfigDict(arbitrary_types_allowed=True)


class LiteLLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        # Configure litellm to use Ollama
        self.api_base = config.api_base
        logger.info(
            f"Initialized LiteLLM client with model: {config.model} at {config.api_base}"
        )

    def generate(
        self,
        prompt: str,
        response_format: Optional[BaseModel] = None,
        **kwargs,
    ) -> str:
        start_time = time.time()

        params = self.config.to_request_params()
        if kwargs:
            logger.debug(f"Overriding default parameters with: {kwargs}")
            params.update(kwargs)

        try:
            # Enable JSON schema validation if response_format is provided
            if response_format:
                params["response_format"] = response_format
            else:
                pass

            response = completion(
                messages=[{"role": "user", "content": prompt}],
                api_base=self.api_base,
                **params,
            )

            generation_time = time.time() - start_time
            logger.info(f"Generated response in {generation_time:.2f} seconds")

            return response.choices[0].message.content

        except Exception as e:
            error_msg = f"LiteLLM API request failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Closed LiteLLM client connection")


class IssueGenerator:
    """Generator for creating JIRA tickets using both JIRA and codebase context.

    Uses RAG (Retrieval Augmented Generation) to find relevant context from both
    JIRA history and codebase, then generates a ticket following a template.

    Attributes:
        vector_store: Vector store client for retrieving similar documents
        config: Generator configuration
    """

    def __init__(
        self,
        vector_store: "VectorStoreClient",
        config: GeneratorConfig,  # noqa: F821
    ) -> None:
        self.vector_store = vector_store
        self.config = config
        logger.info(f"Initialized IssueGenerator with config: {config}")

    def _prepare_context(
        self, similar_docs: List[Dict[str, Any]], context_type: str
    ) -> str:
        """Prepare context from similar documents with length limit.

        Args:
            similar_docs: List of similar documents with their content and metadata
            context_type: Type of context being prepared ('JIRA' or 'codebase')

        Returns:
            Formatted string containing the context with file paths and content
        """
        logger.debug(
            f"Preparing {context_type} context from {len(similar_docs)} documents"
        )
        contexts = []
        total_length = 0
        skipped_docs = 0

        for doc in similar_docs:
            content = doc["content"]
            metadata = doc["metadata"]

            if total_length + len(content) > self.config.max_context_length:
                skipped_docs += 1
                logger.debug(
                    f"Skipped document due to length limit: {metadata['file_path']}"
                )
                continue

            contexts.append(f"File: {metadata['file_path']}\n{content}")
            total_length += len(content)
            logger.debug(f"Added content from: {metadata['file_path']}")

        if skipped_docs:
            logger.info(
                f"Skipped {skipped_docs} documents due to context length limit"
            )

        return "\n\n---\n\n".join(contexts)

    def _create_prompt(
        self,
        message: str,
        jira_context: str,
        codebase_context: str,
        template: str,
    ) -> str:
        """Create a prompt incorporating both JIRA and codebase context.

        Args:
            message: User's request for the ticket
            jira_context: Relevant context from JIRA history
            codebase_context: Relevant context from the codebase
            template: Template to follow for ticket generation

        Returns:
            Complete prompt for the LLM to generate a ticket
        """
        prompt = f"""You are an expert software engineer tasked with generating a JIRA ticket.
Follow the template below exactly, filling in appropriate content based on the message and context.

Template to follow:
{template}

## Potentially Relevant JIRA context for ticket creation:
{jira_context}

## Potentially Relevant codebase context for ticket creation:
{codebase_context}

Using the previous context, generate a JIRA ticket for the following Issue:
{message}

Instructions:
1. Use the exact template structure provided above
2. Generate comprehensive content while maintaining the template format
3. Include technical details and implementation considerations from the context
4. Ensure all acceptance criteria are specific and testable
5. Reference relevant files and components from the context

Generated ticket:"""

        logger.debug(f"Created prompt of length: {len(prompt)}")
        return prompt

    def generate(self, message: str) -> str:
        """Generate a JIRA ticket using RAG and template-guided generation.

        Retrieves relevant context from both JIRA history and codebase,
        then uses an LLM to generate a ticket following the template.

        Args:
            message: User's request for the ticket

        Returns:
            Generated ticket content following the template

        Raises:
            RuntimeError: If ticket generation fails
        """
        logger.info(f"Generating ticket for message: {message}")
        start_time = time.time()

        try:
            # Load template
            template = self.config.template_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded template of length: {len(template)}")

            runtime_dir = self.vector_store.config.db_path.parent.parent

            # Initialize and get JIRA context
            jira_store = VectorStoreClient(
                VectorStoreConfig(
                    collection_name="jira_content",
                    db_path=runtime_dir / "jira_data" / "vector_db",
                )
            )
            jira_store.initialize_store()  # Ensure collection is initialized
            jira_docs = jira_store.query_similar(message)
            logger.info(f"Retrieved {len(jira_docs)} similar JIRA documents")
            jira_context = self._prepare_context(jira_docs, "JIRA")

            # Initialize and get codebase context
            codebase_store = VectorStoreClient(
                VectorStoreConfig(
                    collection_name="codebase_content",
                    db_path=runtime_dir / "codebase_data" / "vector_db",
                )
            )
            codebase_store.initialize_store()  # Ensure collection is initialized
            codebase_docs = codebase_store.query_similar(message)
            logger.info(
                f"Retrieved {len(codebase_docs)} similar codebase documents"
            )
            codebase_context = self._prepare_context(codebase_docs, "codebase")

            # Generate ticket with template-guided prompt
            prompt = self._create_prompt(
                message, jira_context, codebase_context, template
            )

            with LiteLLMClient(self.config.llm_config) as llm:
                ticket_content = llm.generate(
                    prompt,
                    temperature=self.config.llm_config.temperature,
                    max_tokens=self.config.llm_config.max_tokens,
                )

            generation_time = time.time() - start_time
            logger.info(f"Generated ticket in {generation_time:.2f} seconds")

            return ticket_content

        except Exception as e:
            logger.error("Failed to generate ticket", exc_info=True)
            raise RuntimeError(f"Failed to generate ticket: {e}") from e


if __name__ == "__main__":
    config = LLMConfig()
    print(config)
