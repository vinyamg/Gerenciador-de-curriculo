// Funções PURAS — testáveis com Vitest sem navegador

export function sanitizar(valor) {
    return String(valor ?? '').replace(/\s+/g, ' ').trim();
}

export function emailValido(valor) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(valor ?? '').trim());
}

export function senhaForte(valor) {
    return typeof valor === 'string' && valor.length >= 6;
}

export function tempoMinimoOk(inicioMs, minimoMs = 3000, agoraMs = Date.now()) {
    return agoraMs - inicioMs >= minimoMs; // anti-bot: preenchimento instantâneo
}

// Converte nomes com colchetes ("dados_pessoais[email]") em objeto aninhado.
// Recebe pares em vez de FormData → testável fora do navegador.
export function aninharCampos(pares) {
    const saida = {};
    for (const [chave, valor] of pares) {
        const caminho = chave.replace(/\]/g, '').split('[');
        let ref = saida;
        caminho.forEach((parte, i) => {
            if (i === caminho.length - 1) ref[parte] = valor;
            else ref = ref[parte] ??= {};
        });
    }
    return saida;
}

export function formToObject(form) {
    return aninharCampos([...new FormData(form).entries()]);
}

// POST JSON com timeout e parse seguro (nunca quebra feio em HTML de erro)
export async function postJSON(url, corpo, timeoutMs = 15000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const resposta = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': corpo.csrf_token ?? ''
            },
            body: JSON.stringify(corpo),
            signal: controller.signal
        });
        const texto = await resposta.text();
        let dados;
        try { dados = JSON.parse(texto); }
        catch { throw new Error('Resposta inválida do servidor.'); }
        if (!resposta.ok) throw new Error(dados.mensagem || `Erro ${resposta.status}.`);
        return dados;
    } finally {
        clearTimeout(timer);
    }
}