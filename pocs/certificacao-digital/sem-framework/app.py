import io
import os
import sqlite3
import hashlib
import secrets
import tempfile
from functools import wraps
from datetime import datetime

from flask import (Flask, request, redirect, url_for, session,
                   send_file, flash, get_flashed_messages, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import qrcode


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'certifica-dev-mude-em-producao')
DB = 'certifica.db'


# ─── banco de dados ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created  TEXT    DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS courses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            instructor  TEXT    NOT NULL,
            hours       INTEGER NOT NULL,
            created     TEXT    DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            course_id    INTEGER NOT NULL,
            enrolled_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            UNIQUE(user_id, course_id)
        );
        CREATE TABLE IF NOT EXISTS certificates (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enroll_id INTEGER NOT NULL,
            code      TEXT    UNIQUE NOT NULL,
            issued_at TEXT    DEFAULT CURRENT_TIMESTAMP
        );
    """)
    if not conn.execute("SELECT id FROM users WHERE email='admin@certifica.com'").fetchone():
        conn.execute(
            "INSERT INTO users (name, email, password, is_admin) VALUES (?,?,?,1)",
            ('Administrador', 'admin@certifica.com', generate_password_hash('admin123'))
        )
        conn.commit()
    conn.close()


init_db()


# ─── utilitários ─────────────────────────────────────────────────────────────

def get_user():
    if 'uid' not in session:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['uid'],)).fetchone()
    conn.close()
    return user


def login_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        if not get_user():
            return redirect(url_for('login_page'))
        return f(*a, **k)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        u = get_user()
        if not u or not u['is_admin']:
            abort(403)
        return f(*a, **k)
    return wrapper


def novo_codigo(user_id, course_id):
    raw = f"{user_id}:{course_id}:{secrets.token_hex(16)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20].upper()


# ─── layout html ─────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, -apple-system, sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.5; }
header { background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
header h1 { color: #fff; font-size: 1.25rem; letter-spacing: 1px; font-weight: 700; }
nav a { color: #7ecff0; text-decoration: none; margin-left: 1.2rem; font-size: .88rem; }
nav a:hover { color: #fff; }
main { max-width: 980px; margin: 2rem auto; padding: 0 1rem; }
.card { background: #fff; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
h2 { color: #1a1a2e; margin-bottom: 1rem; font-size: 1.25rem; }
h3 { color: #1a1a2e; margin-bottom: .6rem; font-size: 1.05rem; }
label { display: block; font-size: .87rem; font-weight: 600; color: #555; margin-bottom: .25rem; }
input, textarea { width: 100%; padding: .55rem .8rem; border: 1px solid #ddd; border-radius: 5px; font-size: .93rem; margin-bottom: .9rem; font-family: inherit; }
input:focus, textarea:focus { outline: none; border-color: #1a1a2e; box-shadow: 0 0 0 3px rgba(26,26,46,.08); }
textarea { height: 90px; resize: vertical; }
.btn { display: inline-block; padding: .55rem 1.3rem; border-radius: 5px; border: none; cursor: pointer; font-size: .88rem; font-weight: 600; text-decoration: none; }
.btn-primary { background: #1a1a2e; color: #fff; }
.btn-primary:hover { background: #16213e; }
.btn-success { background: #2e7d32; color: #fff; }
.btn-success:hover { background: #1b5e20; }
.btn-gray { background: #555; color: #fff; }
.btn-gray:hover { background: #333; }
.btn-sm { padding: .3rem .75rem; font-size: .8rem; }
.alert { padding: .75rem 1rem; border-radius: 5px; margin-bottom: 1rem; font-size: .88rem; }
.alert-ok  { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
.alert-err { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
table { width: 100%; border-collapse: collapse; font-size: .9rem; }
th { background: #f5f5f5; padding: .55rem .9rem; text-align: left; font-size: .77rem; text-transform: uppercase; color: #777; letter-spacing: .4px; }
td { padding: .55rem .9rem; border-bottom: 1px solid #eee; vertical-align: middle; }
.badge { padding: .18rem .6rem; border-radius: 12px; font-size: .76rem; font-weight: 700; }
.badge-green { background: #e8f5e9; color: #2e7d32; }
.badge-blue  { background: #e3f2fd; color: #1565c0; }
.muted { color: #999; font-size: .87rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.2rem; }
.course-card { background: #fff; border-radius: 8px; padding: 1.4rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.course-card h3 { margin-bottom: .4rem; font-size: 1rem; }
.course-card .desc { color: #555; font-size: .86rem; margin-bottom: .8rem; min-height: 2.4rem; }
.course-card .meta { font-size: .8rem; color: #888; margin-bottom: .9rem; }
footer { text-align: center; padding: 2rem; color: #bbb; font-size: .78rem; margin-top: 1rem; }
code { background: #f5f5f5; padding: .1rem .4rem; border-radius: 3px; font-size: .86rem; font-family: monospace; }
"""


