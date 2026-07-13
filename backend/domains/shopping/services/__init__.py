"""
Bridge per i services Shopping modularizzati.
"""

from .groups import (
    list_groups,
    create_group,
    update_group,
    delete_group,
    list_members,
    add_member,
    invite_member,
    update_member_role,
    remove_member,
)
from .lists import (
    list_lists,
    create_list,
    update_list,
    delete_list,
    list_items,
    create_item,
    update_item,
    delete_item,
)

__all__ = [
    # groups
    "list_groups",
    "create_group",
    "update_group",
    "delete_group",
    "list_members",
    "add_member",
    "invite_member",
    "update_member_role",
    "remove_member",
    # lists
    "list_lists",
    "create_list",
    "update_list",
    "delete_list",
    "list_items",
    "create_item",
    "update_item",
    "delete_item",
]