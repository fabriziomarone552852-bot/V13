"""
Services per ShoppingGroup e ShoppingGroupMember.
Regole di business: ownership, membership, ruoli.
"""

from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.domains.shopping import repository as repo
from backend.domains.shopping import schemas
from backend.domains.shopping.models import ShoppingGroup, ShoppingGroupMember
from backend.domains.users.models import User
from .common import _now

_GROUP_NOT_FOUND = "Gruppo non trovato o non accessibile"
_MEMBER_NOT_FOUND = "Membro non trovato nel gruppo"
_USER_NOT_FOUND = "Utente non trovato"
_ROLE_NOT_FOUND = "Ruolo non valido"


# --- Groups ---

def list_groups(db: Session, current_user: User) -> List[ShoppingGroup]:
    return repo.list_groups(db, current_user.id)


def create_group(
    db: Session,
    current_user: User,
    group_in: schemas.ShoppingGroupCreate,
) -> ShoppingGroup:
    default_status_id = repo.active_group_status_id(db)
    if default_status_id is None:
        raise HTTPException(status_code=500, detail="ConfigCode group_status.active mancante")

    now = _now()
    db_group = ShoppingGroup(
        owner_id=current_user.id,
        name=group_in.name,
        description=group_in.description,
        status_id=group_in.status_id or default_status_id,
        created_at=now,
        updated_at=now,
    )
    return repo.create_group(db, db_group)


def update_group(
    db: Session,
    current_user: User,
    group_id: int,
    group_in: schemas.ShoppingGroupUpdate,
) -> ShoppingGroup:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    for field, value in group_in.model_dump(exclude_unset=True).items():
        setattr(db_group, field, value)
    db_group.updated_at = _now()

    return repo.update_group(db, db_group)


def delete_group(db: Session, current_user: User, group_id: int) -> None:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)
    repo.delete_group(db, db_group)


# --- Group Members ---

def list_members(db: Session, current_user: User, group_id: int) -> List[ShoppingGroupMember]:
    group = repo.get_group_accessible(db, group_id, current_user.id)
    if not group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)
    return repo.list_members(db, group_id)


def add_member(
    db: Session,
    current_user: User,
    group_id: int,
    member_in: schemas.ShoppingGroupMemberCreate,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    existing = repo.get_member(db, group_id, member_in.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="L'utente è già membro del gruppo.")

    now = _now()
    db_member = ShoppingGroupMember(
        group_id=group_id,
        user_id=member_in.user_id,
        role_id=member_in.role_id,
        added_by_user_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    return repo.add_member(db, db_member)


def invite_member(
    db: Session,
    current_user: User,
    group_id: int,
    invite_in: schemas.ShoppingGroupMemberInvite,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    target_user = repo.find_user_by_username_or_email(db, invite_in.username, invite_in.email)
    if not target_user:
        raise HTTPException(status_code=404, detail=_USER_NOT_FOUND)

    existing = repo.get_member(db, group_id, target_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="L'utente è già membro del gruppo.")

    role_id = repo.resolve_role_id(db, invite_in.role_code)
    if role_id is None:
        raise HTTPException(status_code=400, detail=_ROLE_NOT_FOUND)

    now = _now()
    db_member = ShoppingGroupMember(
        group_id=group_id,
        user_id=target_user.id,
        role_id=role_id,
        added_by_user_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    return repo.add_member(db, db_member)


def update_member_role(
    db: Session,
    current_user: User,
    group_id: int,
    user_id: int,
    role_in: schemas.ShoppingGroupMemberRoleUpdate,
) -> ShoppingGroupMember:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    db_member = repo.get_member(db, group_id, user_id)
    if not db_member:
        raise HTTPException(status_code=404, detail[_MEMBER_NOT_FOUND])

    role_id = repo.resolve_role_id(db, role_in.role_code)
    if role_id is None:
        raise HTTPException(status_code=400, detail[_ROLE_NOT_FOUND])

    db_member.role_id = role_id
    db_member.updated_at = _now()
    return repo.update_member(db, db_member)


def remove_member(db: Session, current_user: User, group_id: int, user_id: int) -> None:
    db_group = repo.get_group_owned(db, group_id, current_user.id)
    if not db_group:
        raise HTTPException(status_code=404, detail=_GROUP_NOT_FOUND)

    db_member = repo.get_member(db, group_id, user_id)
    if not db_member:
        raise HTTPException(status_code=404, detail[_MEMBER_NOT_FOUND])

    if db_member.user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Non puoi rimuovere te stesso. Trasferisci la proprietà o elimina il gruppo.",
        )

    repo.remove_member(db, db_member)