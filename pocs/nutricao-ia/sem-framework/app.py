from flask import Flask, request, jsonify, render_template_string
import sqlite3
import json
import os
from datetime import datetime
import anthropic

app = Flask(__name__)
DB = "nutri.db"
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            sex TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exam_data TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exam_id INTEGER,
            plan_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
    """)
    db.commit()
    db.close()

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NutriLab IA</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #333; }
  header { background: #1a6b3c; color: white; padding: 20px 40px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 1.6rem; }
  header span { font-size: 1.8rem; }
  .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
  .tabs { display: flex; gap: 8px; margin-bottom: 24px; }
  .tab { padding: 10px 24px; border-radius: 8px; border: none; cursor: pointer; font-size: 0.95rem; font-weight: 600; background: white; color: #555; box-shadow: 0 1px 4px rgba(0,0,0,0.1); transition: all .2s; }
  .tab.active { background: #1a6b3c; color: white; }
  .card { background: white; border-radius: 12px; padding: 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .card h2 { font-size: 1.1rem; color: #1a6b3c; margin-bottom: 20px; border-bottom: 2px solid #e8f5e9; padding-bottom: 10px; }
  .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group.full { grid-column: 1 / -1; }
  label { font-size: 0.85rem; font-weight: 600; color: #555; }
  input, select, textarea { padding: 10px 14px; border: 1.5px solid #ddd; border-radius: 8px; font-size: 0.95rem; width: 100%; transition: border .2s; }
  input:focus, select:focus, textarea:focus { outline: none; border-color: #1a6b3c; }
  .btn { padding: 12px 28px; background: #1a6b3c; color: white; border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 600; cursor: pointer; transition: background .2s; }
  .btn:hover { background: #145a30; }
  .btn:disabled { background: #aaa; cursor: not-allowed; }
  .btn-outline { background: white; color: #1a6b3c; border: 1.5px solid #1a6b3c; }
  .btn-outline:hover { background: #e8f5e9; }
  .exam-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .exam-item { display: flex; flex-direction: column; gap: 4px; }
  .exam-item label { font-size: 0.78rem; }
  .exam-item input { padding: 8px 10px; font-size: 0.88rem; }
  .result-box { background: #f8fffe; border: 1.5px solid #b2dfdb; border-radius: 10px; padding: 20px; margin-top: 20px; white-space: pre-wrap; font-size: 0.92rem; line-height: 1.7; max-height: 500px; overflow-y: auto; }
  .loading { display: flex; align-items: center; gap: 12px; color: #1a6b3c; font-weight: 600; padding: 16px; }
  .spinner { width: 24px; height: 24px; border: 3px solid #c8e6c9; border-top: 3px solid #1a6b3c; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .user-card { background: #f8fffe; border: 1.5px solid #c8e6c9; border-radius: 10px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
  .user-info { display: flex; flex-direction: column; gap: 4px; }
  .user-info strong { font-size: 1rem; color: #1a6b3c; }
  .user-info small { color: #777; font-size: 0.82rem; }
  .plan-card { border: 1.5px solid #e0e0e0; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
  .plan-card .plan-date { font-size: 0.8rem; color: #888; margin-bottom: 8px; }
  .plan-card .plan-text { white-space: pre-wrap; font-size: 0.9rem; line-height: 1.7; max-height: 300px; overflow-y: auto; }
  .plan-card .exams-summary { font-size: 0.8rem; color: #555; background: #f5f5f5; border-radius: 6px; padding: 8px; margin-bottom: 10px; }
  .msg { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 0.9rem; }
  .msg.success { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
  .msg.error { background: #fce4ec; color: #c62828; border: 1px solid #f48fb1; }
  .hidden { display: none !important; }
  .section { display: none; }
  .section.active { display: block; }
  select#user_select { margin-bottom: 16px; }
</style>
</head>
<body>
<header>
  <span>🥗</span>
  <div>
    <h1>NutriLab IA</h1>
    <small style="opacity:.8">Nutrição personalizada baseada em exames laboratoriais</small>
  </div>
</header>
<div class="container">
  <div class="tabs">
    <button class="tab active" onclick="showSection('cadastro')">Novo Paciente</button>
    <button class="tab" onclick="showSection('exames')">Enviar Exames</button>
    <button class="tab" onclick="showSection('historico')">Histórico</button>
  </div>

  <!-- CADASTRO -->
  <div class="section active" id="cadastro">
    <div class="card">
      <h2>Cadastrar Paciente</h2>
      <div id="cadastro_msg"></div>
      <div class="form-row">
        <div class="form-group full"><label>Nome completo</label><input id="c_name" type="text" placeholder="Ex: Maria Silva"></div>
        <div class="form-group"><label>Idade</label><input id="c_age" type="number" placeholder="Ex: 35"></div>
        <div class="form-group"><label>Sexo</label><select id="c_sex"><option value="">Selecione</option><option value="F">Feminino</option><option value="M">Masculino</option></select></div>
        <div class="form-group"><label>Peso (kg)</label><input id="c_weight" type="number" step="0.1" placeholder="Ex: 68.5"></div>
        <div class="form-group"><label>Altura (cm)</label><input id="c_height" type="number" placeholder="Ex: 165"></div>
      </div>
      <button class="btn" onclick="createUser()">Cadastrar Paciente</button>
    </div>
  </div>

  <!-- EXAMES -->
  <div class="section" id="exames">
    <div class="card">
      <h2>Enviar Exames Laboratoriais</h2>
      <div id="exames_msg"></div>
      <div class="form-group" style="margin-bottom:20px">
        <label>Selecionar Paciente</label>
        <select id="user_select"><option value="">Carregando pacientes...</option></select>
      </div>
      <h2 style="font-size:.95rem; margin-bottom:12px;">Hemograma</h2>
      <div class="exam-grid">
        <div class="exam-item"><label>Hemoglobina (g/dL)</label><input id="e_hemoglobina" type="text" placeholder="Ex: 13.5"></div>
        <div class="exam-item"><label>Hematócrito (%)</label><input id="e_hematocrito" type="text" placeholder="Ex: 40"></div>
        <div class="exam-item"><label>Leucócitos (/mm³)</label><input id="e_leucocitos" type="text" placeholder="Ex: 7500"></div>
        <div class="exam-item"><label>Plaquetas (/mm³)</label><input id="e_plaquetas" type="text" placeholder="Ex: 250000"></div>
        <div class="exam-item"><label>VCM (fL)</label><input id="e_vcm" type="text" placeholder="Ex: 88"></div>
        <div class="exam-item"><label>Ferritina (ng/mL)</label><input id="e_ferritina" type="text" placeholder="Ex: 30"></div>
      </div>
      <h2 style="font-size:.95rem; margin-bottom:12px; margin-top:16px;">Bioquímica</h2>
      <div class="exam-grid">
        <div class="exam-item"><label>Glicose (mg/dL)</label><input id="e_glicose" type="text" placeholder="Ex: 92"></div>
        <div class="exam-item"><label>HbA1c (%)</label><input id="e_hba1c" type="text" placeholder="Ex: 5.4"></div>
        <div class="exam-item"><label>Colesterol Total (mg/dL)</label><input id="e_colesterol" type="text" placeholder="Ex: 190"></div>
        <div class="exam-item"><label>HDL (mg/dL)</label><input id="e_hdl" type="text" placeholder="Ex: 55"></div>
        <div class="exam-item"><label>LDL (mg/dL)</label><input id="e_ldl" type="text" placeholder="Ex: 110"></div>
        <div class="exam-item"><label>Triglicerídeos (mg/dL)</label><input id="e_triglicerides" type="text" placeholder="Ex: 120"></div>
        <div class="exam-item"><label>TSH (mUI/L)</label><input id="e_tsh" type="text" placeholder="Ex: 2.5"></div>
        <div class="exam-item"><label>T4 Livre (ng/dL)</label><input id="e_t4" type="text" placeholder="Ex: 1.2"></div>
        <div class="exam-item"><label>Vitamina D (ng/mL)</label><input id="e_vitd" type="text" placeholder="Ex: 28"></div>
        <div class="exam-item"><label>Vitamina B12 (pg/mL)</label><input id="e_vitb12" type="text" placeholder="Ex: 350"></div>
        <div class="exam-item"><label>Zinco (μg/dL)</label><input id="e_zinco" type="text" placeholder="Ex: 88"></div>
        <div class="exam-item"><label>Magnésio (mg/dL)</label><input id="e_magnesio" type="text" placeholder="Ex: 2.0"></div>
      </div>
      <h2 style="font-size:.95rem; margin-bottom:12px; margin-top:16px;">Função Hepática e Renal</h2>
      <div class="exam-grid">
        <div class="exam-item"><label>TGO/AST (U/L)</label><input id="e_tgo" type="text" placeholder="Ex: 28"></div>
        <div class="exam-item"><label>TGP/ALT (U/L)</label><input id="e_tgp" type="text" placeholder="Ex: 25"></div>
        <div class="exam-item"><label>Creatinina (mg/dL)</label><input id="e_creatinina" type="text" placeholder="Ex: 0.9"></div>
        <div class="exam-item"><label>Ureia (mg/dL)</label><input id="e_ureia" type="text" placeholder="Ex: 30"></div>
        <div class="exam-item"><label>Ácido Úrico (mg/dL)</label><input id="e_acido_urico" type="text" placeholder="Ex: 5.0"></div>
        <div class="exam-item"><label>PCR (mg/L)</label><input id="e_pcr" type="text" placeholder="Ex: 2.0"></div>
      </div>
      <div class="form-group" style="margin-top:20px; margin-bottom:20px;">
        <label>Observações adicionais / Queixas do paciente</label>
        <textarea id="e_obs" rows="3" placeholder="Ex: Fadiga frequente, insônia, desejo de emagrecer 5kg..."></textarea>
      </div>
      <button class="btn" id="btn_gerar" onclick="submitExams()">Gerar Plano Nutricional com IA</button>
      <div id="loading_box" class="loading hidden"><div class="spinner"></div>Analisando exames e gerando plano personalizado...</div>
      <div id="plan_result"></div>
    </div>
  </div>

  <!-- HISTÓRICO -->
  <div class="section" id="historico">
    <div class="card">
      <h2>Histórico de Planos</h2>
      <div class="form-group" style="margin-bottom:20px">
        <label>Selecionar Paciente</label>
        <select id="hist_user_select" onchange="loadHistory()"><option value="">Selecione um paciente...</option></select>
      </div>
      <div id="history_list"><p style="color:#aaa; font-size:.9rem;">Selecione um paciente para ver o histórico.</p></div>
    </div>
  </div>
</div>

<script>
let users = [];

async function loadUsers() {
  const res = await fetch('/api/users');
  users = await res.json();
  ['user_select', 'hist_user_select'].forEach(id => {
    const sel = document.getElementById(id);
    const first = id === 'user_select' ? '<option value="">Selecione um paciente...</option>' : '<option value="">Selecione um paciente...</option>';
    sel.innerHTML = first + users.map(u => `<option value="${u.id}">${u.name} — ${u.age} anos, ${u.weight}kg</option>`).join('');
  });
}

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(name).classList.add('active');
  event.target.classList.add('active');
  if (name === 'exames' || name === 'historico') loadUsers();
}

async function createUser() {
  const name = document.getElementById('c_name').value.trim();
  if (!name) { showMsg('cadastro_msg', 'Informe o nome do paciente.', 'error'); return; }
  const body = {
    name,
    age: parseInt(document.getElementById('c_age').value) || null,
    sex: document.getElementById('c_sex').value || null,
    weight: parseFloat(document.getElementById('c_weight').value) || null,
    height: parseFloat(document.getElementById('c_height').value) || null,
  };
  const res = await fetch('/api/users', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
  const data = await res.json();
  if (res.ok) {
    showMsg('cadastro_msg', `Paciente "${name}" cadastrado com sucesso! ID: ${data.id}`, 'success');
    ['c_name','c_age','c_weight','c_height'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('c_sex').value = '';
  } else {
    showMsg('cadastro_msg', data.error || 'Erro ao cadastrar.', 'error');
  }
}

async function submitExams() {
  const userId = document.getElementById('user_select').value;
  if (!userId) { showMsg('exames_msg', 'Selecione um paciente.', 'error'); return; }

  const fields = {
    hemoglobina: 'e_hemoglobina', hematocrito: 'e_hematocrito', leucocitos: 'e_leucocitos',
    plaquetas: 'e_plaquetas', vcm: 'e_vcm', ferritina: 'e_ferritina',
    glicose: 'e_glicose', hba1c: 'e_hba1c', colesterol_total: 'e_colesterol',
    hdl: 'e_hdl', ldl: 'e_ldl', triglicerides: 'e_triglicerides',
    tsh: 'e_tsh', t4_livre: 'e_t4', vitamina_d: 'e_vitd', vitamina_b12: 'e_vitb12',
    zinco: 'e_zinco', magnesio: 'e_magnesio', tgo: 'e_tgo', tgp: 'e_tgp',
    creatinina: 'e_creatinina', ureia: 'e_ureia', acido_urico: 'e_acido_urico', pcr: 'e_pcr'
  };

  const exams = {};
  for (const [key, id] of Object.entries(fields)) {
    const val = document.getElementById(id).value.trim();
    if (val) exams[key] = val;
  }

  if (Object.keys(exams).length === 0) { showMsg('exames_msg', 'Informe ao menos um exame.', 'error'); return; }

  const obs = document.getElementById('e_obs').value.trim();
  if (obs) exams['observacoes'] = obs;

  document.getElementById('btn_gerar').disabled = true;
  document.getElementById('loading_box').classList.remove('hidden');
  document.getElementById('plan_result').innerHTML = '';
  document.getElementById('exames_msg').innerHTML = '';

  try {
    const res = await fetch(`/api/users/${userId}/exams`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ exams })
    });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('plan_result').innerHTML = `<div class="result-box">${data.plan.replace(/\\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/^# (.+)$/gm, '<h3 style="color:#1a6b3c;margin:12px 0 6px">$1</h3>').replace(/^## (.+)$/gm, '<h4 style="color:#2e7d32;margin:10px 0 4px">$1</h4>')}</div>`;
    } else {
      showMsg('exames_msg', data.error || 'Erro ao gerar plano.', 'error');
    }
  } catch(e) {
    showMsg('exames_msg', 'Erro de conexão.', 'error');
  } finally {
    document.getElementById('btn_gerar').disabled = false;
    document.getElementById('loading_box').classList.add('hidden');
  }
}

async function loadHistory() {
  const userId = document.getElementById('hist_user_select').value;
  if (!userId) { document.getElementById('history_list').innerHTML = '<p style="color:#aaa; font-size:.9rem;">Selecione um paciente para ver o histórico.</p>'; return; }

  document.getElementById('history_list').innerHTML = '<div class="loading"><div class="spinner"></div>Carregando histórico...</div>';
  const res = await fetch(`/api/users/${userId}/plans`);
  const plans = await res.json();

  if (!plans.length) {
    document.getElementById('history_list').innerHTML = '<p style="color:#aaa; font-size:.9rem;">Nenhum plano encontrado para este paciente.</p>';
    return;
  }

  document.getElementById('history_list').innerHTML = plans.map(p => {
    const examsList = Object.entries(p.exams).filter(([k]) => k !== 'observacoes').map(([k,v]) => `${k}: ${v}`).join(' | ');
    const date = new Date(p.created_at).toLocaleString('pt-BR');
    return `<div class="plan-card">
      <div class="plan-date">Gerado em: ${date}</div>
      <div class="exams-summary">Exames: ${examsList}</div>
      <div class="plan-text">${p.plan.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
    </div>`;
  }).join('');
}

function showMsg(id, text, type) {
  document.getElementById(id).innerHTML = `<div class="msg ${type}">${text}</div>`;
  setTimeout(() => { const el = document.getElementById(id); if (el) el.innerHTML = ''; }, 4000);
}

loadUsers();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Nome obrigatório"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO users (name, age, sex, weight, height) VALUES (?, ?, ?, ?, ?)",
        (data["name"], data.get("age"), data.get("sex"), data.get("weight"), data.get("height"))
    )
    db.commit()
    user_id = cur.lastrowid
    db.close()
    return jsonify({"id": user_id, "message": "Usuário criado"})

@app.route("/api/users", methods=["GET"])
def list_users():
    db = get_db()
    users = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    db.close()
    return jsonify([dict(u) for u in users])

@app.route("/api/users/<int:user_id>/exams", methods=["POST"])
def submit_exam(user_id):
    data = request.get_json()
    if not data or not data.get("exams"):
        return jsonify({"error": "Exames obrigatórios"}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "Paciente não encontrado"}), 404

    exam_json = json.dumps(data["exams"], ensure_ascii=False)
    cur = db.execute("INSERT INTO exams (user_id, exam_data) VALUES (?, ?)", (user_id, exam_json))
    exam_id = cur.lastrowid
    db.commit()

    exams = data["exams"]
    obs = exams.pop("observacoes", "")

    exam_lines = "\n".join([f"  - {k.replace('_', ' ').title()}: {v}" for k, v in exams.items()])
    obs_text = f"\nQueixas e observações do paciente: {obs}" if obs else ""

    imc = ""
    if user["weight"] and user["height"]:
        imc_val = user["weight"] / ((user["height"] / 100) ** 2)
        imc = f"\n  - IMC calculado: {imc_val:.1f}"

    prompt = f"""Você é um nutricionista clínico especializado em nutrição funcional e análise de exames laboratoriais. Sua tarefa é analisar os exames a seguir e gerar um plano nutricional personalizado, detalhado e prático.

