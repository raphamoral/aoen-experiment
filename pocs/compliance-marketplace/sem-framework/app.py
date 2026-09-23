import sqlite3
import hashlib
import os
from flask import Flask, request, jsonify, session, g

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
DB = "marketplace.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('client', 'freelancer')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS freelancer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
            bio TEXT,
            hourly_rate REAL,
            specializations TEXT,
            certifications TEXT,
            years_experience INTEGER,
            linkedin TEXT,
            available INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            area TEXT NOT NULL,
            budget REAL,
            deadline TEXT,
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'closed')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL REFERENCES jobs(id),
            freelancer_id INTEGER NOT NULL REFERENCES users(id),
            cover_letter TEXT,
            price REAL NOT NULL,
            delivery_days INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, freelancer_id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_id INTEGER NOT NULL REFERENCES users(id),
            reviewed_id INTEGER NOT NULL REFERENCES users(id),
            job_id INTEGER NOT NULL REFERENCES jobs(id),
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(reviewer_id, job_id)
        );
    """)
    db.commit()
    db.close()

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

def require_auth():
    u = current_user()
    if not u:
        return jsonify({"error": "Login necessário"}), 401
    return u

def require_role(role):
    u = require_auth()
    if isinstance(u, tuple):
        return u
    if u["role"] != role:
        return jsonify({"error": f"Apenas {role}s podem fazer isso"}), 403
    return u

# Auth
@app.post("/register")
def register():
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "")

    if not all([name, email, password, role]):
        return jsonify({"error": "name, email, password e role são obrigatórios"}), 400
    if role not in ("client", "freelancer"):
        return jsonify({"error": "role deve ser client ou freelancer"}), 400
    if len(password) < 6:
        return jsonify({"error": "Senha deve ter pelo menos 6 caracteres"}), 400

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, hash_password(password), role)
        )
        db.commit()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        session["user_id"] = user["id"]
        return jsonify({"message": "Conta criada", "user_id": user["id"], "role": role}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email já cadastrado"}), 409

@app.post("/login")
def login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    user = get_db().execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password))
    ).fetchone()
    if not user:
        return jsonify({"error": "Credenciais inválidas"}), 401
    session["user_id"] = user["id"]
    return jsonify({"message": "Login realizado", "user_id": user["id"], "role": user["role"]})

@app.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logout realizado"})

# Perfil de freelancer
@app.post("/profile")
def create_or_update_profile():
    u = require_role("freelancer")
    if isinstance(u, tuple):
        return u
    data = request.json or {}
    db = get_db()
    existing = db.execute("SELECT id FROM freelancer_profiles WHERE user_id = ?", (u["id"],)).fetchone()
    bio = data.get("bio", "")
    hourly_rate = data.get("hourly_rate")
    specializations = data.get("specializations", "")  # ex: "LGPD,GDPR,SOX"
    certifications = data.get("certifications", "")
    years_experience = data.get("years_experience", 0)
    linkedin = data.get("linkedin", "")
    available = 1 if data.get("available", True) else 0

    if existing:
        db.execute("""
            UPDATE freelancer_profiles SET bio=?, hourly_rate=?, specializations=?,
            certifications=?, years_experience=?, linkedin=?, available=?
            WHERE user_id=?
        """, (bio, hourly_rate, specializations, certifications, years_experience, linkedin, available, u["id"]))
    else:
        db.execute("""
            INSERT INTO freelancer_profiles (user_id, bio, hourly_rate, specializations, certifications, years_experience, linkedin, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (u["id"], bio, hourly_rate, specializations, certifications, years_experience, linkedin, available))
    db.commit()
    return jsonify({"message": "Perfil salvo"})

@app.get("/freelancers")
def list_freelancers():
    specialization = request.args.get("specialization", "")
    max_rate = request.args.get("max_rate", type=float)
    min_experience = request.args.get("min_experience", type=int)

    query = """
        SELECT u.id, u.name, u.email, p.bio, p.hourly_rate, p.specializations,
               p.certifications, p.years_experience, p.linkedin, p.available,
               COALESCE(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM users u
        JOIN freelancer_profiles p ON u.id = p.user_id
        LEFT JOIN reviews r ON u.id = r.reviewed_id
        WHERE u.role = 'freelancer' AND p.available = 1
    """
    params = []
    if specialization:
        query += " AND p.specializations LIKE ?"
        params.append(f"%{specialization}%")
    if max_rate is not None:
        query += " AND p.hourly_rate <= ?"
        params.append(max_rate)
    if min_experience is not None:
        query += " AND p.years_experience >= ?"
        params.append(min_experience)
    query += " GROUP BY u.id ORDER BY avg_rating DESC"

    rows = get_db().execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/freelancers/<int:uid>")
