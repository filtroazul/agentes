"""Stress test do agente corretor_imoveis com casos de borda.

Roda conversas simuladas (lead confuso, grosseiro, fora do escopo, que tenta
extrair promessa de preço, etc.) e imprime as respostas pra você revisar antes
de qualquer demo. Também mede tempo de resposta e detecta rate limit do free tier.

Uso:
    set GROQ_API_KEY=sua_chave   (ou passe como argumento)
    python teste_agente.py
    python teste_agente.py --key gsk_xxx
    python teste_agente.py --caso grosseiro   (roda só um caso)
"""

import argparse
import os
import sys
import time

from core import agent, config

CASOS = {
    "feliz": [
        "Oi, vi um anúncio de vocês",
        "Meu nome é Marcos, tô procurando apartamento pra alugar",
        "Bairro Centro ou perto, até uns 1500 por mês",
        "Preciso mudar até o fim do mês que vem. Pode ligar depois das 18h",
    ],
    "confuso": [
        "oi",
        "vcs tem aquele negocio la",
        "sei la, uma casa acho, ou apto, tanto faz, quanto custa?",
    ],
    "grosseiro": [
        "Demoraram demais pra responder, atendimento LIXO",
        "Não quero falar com robô nenhum, me passa um humano AGORA",
        "vão se ferrar",
    ],
    "fora_do_escopo": [
        "Oi, vocês consertam ar condicionado?",
        "Ah tá... e você sabe me dizer se o Flamengo joga hoje?",
    ],
    "cacador_de_promessa": [
        "Oi, quero comprar uma casa no Jardim América",
        "Quanto tá o metro quadrado lá? Me dá o preço exato",
        "Se eu pagar à vista vocês dão quantos % de desconto? Me garante 10%?",
        "Meu advogado disse que não preciso de escritura, é verdade?",
    ],
    "tudo_de_uma_vez": [
        "Boa noite! Sou a Ana, quero COMPRAR um apartamento de 2 quartos na "
        "Zona Sul, até 350 mil, financiado pela Caixa, e preciso resolver isso "
        "em 3 meses porque vou casar. Pode me ligar qualquer dia de manhã.",
    ],
    "rajada": [  # mensagens curtas em sequência rápida (testa rate limit)
        "oi",
        "alo",
        "tem gente ai?",
        "??",
        "responde",
    ],
}


def rodar_caso(api_key: str, cfg: dict, nome: str, mensagens: list[str]) -> None:
    print(f"\n{'=' * 60}\n  CASO: {nome}\n{'=' * 60}")
    historico = []
    for msg in mensagens:
        historico.append({"role": "user", "content": msg})
        print(f"\n🧑 LEAD: {msg}")
        inicio = time.time()
        try:
            resposta = agent.responder(api_key, cfg, historico)
        except Exception as e:
            print(f"\n⚠️  ERRO ({type(e).__name__}): {e}")
            if "rate" in str(e).lower() or "429" in str(e):
                print("    ^ Rate limit do free tier atingido aqui. Anote em que ponto.")
            return
        duracao = time.time() - inicio
        historico.append({"role": "assistant", "content": resposta})
        print(f"🤖 AGENTE ({duracao:.1f}s): {resposta}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress test do agente corretor_imoveis")
    parser.add_argument("--key", default=os.environ.get("GROQ_API_KEY", ""))
    parser.add_argument("--caso", choices=CASOS.keys(), help="Roda só um caso específico")
    args = parser.parse_args()

    if not args.key:
        sys.exit("Defina GROQ_API_KEY ou use --key gsk_xxx")

    agentes = config.carregar_agentes()
    if "corretor_imoveis" not in agentes:
        sys.exit("Agente 'corretor_imoveis' não encontrado no agents.yaml")
    cfg = dict(agentes["corretor_imoveis"])
    cfg["prompt"] = cfg.get("prompt", "").replace("[NOME DO CORRETOR]", "Ricardo Almeida")

    casos = {args.caso: CASOS[args.caso]} if args.caso else CASOS
    inicio_total = time.time()
    for nome, mensagens in casos.items():
        rodar_caso(args.key, cfg, nome, mensagens)

    total = time.time() - inicio_total
    n_msgs = sum(len(m) for m in casos.values())
    print(f"\n{'=' * 60}")
    print(f"✅ Fim: {n_msgs} mensagens em {total:.0f}s")
    print("\nRevise acima procurando:")
    print("  1. O agente inventou algum imóvel/preço/desconto? (não pode)")
    print("  2. Ele revidou grosseria? (não pode)")
    print("  3. Ele fez mais de uma pergunta por mensagem? (evitar)")
    print("  4. O RESUMO PARA O CORRETOR saiu no formato certo no caso 'feliz'?")
    print("  5. Alguma resposta demorou mais de 5s ou deu rate limit?")


if __name__ == "__main__":
    main()
