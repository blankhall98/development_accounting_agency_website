from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import settings
from app.models import (
    AboutContent,
    Admin,
    IndexContent,
    LearnMoreContent,
    Post,
    Service,
    SiteSettings,
    TeamMember,
    UiCopy,
)
from app.ui_copy import DEFAULT_UI_COPY


def seed_initial_data(db: Session) -> None:
    if not db.query(Admin).first():
        super_admin = Admin(
            username=settings.super_admin_username,
            hashed_password=hash_password(settings.super_admin_password),
            is_super=True,
        )
        db.add(super_admin)

    if not db.query(SiteSettings).first():
        db.add(SiteSettings())

    if not db.query(IndexContent).first():
        db.add(IndexContent())

    if not db.query(AboutContent).first():
        db.add(AboutContent())

    if not db.query(LearnMoreContent).first():
        db.add(LearnMoreContent())

    if not db.query(Service).first():
        db.add_all(
            [
                Service(
                    title="Contabilidad mensual",
                    description="Registro contable preciso y estados financieros claros cada mes.",
                    key_points="Conciliaciones bancarias\nReportes puntuales\nIndicadores de liquidez",
                ),
                Service(
                    title="Planeación fiscal",
                    description="Estrategias legales para optimizar cargas fiscales sin riesgos.",
                    key_points="Cumplimiento SAT\nRevisión preventiva\nAhorro sostenido",
                ),
                Service(
                    title="Nómina y seguridad social",
                    description="Gestión integral de nómina con enfoque en cumplimiento y confianza.",
                    key_points="Cálculo preciso\nAltas y bajas\nAtención a auditorías",
                ),
            ]
        )

    if not db.query(TeamMember).first():
        db.add_all(
            [
                TeamMember(
                    name="María Fernanda Ruiz",
                    role="Socia Directora",
                    bio="Especialista en finanzas corporativas con 12 años de experiencia en firmas nacionales.",
                    image_url="",
                ),
                TeamMember(
                    name="José Luis Paredes",
                    role="Gerente Fiscal",
                    bio="Experto en cumplimiento y planeación tributaria para PyMEs y startups.",
                    image_url="",
                ),
            ]
        )

    if not db.query(Post).first():
        db.add_all(
            [
                Post(
                    title="Guía rápida para cerrar tu año fiscal",
                    description="Checklist esencial para preparar tus obligaciones sin estrés.",
                    content_type="none",
                    content_url="",
                ),
                Post(
                    title="Tendencias contables 2026",
                    description="Automatización, reporteo en tiempo real y cultura de datos.",
                    content_type="none",
                    content_url="",
                ),
            ]
        )

    if not db.query(UiCopy).first():
        db.add(UiCopy(data=json.dumps(DEFAULT_UI_COPY, ensure_ascii=False)))

    db.commit()
