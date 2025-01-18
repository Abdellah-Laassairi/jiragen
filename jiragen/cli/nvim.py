"""Nvim utility for jiragen CLI."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from loguru import logger
from rich.console import Console

console = Console()


def check_markdown_preview_nvim() -> bool:
    """
    Check if markdown-preview.nvim plugin is installed in any of the standard locations.

    Returns:
        bool: True if plugin is found, False otherwise
    """
    possible_paths = [
        Path.home()
        / ".local/share/nvim/site/pack/packer/start/markdown-preview.nvim",
        Path.home() / ".vim/plugged/markdown-preview.nvim",
        Path.home() / ".config/nvim/pack/plugins/start/markdown-preview.nvim",
    ]

    return any(path.exists() for path in possible_paths)


def create_temp_vimrc(preview_enabled: bool) -> Path:
    """
    Create a temporary vimrc file with markdown preview settings.

    Args:
        preview_enabled: Whether markdown preview is available

    Returns:
        Path: Path to temporary vimrc file
    """
    # Create a secure temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".vim")
    os.close(fd)  # Close the file descriptor as we'll use Path
    temp_vimrc = Path(temp_path)

    vimrc_content = [
        "set nocompatible",
        "filetype plugin on",
        "syntax on",
        "set termguicolors",
    ]

    if preview_enabled:
        vimrc_content.extend(
            [
                '" Markdown Preview settings',
                "let g:mkdp_auto_start = 1",  # Auto-start preview
                'let g:mkdp_browser = "firefox"',  # Use Firefox as default browser
                'let g:mkdp_preview_options = { "disable_sync_scroll": 0 }',
                "let g:mkdp_auto_close = 0",  # Don't auto-close preview
                "let g:mkdp_refresh_slow = 0",  # Real-time preview updates
            ]
        )

    with open(temp_vimrc, "w") as f:
        f.write("\n".join(vimrc_content))

    return temp_vimrc


def open_in_neovim(content: str) -> Optional[str]:
    """
    Open content in Neovim with markdown preview if available.

    Args:
        content (str): Initial content to edit

    Returns:
        Optional[str]: Modified content if saved, None if canceled
    """
    try:
        # Check for markdown-preview.nvim plugin
        has_preview = check_markdown_preview_nvim()
        if not has_preview:
            console.print(
                "[yellow]Warning: markdown-preview.nvim plugin not found. Preview will be disabled.[/]"
            )

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".md", delete=False
        ) as tf:
            tf.write(content)
            temp_file_path = tf.name

        # Create temporary vimrc
        temp_vimrc = create_temp_vimrc(has_preview)

        # Clear the screen before opening Neovim
        console.clear()

        try:
            # Construct Neovim command with custom vimrc
            nvim_cmd = ["nvim", "-u", str(temp_vimrc), temp_file_path]

            if has_preview:
                console.print(
                    "[bold blue]Opening Neovim with Markdown preview...[/]"
                )
                console.print(
                    "[dim]Preview will open in your default browser[/]"
                )
            else:
                console.print("[bold blue]Opening Neovim...[/]")

            # Run Neovim
            subprocess.run(nvim_cmd, check=True)

            # Read modified content
            with open(temp_file_path) as f:
                modified_content = f.read()

            # Cleanup temporary files
            os.unlink(temp_file_path)
            os.unlink(temp_vimrc)

            return modified_content

        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            console.print(
                "[red]Error: Neovim (nvim) is not installed or not in PATH[/]"
            )
            return None

    except Exception as e:
        logger.error(f"Error opening Neovim: {str(e)}")
        return None
    finally:
        # Ensure cleanup of temporary files
        for temp_file in [Path(temp_file_path), temp_vimrc]:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass


def setup_nvim_environment() -> None:
    """
    Set up the Neovim environment with required plugins if not already present.
    """
    if not check_markdown_preview_nvim():
        console.print(
            "[yellow]markdown-preview.nvim plugin not found. To enable preview, install it using your plugin manager:[/]"
        )
        console.print("\nFor vim-plug, add to your init.vim/vimrc:")
        console.print(
            "Plug 'iamcco/markdown-preview.nvim', { 'do': 'cd app && yarn install' }"
        )
        console.print("\nFor packer.nvim, add to your init.lua:")
        console.print(
            'use({"iamcco/markdown-preview.nvim", run = "cd app && yarn install"})'
        )
        console.print(
            "\nThen restart Neovim and run :PlugInstall or :PackerSync\n"
        )
