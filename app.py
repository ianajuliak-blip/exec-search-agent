"""
AI Executive Search Associate — Interface Web (Streamlit)
Execute com: streamlit run app.py
"""

import uuid
import streamlit as st
import anthropic
from tools import TOOLS, execute_tool

try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

MODEL = "claude-haiku-4-5"
MAX_ITERATIONS = 20

SYSTEM_PROMPT = """Você é um Executive Search Associate de elite — um copiloto de IA para recrutamento executivo e talent strategy.

Você atua como um consultor sênior de executive search, combinando inteligência de mercado, análise estratégica de talentos e expertise em recrutamento de liderança para empresas de todos os estágios.

🌐 IDIOMAS: Você é fluente em Português, Inglês e Espanhol.
REGRA CRÍTICA: Sempre responda no mesmo idioma que o usuário está utilizando.

💡 PRINCÍPIOS:
• Seja direto, estratégico e orientado a dados
• Use as ferramentas disponíveis para entregar análises completas
• Forneça recomendações claras e acionáveis
• Seja honesto sobre riscos e gaps — não apenas pontos positivos"""

# ── Category quick-start prompts ──────────────────────────────────────────────

CATEGORIES = {
    "🔍 Montar Busca": {
        "color": "#1e88e5",
        "tasks": [
            ("Estratégia de Sourcing", "Crie uma estratégia completa de sourcing para a vaga de [CARGO] na empresa [EMPRESA], segmento [SETOR]. Inclua perfil ideal, empresas-alvo e canais de busca."),
            ("Boolean Search", "Construa strings de busca Boolean para LinkedIn Recruiter e Google X-Ray para a vaga de [CARGO] em [LOCALIDADE]. Empresas-alvo: [EMPRESAS]."),
            ("Mapa de Mercado", "Mapeie o mercado de talentos para [CARGO] no setor de [SETOR] no Brasil. Quero saber as principais empresas formadoras e pools de talentos."),
        ],
    },
    "👤 Avaliar Perfil": {
        "color": "#43a047",
        "tasks": [
            ("Analisar CV", "Analise o perfil/CV abaixo e extraia as informações estruturadas de carreira:\n\n[COLE O CV AQUI]"),
            ("Avaliar Fit", "Avalie o fit deste candidato para a vaga:\n\nCANDIDATO: [PERFIL DO CANDIDATO]\n\nVAGA: [DESCRIÇÃO DA VAGA]\n\nREQUISITOS OBRIGATÓRIOS: [LISTE AQUI]"),
            ("Scorecard", "Gere um scorecard de competências para [NOME DO CANDIDATO] para a vaga de [CARGO].\n\nPerfil: [RESUMO DO PERFIL]\n\nCompetências a avaliar: liderança, visão estratégica, execução, relacionamento, expertise técnica."),
        ],
    },
    "📩 Outreach": {
        "color": "#fb8c00",
        "tasks": [
            ("LinkedIn InMail", "Redija uma mensagem de outreach no LinkedIn para:\n- Candidato: [NOME], atualmente [CARGO ATUAL] na [EMPRESA ATUAL]\n- Vaga: [CARGO] na [EMPRESA CONTRATANTE]\n- Diferenciais: [LISTE OS ATRATIVOS DA VAGA]"),
            ("Mensagem Personalizada", "Crie uma mensagem de outreach hiper-personalizada para [NOME]. Perfil completo:\n\n[COLE O PERFIL AQUI]\n\nVaga: [CARGO] na [EMPRESA]. Conecte a experiência específica dele/dela com a oportunidade."),
            ("Sequência de Follow-up", "Crie uma sequência de 3 mensagens de follow-up para [NOME] que não respondeu ao primeiro contato sobre a vaga de [CARGO]. Canal: [LinkedIn/Email]."),
        ],
    },
    "🎙 Entrevista": {
        "color": "#8e24aa",
        "tasks": [
            ("Perguntas de Entrevista", "Gere perguntas de entrevista para um candidato a [CARGO].\nBackground: [RESUMO DO CANDIDATO]\nFoque em: [COMPETÊNCIAS A AVALIAR]\nEstágio: [screening/primeira rodada/final]"),
            ("Estratégia de Entrevista", "Crie uma estratégia de entrevista de [DURAÇÃO] minutos para [CARGO].\nCandidato: [RESUMO]\nEstágio: [ESTÁGIO]\nRed flags a investigar: [LISTE AQUI]"),
            ("Resumo de Entrevista", "Converta estas notas de entrevista em um resumo profissional para o cliente:\n\nCandidato: [NOME] | Vaga: [CARGO]\n\nNotas: [COLE AS NOTAS AQUI]"),
        ],
    },
    "📋 Shortlist": {
        "color": "#e53935",
        "tasks": [
            ("Criar Shortlist", "Gere um shortlist comparativo para a vaga de [CARGO] na [EMPRESA] com estes candidatos:\n\n1. [NOME] - [PERFIL RESUMIDO] - Fit: [SCORE] - Remuneração: [VALOR]\n2. [NOME] - [PERFIL RESUMIDO] - Fit: [SCORE] - Remuneração: [VALOR]\n3. [NOME] - [PERFIL RESUMIDO] - Fit: [SCORE] - Remuneração: [VALOR]"),
            ("Benchmarking de Remuneração", "Faça um benchmarking de remuneração para [CARGO] em [MERCADO/SETOR].\nCandidatos:\n- [NOME]: base R$[X]k, bônus [Y]%, [EQUITY]\n- [NOME]: base R$[X]k, bônus [Y]%, [EQUITY]\nBudget da empresa: [RANGE]"),
        ],
    },
    "💡 Inteligência": {
        "color": "#00897b",
        "tasks": [
            ("Mapeamento de Talentos", "Onde os melhores candidatos para [CARGO] em [SETOR] no Brasil costumam vir? Quais são as empresas formadoras mais importantes?"),
            ("Tendências de Mercado", "Quais são as principais tendências de contratação para [CARGO/FUNÇÃO] em [SETOR] atualmente? Como está a competitividade do mercado?"),
            ("Brief de Vaga", "Construa um brief completo para esta vaga:\nEmpresa: [NOME] ([SETOR], [ESTÁGIO], [Nº] funcionários)\nVaga: [CARGO]\nReporta para: [CARGO]\nObjetivos: [LISTE]\nBudget: [RANGE]\nUrgência: [PRAZO]"),
        ],
    },
}


