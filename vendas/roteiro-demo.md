# Roteiro — gravar o demo HOJE (vídeo de ~2 min)

> Este vídeo é a ÚNICA prova que existe por enquanto. Tudo do funil depende dele. Inegociável.
> O demo é **GENÉRICO**: pega lead de qualquer ramo. Serve pra vender pra confeitaria, oficina, clínica, salão, imobiliária — qualquer negócio que recebe lead no WhatsApp/Instagram.

## Preparação (5 min)

1. Garantir a chave configurada: copiar `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` e colar a chave Groq (ou `set GROQ_API_KEY=...` antes de iniciar).
2. Abrir o app (`iniciar.bat`) e usar o **modo demo** — visual limpo, sem sidebar de configuração:
   `http://localhost:8501/?agente=atendimento`
   (o link no ar é `https://agentes-s68ksrzb97z5q4qqp7f8nq.streamlit.app/?agente=atendimento` — gravar no localhost é melhor: sem risco do app "dormir" no meio)
3. Fazer UMA conversa de aquecimento pra conferir que está respondendo bem. Recarregar a página (F5) pra zerar antes de gravar.
4. Gravação: **Win + G** (Xbox Game Bar, já vem no Windows) → gravar a janela do navegador. Dar zoom (Ctrl +) pra ficar legível no celular — o dono do negócio vai assistir no WhatsApp.

## Roteiro da conversa (você no papel do lead)

Digitar como lead real digitaria — com pressa, informal. Exemplo com encomenda de bolo (qualquer ramo serve, mas esse é fácil de todo mundo entender):

1. `Oi, vi o perfil de vcs no insta`
2. `Queria encomendar um bolo de aniversário`
3. `É pra umas 30 pessoas, tema futebol, queria gastar uns 300 no máximo`
4. **A curveball (momento-chave do vídeo):** `Vcs tem pronta entrega pra sábado? Quanto sai o de chocolate?` → o agente deve responder que quem confirma preço, prazo e disponibilidade é a equipe, SEM inventar valor nem estoque. **Isso é o que mata a objeção "IA vai falar besteira".**
5. `Preciso pra sábado que vem. Pode me chamar no whats depois das 18h, meu nome é Marcos`
6. Deixar o agente fechar com o **📋 RESUMO DO LEAD** — ele aparece num card verde destacado, esse frame final é o clímax do vídeo.

### Variante pra alvo corretor (opcional)

Se for mandar pra um corretor específico, dá pra gravar uma segunda versão com
`?agente=corretor_imoveis&corretor=Nome%20Do%20Corretor` e o roteiro de imóvel
(apto pra alugar, Centro, até 1500/mês, curveball de "tem apto disponível? quanto tá?").
Mas o vídeo genérico funciona pra TODOS os alvos — gravar ele primeiro.

## Depois de gravar

- [ ] Vídeo com no máx. 2 min (cortar espera de digitação se precisar — o app do Fotos do Windows corta vídeo)
- [ ] Print isolado do 📋 RESUMO (usar como imagem avulsa na abordagem)
- [ ] Print da resposta à curveball (prova de que não inventa preço)
- [ ] Assistir 1x no celular: dá pra ler? Se não, regravar com mais zoom
- [ ] Salvar em `vendas/demo/` e no celular (pra mandar direto do WhatsApp)

## Checklist de qualidade (reprovar = regravar)

- O agente fez UMA pergunta por vez?
- Não inventou preço/estoque/prazo em nenhum momento?
- O resumo final saiu completo e no formato certo?
- Nenhuma resposta demorou mais de ~5s? (se demorou, corta na edição)

## Antes do demo: rodar o stress test 1x

`python teste_agente.py --key gsk_xxx` — revisar os 5 pontos que ele imprime no final. Se algum caso de borda sair ruim, ajustar o prompt ANTES de gravar.
