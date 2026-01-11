from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.auth import get_admin_from_session, hash_password, verify_password
from app.config import settings
from app.database import Base, SessionLocal, engine, get_db
from app.emailer import send_contact_email
from app.models import (
    AboutContent,
    Admin,
    ContactMessage,
    IndexContent,
    LearnMoreContent,
    Post,
    Service,
    SiteSettings,
    TeamMember,
)
from app.seed import seed_initial_data
from app.storage import save_upload
from app.ui_copy import get_ui_copy, save_ui_copy
from app.utils import maps_embed_url, whatsapp_link, youtube_embed_url

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()


def _require_admin(request: Request, db: Session) -> Optional[Admin]:
    admin_id = request.session.get("admin_id")
    return get_admin_from_session(db, admin_id)


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    settings_row = db.query(SiteSettings).first()
    content = db.query(IndexContent).first()
    services = db.query(Service).order_by(Service.id).all()
    contact_status = request.query_params.get("contact")
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "settings": settings_row,
            "content": content,
            "services": services,
            "whatsapp_link": whatsapp_link(settings_row.whatsapp_number if settings_row else ""),
            "contact_status": contact_status,
            "ui": ui,
        },
    )


@app.get("/about")
def about(request: Request, db: Session = Depends(get_db)):
    content = db.query(AboutContent).first()
    settings_row = db.query(SiteSettings).first()
    team = db.query(TeamMember).order_by(TeamMember.id).all()
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "content": content,
            "settings": settings_row,
            "team": team,
            "map_url": maps_embed_url(content.location_map_url if content else ""),
            "ui": ui,
        },
    )


@app.get("/learn-more")
def learn_more(request: Request, db: Session = Depends(get_db)):
    content = db.query(LearnMoreContent).first()
    settings_row = db.query(SiteSettings).first()
    posts = db.query(Post).filter(Post.is_published == True).order_by(Post.created_at.desc()).all()
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "learn_more.html",
        {
            "request": request,
            "content": content,
            "settings": settings_row,
            "posts": posts,
            "ui": ui,
        },
    )


@app.post("/contact")
def contact(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
):
    settings_row = db.query(SiteSettings).first()
    contact_email = settings_row.contact_email if settings_row else settings.smtp_user or ""

    db.add(ContactMessage(name=name, email=email, message=message))
    db.commit()

    sent, _detail = send_contact_email(contact_email, name, email, message)
    status = "sent" if sent else "pending"
    return RedirectResponse(url=f"/?contact={status}#contact", status_code=303)


@app.get("/admin/login")
def admin_login(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@app.post("/admin/login")
def admin_login_post(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "Credenciales incorrectas."},
            status_code=401,
        )

    request.session.clear()
    request.session["admin_id"] = admin.id
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


@app.get("/admin")
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    ui = get_ui_copy(db)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "admin": admin,
            "ui": ui,
        },
    )


@app.get("/admin/index")
def admin_index(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(IndexContent).first()
    settings_row = db.query(SiteSettings).first()
    services = db.query(Service).order_by(Service.id).all()
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "admin/edit_index.html",
        {
            "request": request,
            "admin": admin,
            "content": content,
            "settings": settings_row,
            "services": services,
            "ui": ui,
        },
    )


