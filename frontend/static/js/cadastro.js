import { sanitizar, emailValido, senhaForte, postJSON } from './comum.js';
import { prepararFormulario } from './ui.js';

const form = document.getElementById('form-cadastro');
if (form) {
    prepararFormulario(form, async ({ dados, mostraErro, carregando }) => {
        if (dados.website) return; // honeypot: falha silenciosa, bot não aprende
        if (sanitizar(dados.nome).length < 3) return mostraErro('Informe seu nome completo.');
        if (!emailValido(dados.email))        return mostraErro('Informe um e-mail válido.');
        if (!senhaForte(dados.senha))         return mostraErro('A senha deve ter no mínimo 6 caracteres.');
        if (dados.senha !== dados.senha2)     return mostraErro('As senhas não conferem.');

        carregando(true, 'Criando conta…');
        const resposta = await postJSON('/api/auth/cadastro', dados);
        window.location.href = resposta.redirect;
    });
}