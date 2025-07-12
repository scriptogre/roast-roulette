from __future__ import annotations

from contextvars import ContextVar
from pathlib import Path
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates as StarletteJinja2Templates
from jinja2 import Environment, FileSystemLoader


_current_request: ContextVar[Request] = ContextVar("current_request")
"""Global context variable to store the current request."""

_templates: Jinja2Templates | None = None
"""Holds the loaded Templates instance."""


class Jinja2Templates(StarletteJinja2Templates):
    """
    Enhanced version of Starlette's Jinja2Templates with async rendering and block support while maintaining full compatibility.
    """

    def __init__(self, directory=None, **kwargs):
        """
        Initialize templates with async support.

        Args:
            directory: Template directory path
            **kwargs: All Jinja2 Environment options (filters, globals, etc.)
        """
        # Enable async in kwargs if not specified
        if directory:
            # Create async-enabled environment
            loader = FileSystemLoader(directory)
            env = Environment(
                loader=loader, autoescape=True, enable_async=True, **kwargs
            )
            super().__init__(env=env)
        else:
            # Allow passing custom environment
            # Ensure async is enabled if not specified
            kwargs.setdefault("enable_async", True)
            super().__init__(**kwargs)

    async def render(
        self, template_name: str, context: dict[str, Any] = None, block: str = None
    ) -> str:
        """
        Render template or specific block.

        Args:
            template_name: Template file path, optionally with #block syntax (e.g. "template.html#sidebar")
            context: Template variables
            block: Optional block name (fallback if not using #block syntax)

        Returns:
            Rendered HTML string
        """
        # Parse template#block syntax
        if "#" in template_name:
            template_path, block_name = template_name.split("#", 1)
        else:
            template_path, block_name = template_name, block

        template = self.get_template(template_path)
        final_context = context or {}

        # Auto-inject current request if available
        try:
            request = _current_request.get()
            final_context.setdefault("request", request)
            # Apply context processors like Starlette does
            for processor in self.context_processors:
                final_context.update(processor(request))
        except LookupError:
            # No request context - fine for background tasks, etc.
            pass

        if block_name:
            # Render specific block
            if block_name not in template.blocks:
                available = list(template.blocks.keys())
                raise ValueError(
                    f"Block '{block_name}' not found in template '{template_path}'. "
                    f"Available blocks: {available}"
                )

            # Create context and render block
            ctx = template.new_context(final_context)
            block_func = template.blocks[block_name]

            # Collect chunks from block generator
            chunks = [chunk async for chunk in block_func(ctx)]
            return self.env.concat(chunks)

        # Render full template
        return await template.render_async(final_context)


class FastHTML(FastAPI):
    """FastAPI subclass that defaults to HTML responses and provides convenient template rendering."""

    def __init__(self, *args, **kwargs):
        # https://fastapi.tiangolo.com/advanced/custom-response/#default-response-class
        kwargs.setdefault("default_response_class", HTMLResponse)
        """Default to HTMLResponse for all routes."""

        super().__init__(*args, **kwargs)
        self.templates: Jinja2Templates | None = None

    def add_templates(self, directory: Path | str, **jinja2_options) -> Jinja2Templates:
        """
        Load templates with full customization support.

        Args:
            directory: Template directory path
            **jinja2_options: Any Jinja2 Environment options

        Returns:
            Templates instance for advanced usage

        Examples:
            # Simple setup
            app.load_templates("templates")

            # Custom filters and globals
            app.load_templates("templates",
                filters={"custom_filter": my_filter},
                globals={"app_name": "My App"}
            )

            # Advanced Jinja2 configuration
            app.load_templates("templates",
                trim_blocks=True,
                lstrip_blocks=True,
                cache_size=1000
            )
        """
        # Create templates instance
        self.templates = Jinja2Templates(directory, **jinja2_options)

        # Store globally for render() function
        global _templates
        _templates = self.templates

        # Add middleware for request context injection
        @self.middleware("http")
        async def inject_request_context(request: Request, call_next):
            token = _current_request.set(request)
            try:
                response = await call_next(request)
                return response
            finally:
                _current_request.reset(token)

        return self.templates


async def render(
    template_name: str, context: dict[str, Any] = None, block: str = None
) -> str:
    """
    Render templates from anywhere in your application with automatic request context.

    Args:
        template_name: Template file path, optionally with #block syntax (e.g. "template.html#sidebar")
        context: Variables to pass to template
        block: Optional block name (fallback if not using #block syntax)

    Returns:
        Rendered HTML as string

    Examples:
        await render("home.html")
        await render("users/profile.html", {"user": user})
        await render("layout.html#sidebar", {"items": items})
        await render("chats/chat.html#messages", {"chat": chat})
    """
    if _templates is None:
        raise RuntimeError("Templates not loaded. Call app.load_templates() first.")

    return await _templates.render(template_name, context, block)


def url_for(name: str, **path_params: Any) -> str:
    """
    Generate URLs from anywhere in your application with automatic request context.

    Args:
        name: Route name (function name)
        **path_params: Path parameters for the route

    Returns:
        URL string

    Examples:
        url_for("get_game", game_code=game.code)
        url_for("user_profile", user_id=123)
    """
    try:
        request = _current_request.get()
    except LookupError:
        raise RuntimeError(
            "No request context available. url_for() can only be called "
            "during request handling."
        )

    return str(request.url_for(name, **path_params))
