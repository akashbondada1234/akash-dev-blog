import os, re
import httpx
from pathlib import Path
from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session, joinedload
from database import Base, engine, get_db, SessionLocal
from models import User, Category, Post
from auth import admin_user, current_user, create_token, hash_password, verify_password

app = FastAPI(title="Lumina Blog API", version="1.0.0")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", FRONTEND_URL], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
UPLOADS = Path(__file__).parent / "uploads"; UPLOADS.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")

class Register(BaseModel): name: str = Field(min_length=2, max_length=120); email: EmailStr; password: str = Field(min_length=8)
class Login(BaseModel): email: EmailStr; password: str
class CategoryIn(BaseModel): name: str = Field(min_length=2, max_length=80)
class PostIn(BaseModel): title: str = Field(min_length=3, max_length=220); excerpt: str = Field(min_length=10, max_length=500); content: str = Field(min_length=20); category_id: int; status: str = "draft"; cover_image: str | None = None
class AIAssistIn(BaseModel): task: str = Field(min_length=2, max_length=40); title: str = ""; excerpt: str = ""; content: str = ""; topic: str = ""; tone: str = "professional"
class AIAskIn(BaseModel): question: str = Field(min_length=2, max_length=500); content: str = Field(min_length=20, max_length=30000)
class AIChatIn(BaseModel): message: str = Field(min_length=1, max_length=1000); history: list[dict] = []

def slugify(value): return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
def user_json(u): return {"id":u.id,"name":u.name,"email":u.email}
def post_json(p): return {"id":p.id,"title":p.title,"slug":p.slug,"excerpt":p.excerpt,"content":p.content,"cover_image":p.cover_image,"status":p.status,"category":{"id":p.category.id,"name":p.category.name},"author":{"id":p.author.id,"name":p.author.name},"created_at":p.created_at.isoformat(),"updated_at":p.updated_at.isoformat()}

async def ai_completion(system: str, prompt: str):
    key = os.getenv("OPENAI_API_KEY")
    if not key: raise HTTPException(503, "AI is not configured. Add OPENAI_API_KEY to the backend environment.")
    url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json={"model": model, "temperature": 0.7, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]})
    if response.status_code >= 400: raise HTTPException(502, "The AI provider returned an error")
    return response.json()["choices"][0]["message"]["content"]

