"""ProntoClin - copiloto de documentação médica.

Execute com:
    streamlit run main.py

Dependências:
    pip install streamlit openai
"""

import base64
import io
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import streamlit as st
from openai import OpenAI


st.set_page_config(
    page_title="ProntoClin | Documentação médica",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


SOAP_EXAMPLE = """S — Subjetivo
Paciente relata dor lombar há 5 dias, de início gradual, sem irradiação para membros inferiores. Refere piora ao permanecer sentado por longos períodos. Nega febre, trauma recente ou alterações esfincterianas.

O — Objetivo
Dados objetivos não identificados na transcrição. Realizar exame físico direcionado e registrar sinais vitais.

A — Avaliação
1. Lombalgia aguda inespecífica — CID-10: M54.5

P — Plano / Conduta
• Realizar exame físico completo, com avaliação neurológica e musculoesquelética.
• Orientar medidas posturais e evitar repouso prolongado.
• Considerar analgesia conforme avaliação clínica e contraindicações.
• Retorno se houver piora, déficit neurológico, febre ou alterações esfincterianas."""


def logo_data_uri() -> str:
   def logo_data_uri() -> str:
    """Return an empty string if no logo is provided."""
    return ""


def inject_styles() -> None:
    """Apply the visual system without changing Streamlit's functionality."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {
            --pc-navy: #0F172A;
            --pc-blue: #2563EB;
            --pc-blue-dark: #1D4ED8;
            --pc-blue-soft: #EFF6FF;
            --pc-bg: #F8FAFC;
            --pc-muted: #64748B;
            --pc-border: #E2E8F0;
            --pc-green: #0F766E;
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .stApp {
            background: var(--pc-bg);
            color: var(--pc-navy);
        }

        .block-container {
            max-width: 1440px;
            padding: 0 3.5rem 3.5rem;
        }

        header[data-testid="stHeader"] {
            background: var(--pc-navy);
        }

        .pc-topbar {
            margin: 0 -3.5rem 3rem;
            padding: 1.25rem 3.5rem;
            background: var(--pc-navy);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }

        .pc-brand {
            display: flex;
            align-items: center;
            gap: .75rem;
        }

        .pc-brand-mark {
            width: 2.25rem;
            height: 2.25rem;
            display: grid;
            place-items: center;
            border-radius: .75rem;
            background: var(--pc-blue);
            color: #fff;
            font-size: 1.1rem;
            font-weight: 700;
        }

        .pc-brand-logo {
            width: 2.25rem;
            height: 2.25rem;
            flex: 0 0 auto;
            object-fit: cover;
            border-radius: .75rem;
        }

        .pc-brand-name {
            font-family: 'Manrope', sans-serif;
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -.02em;
        }

        .pc-nav-brand {
            display: flex;
            align-items: center;
            gap: .7rem;
            color: var(--pc-navy);
            font-size: 1.05rem;
        }

        .pc-nav-brand .pc-brand-logo {
            width: 2.15rem;
            height: 2.15rem;
            border-radius: .65rem;
        }

        .pc-nav-links {
            display: flex;
            justify-content: center;
            gap: 1.65rem;
            color: var(--pc-muted);
            font-size: .82rem;
        }

        .pc-nav-links span {
            white-space: nowrap;
        }

        .pc-nav-active {
            color: var(--pc-blue);
            font-weight: 700;
        }

        .pc-landing-hero {
            max-width: 58rem;
            padding: 5.5rem 0 2.2rem;
        }

        .pc-landing-title {
            max-width: 53rem;
            margin: 0;
            color: var(--pc-navy);
            font-family: 'Manrope', sans-serif;
            font-size: clamp(2.35rem, 5vw, 4.8rem);
            line-height: 1.03;
            letter-spacing: -.065em;
        }

        .pc-landing-title span {
            color: var(--pc-blue);
        }

        .pc-landing-copy {
            max-width: 43rem;
            margin: 1.5rem 0 0;
            color: var(--pc-muted);
            font-size: 1.08rem;
            line-height: 1.7;
        }

        .pc-trust-line {
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            margin-top: 1.3rem;
            color: var(--pc-muted);
            font-size: .82rem;
        }

        .pc-trust-dot {
            width: .5rem;
            height: .5rem;
            border-radius: 50%;
            background: #14B8A6;
            box-shadow: 0 0 0 .25rem #CCFBF1;
        }

        .pc-lead-box {
            padding: 1.4rem;
            border: 1px solid var(--pc-border);
            border-radius: 1rem;
            background: #fff;
            box-shadow: 0 14px 40px rgba(15, 23, 42, .06);
        }

        .pc-lead-title {
            margin: 0;
            color: var(--pc-navy);
            font-family: 'Manrope', sans-serif;
            font-size: 1rem;
            font-weight: 800;
        }

        .pc-lead-copy {
            margin: .35rem 0 1rem;
            color: var(--pc-muted);
            font-size: .82rem;
            line-height: 1.45;
        }

        .pc-metric-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-top: 4.5rem;
            padding-top: 1.4rem;
            border-top: 1px solid var(--pc-border);
        }

        .pc-metric {
            display: grid;
            gap: .25rem;
            padding: .75rem 1rem .75rem 0;
            border-right: 1px solid var(--pc-border);
        }

        .pc-metric:last-child {
            border-right: 0;
        }

        .pc-metric strong {
            color: var(--pc-navy);
            font-family: 'Manrope', sans-serif;
            font-size: 1.4rem;
        }

        .pc-metric span {
            color: var(--pc-muted);
            font-size: .78rem;
            line-height: 1.35;
        }

        .pc-landing-footer {
            margin-top: 5rem;
            color: #94A3B8;
            font-size: .76rem;
        }

        .pc-landing-footer span {
            color: var(--pc-navy);
            font-weight: 700;
        }

        .pc-platform-heading {
            padding: 3.5rem 0 1.75rem;
        }

        .pc-whatsapp {
            display: block;
            margin-top: .75rem;
            padding: .85rem 1rem;
            border-radius: .75rem;
            background: #DCFCE7;
            color: #166534 !important;
            font-size: .82rem;
            font-weight: 700;
            text-align: center;
            text-decoration: none !important;
        }

        .pc-whatsapp:hover {
            background: #BBF7D0;
        }

        .pc-secure {
            color: #CBD5E1;
            font-size: .82rem;
            display: flex;
            align-items: center;
            gap: .45rem;
        }

        .pc-hero {
            margin-bottom: 2rem;
        }

        .pc-eyebrow {
            color: var(--pc-blue);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .12em;
            font-size: .72rem;
            margin-bottom: .65rem;
        }

        .pc-title {
            font-family: 'Manrope', sans-serif;
            color: var(--pc-navy);
            font-size: clamp(2rem, 3.6vw, 3.35rem);
            line-height: 1.06;
            letter-spacing: -.05em;
            margin: 0 0 .75rem;
        }

        .pc-subtitle {
            color: var(--pc-muted);
            font-size: 1.05rem;
            max-width: 45rem;
            line-height: 1.6;
            margin: 0;
        }

        .pc-panel {
            background: #fff;
            border: 1px solid var(--pc-border);
            border-radius: 1.25rem;
            padding: 1.5rem;
            min-height: 32rem;
            box-shadow: 0 14px 40px rgba(15, 23, 42, .05);
        }

        .pc-panel-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.35rem;
        }

        .pc-panel-title {
            font-family: 'Manrope', sans-serif;
            color: var(--pc-navy);
            font-size: 1.1rem;
            font-weight: 800;
            margin: 0;
        }

        .pc-panel-copy {
            color: var(--pc-muted);
            font-size: .86rem;
            line-height: 1.45;
            margin: .35rem 0 0;
        }

        .pc-step {
            display: grid;
            place-items: center;
            flex: 0 0 auto;
            width: 2rem;
            height: 2rem;
            border-radius: .7rem;
            color: var(--pc-blue);
            background: var(--pc-blue-soft);
            font-size: .8rem;
            font-weight: 800;
        }

        [data-testid="stFileUploader"] {
            background: var(--pc-blue-soft);
            border: 1px dashed #93C5FD;
            border-radius: .9rem;
            padding: .35rem;
        }

        [data-testid="stFileUploader"] section {
            padding: 1.5rem 1rem;
        }

        [data-testid="stFileUploader"] small {
            color: var(--pc-muted);
        }

        .pc-note {
            display: flex;
            gap: .65rem;
            align-items: flex-start;
            color: var(--pc-muted);
            font-size: .78rem;
            line-height: 1.45;
            padding: 1rem;
            margin-top: 1rem;
            border-radius: .75rem;
            background: #F8FAFC;
        }

        .pc-note strong {
            color: var(--pc-navy);
        }

        .stButton > button {
            width: 100%;
            min-height: 3.25rem;
            margin-top: .5rem;
            border: 0;
            border-radius: .75rem;
            background: var(--pc-blue);
            color: #fff;
            font-weight: 700;
            box-shadow: 0 8px 20px rgba(37, 99, 235, .18);
            transition: background .2s ease, transform .2s ease, box-shadow .2s ease;
        }

        .stButton > button:hover {
            background: var(--pc-blue-dark);
            box-shadow: 0 12px 24px rgba(37, 99, 235, .25);
            transform: translateY(-1px);
        }

        .stTextArea textarea {
            min-height: 25rem;
            border: 1px solid var(--pc-border);
            border-radius: .75rem;
            background: #FCFDFE;
            color: var(--pc-navy);
            font-size: .9rem;
            line-height: 1.6;
            padding: 1rem;
        }

        .pc-status {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            border: 1px solid #BBF7D0;
            background: #F0FDF4;
            color: var(--pc-green);
            border-radius: 99px;
            font-size: .72rem;
            font-weight: 700;
            padding: .35rem .6rem;
            white-space: nowrap;
        }

        .pc-footer {
            color: #94A3B8;
            font-size: .75rem;
            margin-top: 1.25rem;
            text-align: center;
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 0 1rem 2rem;
            }

            .pc-topbar {
                margin: 0 -1rem 2rem;
                padding: 1rem;
            }

            .pc-secure {
                display: none;
            }

            .pc-panel {
                min-height: auto;
                padding: 1.1rem;
            }

            .pc-nav-links {
                display: none;
            }

            .pc-landing-hero {
                padding: 3.25rem 0 1.5rem;
            }

            .pc-metric-grid {
                grid-template-columns: 1fr;
                margin-top: 2.5rem;
            }

            .pc-metric {
                border-right: 0;
                border-bottom: 1px solid var(--pc-border);
            }

            .pc-metric:last-child {
                border-bottom: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def openai_client() -> OpenAI:
    """Create the official OpenAI client using only the environment secret."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "A variável de ambiente OPENAI_API_KEY não está configurada. "
            "Adicione-a antes de processar uma consulta."
        )
    return OpenAI(api_key=api_key)


