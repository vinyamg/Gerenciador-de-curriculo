from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


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

    candidato = {
        "nome": "joao teste",
        "cargo": "Pentest junior",
        "telefone": "(11) 99999-9999",
        "email": "joao@email.com",
        "localizacao": "São Paulo - SP",
        "sites": ["https://github.com/teste"]
    }

    perfil = (
        "Profissional organizado, responsável e comprometido, "
        "com experiência em pentest, pesquisa e appsec "
        "Com conhecimentos em engenharia reversa, web e embarcados"
    )

    experiencias = [
        {
            "cargo": "Assistente Administrativo",
            "empresa": "Empresa ABC",
            "periodo": "2023 - 2026",
            "descricao": (
                "Atendimento ao cliente, organização de documentos, "
                "elaboração de relatórios e suporte às atividades administrativas."
            )
        },
        {
            "cargo": "Auxiliar Administrativo",
            "empresa": "Empresa XYZ",
            "periodo": "2021 - 2023",
            "descricao": (
                "Controle de documentos, atendimento telefônico "
                "e apoio às rotinas administrativas."
            )
        }
    ]

    formacoes = [
        {
            "curso": "Cibersegurança",
            "instituicao": "Faculdade x",
            "periodo": "2024 - 2025"
        },
        {
            "curso": "Ensino Médio",
            "instituicao": "Escola Estadual Exemplo",
            "periodo": "2019 - 2026"
        }
    ]

    # Template de projeto: titulo, objetivo, descricao e tecnologias (lista).
    projetos = [
        {
            "titulo": "Análise de Firmware de Dispositivo IoT",
            "objetivo": (
                "Identificar vulnerabilidades de segurança em firmware embarcado "
                "de um roteador doméstico."
            ),
            "descricao": (
                "Extração e engenharia reversa do firmware, mapeamento de "
                "binários e identificação de falhas de autenticação e "
                "armazenamento inseguro de credenciais."
            ),
            "tecnologias": ["Ghidra", "Binwalk", "QEMU", "Python"]
        },
        {
            "titulo": "Teste de Intrusão em Aplicação Web",
            "objetivo": (
                "Avaliar a segurança de uma aplicação web corporativa "
                "simulando ataques externos."
            ),
            "descricao": (
                "Levantamento de vulnerabilidades como injeção de SQL, XSS "
                "e falhas de controle de acesso, com relatório técnico "
                "detalhado das descobertas e recomendações de correção."
            ),
            "tecnologias": ["Burp Suite", "SQLMap", "Nmap", "OWASP ZAP"]
        }
    ]

    conhecimentos_tecnicos = {
        "Programação": [
            "Python",
            "SQL",
            "JavaScript"
        ],
        "Ferramentas e Softwares": [
            "Excel Avançado",
            "Word",
            "Power BI"
        ],
        "Habilidades Gerais": [
            "Organização",
            "Atendimento ao cliente",
            "Trabalho em equipe",
            "Comunicação"
        ],
        "Pesquisa": [
            "Assembly",
            "GHidra",
            "JavaScript"
        ]
    }

    criarCurriculo(
        candidato,
        perfil,
        experiencias,
        formacoes,
        projetos,
        conhecimentos_tecnicos
    )