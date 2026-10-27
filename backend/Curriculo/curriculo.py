from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import json, os, sys


def carregar_dados_candidato():
    """
    Localiza a pasta data na raiz do projeto subindo os níveis necessários
    e carrega o arquivo de inscrição correto.
    """
    # 1. Caminho absoluto de onde o 'curriculo.py' está:
    # -> c:\Users\adria\Desktop\Estudos\Adrian\Faculdade\git\Gerenciador_de_curriculo_teste\backend\Curriculo
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Sobe duas pastas para chegar na raiz do projeto:
    # -> Sobe 1 (backend) e Sobe 2 (Gerenciador_de_curriculo_teste)
    raiz_projeto = os.path.abspath(os.path.join(diretorio_script, "..", ".."))
    
    # 3. Aponta para a pasta 'data' correta na raiz e localiza o arquivo do candidato
    pasta_data = os.path.join(raiz_projeto, 'data')
    caminho_json = os.path.join(pasta_data, 'inscricao_adriancarlos.json')

    # Validação de segurança
    if not os.path.exists(caminho_json):
        print(f"\nErro Crítico: O arquivo não foi encontrado.", file=sys.stderr)
        print(f"Caminho tentado: {caminho_json}\n", file=sys.stderr)
        sys.exit(1)

    try:
        with open(caminho_json, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError:
        print("Erro Crítico: O arquivo JSON está corrompido ou mal formatado.", file=sys.stderr)
        sys.exit(1)
        
def criarCurriculo(
    candidato,
    perfil,
    experiencias,
    formacoes,
    projetos,
    conhecimentos_tecnicos,
    arquivo="Curriculo.pdf"
):
    """
    Gera o PDF do currículo a partir dos dados recebidos.

    candidato: dict com "nome", "cargo", "telefone", "email",
               "localizacao" e opcionalmente "sites" (lista de URLs,
               ex: GitHub, LinkedIn, portfólio).
    perfil: string com o resumo profissional.
    experiencias: lista de dicts com "cargo", "empresa", "periodo", "descricao".
    formacoes: lista de dicts com "curso", "instituicao", "periodo".
    projetos: lista de dicts com "titulo", "objetivo", "descricao", "tecnologias" (lista).
    conhecimentos_tecnicos: dict {"Categoria": ["item1", "item2", ...]}.
    arquivo: caminho do PDF de saída.
    """

    # ==========================================
    # CONFIGURAÇÃO DO PDF
    # ==========================================

    pdf = canvas.Canvas(
        arquivo,
        pagesize=A4
    )

    largura, altura = A4

    MARGEM_INFERIOR = 20 * mm

    # ==========================================
    # CORES
    # ==========================================

    azul = colors.HexColor("#1F3C5B")
    cinza = colors.HexColor("#666666")
    cinza_claro = colors.HexColor("#E8EEF3")

    # ==========================================
    # POSIÇÃO INICIAL / LARGURA ÚTIL
    # ==========================================

    x = 20 * mm
    largura_texto = largura - 40 * mm  # respeita margem de 20mm dos dois lados

    # ==========================================
    # ESTILOS DE PARÁGRAFO (com wrap automático)
    # ==========================================

    estilo_texto = ParagraphStyle(
        "texto",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.black,
    )

    estilo_cargo = ParagraphStyle(
        "cargo",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.black,
    )

    estilo_empresa = ParagraphStyle(
        "empresa",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=cinza,
    )

    estilo_descricao = ParagraphStyle(
        "descricao",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    estilo_item = ParagraphStyle(
        "item",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
        leftIndent=3 * mm,
    )

    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=azul,
    )

    estilo_campo_projeto = ParagraphStyle(
        "campo_projeto",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.black,
    )

    # ==========================================
    # FUNÇÕES AUXILIARES
    # ==========================================

    def nova_pagina():
        """Abre uma nova página e devolve o y inicial do topo dela.
        Sempre use: y = nova_pagina()."""
        pdf.showPage()
        return altura - 20 * mm

    def escrever_paragrafo(pdf, texto, x, y, largura, estilo):
        """Desenha um parágrafo com quebra de linha automática e devolve o novo y.
        Funciona para qualquer tamanho de texto: se não couber na página,
        pula automaticamente para a próxima."""
        paragrafo = Paragraph(texto, estilo)

        _, altura_par = paragrafo.wrap(largura, 5000 * mm)

        if y - altura_par < MARGEM_INFERIOR:
            y = nova_pagina()

        paragrafo.drawOn(pdf, x, y - altura_par)

        return y - altura_par

    def verificar_espaco(y, altura_necessaria):
        """Garante que exista espaço suficiente antes da margem inferior."""
        if y - altura_necessaria < MARGEM_INFERIOR:
            y = nova_pagina()
        return y

    def desenhar_cabecalho():
        pdf.setFillColor(azul)

        pdf.rect(
            0,
            altura - 55 * mm,
            largura,
            55 * mm,
            fill=1,
            stroke=0
        )

        # Nome
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 25)
        pdf.drawString(20 * mm, altura - 23 * mm, candidato["nome"])

        # Cargo
        pdf.setFont("Helvetica", 12)
        pdf.drawString(20 * mm, altura - 32 * mm, candidato["cargo"])

        # Linha 1 de contatos: telefone | email
        pdf.setFont("Helvetica", 9)
        pdf.drawString(20 * mm, altura - 43 * mm, candidato["telefone"])
        pdf.drawString(75 * mm, altura - 43 * mm, candidato["email"])

        # Linha 2 de contatos: localização | sites (github, linkedin, portfólio...)
        pdf.drawString(20 * mm, altura - 49 * mm, candidato["localizacao"])

        sites = candidato.get("sites", [])
        if sites:
            pdf.drawString(75 * mm, altura - 49 * mm, " | ".join(sites))

    def titulo_secao(texto, y, espaco_extra=10 * mm):
        """
        Desenha o título da seção. 'espaco_extra' garante espaço mínimo
        para pelo menos a primeira linha de conteúdo logo abaixo, evitando
        que o título fique sozinho no fim da página (título "órfão").
        """
        y = verificar_espaco(y, 15 * mm + espaco_extra)

        pdf.setFillColor(azul)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(x, y, texto)

        y -= 3 * mm

        pdf.setStrokeColor(azul)
        pdf.line(x, y, largura - 20 * mm, y)

        y -= 7 * mm

        return y

    # ==========================================
    # CABEÇALHO
    # ==========================================

    desenhar_cabecalho()

    y = altura - 64 * mm

    # ==========================================
    # PERFIL PROFISSIONAL
    # ==========================================

    y = titulo_secao("PERFIL PROFISSIONAL", y)

    y = escrever_paragrafo(pdf, perfil, x, y, largura_texto, estilo_texto)

    y -= 7 * mm

    # ==========================================
    # EXPERIÊNCIA E PROJETOS
    # ==========================================

    y = titulo_secao("EXPERIÊNCIA E PROJETOS", y)

    for experiencia in experiencias:

        y = verificar_espaco(y, 20 * mm)

        y = escrever_paragrafo(
            pdf,
            experiencia["cargo"],
            x, y, largura_texto,
            estilo_cargo
        )

        y = escrever_paragrafo(
            pdf,
            f'{experiencia["empresa"]} | {experiencia["periodo"]}',
            x, y, largura_texto,
            estilo_empresa
        )

        y -= 1 * mm

        y = escrever_paragrafo(
            pdf,
            experiencia["descricao"],
            x, y, largura_texto,
            estilo_descricao
        )

        y -= 6 * mm

    # ------------------------------------------
    # Projetos (dentro da mesma seção "Experiência e Projetos")
    # ------------------------------------------

    if projetos:

        for projeto in projetos:

            y = verificar_espaco(y, 25 * mm)

            y = escrever_paragrafo(
                pdf,
                projeto["titulo"],
                x, y, largura_texto,
                estilo_cargo
            )

            y -= 1 * mm

            y = escrever_paragrafo(
                pdf,
                f'<b>Objetivo:</b> {projeto["objetivo"]}',
                x, y, largura_texto,
                estilo_campo_projeto
            )

            y = escrever_paragrafo(
                pdf,
                f'<b>Descrição:</b> {projeto["descricao"]}',
                x, y, largura_texto,
                estilo_campo_projeto
            )

            y = escrever_paragrafo(
                pdf,
                f'<b>Tecnologias:</b> {", ".join(projeto["tecnologias"])}',
                x, y, largura_texto,
                estilo_campo_projeto
            )

            y -= 6 * mm

    # ==========================================
    # CONHECIMENTOS TÉCNICOS
    # (organizados por categoria, cada uma com um mini título)
    # ==========================================

    y = titulo_secao("CONHECIMENTOS TÉCNICOS", y)

    for categoria, itens in conhecimentos_tecnicos.items():

        # garante espaço para o mini título + pelo menos o 1º item da lista
        y = verificar_espaco(y, 6 * mm + 6 * mm)

        y = escrever_paragrafo(
            pdf,
            categoria,
            x, y, largura_texto,
            estilo_subtitulo
        )

        y -= 1 * mm

        for item in itens:
            y = verificar_espaco(y, 6 * mm)
            y = escrever_paragrafo(
                pdf,
                f"• {item}",
                x, y, largura_texto,
                estilo_item
            )

        y -= 3 * mm

    y -= 3 * mm

    # ==========================================
    # CURSOS E FORMAÇÃO
    # ==========================================

    y = titulo_secao("CURSOS E FORMAÇÃO", y, espaco_extra=14 * mm)

    for formacao in formacoes:

        y = verificar_espaco(y, 14 * mm)

        y = escrever_paragrafo(
            pdf,
            formacao["curso"],
            x, y, largura_texto,
            estilo_cargo
        )

        y = escrever_paragrafo(
            pdf,
            f'{formacao["instituicao"]} | {formacao["periodo"]}',
            x, y, largura_texto,
            estilo_empresa
        )

        y -= 3 * mm

    y -= 2 * mm

    # ==========================================
    # SALVAR
    # ==========================================

    pdf.save()

    print("Currículo gerado com sucesso!")
    print(f"Arquivo: {arquivo}")


