"""Asynchronous client for the Headscale API."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from typing import Any, Self

from aiohttp.client import ClientError, ClientResponseError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import (
    HeadscaleAuthenticationError,
    HeadscaleConnectionError,
    HeadscaleError,
)
from .model import ListNodesResponse, Node


@dataclass
class Headscale:
    """Main class for handling connections with the Headscale API."""

    host: str
    api_key: str

    request_timeout: int = 8
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to the Headscale API.

        A generic method for sending/handling HTTP requests done against
        the Headscale API.

        Args:
        ----
            uri: Request URI, without '/api/v1/'.
            method: HTTP Method to use.
            data: Dictionary of data to send to the Headscale API.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from
            the Headscale API.

        Raises:
        ------
            HeadscaleAuthenticationError: If the API key is invalid.
            HeadscaleConnectionError: An error occurred while communicating with
                the Headscale API.
            HeadscaleError: Received an unexpected response from the Headscale
                API.

        """
        if self.host.startswith("https://"):
            url = URL(f"{self.host}/api/v1/").join(URL(uri))
        else:
            url = URL(f"https://{self.host}/api/v1/").join(URL(uri))

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Headscale API"
            raise HeadscaleConnectionError(msg) from exception
        except ClientResponseError as exception:
            if exception.status == 401:
                msg = "Authentication to the Headscale API failed"
                raise HeadscaleAuthenticationError(msg) from exception
            msg = "Error occurred while connecting to the Headscale API"
            raise HeadscaleError(msg) from exception
        except (
            ClientError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with the Headscale API"
            raise HeadscaleConnectionError(msg) from exception

        return await response.text()

    async def nodes(self) -> dict[str, Node]:
        """Get devices information from the Headscale API.

        Returns:
        -------
            Returns a dictionary of Headscale nodes.

        """
        data = await self._request("node")
        return ListNodesResponse.from_json(data).nodes

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns:
        -------
            The Headscale object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