# ── PDF extraction ─────────────────────────────────────────────────────────────

def extract_pdf_text(file) -> str:
    if not PDF_AVAILABLE:
        return ""
    reader = pypdf.PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


# ── Agent ──────────────────────────────────────────────────────────────────────

def run_agent_streaming(user_message: str, history: list[dict], api_key: str, placeholder) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    messages = history + [{"role": "user", "content": user_message}]
    full_text = ""

    for _ in range(MAX_ITERATIONS):
        current_text = ""

        with client.messages.stream(
            model=MODEL,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for delta in stream.text_stream:
                current_text += delta
                placeholder.markdown(full_text + current_text + "▌")
            final = stream.get_final_message()

        messages.append({"role": "assistant", "content": final.content})
        full_text += current_text

        if final.stop_reason == "end_turn":
            placeholder.markdown(full_text)
            return full_text

        if final.stop_reason == "pause_turn":
            continue

        if final.stop_reason == "tool_use":
            tool_results = []
            for block in final.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    label = block.name.replace("_", " ").title()
                    placeholder.markdown(full_text + f"\n\n*⚙️ {label}...*")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

    placeholder.markdown(full_text or "⚠️ O agente atingiu o limite de iterações.")
    return full_text


# ── Session state init ─────────────────────────────────────────────────────────

def init_state():
    if "projects" not in st.session_state:
        default_id = str(uuid.uuid4())
        st.session_state.projects = {
            default_id: {"name": "Projeto 1", "messages": [], "history": []}
        }
        st.session_state.current_project = default_id

    if "pending_input" not in st.session_state:
        st.session_state.pending_input = None
    if "show_category" not in st.session_state:
        st.session_state.show_category = None
    if "renaming" not in st.session_state:
        st.session_state.renaming = None


def current_project() -> dict:
    return st.session_state.projects[st.session_state.current_project]


# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Executive Search Associate",
    page_icon="🎯",
    layout="wide",
)

