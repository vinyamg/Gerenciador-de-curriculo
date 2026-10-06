import requests
from bs4 import BeautifulSoup

class gupy:
    @staticmethod
    def vagas(
        termo,
        tipo, #remote ex
        quantidade,
        cidade=None,
        estado=None,
        ordenar_por=None,
        ordem=None
    ):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

        vagas_coletadas = []

        limit = quantidade
        offset = 0

        while True:

            params = {
                "jobName": termo,
                "workplaceType": tipo,
                "limit": limit,
                "offset": offset
            }

            # Adiciona somente os parâmetros que foram informados
            if cidade is not None:
                params["city"] = cidade

            if estado is not None:
                params["state"] = estado

            if ordenar_por is not None:
                params["sortBy"] = ordenar_por

            if ordem is not None:
                params["sortOrder"] = ordem

            response = requests.get(
                "https://portal.gupy.io/api/job-search/jobs",
                headers=headers,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            dados = response.json()

            vagas = dados.get("data", [])
            pagination = dados.get("pagination", {})

            total = pagination.get("total", 0)

            for vaga in vagas:

                vagas_coletadas.append({
                    "id": vaga.get("id"),
                    "titulo": vaga.get("name"),
                    "empresa": vaga.get("careerPageName"),

                    "local": (
                        f"{vaga.get('city')} - "
                        f"{vaga.get('state')}"
                    ),

                    "modelo": vaga.get("workplaceType"),
                    "contrato": vaga.get("type"),
                    "data_publicacao": vaga.get("publishedDate"),
                    "pcd": vaga.get("disabilities"),
                    "url": vaga.get("jobUrl")
                })

            offset += limit

            if len(vagas_coletadas) >= total or not vagas:
                break

        return {
            "quantidade": len(vagas_coletadas),
            "vagas": vagas_coletadas
        }
    @staticmethod
    def coletaInfo(url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Localiza o título da seção
        titulo = soup.select_one(
            '[data-testid="section-Requisitos e qualificações-title"]'
        )

        if not titulo:
            return []

        # Encontra o container da seção
        container = titulo.find_parent(
            "div",
            attrs={"data-testid": "text-section"}
        )

        if not container:
            return []

        requisitos = []

        # Pega todos os parágrafos e itens de lista
        elementos = container.select("p, li")

        for elemento in elementos:

            texto = elemento.get_text(" ", strip=True)

            if not texto:
                continue

            # Remove bullet caso exista
            texto = texto.lstrip("•").strip()

            if not texto:
                continue

            # Ignora títulos/subtítulos em negrito
            if elemento.name == "p" and elemento.find("strong"):
                continue

            # Evita duplicações
            if texto not in requisitos:
                requisitos.append(texto)

        return requisitos