def transcribe_audio(uploaded_file) -> str:
    """Send the uploaded audio to OpenAI Whisper without writing it to disk."""
    client = openai_client()
    audio_stream = io.BytesIO(uploaded_file.getvalue())
    audio_stream.name = uploaded_file.name
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_stream,
        response_format="text",
    )
    return str(transcription).strip()


def generate_documentation(transcription: str) -> tuple[str, str]:
    """Generate the official SOAP note and a separate patient-friendly summary."""
    client = openai_client()
    soap_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um copiloto de documentação médica. Organize a "
                    "transcrição em uma nota clínica estritamente no formato SOAP, "
                    "em português do Brasil. Use exatamente estas quatro seções e "
                    "nesta ordem: S — Subjetivo, O — Objetivo, A — Avaliação e "
                    "P — Plano / Conduta. Na seção A, inclua diagnóstico ou "
                    "hipótese e CID-10 apenas quando houver suporte na transcrição. "
                    "Não invente dados; escreva 'Não informado na transcrição' "
                    "quando necessário. Use linguagem clínica objetiva e não "
                    "inclua introdução, conclusão ou seções adicionais."
                ),
            },
            {"role": "user", "content": f"Transcrição:\n\n{transcription}"},
        ],
    )
    soap_note = soap_response.choices[0].message.content
    if not soap_note:
        raise RuntimeError("A OpenAI não retornou o prontuário SOAP.")

    patient_response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.35,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você transforma uma consulta médica em orientações de "
                    "pós-consulta para o paciente, em português do Brasil. Escreva "
                    "de forma acolhedora, simples e objetiva, sem jargões. Use "
                    "somente informações presentes na transcrição: resumo do que "
                    "foi conversado, cuidados e próximos passos mencionados pelo "
                    "médico. Não invente diagnóstico, prescrição, dose, prazo ou "
                    "sinal de alarme. Não substitua a orientação médica. Organize "
                    "com títulos curtos e listas quando ajudar."
                ),
            },
            {"role": "user", "content": f"Transcrição:\n\n{transcription}"},
        ],
    )
    patient_guidance = patient_response.choices[0].message.content
    if not patient_guidance:
        raise RuntimeError("A OpenAI não retornou as orientações ao paciente.")

    return soap_note.strip(), patient_guidance.strip()