# ==========================================
# EXEMPLO DE USO
# (os dados abaixo viriam de outro lugar: formulário, banco de dados, API etc.
#  este bloco só roda quando o arquivo é executado diretamente)
# ==========================================

if __name__ == "__main__":
    # Carrega os dados do JSON dinamicamente
    dados = carregar_dados_candidato()

    # Tratamento seguro usando .get() para evitar quebras por chaves ausentes
    dados_pessoais = dados.get("dados_pessoais", {})
    localizacao = dados_pessoais.get("localizacao", {})
    links = dados_pessoais.get("links", {})
    preferencias = dados.get("preferencias_de_carreira", {})
    formacao = dados.get("formacao", {})
    competencias = dados.get("competencias", {})

    # ==========================================
    # MAPEAMENTO DINÂMICO
    # ==========================================
    
    candidato = {
        "nome": dados_pessoais.get("nome_completo", "Não informado"),
        "cargo": dados.get("vaga_interesse", "Não informado"),
        "telefone": dados_pessoais.get("telefone", "Não informado"),
        "email": dados_pessoais.get("email", "Não informado"),
        "localizacao": f"{localizacao.get('cidade', 'Não informada')} - {localizacao.get('estado', '')}",
        "sites": [
            links.get("linkedin", ""),
            links.get("portfolio_github", "")
        ]
    }

    perfil = dados.get("resumo_profissional", "")

    experiencias = [
        # O formulário web atual não coletou experiências cronológicas ainda.
    ]

    formacoes = [
        {
            "curso": formacao.get("form_area", "Não informado"),
            "instituicao": formacao.get("instituicao", "Não informada"),
            "periodo": formacao.get("nivel", "Não informado")  # Nível de formação atual
        }
    ]

    projetos = [
        # O formulário web não possui mapeamento para projetos nesta fase.
    ]

    conhecimentos_tecnicos = {
        # Divide as strings separadas por vírgula em listas limpas usando list comprehension
        "Hard Skills": [skill.strip() for skill in competencias.get("hard_skills", "").split(",") if skill.strip()],
        "Soft Skills": [skill.strip() for skill in competencias.get("soft_skills", "").split(",") if skill.strip()],
        "Preferências de Carreira": [
            f"Pretensão Salarial: R$ {preferencias.get('pretensao_salarial', 'Não informada')}",
            f"Regime de Contratação: {preferencias.get('regime_contratacao', 'Não informado')}",
            f"Observações de Busca: {dados.get('observacoes_busca', 'Nenhuma')}"
        ]
    }

    # ==========================================
    # Exemplo de saída / validação interna
    # ==========================================
    print(f"Perfil de {candidato['nome']} carregado com sucesso para a vaga de {candidato['cargo']}.")

    criarCurriculo(
        candidato,
        perfil,
        experiencias,
        formacoes,
        projetos,
        conhecimentos_tecnicos
    )