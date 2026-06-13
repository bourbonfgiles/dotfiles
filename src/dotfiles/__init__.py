"""Cross-platform dotfiles bootstrap package.

A standard-library-only toolkit that installs and configures the same
environment across macOS, Bazzite, and Fedora Silverblue. It deliberately has no
third-party runtime dependencies so it can run on a fresh machine before any
packages are installed.
"""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["__version__"]
