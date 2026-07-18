"""
Repository per ShoppingGroup e ShoppingGroupMember.
Solo accesso ai dati, nessuna regola di business.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from backend.domains.config import ConfigCode
from backend.domains.shopping.models import ShoppingGroup, ShoppingGroupMember
from backend.domains.users.models import User
from .common import soft_delete_criteria, _now


# --- Groups ---

def list_groups(db: Session, user_id: int) -> List[ShoppingGroup]:
    """Lista gruppi posseduti dall'utente e gruppi dove è membro attivo."""
    owned = (
        db.query(ShoppingGroup)
        .options(*soft_delete_criteria())
        .filter(
            ShoppingGroup.owner_id == user_id,
            ShoppingGroup.deleted_at.is_(None),
        )
        .order_by(ShoppingGroup.created_at.asc())
        .all()
    )

    member_of = (
        db.query(ShoppingGroup)
        .options(*soft_delete_criteria())
        .join(ShoppingGroupMember, ShoppingGroupMember.group_id == ShoppingGroup.id)
        .filter(
            ShoppingGroup.deleted_at.is_(None),
            ShoppingGroupMember.user_id == user_id,
            ShoppingGroupMember.removed_at.is_(None),
            ShoppingGroup.owner_id != user_id,
        )
        .order_by(ShoppingGroup.created_at.asc())
        .all()
    )

    return owned + member_of


def get_group_owned(db: Session, group_id: int, user_id: int) -> Optional[ShoppingGroup]:
    return (
        db.query(ShoppingGroup)
        .options(*soft_delete_criteria())
        .filter(
            ShoppingGroup.id == group_id,
            ShoppingGroup.owner_id == user_id,
            ShoppingGroup.deleted_at.is_(None),
        )
        .first()
    )


def get_group_accessible(db: Session, group_id: int, user_id: int) -> Optional[ShoppingGroup]:
    """Gruppo che l'utente possiede oppure dove è membro attivo."""
    group = (
        db.query(ShoppingGroup)
        .options(*soft_delete_criteria())
        .filter(
            ShoppingGroup.id == group_id,
            ShoppingGroup.deleted_at.is_(None),
        )
        .first()
    )
    if not group:
        return None

    if group.owner_id == user_id:
        return group

    membership = (
        db.query(ShoppingGroupMember)
        .filter(
            ShoppingGroupMember.group_id == group_id,
            ShoppingGroupMember.user_id == user_id,
            ShoppingGroupMember.removed_at.is_(None),
        )
        .first()
    )
    return group if membership else None


def create_group(db: Session, group: ShoppingGroup) -> ShoppingGroup:
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def update_group(db: Session, group: ShoppingGroup) -> ShoppingGroup:
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group: ShoppingGroup) -> None:
    """
    Soft delete per i gruppi con gestione manuale della cascata:
    - group.deleted_at impostato
    - membri attivi marcati come rimossi
    - group_id delle liste impostato a NULL
    """
    now = _now()
    group.deleted_at = now

    for member in group.members:
        if member.removed_at is None:
            member.removed_at = now

    for shopping_list in group.shopping_lists:
        shopping_list.group_id = None

    db.commit()


# --- Group Members ---

def list_members(db: Session, group_id: int) -> List[ShoppingGroupMember]:
    return (
        db.query(ShoppingGroupMember)
        .filter(
            ShoppingGroupMember.group_id == group_id,
            ShoppingGroupMember.removed_at.is_(None),
        )
        .order_by(ShoppingGroupMember.created_at.asc())
        .all()
    )


def get_member(db: Session, group_id: int, user_id: int) -> Optional[ShoppingGroupMember]:
    return (
        db.query(ShoppingGroupMember)
        .filter(
            ShoppingGroupMember.group_id == group_id,
            ShoppingGroupMember.user_id == user_id,
            ShoppingGroupMember.removed_at.is_(None),
        )
        .first()
    )


def add_member(db: Session, member: ShoppingGroupMember) -> ShoppingGroupMember:
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member: ShoppingGroupMember) -> ShoppingGroupMember:
    db.commit()
    db.refresh(member)
    return member


def remove_member(db: Session, member: ShoppingGroupMember) -> None:
    member.removed_at = _now()
    db.commit()


# --- Helpers per utenti e ruoli ---

def find_user_by_username_or_email(
    db: Session,
    username: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    query = db.query(User)
    if username:
        return query.filter(User.username == username).first()
    if email:
        return query.filter(User.email == email.lower()).first()
    return None


def resolve_role_id(db: Session, role_code: str) -> Optional[int]:
    return (
        db.query(ConfigCode.id)
        .filter(
            ConfigCode.code_type == "shopping_group_role",
            ConfigCode.code_value == role_code,
        )
        .scalar()
    )


def active_group_status_id(db: Session) -> Optional[int]:
    return (
        db.query(ConfigCode.id)
        .filter(
            ConfigCode.code_type == "group_status",
            ConfigCode.code_value == "active",
        )
        .scalar()
    )