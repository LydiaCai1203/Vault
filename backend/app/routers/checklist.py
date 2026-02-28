from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import ChecklistORM
from ..dependencies import get_current_user, get_db
from ..domain.checklist import ChecklistItem, ChecklistOut

router = APIRouter(prefix="/api/checklist", tags=["checklist"])


def _get_checklist(db: Session, user_id: str) -> ChecklistOut:
    rows = db.query(ChecklistORM).filter(ChecklistORM.user_id == user_id).all()
    items = [ChecklistItem(id=r.id, text=r.text, done=r.done) for r in rows]
    return ChecklistOut(items=items)


@router.get("", response_model=ChecklistOut)
def get_checklist(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return _get_checklist(db, user_id)


@router.post("", response_model=ChecklistOut)
def set_checklist(
    items: list[ChecklistItem],
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    db.query(ChecklistORM).filter(ChecklistORM.user_id == user_id).delete()
    for it in items:
        db.add(ChecklistORM(id=it.id, user_id=user_id, text=it.text, done=it.done))
    db.commit()
    return _get_checklist(db, user_id)
