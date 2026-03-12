"""
AI Executive Search Associate — Interface Web (Streamlit)
Execute com: streamlit run app.py
"""

import streamlit as st
import anthropic
from tools import TOOLS, execute_tool

MODEL = "claude-opus-4-6"
MAX_ITERATIONS = 20

SYSTEM_PROMPT = """Você é um Executive Search Associate de elite — um copiloto de IA para recrutamento executivo e talent strategy.

Você atua como um consultor sênior de executive search, combinando inteligência de mercado, análise estratégica de talentos e expertise em recrutamento de liderança para empresas de todos os estágios.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 IDIOMAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Você é fluente em Português, Inglês e Espanhol.
REGRA CRÍTICA: Sempre responda no mesmo idioma que o usuário está utilizando.
• Se o usuário escrever em português → responda em português
• Se o usuário escrever em inglês → responda em inglês
• Se o usuário escrever em espanhol → responda em espanhol

Você analisa CVs, perfis e documentos em qualquer um dos três idiomas.
Ao redigir mensagens de outreach, use o idioma mais adequado para o candidato e mercado.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CAPACIDADES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SOURCING — perfil ideal, Boolean search, mapa de mercado
2. ANÁLISE DE PERFIL — CV, fit score 0–100, scorecard de competências
3. COMUNICAÇÃO — outreach LinkedIn/email/WhatsApp, personalização
4. ENTREVISTAS — perguntas, estratégia e roteiro estruturado
5. RESUMOS E SHORTLISTS — resumo de entrevista, shortlist comparativa
6. REMUNERAÇÃO — benchmarking de compensação executiva
7. DEFINIÇÃO DA VAGA — brief completo + estratégia de contratação
8. INTELIGÊNCIA DE TALENTOS — mapeamento, tendências, posicionamento

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 PRINCÍPIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Seja direto, estratégico e orientado a dados
• Use as ferramentas disponíveis para entregar análises completas
• Forneça recomendações claras e acionáveis
• Seja honesto sobre riscos e gaps — não apenas pontos positivos"""


def run_agent(user_message: str, history: list[dict], api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)

    messages = history + [{"role": "user", "content": user_message}]

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=8096,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return "".join(
                block.text
                for block in response.content
                if hasattr(block, "type") and block.type == "text"
            )

        if response.stop_reason == "pause_turn":
            continue

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

    return "⚠️ O agente atingiu o limite de iterações."


# ── Streamlit UI ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Executive Search Associate",
    page_icon="🎯",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎯 Executive Search AI")
    st.caption("Powered by Claude Opus 4.6")

    st.divider()

    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Obtenha sua chave em console.anthropic.com",
    )

    st.divider()

    st.markdown("**🛠 Capacidades**")
    st.markdown("""
- 📍 Sourcing de candidatos
- 🔍 Análise de CV e fit score
- 📋 Scorecard de competências
- 📩 Outreach personalizado
- 🎙 Perguntas de entrevista
- 📊 Estratégia de entrevista
- 📝 Resumo de entrevista
- 🏆 Shortlist comparativa
- 💰 Benchmarking de remuneração
- 📄 Brief de vaga
- 💡 Inteligência de talentos
""")

    st.divider()

    st.markdown("**💬 Idiomas**")
    st.markdown("🇧🇷 Português · 🇺🇸 English · 🇪🇸 Español")

    st.divider()

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.markdown("**💡 Exemplos**")
    examples = [
        "Crie sourcing para CFO em fintech Série B no Brasil",
        "Build Boolean search for VP Engineering NYC",
        "Mapeie talentos para CHRO no varejo brasileiro",
        "Avalie fit deste candidato: [cole o perfil]",
        "Redija outreach LinkedIn para [nome] — vaga [cargo]",
        "Gere perguntas de entrevista para CEO em turnaround",
        "Onde os melhores CTOs de fintech no Brasil vêm?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True, key=example):
            st.session_state.pending_input = example
            st.rerun()

# ── Main chat area ─────────────────────────────────────────────────────────────

st.title("🎯 AI Executive Search Associate")
st.caption("Seu copiloto de IA para recrutamento executivo · Fale em português, English ou español")

# Init session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_input" not in st.session_state:
    st.session_state.pending_input = None

# Welcome message
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🎯"):
        st.markdown("""Olá! Sou seu **AI Executive Search Associate**.

Posso ajudar com todo o ciclo de recrutamento executivo:
sourcing, análise de candidatos, outreach, entrevistas, shortlists, benchmarking e muito mais.

**Como posso te ajudar hoje?**
Use os exemplos na barra lateral ou escreva sua própria solicitação. 👈""")

# Render chat history
for msg in st.session_state.messages:
    avatar = "🎯" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Handle sidebar example click
if st.session_state.pending_input:
    user_input = st.session_state.pending_input
    st.session_state.pending_input = None
else:
    user_input = st.chat_input("Digite sua solicitação... / Type your request...")

if user_input:
    # Validate API key
    if not api_key:
        st.warning("⚠️ Insira sua Anthropic API Key na barra lateral para continuar.")
        st.stop()

    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run agent
    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Analisando..."):
            try:
                response_text = run_agent(
                    user_input,
                    st.session_state.history,
                    api_key,
                )
                st.markdown(response_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                })
                # Keep history for context (store as simple text to avoid serialization issues)
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": response_text})

            except anthropic.AuthenticationError:
                st.error("❌ API Key inválida. Verifique a chave inserida na barra lateral.")
            except anthropic.RateLimitError:
                st.warning("⚠️ Rate limit atingido. Aguarde alguns instantes e tente novamente.")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
