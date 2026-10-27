import { sanitizar, tempoMinimoOk, postJSON } from './comum.js';
import { prepararFormulario } from './ui.js';

const form = document.getElementById('form-candidato');
if (form) {
    const abertoEm = Date.now();
    const TEMPO_MINIMO_MS = 3000;
    const telaSucesso = document.getElementById('tela-sucesso');

    prepararFormulario(form, async ({ dados, mostraErro, carregando }) => {
        // 1. Validações de Segurança (utilizando o objeto estruturado pelo formToObject)
        if (dados.website) return mostraErro('Requisição bloqueada por segurança.');
        if (!dados.consentimento_lgpd)
            return mostraErro('É necessário aceitar o uso dos dados (LGPD) para continuar.');
        if (!tempoMinimoOk(abertoEm, TEMPO_MINIMO_MS))
            return mostraErro('Envio muito rápido. Revise os dados e tente novamente.');

        // 2. Sanitização leve usando a estrutura aninhada do formToObject
        if (dados.dados_pessoais) {
            dados.dados_pessoais.nome_completo = sanitizar(dados.dados_pessoais.nome_completo);
        }
        dados.vaga_interesse = sanitizar(dados.vaga_interesse);
        if (dados.dados_pessoais?.localizacao) {
            dados.dados_pessoais.localizacao.cidade = sanitizar(dados.dados_pessoais.localizacao.cidade);
        }

        // 3. Atualiza estado visual para processamento
        carregando(true, 'Enviando...');

        // 4. Envio dos dados para a API externa (se houver backend)
        const resposta = await postJSON('/api/inscricao', dados);

        if (!resposta || resposta.erro || resposta.sucesso === false) {
            throw new Error(resposta?.mensagem || 'Falha ao processar inscrição no servidor.');
        }

        // ==========================================
        // NOVO: SALVAMENTO AUTOMÁTICO EM ARQUIVO .JSON
        // ==========================================
        try {
            // Converte o objeto de dados estruturado em uma String JSON formatada
            const dadosJSONStr = JSON.stringify(dados, null, 4);
            const blob = new Blob([dadosJSONStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            // Cria um link temporário oculto para forçar o download do arquivo
            const linkDownload = document.createElement('a');
            linkDownload.href = url;
            // Define o nome do arquivo usando o nome do candidato sanitizado ou padrão
            const nomeArquivo = dados.dados_pessoais?.nome_completo 
                ? `inscricao_${dados.dados_pessoais.nome_completo.toLowerCase().replace(/\s+/g, '_')}.json`
                : 'registro_candidato.json';
                
            linkDownload.download = nomeArquivo;
            document.body.appendChild(linkDownload);
            linkDownload.click();
            
            // Limpa o elemento da memória
            document.body.removeChild(linkDownload);
            URL.revokeObjectURL(url);
        } catch (erroJson) {
            console.error('Erro ao gerar o arquivo JSON local:', erroJson);
        }
        // ==========================================

        // 5. Fluxo de Sucesso na Interface
        form.hidden = true;
        
        // Correção do erro anterior: Verifica a existência do elemento antes de setar o texto
        const elementoMensagem = document.getElementById('msg-sucesso');
        if (elementoMensagem) {
            elementoMensagem.textContent = resposta.mensagem || 'Inscrição concluída com sucesso!';
        }
        
        telaSucesso.hidden = false;
        carregando(false);
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // 5. Validação da resposta
        // Se o seu postJSON não lançar erro em status 400/500, tratamos aqui:
        if (!resposta || resposta.erro || resposta.sucesso === false) {
            throw new Error(resposta?.mensagem || 'Falha ao processar inscrição no servidor.');
        }

        // 6. Fluxo de Sucesso: Esconde formulário e exibe feedback visual
        form.hidden = true;
        document.getElementById('msg-sucesso').textContent = resposta.mensagem || 'Inscrição realizada com sucesso!';
        telaSucesso.hidden = false;
        
        // Desliga o estado de carregamento para que o botão não volte travado caso o usuário reinicie
        carregando(false);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Reseta o formulário caso o usuário clique em "Novo Cadastro"
    document.getElementById('btn-novo-cadastro')?.addEventListener('click', () => {
        form.reset();
        form.classList.remove('tentado');
        telaSucesso.hidden = true;
        form.hidden = false;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}