def get_freelancer(uid):
    db = get_db()
    profile = db.execute("""
        SELECT u.id, u.name, u.email, p.bio, p.hourly_rate, p.specializations,
               p.certifications, p.years_experience, p.linkedin, p.available,
               COALESCE(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM users u
        JOIN freelancer_profiles p ON u.id = p.user_id
        LEFT JOIN reviews r ON u.id = r.reviewed_id
        WHERE u.id = ? AND u.role = 'freelancer'
        GROUP BY u.id
    """, (uid,)).fetchone()
    if not profile:
        return jsonify({"error": "Freelancer não encontrado"}), 404
    reviews = db.execute("""
        SELECT r.rating, r.comment, r.created_at, u.name as reviewer_name
        FROM reviews r JOIN users u ON r.reviewer_id = u.id
        WHERE r.reviewed_id = ? ORDER BY r.created_at DESC
    """, (uid,)).fetchall()
    result = dict(profile)
    result["reviews"] = [dict(r) for r in reviews]
    return jsonify(result)

# Jobs
@app.post("/jobs")
def create_job():
    u = require_role("client")
    if isinstance(u, tuple):
        return u
    data = request.json or {}
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    area = data.get("area", "").strip()
    budget = data.get("budget")
    deadline = data.get("deadline", "")

    if not all([title, description, area]):
        return jsonify({"error": "title, description e area são obrigatórios"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO jobs (client_id, title, description, area, budget, deadline) VALUES (?, ?, ?, ?, ?, ?)",
        (u["id"], title, description, area, budget, deadline)
    )
    db.commit()
    return jsonify({"message": "Vaga criada", "job_id": cur.lastrowid}), 201

@app.get("/jobs")
def list_jobs():
    area = request.args.get("area", "")
    status = request.args.get("status", "open")
    query = """
        SELECT j.*, u.name as client_name, COUNT(p.id) as proposal_count
        FROM jobs j JOIN users u ON j.client_id = u.id
        LEFT JOIN proposals p ON j.id = p.job_id
        WHERE 1=1
    """
    params = []
    if area:
        query += " AND j.area LIKE ?"
        params.append(f"%{area}%")
    if status:
        query += " AND j.status = ?"
        params.append(status)
    query += " GROUP BY j.id ORDER BY j.created_at DESC"
    rows = get_db().execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/jobs/<int:job_id>")
def get_job(job_id):
    db = get_db()
    job = db.execute("""
        SELECT j.*, u.name as client_name
        FROM jobs j JOIN users u ON j.client_id = u.id
        WHERE j.id = ?
    """, (job_id,)).fetchone()
    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404
    proposals = []
    u = current_user()
    if u and (u["id"] == job["client_id"] or u["role"] == "freelancer"):
        proposals = db.execute("""
            SELECT p.*, u.name as freelancer_name
            FROM proposals p JOIN users u ON p.freelancer_id = u.id
            WHERE p.job_id = ?
        """, (job_id,)).fetchall()
        proposals = [dict(p) for p in proposals]
    result = dict(job)
    result["proposals"] = proposals
    return jsonify(result)

@app.get("/my-jobs")
def my_jobs():
    u = require_auth()
    if isinstance(u, tuple):
        return u
    db = get_db()
    if u["role"] == "client":
        rows = db.execute("""
            SELECT j.*, COUNT(p.id) as proposal_count
            FROM jobs j LEFT JOIN proposals p ON j.id = p.job_id
            WHERE j.client_id = ?
            GROUP BY j.id ORDER BY j.created_at DESC
        """, (u["id"],)).fetchall()
    else:
        rows = db.execute("""
            SELECT j.*, p.status as proposal_status, p.price as my_price, u.name as client_name
            FROM proposals p
            JOIN jobs j ON p.job_id = j.id
            JOIN users u ON j.client_id = u.id
            WHERE p.freelancer_id = ?
            ORDER BY p.created_at DESC
        """, (u["id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

# Propostas
@app.post("/jobs/<int:job_id>/proposals")
def submit_proposal(job_id):
    u = require_role("freelancer")
    if isinstance(u, tuple):
        return u
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ? AND status = 'open'", (job_id,)).fetchone()
    if not job:
        return jsonify({"error": "Vaga não encontrada ou encerrada"}), 404

    data = request.json or {}
    price = data.get("price")
    delivery_days = data.get("delivery_days")
    cover_letter = data.get("cover_letter", "")

    if not price or not delivery_days:
        return jsonify({"error": "price e delivery_days são obrigatórios"}), 400

    try:
        cur = db.execute(
            "INSERT INTO proposals (job_id, freelancer_id, cover_letter, price, delivery_days) VALUES (?, ?, ?, ?, ?)",
            (job_id, u["id"], cover_letter, price, delivery_days)
        )
        db.commit()
        return jsonify({"message": "Proposta enviada", "proposal_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Você já enviou uma proposta para esta vaga"}), 409

@app.patch("/proposals/<int:proposal_id>")
def update_proposal_status(proposal_id):
    u = require_role("client")
    if isinstance(u, tuple):
        return u
    data = request.json or {}
    status = data.get("status")
    if status not in ("accepted", "rejected"):
        return jsonify({"error": "status deve ser accepted ou rejected"}), 400

    db = get_db()
    proposal = db.execute("""
        SELECT p.*, j.client_id FROM proposals p
        JOIN jobs j ON p.job_id = j.id
        WHERE p.id = ?
    """, (proposal_id,)).fetchone()
    if not proposal:
        return jsonify({"error": "Proposta não encontrada"}), 404
    if proposal["client_id"] != u["id"]:
        return jsonify({"error": "Sem permissão"}), 403

    db.execute("UPDATE proposals SET status = ? WHERE id = ?", (status, proposal_id))
    if status == "accepted":
        db.execute("UPDATE jobs SET status = 'in_progress' WHERE id = ?", (proposal["job_id"],))
        db.execute("UPDATE proposals SET status = 'rejected' WHERE job_id = ? AND id != ?",
                   (proposal["job_id"], proposal_id))
    db.commit()
    return jsonify({"message": f"Proposta {status}"})

# Reviews
@app.post("/reviews")
def create_review():
    u = require_auth()
    if isinstance(u, tuple):
        return u
    data = request.json or {}
    reviewed_id = data.get("reviewed_id")
    job_id = data.get("job_id")
    rating = data.get("rating")
    comment = data.get("comment", "")

    if not all([reviewed_id, job_id, rating]):
        return jsonify({"error": "reviewed_id, job_id e rating são obrigatórios"}), 400
    if not isinstance(rating, int) or not 1 <= rating <= 5:
        return jsonify({"error": "rating deve ser inteiro entre 1 e 5"}), 400

    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404

    # Só pode avaliar se participou da vaga
    if u["role"] == "client" and job["client_id"] != u["id"]:
        return jsonify({"error": "Sem permissão"}), 403
    if u["role"] == "freelancer":
        accepted = db.execute("""
            SELECT id FROM proposals WHERE job_id = ? AND freelancer_id = ? AND status = 'accepted'
        """, (job_id, u["id"])).fetchone()
        if not accepted:
            return jsonify({"error": "Você não foi contratado para esta vaga"}), 403

    try:
        db.execute(
            "INSERT INTO reviews (reviewer_id, reviewed_id, job_id, rating, comment) VALUES (?, ?, ?, ?, ?)",
            (u["id"], reviewed_id, job_id, rating, comment)
        )
        db.commit()
        return jsonify({"message": "Avaliação enviada"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Você já avaliou este usuário nesta vaga"}), 409

# Fechar vaga
@app.patch("/jobs/<int:job_id>/close")
def close_job(job_id):
    u = require_role("client")
    if isinstance(u, tuple):
        return u
    db = get_db()
    job = db.execute("SELECT * FROM jobs WHERE id = ? AND client_id = ?", (job_id, u["id"])).fetchone()
    if not job:
        return jsonify({"error": "Vaga não encontrada"}), 404
    db.execute("UPDATE jobs SET status = 'closed' WHERE id = ?", (job_id,))
    db.commit()
    return jsonify({"message": "Vaga encerrada"})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)