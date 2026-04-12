from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


class RegisterMethod(str, Enum):
    UNSPECIFIED = "REGISTER_METHOD_UNSPECIFIED"
    AUTH_KEY = "REGISTER_METHOD_AUTH_KEY"
    CLI = "REGISTER_METHOD_CLI"
    OIDC = "REGISTER_METHOD_OIDC"


@dataclass
class User(DataClassORJSONMixin):
    id: str | None = None
    name: str | None = None
    created_at: datetime | None = field(
        default=None, metadata=field_options(alias="createdAt")
    )
    display_name: str | None = field(
        default=None, metadata=field_options(alias="displayName")
    )
    email: str | None = None
    provider_id: str | None = field(
        default=None, metadata=field_options(alias="providerId")
    )
    provider: str | None = None
    profile_pic_url: str | None = field(
        default=None, metadata=field_options(alias="profilePicUrl")
    )


@dataclass
class PreAuthKey(DataClassORJSONMixin):
    id: str | None = None
    key: str | None = None
    reusable: bool | None = None
    ephemeral: bool | None = None
    used: bool | None = None
    expiration: datetime | None = None
    created_at: datetime | None = field(
        default=None, metadata=field_options(alias="createdAt")
    )
    user: User | None = None
    acl_tags: list[str] = field(
        default_factory=list, metadata=field_options(alias="aclTags")
    )


@dataclass
class Node(DataClassORJSONMixin):
    id: str
    machine_key: str | None = field(
        default=None, metadata=field_options(alias="machineKey")
    )
    node_key: str | None = field(default=None, metadata=field_options(alias="nodeKey"))
    disco_key: str | None = field(
        default=None, metadata=field_options(alias="discoKey")
    )
    ip_addresses: list[str] = field(
        default_factory=list, metadata=field_options(alias="ipAddresses")
    )
    name: str | None = None
    user: User | None = None
    last_seen: datetime | None = field(
        default=None, metadata=field_options(alias="lastSeen")
    )
    expiry: datetime | None = None
    pre_auth_key: PreAuthKey | None = field(
        default=None, metadata=field_options(alias="preAuthKey")
    )
    created_at: datetime | None = field(
        default=None, metadata=field_options(alias="createdAt")
    )
    register_method: RegisterMethod | None = field(
        default=None, metadata=field_options(alias="registerMethod")
    )
    given_name: str | None = field(
        default=None, metadata=field_options(alias="givenName")
    )
    online: bool | None = None
    approved_routes: list[str] = field(
        default_factory=list, metadata=field_options(alias="approvedRoutes")
    )
    available_routes: list[str] = field(
        default_factory=list, metadata=field_options(alias="availableRoutes")
    )
    subnet_routes: list[str] = field(
        default_factory=list, metadata=field_options(alias="subnetRoutes")
    )
    tags: list[str] = field(default_factory=list)


@dataclass
class ListNodesResponse(DataClassORJSONMixin):
    nodes: dict[str, Node] = field(default_factory=dict)

    @classmethod
    def __pre_deserialize__(cls, data: dict) -> dict:
        return {"nodes": {node["id"]: node for node in data.get("nodes", [])}}