def page(title, body):
    u = get_user()
    year = datetime.now().year

    if u:
        admin_lnk = f'<a href="{url_for("admin_page")}">Admin</a>' if u['is_admin'] else ''
        nav = (f'<a href="{url_for("courses_page")}">Cursos</a>'
               f'<a href="{url_for("my_certs")}">Meus Certificados</a>'
               f'{admin_lnk}'
               f'<a href="{url_for("logout")}">Sair ({u["name"]})</a>')
    else:
        nav = (f'<a href="{url_for("login_page")}">Entrar</a>'
               f'<a href="{url_for("register_page")}">Cadastrar</a>')

    cat_to_cls = {'success': 'alert-ok'}
    alerts = ''.join(
        f'<div class="alert {cat_to_cls.get(cat, "alert-err")}">{msg}</div>'
        for cat, msg in get_flashed_messages(with_categories=True)
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} – Certifica</title>
  <style>{CSS}</style>
</head>
<body>
  <header>
    <h1>Certifica</h1>
    <nav>{nav}</nav>
  </header>
  <main>
    {alerts}
    {body}
  </main>
  <footer>Certifica &copy; {year} – Plataforma de Certificacao Digital de Cursos Livres</footer>
</body>
</html>"""


# ─── geração de certificado PDF ───────────────────────────────────────────────

def gerar_pdf(nome_aluno, titulo_curso, instrutor, horas, codigo, emitido_em, url_verificacao):
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(url_verificacao)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=(26, 26, 46), back_color=(255, 255, 255))

    qr_tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    qr_tmp.close()
    qr_img.save(qr_tmp.name)

    try:
        try:
            dt = datetime.strptime(emitido_em, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            dt = datetime.strptime(emitido_em[:10], '%Y-%m-%d')
        data_fmt = dt.strftime('%d/%m/%Y')

        W, H = 297, 210

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(False)
        pdf.add_page()

        # fundo creme
        pdf.set_fill_color(252, 249, 240)
        pdf.rect(0, 0, W, H, 'F')

        # borda externa
        pdf.set_draw_color(26, 26, 46)
        pdf.set_line_width(1.5)
        pdf.rect(10, 10, W - 20, H - 20)

        # borda interna dourada
        pdf.set_draw_color(180, 140, 60)
        pdf.set_line_width(0.5)
        pdf.rect(13, 13, W - 26, H - 26)

        # cabeçalho escuro
        pdf.set_fill_color(26, 26, 46)
        pdf.rect(10, 10, W - 20, 18, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_xy(10, 14)
        pdf.cell(W - 20, 10, 'CERTIFICA  |  PLATAFORMA DE CERTIFICACAO DIGITAL DE CURSOS LIVRES', align='C')

        # título principal
        pdf.set_text_color(26, 26, 46)
        pdf.set_font('Helvetica', 'B', 25)
        pdf.set_xy(20, 38)
        pdf.cell(W - 40, 14, 'CERTIFICADO DE CONCLUSAO', align='C')

        # linha decorativa dourada
        pdf.set_draw_color(180, 140, 60)
        pdf.set_line_width(0.7)
        pdf.line(65, 55, W - 65, 55)

        # "Certificamos que"
        pdf.set_font('Helvetica', 'I', 12)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(20, 61)
        pdf.cell(W - 40, 8, 'Certificamos que', align='C')

        # nome do aluno
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(26, 26, 46)
        pdf.set_xy(20, 71)
        pdf.cell(W - 40, 12, nome_aluno.upper(), align='C')

        # texto do curso
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(20, 85)
        pdf.cell(W - 40, 7, 'concluiu com exito o curso de livre formacao', align='C')

        # título do curso
        pdf.set_font('Helvetica', 'BI', 15)
        pdf.set_text_color(26, 26, 46)
        pdf.set_xy(20, 94)
        pdf.cell(W - 40, 10, titulo_curso, align='C')

        # instrutor e carga
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(110, 110, 110)
        pdf.set_xy(20, 107)
        pdf.cell(W - 40, 7, f'Instrutor: {instrutor}   |   Carga Horaria: {horas} horas', align='C')

        # linha dourada inferior
        pdf.set_draw_color(180, 140, 60)
        pdf.set_line_width(0.5)
        pdf.line(65, 117, W - 65, 117)

        # data e código
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.set_xy(20, 121)
        pdf.cell(W - 40, 5, f'Emitido em: {data_fmt}   |   Codigo de verificacao: {codigo}', align='C')
        pdf.set_xy(20, 127)
        pdf.cell(W - 40, 5, f'Verifique em: {url_verificacao}', align='C')

        # QR code
        pdf.image(qr_tmp.name, x=W - 53, y=H - 53, w=38, h=38)

        # linha de assinatura
        pdf.set_draw_color(26, 26, 46)
        pdf.set_line_width(0.4)
        pdf.line(55, H - 26, 135, H - 26)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(26, 26, 46)
        pdf.set_xy(55, H - 24)
        pdf.cell(80, 5, 'Direcao – Certifica', align='C')

    finally:
        os.unlink(qr_tmp.name)

    return bytes(pdf.output())


# ─── rotas ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return redirect(url_for('courses_page'))


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        name  = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        pwd   = request.form.get('password', '')
        if not name or not email or len(pwd) < 6:
            flash('Preencha todos os campos (senha minimo 6 caracteres).', 'error')
            return redirect(url_for('register_page'))
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?,?,?)",
                (name, email, generate_password_hash(pwd))
            )
            conn.commit()
            flash('Conta criada com sucesso! Faca o login.', 'success')
            return redirect(url_for('login_page'))
        except sqlite3.IntegrityError:
            flash('Este e-mail ja esta cadastrado.', 'error')
        finally:
            conn.close()

    return page('Cadastro', """
    <div class="card" style="max-width:420px;margin:0 auto">
      <h2>Criar conta</h2>
      <form method="POST" action="/register">
        <label>Nome completo</label>
        <input name="name" required placeholder="Seu nome">
        <label>E-mail</label>
        <input type="email" name="email" required placeholder="seu@email.com">
        <label>Senha</label>
        <input type="password" name="password" required minlength="6" placeholder="Minimo 6 caracteres">
        <button class="btn btn-primary" type="submit" style="width:100%">Cadastrar</button>
      </form>
      <p class="muted" style="margin-top:1rem;text-align:center">
        Ja tem conta? <a href="/login">Entrar</a>
      </p>
    </div>""")


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pwd   = request.form.get('password', '')
        conn  = get_db()
        user  = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], pwd):
            session['uid'] = user['id']
            return redirect(url_for('courses_page'))
        flash('E-mail ou senha incorretos.', 'error')

    return page('Login', """
    <div class="card" style="max-width:420px;margin:0 auto">
      <h2>Entrar</h2>
      <form method="POST" action="/login">
        <label>E-mail</label>
        <input type="email" name="email" required placeholder="seu@email.com">
        <label>Senha</label>
        <input type="password" name="password" required placeholder="Sua senha">
        <button class="btn btn-primary" type="submit" style="width:100%">Entrar</button>
      </form>
      <p class="muted" style="margin-top:1rem;text-align:center">
        Sem conta? <a href="/register">Cadastrar</a>
      </p>
      <p class="muted" style="text-align:center">
        Admin padrao: admin@certifica.com / admin123
      </p>
    </div>""")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


@app.route('/courses')
def courses_page():
    u = get_user()
    conn = get_db()
    courses = conn.execute("SELECT * FROM courses ORDER BY created DESC").fetchall()
    inscricoes = {}
    if u:
        for r in conn.execute(
            "SELECT course_id, completed_at FROM enrollments WHERE user_id=?", (u['id'],)
        ).fetchall():
            inscricoes[r['course_id']] = r['completed_at']
    conn.close()

    cards = ''
    for co in courses:
        status = inscricoes.get(co['id'], -1)
        if status == -1:
            badge = ''
            if u:
                botao = (f'<form method="POST" action="/courses/{co["id"]}/enroll">'
                         '<button class="btn btn-success btn-sm" type="submit">Inscrever-se</button>'
                         '</form>')
            else:
                botao = '<a href="/login" class="btn btn-gray btn-sm">Entre para se inscrever</a>'
        elif status:
            badge = '<span class="badge badge-green">Concluido</span> '
            botao = ''
        else:
            badge = '<span class="badge badge-blue">Inscrito</span> '
            botao = ''

        desc = co['description'] or ''
        cards += f"""
        <div class="course-card">
          <h3>{badge}{co['title']}</h3>
          <p class="desc">{desc}</p>
          <p class="meta">Instrutor: {co['instructor']} &bull; {co['hours']}h</p>
          {botao}
        </div>"""

    if not courses:
        cards = '<p class="muted">Nenhum curso disponivel ainda.</p>'

    return page('Cursos', f'<h2>Cursos Disponiveis</h2><div class="grid">{cards}</div>')


@app.route('/courses/<int:cid>/enroll', methods=['POST'])
@login_required
def enroll(cid):
    u = get_user()
    conn = get_db()
    if not conn.execute("SELECT id FROM courses WHERE id=?", (cid,)).fetchone():
        conn.close()
        abort(404)
    try:
        conn.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?,?)", (u['id'], cid))
        conn.commit()
        flash('Inscricao realizada com sucesso!', 'success')
    except sqlite3.IntegrityError:
        flash('Voce ja esta inscrito neste curso.', 'error')
    finally:
        conn.close()
    return redirect(url_for('courses_page'))


@app.route('/my-certificates')
@login_required
def my_certs():
    u = get_user()
    conn = get_db()
    certs = conn.execute("""
        SELECT ct.code, ct.issued_at, co.title, co.instructor, co.hours
        FROM certificates ct
        JOIN courses co ON co.id = ct.course_id
        WHERE ct.user_id = ?
        ORDER BY ct.issued_at DESC
    """, (u['id'],)).fetchall()
    conn.close()

    linhas = ''
    for c in certs:
        linhas += f"""<tr>
          <td>{c['title']}</td>
          <td>{c['instructor']}</td>
          <td>{c['hours']}h</td>
          <td>{c['issued_at'][:10]}</td>
          <td><code>{c['code']}</code></td>
          <td>
            <a href="/certificates/{c['code']}/download" class="btn btn-primary btn-sm">PDF</a>
            &nbsp;
            <a href="/verify/{c['code']}" class="btn btn-gray btn-sm" target="_blank">Verificar</a>
          </td>
        </tr>"""

    if not linhas:
        linhas = '<tr><td colspan="6" style="text-align:center;padding:2rem;color:#bbb">Nenhum certificado ainda. Conclua um curso para receber seu certificado.</td></tr>'

    return page('Meus Certificados', f"""
    <h2>Meus Certificados</h2>
    <div class="card" style="padding:0;overflow:hidden">
      <table>
        <thead>
          <tr>
            <th>Curso</th><th>Instrutor</th><th>Carga</th>
            <th>Emitido em</th><th>Codigo</th><th>Acoes</th>
          </tr>
        </thead>
        <tbody>{linhas}</tbody>
      </table>
    </div>""")


@app.route('/certificates/<code>/download')
@login_required
def download_cert(code):
    u = get_user()
    conn = get_db()
    row = conn.execute("""
        SELECT ct.code, ct.issued_at, co.title, co.instructor, co.hours
        FROM certificates ct
        JOIN courses co ON co.id = ct.course_id
        WHERE ct.code = ? AND ct.user_id = ?
    """, (code, u['id'])).fetchone()
    conn.close()
    if not row:
        abort(404)
    url_verificacao = request.host_url.rstrip('/') + url_for('verify_cert', code=code)
    pdf_bytes = gerar_pdf(
        u['name'], row['title'], row['instructor'],
        row['hours'], row['code'], row['issued_at'], url_verificacao
    )
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'certificado-{code}.pdf'
    )


@app.route('/verify/<code>')
def verify_cert(code):
    conn = get_db()
    cert = conn.execute("""
        SELECT ct.code, ct.issued_at,
               u.name  AS aluno,
               co.title AS curso, co.instructor AS instrutor, co.hours AS horas
        FROM certificates ct
        JOIN users   u  ON u.id  = ct.user_id
        JOIN courses co ON co.id = ct.course_id
        WHERE ct.code = ?
    """, (code,)).fetchone()
    conn.close()

    if not cert:
        return page('Verificacao', f"""
        <div class="card" style="max-width:500px;margin:0 auto;text-align:center;padding:2.5rem">
          <div style="font-size:3rem;margin-bottom:1rem;color:#c62828">&#10008;</div>
          <h2 style="color:#c62828;margin-bottom:.6rem">Certificado invalido</h2>
          <p class="muted">O codigo <code>{code}</code> nao corresponde a nenhum certificado valido.</p>
        </div>""")

    data = cert['issued_at'][:10]
    td = 'padding:.5rem 1.2rem;border-bottom:1px solid #eee'
    th = 'padding:.5rem 1.2rem;background:#f5f5f5;font-weight:600;white-space:nowrap'
    return page('Verificacao de Certificado', f"""
    <div class="card" style="max-width:580px;margin:0 auto;text-align:center;padding:2.5rem">
      <div style="font-size:3rem;margin-bottom:1rem;color:#2e7d32">&#10004;</div>
      <h2 style="color:#2e7d32;margin-bottom:.5rem">Certificado Autentico</h2>
      <p class="muted" style="margin-bottom:1.8rem">
        Este certificado foi emitido pela plataforma Certifica e e autentico.
      </p>
      <table style="margin:0 auto;text-align:left;border-collapse:collapse;width:100%">
        <tr><th style="{th}">Aluno</th>       <td style="{td}">{cert['aluno']}</td></tr>
        <tr><th style="{th}">Curso</th>        <td style="{td}">{cert['curso']}</td></tr>
        <tr><th style="{th}">Instrutor</th>    <td style="{td}">{cert['instrutor']}</td></tr>
        <tr><th style="{th}">Carga Horaria</th><td style="{td}">{cert['horas']} horas</td></tr>
        <tr><th style="{th}">Emitido em</th>   <td style="{td}">{data}</td></tr>
        <tr><th style="{th}">Codigo</th>        <td style="padding:.5rem 1.2rem"><code>{cert['code']}</code></td></tr>
      </table>
    </div>""")


# ─── painel admin ─────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_page():
    conn = get_db()
    cursos = conn.execute("SELECT * FROM courses ORDER BY created DESC").fetchall()
    pendentes = conn.execute("""
        SELECT e.id, e.enrolled_at,
               u.name AS aluno, u.email,
               co.title AS curso
        FROM enrollments e
        JOIN users   u  ON u.id  = e.user_id
        JOIN courses co ON co.id = e.course_id
        WHERE e.completed_at IS NULL
        ORDER BY e.enrolled_at
    """).fetchall()
    conn.close()

    linhas_cursos = ''.join(
        f'<tr><td>{c["title"]}</td><td>{c["instructor"]}</td><td>{c["hours"]}h</td><td>{c["created"][:10]}</td></tr>'
        for c in cursos
    ) or '<tr><td colspan="4" style="text-align:center;padding:1.5rem;color:#bbb">Nenhum curso cadastrado.</td></tr>'

    linhas_pend = ''
    for p in pendentes:
        linhas_pend += f"""<tr>
          <td>{p['aluno']}</td>
          <td>{p['email']}</td>
          <td>{p['curso']}</td>
          <td>{p['enrolled_at'][:10]}</td>
          <td>
            <form method="POST" action="/admin/enrollments/{p['id']}/complete" style="margin:0">
              <button class="btn btn-success btn-sm">Concluir e Emitir Certificado</button>
            </form>
          </td>
        </tr>"""
    if not linhas_pend:
        linhas_pend = '<tr><td colspan="5" style="text-align:center;padding:1.5rem;color:#bbb">Sem inscricoes pendentes.</td></tr>'

    return page('Admin', f"""
    <h2>Painel Administrativo</h2>

    <div class="card">
      <h3>Novo Curso</h3>
      <form method="POST" action="/admin/courses">
        <label>Titulo do curso</label>
        <input name="title" required placeholder="Ex: Python para Iniciantes">
        <label>Descricao</label>
        <textarea name="description" placeholder="Descricao breve do curso..."></textarea>
        <label>Nome do instrutor</label>
        <input name="instructor" required placeholder="Ex: Prof. Ana Silva">
        <label>Carga horaria (horas)</label>
        <input type="number" name="hours" min="1" required placeholder="Ex: 40">
        <button class="btn btn-primary" type="submit">Criar Curso</button>
      </form>
    </div>

    <div class="card" style="padding:0;overflow:hidden">
      <div style="padding:1rem 1.5rem"><h3>Cursos Cadastrados ({len(cursos)})</h3></div>
      <table>
        <thead><tr><th>Titulo</th><th>Instrutor</th><th>Carga</th><th>Criado em</th></tr></thead>
        <tbody>{linhas_cursos}</tbody>
      </table>
    </div>

    <div class="card" style="padding:0;overflow:hidden">
      <div style="padding:1rem 1.5rem"><h3>Inscricoes Pendentes de Conclusao ({len(pendentes)})</h3></div>
      <table>
        <thead>
          <tr><th>Aluno</th><th>E-mail</th><th>Curso</th><th>Inscrito em</th><th>Acao</th></tr>
        </thead>
        <tbody>{linhas_pend}</tbody>
      </table>
    </div>""")


@app.route('/admin/courses', methods=['POST'])
@admin_required
def criar_curso():
    title       = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    instructor  = request.form.get('instructor', '').strip()
    try:
        hours = int(request.form.get('hours', 0))
    except ValueError:
        hours = 0
    if not title or not instructor or hours < 1:
        flash('Preencha todos os campos corretamente.', 'error')
        return redirect(url_for('admin_page'))
    conn = get_db()
    conn.execute(
        "INSERT INTO courses (title, description, instructor, hours) VALUES (?,?,?,?)",
        (title, description, instructor, hours)
    )
    conn.commit()
    conn.close()
    flash(f'Curso "{title}" criado com sucesso!', 'success')
    return redirect(url_for('admin_page'))


@app.route('/admin/enrollments/<int:eid>/complete', methods=['POST'])
@admin_required
def concluir_inscricao(eid):
    conn   = get_db()
    enroll = conn.execute("SELECT * FROM enrollments WHERE id=?", (eid,)).fetchone()
    if not enroll or enroll['completed_at']:
        conn.close()
        flash('Inscricao nao encontrada ou ja concluida.', 'error')
        return redirect(url_for('admin_page'))
    agora  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    codigo = novo_codigo(enroll['user_id'], enroll['course_id'])
    conn.execute("UPDATE enrollments SET completed_at=? WHERE id=?", (agora, eid))
    conn.execute(
        "INSERT INTO certificates (user_id, course_id, enroll_id, code, issued_at) VALUES (?,?,?,?,?)",
        (enroll['user_id'], enroll['course_id'], eid, codigo, agora)
    )
    conn.commit()
    conn.close()
    flash('Curso concluido! Certificado digital emitido com sucesso.', 'success')
    return redirect(url_for('admin_page'))


# ─── start ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)