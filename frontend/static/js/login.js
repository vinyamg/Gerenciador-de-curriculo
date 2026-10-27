import { emailValido, postJSON } from './comum.js';
import { prepararFormulario } from './ui.js';

const form = document.getElementById('form-login');
if (form) {
    prepararFormulario(form, async ({ dados, mostraErro, carregando }) => {
        if (!emailValido(dados.email)) return mostraErro('Informe um e-mail válido.');
        if (!dados.senha) return mostraErro('Informe sua senha.');

        carregando(true, 'Entrando…');
        const resposta = await postJSON('/api/auth/login', dados);
        window.location.href = resposta.redirect;
    });
}