def normalize_phone(phone: str) -> str:
    """Normalize Brazilian phone input to the international WhatsApp format."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("00"):
        digits = digits[2:]
    if digits and not digits.startswith("55"):
        digits = f"55{digits}"
    return digits


def whatsapp_url(phone: str, message: str) -> Optional[str]:
    normalized = normalize_phone(phone)
    if not normalized:
        return None
    return f"https://api.whatsapp.com/send?phone={normalized}&text={quote(message)}"


def render_top_nav(platform: bool = False) -> None:
    logo_uri = logo_data_uri()
    left, middle, right = st.columns([1.2, 2.2, 1.05])
    with left:
        st.markdown(
            f"""
            <div class="pc-nav-brand">
                <img class="pc-brand-logo" src="{logo_uri}" alt="Logo ProntoClin">
                <strong>ProntoClin</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with middle:
        if platform:
            st.markdown(
                '<div class="pc-nav-links"><span class="pc-nav-active">Workspace Médico</span>'
                '<span>Histórico</span><span>Preferências</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="pc-nav-links"><span>Como funciona</span><span>Benefícios</span>'
                '<span>Para médicos</span></div>',
                unsafe_allow_html=True,
            )
    with right:
        if platform:
            if st.button("Página inicial", key="nav_home", use_container_width=True):
                st.session_state["screen"] = "landing"
                st.rerun()
        elif st.button("Acessar plataforma", key="nav_platform", use_container_width=True):
            st.session_state["screen"] = "platform"
            st.rerun()


