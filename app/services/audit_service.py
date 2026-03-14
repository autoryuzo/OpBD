from app.core.db import SessionLocal
from app.models.audit_log import AuditLog


def log_action(action: str, entity: str, entity_id: int, performed_by: str = None):
    db = SessionLocal()

    log_entry = AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        performed_by=performed_by
    )

    db.add(log_entry)
    db.commit()
    db.close()