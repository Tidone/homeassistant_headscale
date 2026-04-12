"""Exceptions for the Headscale API client."""


class HeadscaleError(Exception):
    """Generic Headscale exception."""


class HeadscaleAuthenticationError(HeadscaleError):
    """Headscale authentication exception."""


class HeadscaleConnectionError(HeadscaleError):
    """Headscale connection exception."""