== DADOS DO PACIENTE ==
  - Nome: {user['name']}
  - Idade: {user['age'] or 'não informado'} anos
  - Sexo: {'Feminino' if user['sex'] == 'F' else 'Masculino' if user['sex'] == 'M' else 'não informado'}
  - Peso: {user['weight'] or 'não informado'} kg
  - Altura: {user['height'] or 'não informado'} cm{imc}{obs_text}

== RESULTADOS DOS EXAMES ==
{exam_lines}

== INSTRUÇÕES ==
Com base nesses dados, forneça uma análise completa e um plano nutricional seguindo EXATAMENTE esta estrutura:

## 1. Análise dos Exames
Liste cada exame com seu valor, se está normal/alterado e o significado clínico nutricional.

## 2. Diagnóstico Nutricional
Identifique as principais deficiências, excessos, riscos metabólicos e padrões encontrados.

## 3. Objetivos Nutricionais Prioritários
Liste de 3 a 5 objetivos específicos com base nos achados.

## 4. Plano Alimentar Diário
Descreva refeições detalhadas (café da manhã, lanche manhã, almoço, lanche tarde, jantar) com alimentos específicos e porções aproximadas.

## 5. Alimentos Funcionais Prioritários
Liste alimentos-chave para corrigir as alterações encontradas, explicando brevemente o porquê.