def render_landing_page() -> None:
    render_top_nav()
    st.markdown(
        """
        <div class="pc-landing-hero">
            <div class="pc-eyebrow">AI MEDICAL CLINICAL COPILOT</div>
            <h1 class="pc-landing-title">Reduza o tempo de prontuário<br>
            e foque no atendimento <span>do seu paciente.</span></h1>
            <p class="pc-landing-copy">
                O ProntoClin transcreve suas consultas, gera notas SOAP precisas
                e prepara orientações pós-consulta em uma experiência simples,
                segura e sob seu controle.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_left, hero_right = st.columns([1.25, 0.75], gap="large")
    with hero_left:
        st.markdown(
            """
            <div class="pc-trust-line">
                <span class="pc-trust-dot"></span>
                Feito para profissionais que valorizam tempo e cuidado
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_right:
        st.markdown('<div class="pc-lead-box">', unsafe_allow_html=True)
        st.markdown(
            '<p class="pc-lead-title">Pronto para experimentar?</p>'
            '<p class="pc-lead-copy">Deixe seu contato para receber acesso antecipado.</p>',
            unsafe_allow_html=True,
        )
        lead_contact = st.text_input(
            "WhatsApp ou e-mail profissional",
            placeholder="voce@clinica.com.br",
            key="lead_contact",
            label_visibility="collapsed",
        )
        if st.button("Solicitar acesso antecipado", key="lead_submit", type="primary", use_container_width=True):
            if "@" in lead_contact or len(normalize_phone(lead_contact)) >= 12:
                st.success("Cadastro recebido. Em breve entraremos em contato.")
            else:
                st.warning("Informe um e-mail profissional ou WhatsApp válido.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="pc-metric-grid">
            <div class="pc-metric"><strong>Até 2h</strong><span>economizadas por dia em burocracia</span></div>
            <div class="pc-metric"><strong>100%</strong><span>sob controle do médico</span></div>
            <div class="pc-metric"><strong>SOAP</strong><span>pronto para revisar e usar</span></div>
        </div>
        <div class="pc-landing-footer">
            <span>ProntoClin</span> · documentação inteligente para uma medicina mais presente
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_platform_page() -> None:
    render_top_nav(platform=True)
    st.markdown(
        """
        <div class="pc-platform-heading">
            <div class="pc-eyebrow">Workspace médico</div>
            <h1 class="pc-title">Transforme a consulta em cuidado contínuo.</h1>
            <p class="pc-subtitle">Envie o áudio, revise a documentação e compartilhe orientações claras com o paciente.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_column, right_column = st.columns([0.86, 1.14], gap="large")
    with left_column:
        st.markdown('<div class="pc-panel">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="pc-panel-header">
                <div><p class="pc-panel-title">Entrada de dados</p>
                <p class="pc-panel-copy">O áudio é usado somente durante esta sessão.</p></div>
                <div class="pc-step">01</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Áudio da consulta",
            type=["mp3", "m4a", "wav"],
            key="platform_audio",
            help="Formatos aceitos: MP3, M4A e WAV. Limite recomendado: 25 MB.",
        )
        patient_phone = st.text_input(
            "WhatsApp do paciente (opcional)",
            placeholder="(11) 99999-9999",
            key="patient_phone",
        )
        if uploaded_file:
            size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.success(f"{uploaded_file.name} · {size_mb:.1f} MB")
        st.markdown(
            """
            <div class="pc-note"><span>◉</span><div><strong>Você mantém a decisão clínica.</strong><br>
            Revise cada sugestão antes de registrar ou compartilhar qualquer informação.</div></div>
            """,
            unsafe_allow_html=True,
        )
        process_clicked = st.button(
            "⚡ Processar Consulta",
            disabled=uploaded_file is None,
            type="primary",
            use_container_width=True,
            key="process_consultation",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_column:
        st.markdown('<div class="pc-panel">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="pc-panel-header">
                <div><p class="pc-panel-title">Resultados da consulta</p>
                <p class="pc-panel-copy">Duas saídas para dois momentos do cuidado.</p></div>
                <div class="pc-status">● Revisão médica</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if "soap_note" not in st.session_state:
            st.session_state["soap_note"] = ""
        if "patient_guidance" not in st.session_state:
            st.session_state["patient_guidance"] = ""
        st.text_area(
            "Prontuário Oficial SOAP",
            key="soap_note",
            height=330,
            placeholder="O prontuário SOAP aparecerá aqui após o processamento.",
        )
        st.text_area(
            "Orientações de Pós-Consulta para o Paciente",
            key="patient_guidance",
            height=240,
            placeholder="As orientações em linguagem simples aparecerão aqui após o processamento.",
        )
        if st.session_state["soap_note"]:
            combined_note = (
                "PRONTOCLIN · PRONTUÁRIO SOAP\n\n"
                f"{st.session_state['soap_note']}\n\n"
                "ORIENTAÇÕES DE PÓS-CONSULTA\n\n"
                f"{st.session_state['patient_guidance']}\n"
            )
            st.download_button(
                "Baixar documentação completa",
                data=combined_note,
                file_name="prontoclin-documentacao-consulta.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_documentation",
            )
            message = st.session_state["patient_guidance"]
            link = whatsapp_url(patient_phone, message)
            if link:
                st.markdown(
                    f'<a class="pc-whatsapp" href="{link}" target="_blank" rel="noopener noreferrer">'
                    "Abrir WhatsApp com orientações pré-preenchidas</a>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    if process_clicked and uploaded_file:
        with st.status("Processando consulta...", expanded=True) as status:
            try:
                status.write("Transcrevendo o áudio com Whisper...")
                transcription = transcribe_audio(uploaded_file)
                if not transcription:
                    raise RuntimeError("Não foi possível identificar fala no áudio enviado.")
                status.write("Gerando o prontuário SOAP...")
                soap_note, patient_guidance = generate_documentation(transcription)
                st.session_state["soap_note"] = soap_note
                st.session_state["patient_guidance"] = patient_guidance
                status.update(label="Documentação gerada com sucesso.", state="complete")
                st.rerun()
            except Exception as error:
                status.update(label="Não foi possível processar a consulta.", state="error")
                st.error(str(error))


def main() -> None:
    inject_styles()
    st.session_state.setdefault("screen", "landing")
    if st.session_state["screen"] == "platform":
        render_platform_page()
    else:
        render_landing_page()
    st.markdown(
        '<div class="pc-footer">ProntoClin é uma ferramenta de apoio à documentação. '
        "A decisão clínica e a revisão final são sempre do profissional de saúde.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
