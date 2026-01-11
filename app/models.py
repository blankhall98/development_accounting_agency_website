from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_super: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contact_email: Mapped[str] = mapped_column(String(255), default="contacto@agencia.mx")
    whatsapp_number: Mapped[str] = mapped_column(String(30), default="+5215512345678")
    phone_number: Mapped[str] = mapped_column(String(30), default="+52 55 1234 5678")
    address_text: Mapped[str] = mapped_column(String(255), default="Ciudad de México, México")

    social_facebook: Mapped[str] = mapped_column(String(255), default="https://facebook.com")
    social_instagram: Mapped[str] = mapped_column(String(255), default="https://instagram.com")
    social_x: Mapped[str] = mapped_column(String(255), default="https://x.com")
    social_linkedin: Mapped[str] = mapped_column(String(255), default="https://linkedin.com")


class IndexContent(Base):
    __tablename__ = "index_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hero_title: Mapped[str] = mapped_column(String(150), default="Contabilidad clara, crecimiento seguro")
    hero_subtitle: Mapped[str] = mapped_column(
        String(255),
        default="Acompañamos a negocios mexicanos con planeación fiscal, cumplimiento y estrategia financiera.",
    )
    mission_title: Mapped[str] = mapped_column(String(80), default="Misión")
    mission_text: Mapped[str] = mapped_column(
        Text,
        default="Impulsar a nuestros clientes con soluciones contables confiables, transparentes y oportunas.",
    )
    values_title: Mapped[str] = mapped_column(String(80), default="Valores")
    values_text: Mapped[str] = mapped_column(
        Text,
        default="Ética, precisión, confidencialidad, enfoque humano y mejora continua.",
    )
    services_title: Mapped[str] = mapped_column(String(80), default="Servicios")
    contact_title: Mapped[str] = mapped_column(String(80), default="Contacto")
    contact_text: Mapped[str] = mapped_column(
        Text,
        default="Agenda una asesoría y recibe un diagnóstico inicial sin costo.",
    )


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[str] = mapped_column(Text, default="")


class AboutContent(Base):
    __tablename__ = "about_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), default="Nuestra trayectoria")
    story_text: Mapped[str] = mapped_column(
        Text,
        default=(
            "Más de una década acompañando a empresas familiares, startups y corporativos en México, "
            "con soluciones contables y fiscales que respaldan cada decisión."
        ),
    )
    team_title: Mapped[str] = mapped_column(String(80), default="Equipo")
    location_title: Mapped[str] = mapped_column(String(80), default="Ubicación")
    location_map_url: Mapped[str] = mapped_column(
        String(500),
        default="https://www.google.com/maps?q=Ciudad%20de%20Mexico&output=embed",
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), default="")


class LearnMoreContent(Base):
    __tablename__ = "learn_more_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), default="Aprende más")
    intro_text: Mapped[str] = mapped_column(
        Text,
        default=(
            "Consejos, noticias y análisis para tomar decisiones informadas en tu negocio. "
            "Explora nuestras publicaciones recientes."
        ),
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(30), default="none")
    content_url: Mapped[str] = mapped_column(String(500), default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UiCopy(Base):
    __tablename__ = "ui_copy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[str] = mapped_column(Text, default="{}")
