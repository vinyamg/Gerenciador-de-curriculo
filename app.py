# senha 8.huUs5-c6SxfnQ email adrian@gmail.com
import secrets, os
from functools import wraps
from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for)

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.config['SECRET_KEY'] = secrets.token_hex(32)  # TODO: variável de ambiente em produção

# ---------- CSRF (Nível 3) ----------
@app.context_processor
def injeta_csrf():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return {'csrf_token': session['_csrf_token']}

def exige_csrf(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        corpo = request.get_json(silent=True) or {}
        token = request.headers.get('X-CSRF-Token') or corpo.get('csrf_token')
        if not token or token != session.get('_csrf_token'):
            return jsonify(status='erro',
                           mensagem='Sessão expirada. Recarregue a página.'), 403
        return f(*args, **kwargs)
    return wrapper

# ---------- PÁGINAS ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def pagina_login():
    return render_template('login.html')

@app.route('/cadastro')
def pagina_cadastro():
    return render_template('cadastro.html')

@app.route('/inscricao')
def pagina_inscricao():
    if not session.get('usuario_id'):
        return redirect(url_for('pagina_login'))
    return render_template('inscricao.html')

# ---------- API: criar conta ----------
@app.route('/api/auth/cadastro', methods=['POST'])
@exige_csrf
def api_cadastro():
    dados = request.get_json(silent=True) or {}

    if dados.get('website'):  # honeypot
        return jsonify(status='erro', mensagem='Requisição bloqueada por segurança.'), 400

    nome  = (dados.get('nome') or '').strip()
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    erros = []
    if len(nome) < 3:   erros.append('Informe seu nome completo.')
    if '@' not in email: erros.append('E-mail inválido.')
    if len(senha) < 8:  erros.append('A senha deve ter no mínimo 8 caracteres.')
    if erros:
        return jsonify(status='erro', mensagem=' '.join(erros)), 400

    # TODO (Vinicius): e-mail único + hash da senha (argon2/bcrypt) + Supabase
    return jsonify(status='sucesso',
                   mensagem='Conta criada! Faça login para continuar.',
                   redirect=url_for('pagina_login')), 201

# ---------- API: login ----------
@app.route('/api/auth/login', methods=['POST'])
@exige_csrf
def api_login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip().lower()
    senha = dados.get('senha') or ''

    # TODO (Vinicius): buscar usuário no Supabase e conferir hash
    credenciais_ok = True  # placeholder enquanto o backend não está plugado
    if not credenciais_ok:
        return jsonify(status='erro', mensagem='E-mail ou senha incorretos.'), 401

    session['usuario_id'] = 1  # placeholder
    return jsonify(status='sucesso', mensagem='Login realizado.',
                   redirect=url_for('pagina_inscricao')), 200

# ---------- API: inscrição do candidato ----------
@app.route('/api/inscricao', methods=['POST'])
@exige_csrf
def api_inscricao():
    if not session.get('usuario_id'):
        return jsonify(status='erro', mensagem='Faça login antes de continuar.'), 401

    dados = request.get_json(silent=True) or {}
    if dados.get('website'):
        return jsonify(status='erro', mensagem='Requisição bloqueada por segurança.'), 400
    if not dados.get('consentimento_lgpd'):
        return jsonify(status='erro', mensagem='É necessário aceitar a LGPD.'), 400

    dp = dados.get('dados_pessoais') or {}
    if len((dp.get('nome_completo') or '').strip()) < 3:
        return jsonify(status='erro', mensagem='Informe seu nome completo.'), 400

    # TODO (Vinicius/Enzo): persistir perfil completo no Supabase
    return jsonify(status='sucesso',
                   mensagem='Inscrição concluída! Vamos buscar vagas para você.'), 201

if __name__ == '__main__':
    app.run(debug=True)