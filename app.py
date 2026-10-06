"""
Para rodar o web corretamente, inicie esse .py e coloque na porta local :5000

    Ao iniciar ele vai servir de escuta da UI e processamento de dados para
    um .json que vai estar presente em /data
"""

from flask import Flask, render_template, request, jsonify
import unicodedata, re, json, os

#config dos caminhos
app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# auto descritivo... 
def limpar_texto(texto):
    if not texto:
        return ""
    # separar a letra do acento
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto_tratado = "".join([c for c in nfkd_form if not unicodedata.category(c) == 'Mn'])
    texto_limpo = texto_tratado.lower()
    texto_limpo = re.sub(r'[^a-z0-9\s]', '', texto_limpo)
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
    return texto_limpo

# uso da virgula para separar um texto em uma lista
def div_text(texto):
    if not texto:
        return []
    return [item.strip() for item in texto.split(',') if item.strip()]

@app.route('/')
def index():
    return render_template('index.html')

# aqui é a parte dos dados que ele espera do formulario http ja limpo o que for necessario
# Obs. tudo que termina com "usu" vem direto do formulario para depois ser formatado/limpo
@app.route('/processar', methods=['POST'])
def processar_formulario():
    nome_usu = request.form.get('dados_pessoais[nome_completo]')
    nome = limpar_texto(nome_usu)  
    email = request.form.get('dados_pessoais[email]')
    telefone = request.form.get('dados_pessoais[telefone]')
    
    cidade_usu = request.form.get('dados_pessoais[localizacao][cidade]')
    cidade = limpar_texto(cidade_usu)
    estado = request.form.get('dados_pessoais[localizacao][estado]')
    
    nv_formacao = request.form.get('formacao[nivel]')
    instituicao_formacao_usu = request.form.get('formacao[instituicao]')
    instituicao_formacao = limpar_texto(instituicao_formacao_usu)
    area_formacao_usu = request.form.get('formacao[form_area]')
    area_formacao = limpar_texto(area_formacao_usu)

    linkedin = request.form.get('dados_pessoais[links][linkedin]')
    github = request.form.get('dados_pessoais[links][portfolio_github]')
    
    vaga_usu = request.form.get('vaga_interesse')
    vaga = limpar_texto(vaga_usu)
    min_salario = request.form.get('preferencias_de_carreira[pretensao_salarial]')
    regime = request.form.get('preferencias_de_carreira[regime_contratacao]')
    data_limite_dias = request.form.get('busca_dias_passados')
    
    obs_usu = request.form.get('observacoes_busca')
    obs = limpar_texto(obs_usu)
    resumo_usu = request.form.get('resumo_profissional')
    resumo = limpar_texto(resumo_usu)
    hard_skills_raw = request.form.get('competencias[hard_skills]')
    soft_skills_raw = request.form.get('competencias[soft_skills]')

    # caso não tenha preenchido o minimo salarial, valida valor = 0
    try:
        min_salario = float(min_salario) if min_salario else 0.0
    except ValueError:
        min_salario = 0.0
        
    # caso não tenha colocado uma data, lança 1 ano de vagas ativas...
    try:
        data_limite_dias = int(data_limite_dias) if data_limite_dias else 365
    except ValueError:
        data_limite_dias = 365

    # Esqueleto do JSON
    registro_candidato = {
        "dados_pessoais": {
            "nome_completo": nome,
            "email": email,
            "telefone": telefone,
            "localizacao": {
                "cidade": cidade,
                "estado": estado,
                "pais": "Brasil"
            },
            "links": {
                "linkedin": linkedin,
                "portfolio_github": github
            }
        },
        "resumo_profissional": resumo,
        "formacao_academica": {
            "nivel_formacao": nv_formacao,
            "instituicao_formacao": instituicao_formacao,
            "area_formacao": area_formacao
            },       
        "competencias": {
            "hard_skills": div_text(hard_skills_raw),
            "soft_skills": div_text(soft_skills_raw), 
            "observacoes": obs,
        },
        "preferencias_de_carreira": {
            "regime_contratacao": regime,
            "pretensao_salarial": min_salario,
            "vaga": vaga,
            "vagas_publicadas_nos_ultimos_dias": data_limite_dias
        },
    }
    
    # Cria e salva o arquivo .json e o nomeia o json com o nome do usuario
    nome_arq = f"curriculo_{nome}.json"
    
    # Define o caminho para dentro da pasta /data
    caminho = os.path.join(DATA_DIR, nome_arq)
    
    try:
        # como boa pratica -- /data existe antes de salvar
        os.makedirs(DATA_DIR, exist_ok=True)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(registro_candidato, f, indent=4, ensure_ascii=False)
        print(f"Arquivo salvo com sucesso em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")
        return jsonify({"status": "erro", "mensagem": "Não foi possível salvar os dados."}), 500

    """
    Usando como debug com um retorno de resposta para o navegador.
    Interessante colocar uma tela de carregamento ou algo assim aqui
    ou uma interfasse para carregar o curriculo que vai ser gerado
    """
    return jsonify({
        "status": "sucesso",
        "mensagem": f"Insrição concluida! {nome_arq} ",
        "dados": registro_candidato
    })

if __name__ == '__main__':
    app.run(debug=True)
