import { formToObject } from './comum.js';

// Amarra submit, caixa de erro e botão de qualquer página
export function prepararFormulario(form, aoEnviar) {
    const caixaErro = document.getElementById('caixa-erro');
    const botao = form.querySelector('[type="submit"]');
    const textoOriginal = botao.textContent;

    // campos só ficam vermelhos após a 1ª tentativa
    form.addEventListener('invalid', () => form.classList.add('tentado'), true);

    form.addEventListener('submit', async (evento) => {
        evento.preventDefault();
        caixaErro.hidden = true;

        const mostraErro = (msg) => {
            caixaErro.textContent = '⚠ ' + msg;
            caixaErro.hidden = false;
            caixaErro.scrollIntoView({ behavior: 'smooth', block: 'center' });
        };
        const carregando = (ativo, texto = 'Enviando…') => {
            botao.disabled = ativo;
            botao.textContent = ativo ? texto : textoOriginal;
        };

        try {
            await aoEnviar({ dados: formToObject(form), mostraErro, carregando });
        } catch (erro) {
            carregando(false);
            mostraErro(erro.message || 'Erro inesperado. Tente novamente.');
        }
    });
}