@app.on_event("startup")
def seed():
    Base.metadata.create_all(bind=engine); db = SessionLocal()
    admin_email = os.getenv("ADMIN_EMAIL", "admin@akash.dev")
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin_password = os.getenv("ADMIN_PASSWORD", "password123" if os.getenv("ENVIRONMENT", "development").lower() != "production" else "")
        if not admin_password: raise RuntimeError("Set ADMIN_PASSWORD before running in production")
        admin = User(name="Akash Bondada", email=admin_email, password_hash=hash_password(admin_password)); db.add(admin); db.flush()
    names = ["Java", "Spring Boot", "Python", "SQL", "Linux", "REST APIs", "Git", "FastAPI", "Apigee", "Application Support"]
    categories = {c.name: c for c in db.query(Category).all()}
    for name in names:
        if name not in categories:
            categories[name] = Category(name=name); db.add(categories[name]); db.flush()
    samples = [
        ("Apigee API Management Patterns", "Notes on API proxies, OAuth 2.0, JWT validation, quota, spike arrest, fault handling, and API lifecycle thinking.", "Apigee", "My mentored Apigee/API Management exposure introduced me to API proxy development, REST API design, OAuth 2.0, JWT validation, API key verification, quota, spike arrest, request and response handling, fault policies, Postman, and Swagger/OpenAPI.\n\nThe key lesson is that an API gateway is more than a route. It is a controlled boundary where security, traffic management, observability, documentation, and consistent error handling come together.", "published"),
        ("Building a Job Portal with Python, PDBC, and FastAPI", "A staged Job Application System using MySQL, PDBC, FastAPI, mysql.connector, and a Python virtual environment.", "Python", "The Job Portal / Job Application System is intentionally built step by step instead of copied from a ready-made project.\n\nThe plan starts with requirements and a MySQL design for jobs, candidates, and applications. SQL queries are tested in MySQL Workbench before Python is introduced. The project uses PDBC principles, a Python venv, mysql.connector, database.py for the connection, functions.py for operations, and a menu-driven main.py. FastAPI can expose the same operations through clean REST endpoints as the project grows.\n\nThe workflow includes job creation and search, candidate registration, applications, status updates, sorting, parameterized SQL, commits, fetchone/fetchall, input validation, try/except handling, and clean cursor and connection closing. The final stages focus on testing, README documentation, resume bullets, and interview preparation.", "published"),
        ("Building a Student Management System with Spring Boot", "A practical case study of the Java full-stack project, from CRUD workflows to validation and REST APIs.", "Spring Boot", "The Student Management System was designed around a simple goal: make student records, course enrolments, and academic results easy to manage.\n\nThe application uses Spring Boot, Spring MVC, JPA, Hibernate, MySQL, and Thymeleaf. The most valuable lessons were keeping validation close to the boundary, separating controller and service responsibilities, and designing APIs that are easy to test.\n\nThis project gave me practical experience connecting a database-backed domain model to a usable interface.", "published"),
        ("From REST API Design to Apigee API Management", "What I learned while exploring proxies, policies, OAuth 2.0, JWT validation, and API traffic controls.", "Apigee", "My mentored Apigee/API Management training introduced me to the lifecycle around a production API. An API proxy is not only a route: it is also a place for authentication, quota, spike arrest, request and response handling, fault handling, and documentation.\n\nI practiced with Apigee Edge/X, Swagger/OpenAPI, Postman, OAuth 2.0, API keys, and JWT validation. These concepts connected my Java and Python development work with the operational side of delivering APIs safely.", "published"),
        ("Application Log Monitoring with Bash and Linux", "A support practice project for detecting errors, validating processes, checking disk space, and generating alerts.", "Application Support", "Production and application support starts with disciplined observation. My log monitor practice workflow uses Bash and Unix/Linux commands to scan logs for error patterns, check disk usage, validate processes, and produce an actionable alert.\n\nThe exercise reinforced why runbooks, clear ticket notes, monitoring, and repeatable checks matter. It also gave me a practical way to connect shell scripting with application troubleshooting.", "published"),
        ("SQL Troubleshooting Lessons from Full Stack Projects", "How database design, query thinking, and troubleshooting support reliable applications.", "SQL", "SQL is part of every layer of my development work. In the Student Management System and Instagram relational database project, I practiced normalized design, relationships, CRUD queries, and data validation.\n\nMy support training extended that practice into Oracle 19C, PL/SQL, SQL troubleshooting, and log-based investigation. The recurring lesson is simple: understand the data model first, then measure the query and the surrounding application behaviour.", "published"),
        ("Combining Gesture Recognition and Voice Commands", "A project reflection on building touchless human-computer interaction with Python and computer vision.", "Python", "The Hand Gesture Recognition project combines Python, TensorFlow, OpenCV, MediaPipe, and SpeechRecognition. The goal was to connect visual gesture detection with voice commands for a more natural touchless interaction.\n\nThe project helped me practise working with real-time input, model output, and the practical challenge of turning an experiment into a usable interaction. It also strengthened my interest in Python alongside my Java backend work.", "published"),
    ]
    for title, excerpt, category, content, status in samples:
        if not db.query(Post).filter(Post.title == title).first():
            db.add(Post(title=title, slug=slugify(title), excerpt=excerpt, content=content, status=status, category_id=categories[category].id, author_id=admin.id))
    legacy = db.query(Post).filter(Post.title == "From REST API Design to Apigee API Management").first()
    if legacy:
        legacy.title = "Building APIs with FastAPI and PDBC"
        legacy.slug = "building-apis-with-fastapi-and-pdbc"
        legacy.excerpt = "A practical note on FastAPI, PDBC principles, MySQL connectivity, validation, and clean Python project structure."
        legacy.content = "FastAPI gives a Python project a clear path from database functions to documented REST endpoints. In this note, I connect the Job Portal learning plan with PDBC principles, mysql.connector, a Python virtual environment, validation, and reusable functions.\n\nThe goal is not to copy a ready-made project. It is to understand requirements, design jobs, candidates, and applications tables, test SQL in MySQL Workbench, then build database.py, functions.py, and a menu-driven main.py before exposing useful operations through FastAPI."
        legacy.category_id = categories["Python"].id
    db.commit(); db.close()