init_state()

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 Executive Search AI")
    st.caption("Powered by Claude · Haiku")

    st.divider()

    # API Key
    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Obtenha em console.anthropic.com",
    )

    st.divider()

    # ── Projects ──────────────────────────────────────────────────────────────
    st.markdown("**📁 Projetos**")

    if st.button("＋ Novo Projeto", use_container_width=True):
        new_id = str(uuid.uuid4())
        n = len(st.session_state.projects) + 1
        st.session_state.projects[new_id] = {
            "name": f"Projeto {n}",
            "messages": [],
            "history": [],
        }
        st.session_state.current_project = new_id
        st.rerun()

    for pid, proj in list(st.session_state.projects.items()):
        is_active = pid == st.session_state.current_project
        cols = st.columns([5, 1])

        # Rename mode
        if st.session_state.renaming == pid:
            new_name = st.text_input(
                "Renomear",
                value=proj["name"],
                key=f"rename_{pid}",
                label_visibility="collapsed",
            )
            if st.button("✓", key=f"confirm_{pid}"):
                st.session_state.projects[pid]["name"] = new_name
                st.session_state.renaming = None
                st.rerun()
        else:
            label = ("🔵 " if is_active else "○ ") + proj["name"]
            if cols[0].button(label, key=f"proj_{pid}", use_container_width=True):
                st.session_state.current_project = pid
                st.rerun()
            if cols[1].button("✏️", key=f"edit_{pid}"):
                st.session_state.renaming = pid
                st.rerun()

    # Delete current project (only if more than 1 exists)
    if len(st.session_state.projects) > 1:
        if st.button("🗑 Excluir projeto atual", use_container_width=True):
            del st.session_state.projects[st.session_state.current_project]
            st.session_state.current_project = list(st.session_state.projects.keys())[0]
            st.rerun()

    st.divider()

    # Clear current chat
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        current_project()["messages"] = []
        current_project()["history"] = []
        st.session_state.show_category = None
        st.rerun()

    st.divider()

    # ── PDF Upload ────────────────────────────────────────────────────────────
    st.markdown("**📎 Enviar Arquivo**")
    uploaded_file = st.file_uploader(
        "PDF ou TXT",
        type=["pdf", "txt"],
        label_visibility="collapsed",
        help="Envie um CV, perfil LinkedIn (PDF) ou qualquer documento de texto",
    )
    if uploaded_file:
        if st.button("📄 Analisar arquivo", use_container_width=True):
            if uploaded_file.type == "application/pdf":
                if PDF_AVAILABLE:
                    text = extract_pdf_text(uploaded_file)
                    if text:
                        st.session_state.pending_input = f"Analise este perfil/CV:\n\n{text}"
                    else:
                        st.warning("Não consegui extrair texto do PDF. Tente um PDF não-escaneado.")
                else:
                    st.warning("pypdf não instalado. Adicione 'pypdf' ao requirements.txt.")
            else:
                text = uploaded_file.read().decode("utf-8", errors="ignore")
                st.session_state.pending_input = f"Analise este perfil/CV:\n\n{text}"
            st.rerun()


# ── Main area ──────────────────────────────────────────────────────────────────

proj = current_project()

st.markdown(f"## 🎯 {proj['name']}")
st.caption("AI Executive Search Associate · Fale em português, English ou español")

# ── Category buttons ───────────────────────────────────────────────────────────

cat_cols = st.columns(len(CATEGORIES))
for i, (cat_name, cat_data) in enumerate(CATEGORIES.items()):
    if cat_cols[i].button(cat_name, use_container_width=True, key=f"cat_{i}"):
        if st.session_state.show_category == cat_name:
            st.session_state.show_category = None
        else:
            st.session_state.show_category = cat_name
        st.rerun()

# ── Category task panel ────────────────────────────────────────────────────────

if st.session_state.show_category:
    cat = CATEGORIES[st.session_state.show_category]
    with st.container(border=True):
        st.markdown(f"**{st.session_state.show_category}** — escolha uma tarefa:")
        task_cols = st.columns(len(cat["tasks"]))
        for i, (task_name, task_prompt) in enumerate(cat["tasks"]):
            if task_cols[i].button(f"▶ {task_name}", use_container_width=True, key=f"task_{i}"):
                st.session_state.pending_input = task_prompt
                st.session_state.show_category = None
                st.rerun()

st.divider()

# ── Chat messages ──────────────────────────────────────────────────────────────

if not proj["messages"]:
    with st.chat_message("assistant", avatar="🎯"):
        st.markdown(f"""Olá! Sou seu **AI Executive Search Associate** para o projeto **{proj['name']}**.

Use os botões acima para acesso rápido por categoria, ou escreva diretamente.
Também pode enviar um **PDF de CV** pela barra lateral 👈

**Como posso ajudar hoje?**""")

for msg in proj["messages"]:
    avatar = "🎯" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ──────────────────────────────────────────────────────────────────────

if st.session_state.pending_input:
    user_input = st.session_state.pending_input
    st.session_state.pending_input = None
else:
    user_input = st.chat_input("Digite sua solicitação ou use os botões acima...")

if user_input:
    if not api_key:
        st.warning("⚠️ Insira sua Anthropic API Key na barra lateral.")
        st.stop()

    with st.chat_message("user", avatar="👤"):
        # For long template prompts, show a preview
        display = user_input if len(user_input) < 300 else user_input[:300] + "..."
        st.markdown(display)
    proj["messages"].append({"role": "user", "content": user_input})

    with st.chat_message("assistant", avatar="🎯"):
        placeholder = st.empty()
        placeholder.markdown("▌")
        try:
            response_text = run_agent_streaming(
                user_input,
                proj["history"],
                api_key,
                placeholder,
            )
            proj["messages"].append({"role": "assistant", "content": response_text})
            proj["history"].append({"role": "user", "content": user_input})
            proj["history"].append({"role": "assistant", "content": response_text})

        except anthropic.AuthenticationError:
            placeholder.error("❌ API Key inválida. Verifique na barra lateral.")
        except anthropic.RateLimitError:
            placeholder.warning("⚠️ Rate limit atingido. Aguarde e tente novamente.")
        except Exception as e:
            placeholder.error(f"❌ Erro: {e}")
