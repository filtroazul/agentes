# Script 1 — Convite pro piloto (seu pai)

> Mandar quando ele estiver recuperado. Tom leve, sem pressão, sem "vender" — é um presente que resolve uma dor dele.

---

Pai, quando tiver melhor e com a cabeça no lugar, queria te mostrar uma coisa que fiz.

Montei um assistente com inteligência artificial que responde os leads de imóvel na hora, a qualquer horário. Ele conversa com a pessoa, descobre o que ela procura (compra ou aluguel, bairro, faixa de preço, prazo) e te manda um resumo prontinho pra você já ligar sabendo tudo.

Quero deixar ele funcionando pra você **de graça** — pra mim vale como teste no mundo real. Você não precisa fazer nada além de me deixar acompanhar como os leads chegam pra ti hoje.

Se funcionar bem no seu dia a dia, aí sim penso em oferecer pros teus colegas. Topa testar quando estiver 100%?

---

## Checklist antes de mandar
- [ ] Agente testado com os casos de borda (`python teste_agente.py`)
- [ ] Prompt personalizado com o nome dele (trocar `[NOME DO CORRETOR]` no agents.yaml)
- [ ] Decidido COMO ele vai usar na prática (ver nota abaixo)

## Nota importante — o "como" da entrega
O agente hoje roda no Streamlit local. Pro piloto com seu pai, opções em ordem de esforço:
1. **Modo copiloto (dá pra fazer JÁ):** o lead manda mensagem no WhatsApp dele, você (ou ele) cola no agente, e cola a resposta de volta. Feio, mas valida o roteiro de qualificação em 1 dia.
2. **Streamlit na nuvem (1 dia de trabalho):** deploy grátis no Streamlit Community Cloud, ele acessa de qualquer lugar pelo celular.
3. **WhatsApp de verdade (1-2 semanas):** integração via Evolution API ou similar. É o produto final que se cobra R$300-800 de setup. Só construir DEPOIS de validar com o modo 1 ou 2.
