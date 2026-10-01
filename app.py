import streamlit as st
from typesafe_sdk import TypeSafeError

from jev import EXAMPLES, Analysis, analyze


def set_message(text: str = "") -> None:
    st.session_state.message = text
    st.session_state.result = None


def show_result(result: Analysis) -> None:
    st.space("large")
    who = "A person should step in." if result.human_attention else "No one needs to step in."
    st.header(f"{result.urgency_label}.", anchor=False, text_alignment="center")
    st.markdown(f":gray[A {result.category.lower()} message. {who}]", text_alignment="center")
    with st.container(horizontal=True):
        st.metric("Category", result.category, border=True,
                  delta_description=f"{result.category_confidence:.0%} confidence")
        st.metric("Urgency", f"{result.urgency:g} / 10", border=True,
                  delta_description=f"{result.urgency_confidence:.0%} confidence")
        st.metric("Human attention", "Yes" if result.human_attention else "No", border=True,
                  delta_description=f"{result.human_attention_confidence:.0%} confidence")


st.set_page_config(page_title="Jev Inbox")
st.session_state.setdefault("result", None)

st.space("large")
st.caption("Jev Inbox · a tiny experiment", text_alignment="center")
st.title("Paste a message. Get three decisions.", anchor=False, text_alignment="center")
st.markdown(":gray[Category, urgency, and whether a person should step in.]", text_alignment="center")
st.space("medium")

with st.container(border=True):
    message = st.text_area("Message", key="message", height=120,
                           placeholder="Type or paste a customer message…")
    with st.container(horizontal=True, vertical_alignment="center"):
        st.button("Clear", type="tertiary", on_click=set_message)
        st.space("stretch")
        analyze_clicked = st.button("Analyze", type="primary")

st.caption("Or try an example", text_alignment="center")
with st.container(horizontal=True, horizontal_alignment="center"):
    for label, text in EXAMPLES.items():
        st.button(label, on_click=set_message, args=(text,))

if analyze_clicked:
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        try:
            with st.spinner("Asking Jev..."):
                st.session_state.result = analyze(message)
        except TypeSafeError as error:
            st.error(f"Jev could not analyze this message: {error}")

if st.session_state.result:
    show_result(st.session_state.result)