@app.post("/register")
def register(data:Register, response:Response, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(400,"Email already registered")
    user=User(name=data.name,email=data.email,password_hash=hash_password(data.password)); db.add(user); db.commit(); db.refresh(user)
    token = create_token(user.id); response.set_cookie("access_token", token, httponly=True, secure=os.getenv("ENVIRONMENT", "development").lower() == "production", samesite="lax", max_age=86400)
    return {"user":user_json(user)}
@app.post("/login")
def login(data:Login, response:Response, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    token = create_token(user.id); response.set_cookie("access_token", token, httponly=True, secure=os.getenv("ENVIRONMENT", "development").lower() == "production", samesite="lax", max_age=86400)
    return {"user":user_json(user)}
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", httponly=True, secure=os.getenv("ENVIRONMENT", "development").lower() == "production", samesite="lax")
    return {"ok": True}
@app.get("/me")
def me(user=Depends(current_user)): return user_json(user)
@app.get("/categories")
def categories(db:Session=Depends(get_db)): return [{"id":c.id,"name":c.name,"count":len(c.posts)} for c in db.query(Category).order_by(Category.name).all()]
@app.post("/categories")
def add_category(data:CategoryIn, db:Session=Depends(get_db), user=Depends(admin_user)):
    if db.query(Category).filter(Category.name.ilike(data.name)).first(): raise HTTPException(400,"Category already exists")
    c=Category(name=data.name.strip()); db.add(c); db.commit(); db.refresh(c); return {"id":c.id,"name":c.name,"count":0}
@app.get("/posts")
def posts(page:int=1, limit:int=9, search:str="", category:int|None=None, db:Session=Depends(get_db)):
    q=db.query(Post).options(joinedload(Post.category),joinedload(Post.author)).filter(Post.status=="published")
    if search: q=q.filter(Post.title.ilike(f"%{search}%"))
    if category: q=q.filter(Post.category_id==category)
    total=q.count(); rows=q.order_by(Post.created_at.desc()).offset((page-1)*limit).limit(limit).all()
    return {"items":[post_json(p) for p in rows],"total":total,"page":page,"pages":max(1,(total+limit-1)//limit)}
@app.get("/posts/{slug}")
def post(slug:str, db:Session=Depends(get_db)):
    p=db.query(Post).options(joinedload(Post.category),joinedload(Post.author)).filter(Post.slug==slug).first()
    if not p or p.status != "published": raise HTTPException(404,"Post not found")
    return post_json(p)
@app.get("/admin/posts")
def admin_posts(db:Session=Depends(get_db), user=Depends(admin_user)):
    return [post_json(p) for p in db.query(Post).options(joinedload(Post.category),joinedload(Post.author)).order_by(Post.updated_at.desc()).all()]
@app.post("/posts")
def create_post(data:PostIn, db:Session=Depends(get_db), user=Depends(admin_user)):
    slug=slugify(data.title); base=slug; i=2
    while db.query(Post).filter(Post.slug==slug).first(): slug=f"{base}-{i}"; i+=1
    p=Post(**data.model_dump(),slug=slug,author_id=user.id); db.add(p); db.commit(); db.refresh(p); return post_json(p)
@app.put("/posts/{id}")
def update_post(id:int,data:PostIn,db:Session=Depends(get_db),user=Depends(admin_user)):
    p=db.get(Post,id)
    if not p: raise HTTPException(404,"Post not found")
    for k,v in data.model_dump().items(): setattr(p,k,v)
    db.commit(); db.refresh(p); return post_json(p)
@app.delete("/posts/{id}")
def delete_post(id:int,db:Session=Depends(get_db),user=Depends(admin_user)):
    p=db.get(Post,id)
    if not p: raise HTTPException(404,"Post not found")
    db.delete(p); db.commit(); return {"ok":True}
@app.post("/upload")
async def upload(file:UploadFile=File(...),user=Depends(admin_user)):
    ext=Path(file.filename or "image.jpg").suffix.lower()
    if ext not in {".jpg",".jpeg",".png",".webp"}: raise HTTPException(400,"Unsupported image type")
    data = await file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024: raise HTTPException(413, "Image must be 5MB or smaller")
    name=f"{__import__('uuid').uuid4().hex}{ext}"; (UPLOADS/name).write_bytes(data); return {"url":f"/uploads/{name}"}

@app.post("/ai/assist")
async def ai_assist(data: AIAssistIn, user=Depends(admin_user)):
    tasks = {"draft": "Create a useful, accurate technical blog article in Markdown.", "improve": "Improve the supplied technical article for clarity, structure, and practical value while preserving the author voice.", "ideas": "Suggest five strong technical blog titles and a one-sentence angle for each.", "excerpt": "Write three concise SEO-friendly excerpts for the supplied article."}
    task = tasks.get(data.task, tasks["draft"])
    result = await ai_completion("You are Akash Bondada's careful technical writing assistant. Write for software developers. Never invent personal experience, benchmarks, or citations. Use Markdown when producing an article.", f"{task}\nTopic: {data.topic}\nTitle: {data.title}\nExcerpt: {data.excerpt}\nExisting content: {data.content}\nTone: {data.tone}")
    return {"result": result, "task": data.task}

@app.post("/ai/ask")
async def ai_ask(data: AIAskIn):
    result = await ai_completion("Answer only from the supplied article. If the answer is not present, say so clearly. Be concise and include code only when useful.", f"Article:\n{data.content}\n\nReader question: {data.question}")
    return {"answer": result}

@app.post("/ai/chat")
async def ai_chat(data: AIChatIn):
    context = """You are Akash Assistant, the friendly website assistant for Akash Bondada. Akash is an MCA graduate and Java/Python Full Stack Developer focused on Java, Spring Boot, REST APIs, SQL, Python, FastAPI, Git, Linux, and backend development. His projects include a Student Management System, Hand Gesture Recognition, and Instagram Database Design. Answer questions about Akash, his portfolio, projects, skills, and technical blog topics. Be concise, helpful, and honest. If asked for contact details, direct users to the Contact section or akashbondada.dev@gmail.com. Do not claim facts that are not in this context."""
    result = await ai_completion(context, f"Conversation history: {data.history[-8:]}\n\nVisitor message: {data.message}")
    return {"answer": result}
