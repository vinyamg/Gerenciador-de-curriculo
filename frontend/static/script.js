// Camada 2 de segurança: validação e endurecimento no navegador
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-candidato');
    if (!form) return;

    const btn = form.querySelector('.btn-enviar');
    const caixaErro = document.getElementById('caixa-erro');
    const telaSucesso = document.getElementById('tela-sucesso');
    const TEMPO_MINIMO_MS = 3000; // bot preenche instantâneo
    const abertoEm = Date.now();

    // Marca o form para estilizar campos inválidos só após a 1ª tentativa
    form.addEventListener('invalid', () => form.classList.add('tentado'), true);

    form.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        escondeErro();

        // 1) Honeypot preenchido = bot
        if (form.elements['website'].value.trim() !== '') {
            mostraErro('Requisição bloqueada por segurança.');
            return;
        }

        // 2) Consentimento LGPD obrigatório
        if (!form.elements['consentimento_lgpd'].checked) {
            mostraErro('É necessário aceitar o uso dos dados (LGPD) para continuar.');
            return;
        }

        // 3) Tempo mínimo de preenchimento
        if (Date.now() - abertoEm < TEMPO_MINIMO_MS) {
            mostraErro('Envio muito rápido. Revise os dados e tente novamente.');
            return;
        }

        // 4) Sanitização leve antes de enviar (o backend refaz a limpeza)
        ['dados_pessoais[nome_completo]', 'vaga_interesse', 'dados_pessoais[localizacao][cidade]']
            .forEach((nomeCampo) => {
                const campo = form.elements[nomeCampo];
                if (campo) campo.value = campo.value.replace(/\s+/g, ' ').trim();
            });

        carregando(true);

        try {
            const resposta = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            });
            const dados = await resposta.json();

            if (!resposta.ok || dados.status !== 'sucesso') {
                throw new Error(dados.mensagem || 'Erro ao processar o formulário.');
            }

            // Sucesso: troca o formulário pela tela de confirmação
            form.hidden = true;
            document.getElementById('msg-sucesso').textContent = dados.mensagem;
            telaSucesso.hidden = false;
            window.scrollTo({ top: 0, behavior: 'smooth' });

        } catch (erro) {
            mostraErro(erro.message + ' Verifique sua conexão e tente novamente.');
            carregando(false);
        }
    });

    document.getElementById('btn-novo-cadastro').addEventListener('click', () => {
        form.reset();
        form.classList.remove('tentado');
        telaSucesso.hidden = true;
        form.hidden = false;
        carregando(false);
        escondeErro();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    function carregando(estado) {
        btn.disabled = estado;
        btn.textContent = estado ? 'Enviando com segurança…' : 'Ir para fase 2';
    }

    function mostraErro(msg) {
        caixaErro.textContent = '⚠ ' + msg;
        caixaErro.hidden = false;
        caixaErro.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function escondeErro() { caixaErro.hidden = true; }
});