@app.post("/admin/index")
def admin_index_update(
    request: Request,
    db: Session = Depends(get_db),
    hero_title: str = Form(...),
    hero_subtitle: str = Form(...),
    mission_title: str = Form(...),
    mission_text: str = Form(...),
    values_title: str = Form(...),
    values_text: str = Form(...),
    services_title: str = Form(...),
    contact_title: str = Form(...),
    contact_text: str = Form(...),
    contact_email: str = Form(...),
    whatsapp_number: str = Form(...),
    phone_number: str = Form(...),
    address_text: str = Form(...),
    social_facebook: str = Form(""),
    social_instagram: str = Form(""),
    social_x: str = Form(""),
    social_linkedin: str = Form(""),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(IndexContent).first() or IndexContent()
    content.hero_title = hero_title
    content.hero_subtitle = hero_subtitle
    content.mission_title = mission_title
    content.mission_text = mission_text
    content.values_title = values_title
    content.values_text = values_text
    content.services_title = services_title
    content.contact_title = contact_title
    content.contact_text = contact_text
    db.add(content)

    settings_row = db.query(SiteSettings).first() or SiteSettings()
    settings_row.contact_email = contact_email
    settings_row.whatsapp_number = whatsapp_number
    settings_row.phone_number = phone_number
    settings_row.address_text = address_text
    settings_row.social_facebook = social_facebook
    settings_row.social_instagram = social_instagram
    settings_row.social_x = social_x
    settings_row.social_linkedin = social_linkedin
    db.add(settings_row)

    db.commit()
    return RedirectResponse("/admin/index?updated=1", status_code=303)


@app.post("/admin/services/create")
def admin_service_create(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(...),
    key_points: str = Form(""),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    db.add(Service(title=title, description=description, key_points=key_points))
    db.commit()
    return RedirectResponse("/admin/index?services=1", status_code=303)


@app.post("/admin/services/{service_id}/update")
def admin_service_update(
    request: Request,
    service_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(...),
    key_points: str = Form(""),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        service.title = title
        service.description = description
        service.key_points = key_points
        db.add(service)
        db.commit()

    return RedirectResponse("/admin/index?services=1", status_code=303)


@app.post("/admin/services/{service_id}/delete")
def admin_service_delete(request: Request, service_id: int, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        db.delete(service)
        db.commit()

    return RedirectResponse("/admin/index?services=1", status_code=303)


@app.get("/admin/about")
def admin_about(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(AboutContent).first()
    team = db.query(TeamMember).order_by(TeamMember.id).all()
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "admin/edit_about.html",
        {
            "request": request,
            "admin": admin,
            "content": content,
            "team": team,
            "ui": ui,
        },
    )


@app.post("/admin/about")
def admin_about_update(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    story_text: str = Form(...),
    team_title: str = Form(...),
    location_title: str = Form(...),
    location_map_url: str = Form(...),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(AboutContent).first() or AboutContent()
    content.title = title
    content.story_text = story_text
    content.team_title = team_title
    content.location_title = location_title
    content.location_map_url = location_map_url
    db.add(content)
    db.commit()

    return RedirectResponse("/admin/about?updated=1", status_code=303)


@app.post("/admin/team/create")
def admin_team_create(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    role: str = Form(...),
    bio: str = Form(...),
    image: UploadFile | None = File(None),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    image_url = ""
    if image and image.filename:
        image_url, _storage = save_upload(image, "team")

    db.add(TeamMember(name=name, role=role, bio=bio, image_url=image_url))
    db.commit()
    return RedirectResponse("/admin/about?team=1", status_code=303)


@app.post("/admin/team/{member_id}/update")
def admin_team_update(
    request: Request,
    member_id: int,
    db: Session = Depends(get_db),
    name: str = Form(...),
    role: str = Form(...),
    bio: str = Form(...),
    image: UploadFile | None = File(None),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if member:
        member.name = name
        member.role = role
        member.bio = bio
        if image and image.filename:
            member.image_url, _storage = save_upload(image, "team")
        db.add(member)
        db.commit()

    return RedirectResponse("/admin/about?team=1", status_code=303)


@app.post("/admin/team/{member_id}/delete")
def admin_team_delete(request: Request, member_id: int, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if member:
        db.delete(member)
        db.commit()

    return RedirectResponse("/admin/about?team=1", status_code=303)


@app.get("/admin/learn-more")
def admin_learn_more(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(LearnMoreContent).first()
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    ui = get_ui_copy(db)

    return templates.TemplateResponse(
        "admin/edit_learn_more.html",
        {
            "request": request,
            "admin": admin,
            "content": content,
            "posts": posts,
            "ui": ui,
        },
    )


@app.post("/admin/learn-more")
def admin_learn_more_update(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    intro_text: str = Form(...),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    content = db.query(LearnMoreContent).first() or LearnMoreContent()
    content.title = title
    content.intro_text = intro_text
    db.add(content)
    db.commit()

    return RedirectResponse("/admin/learn-more?updated=1", status_code=303)


@app.post("/admin/posts/create")
def admin_post_create(
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form("none"),
    content_url: str = Form(""),
    is_published: Optional[str] = Form(None),
    content_file: UploadFile | None = File(None),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    final_url = ""
    if content_type in {"image", "video"} and content_file and content_file.filename:
        final_url, _storage = save_upload(content_file, "posts")
    elif content_type == "youtube":
        final_url = youtube_embed_url(content_url)
    elif content_type == "social":
        final_url = content_url

    post = Post(
        title=title,
        description=description,
        content_type=content_type,
        content_url=final_url,
        is_published=is_published == "on",
    )
    db.add(post)
    db.commit()
    return RedirectResponse("/admin/learn-more?posts=1", status_code=303)


@app.post("/admin/posts/{post_id}/update")
def admin_post_update(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    title: str = Form(...),
    description: str = Form(...),
    content_type: str = Form("none"),
    content_url: str = Form(""),
    is_published: Optional[str] = Form(None),
    content_file: UploadFile | None = File(None),
):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        post.title = title
        post.description = description
        post.content_type = content_type
        post.is_published = is_published == "on"

        if content_type in {"image", "video"} and content_file and content_file.filename:
            post.content_url, _storage = save_upload(content_file, "posts")
        elif content_type == "youtube":
            post.content_url = youtube_embed_url(content_url)
        elif content_type == "social":
            post.content_url = content_url
        elif content_type == "none":
            post.content_url = ""

        db.add(post)
        db.commit()

    return RedirectResponse("/admin/learn-more?posts=1", status_code=303)


@app.post("/admin/posts/{post_id}/delete")
def admin_post_delete(request: Request, post_id: int, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()

    return RedirectResponse("/admin/learn-more?posts=1", status_code=303)


@app.get("/admin/admins")
def admin_manage_admins(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)

    admins = db.query(Admin).order_by(Admin.id).all()
    ui = get_ui_copy(db)
    return templates.TemplateResponse(
        "admin/manage_admins.html",
        {"request": request, "admin": admin, "admins": admins, "ui": ui},
    )


@app.get("/admin/site-copy")
def admin_site_copy(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)
    ui = get_ui_copy(db)
    return templates.TemplateResponse(
        "admin/site_copy.html",
        {"request": request, "admin": admin, "ui": ui},
    )


@app.post("/admin/site-copy")
async def admin_site_copy_update(request: Request, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin:
        return RedirectResponse("/admin/login", status_code=303)
    form = await request.form()
    payload = {key: str(value) for key, value in form.items()}
    save_ui_copy(db, payload)
    return RedirectResponse("/admin/site-copy?updated=1", status_code=303)


@app.post("/admin/admins/create")
def admin_create_admin(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
):
    admin = _require_admin(request, db)
    if not admin or not admin.is_super:
        return RedirectResponse("/admin", status_code=303)

    if db.query(Admin).filter(Admin.username == username).first():
        return RedirectResponse("/admin/admins?error=exists", status_code=303)

    new_admin = Admin(username=username, hashed_password=hash_password(password), is_super=False)
    db.add(new_admin)
    db.commit()
    return RedirectResponse("/admin/admins?created=1", status_code=303)


@app.post("/admin/admins/{admin_id}/update")
def admin_update_admin(
    request: Request,
    admin_id: int,
    db: Session = Depends(get_db),
    password: str = Form(...),
):
    admin = _require_admin(request, db)
    if not admin or not admin.is_super:
        return RedirectResponse("/admin", status_code=303)

    target = db.query(Admin).filter(Admin.id == admin_id).first()
    if target:
        target.hashed_password = hash_password(password)
        db.add(target)
        db.commit()

    return RedirectResponse("/admin/admins?updated=1", status_code=303)


@app.post("/admin/admins/{admin_id}/delete")
def admin_delete_admin(request: Request, admin_id: int, db: Session = Depends(get_db)):
    admin = _require_admin(request, db)
    if not admin or not admin.is_super:
        return RedirectResponse("/admin", status_code=303)

    target = db.query(Admin).filter(Admin.id == admin_id).first()
    if target and not target.is_super:
        db.delete(target)
        db.commit()

    return RedirectResponse("/admin/admins?deleted=1", status_code=303)
