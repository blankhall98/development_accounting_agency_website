from __future__ import annotations

import json
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import UiCopy


DEFAULT_UI_COPY: Dict[str, str] = {
    "brand_mark": "AC",
    "brand_title": "Agencia Contable",
    "brand_subtitle": "Estrategia financiera en México",
    "nav_home_label": "Inicio",
    "nav_about_label": "Nosotros",
    "nav_learn_label": "Aprende más",
    "nav_contact_label": "Contactar",
    "footer_title": "Atención directa",
    "footer_text": "Agenda una cita con nuestro equipo y recibe un diagnóstico inicial.",
    "footer_contact_title": "Contacto",
    "footer_social_title": "Redes",
    "footer_bottom": "© 2026 Agencia Contable. Todos los derechos reservados.",
    "index_eyebrow": "Firma contable en México",
    "hero_primary_cta": "Agenda una asesoría",
    "hero_secondary_cta": "Explorar contenido",
    "index_identity_eyebrow": "Identidad",
    "index_services_eyebrow": "Lo que hacemos",
    "index_services_intro": "Servicios diseñados para simplificar tu operación y fortalecer tu estrategia.",
    "hero_card_title": "Respaldo integral",
    "hero_card_text": "Coordinamos contabilidad, fiscal y nómina para que tomes decisiones seguras y oportunas.",
    "metric_1_value": "350",
    "metric_1_prefix": "+",
    "metric_1_suffix": "",
    "metric_1_label": "clientes activos",
    "metric_2_value": "12",
    "metric_2_prefix": "",
    "metric_2_suffix": "",
    "metric_2_label": "trayectoria",
    "metric_3_value": "98",
    "metric_3_prefix": "",
    "metric_3_suffix": "%",
    "metric_3_label": "satisfacción",
    "contact_heading": "Hablemos de tu crecimiento",
    "contact_form_heading": "Envíanos un mensaje",
    "contact_button_label": "Enviar",
    "contact_direct_label": "Contacto Directo",
    "social_label_facebook": "Facebook",
    "social_label_instagram": "Instagram",
    "social_label_x": "X",
    "social_label_linkedin": "LinkedIn",
    "contact_label_whatsapp": "WhatsApp",
    "contact_label_email": "Email",
    "contact_label_phone": "Teléfono",
    "contact_label_address": "Dirección",
    "contact_label_name": "Nombre",
    "contact_label_email_field": "Correo",
    "contact_label_message": "Mensaje",
    "contact_alert_sent": "Mensaje enviado. Te responderemos pronto.",
    "contact_alert_pending": "Mensaje registrado. Configura el correo SMTP para envío automático.",
    "about_eyebrow": "Nosotros",
    "team_eyebrow": "Personas",
    "team_intro": "Profesionales con experiencia en contabilidad, fiscal y estrategia financiera.",
    "location_heading": "Estamos en el corazón financiero",
    "location_intro": "Visítanos en nuestras oficinas o agenda una reunión virtual con el equipo.",
    "learn_more_eyebrow": "Conocimiento",
    "learn_more_link_label": "Ver publicación",
}


def get_ui_copy(db: Session) -> Dict[str, str]:
    row = db.query(UiCopy).first()
    data: Dict[str, Any] = {}
    if row and row.data:
        try:
            data = json.loads(row.data)
        except json.JSONDecodeError:
            data = {}
    merged = {**DEFAULT_UI_COPY, **data}
    return merged


def save_ui_copy(db: Session, payload: Dict[str, str]) -> None:
    filtered = {key: payload.get(key, "") for key in DEFAULT_UI_COPY}
    row = db.query(UiCopy).first()
    if not row:
        row = UiCopy(data=json.dumps(filtered, ensure_ascii=False))
        db.add(row)
    else:
        row.data = json.dumps(filtered, ensure_ascii=False)
        db.add(row)
    db.commit()