## 6. Alimentos a Evitar ou Reduzir
Com justificativas baseadas nos exames.

## 7. Suplementação Recomendada
Apenas se indicada pelos exames. Especifique nutriente, forma, dose sugerida e melhor horário.

## 8. Orientações de Estilo de Vida
Hidratação, sono, atividade física e outros fatores que potencializam o plano nutricional.

## 9. Monitoramento
Quais exames devem ser repetidos e em quanto tempo para avaliar a evolução.

Seja específico, prático e use linguagem acessível. Baseie TODAS as recomendações nos valores dos exames apresentados."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    plan_text = message.content[0].text

    db.execute(
        "INSERT INTO plans (user_id, exam_id, plan_text) VALUES (?, ?, ?)",
        (user_id, exam_id, plan_text)
    )
    db.commit()
    db.close()

    return jsonify({"exam_id": exam_id, "plan": plan_text})

@app.route("/api/users/<int:user_id>/plans", methods=["GET"])
def get_plans(user_id):
    db = get_db()
    plans = db.execute("""
        SELECT p.id, p.plan_text, p.created_at, e.exam_data
        FROM plans p
        JOIN exams e ON p.exam_id = e.id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC
    """, (user_id,)).fetchall()
    db.close()
    return jsonify([{
        "id": p["id"],
        "plan": p["plan_text"],
        "exams": json.loads(p["exam_data"]),
        "created_at": p["created_at"]
    } for p in plans])

if __name__ == "__main__":
    init_db()
    print("NutriLab IA rodando em http://localhost:5000")
    app.run(debug=True, port=5000)