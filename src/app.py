"""The one screen: a question box and a button. Run with: streamlit run src/app.py

`TUTOR` in .env chooses the tutor: `routed` (default) or `agentic`.
"""
import streamlit as st
from dotenv import load_dotenv

from course_material import COURSE_NAMES
from llm import get_chat_model
from screen import ask, markdown_safe, tutor_setting
from tutor import AGENTIC_TUTOR, OUT_OF_SCOPE

OUT_OF_SCOPE_MESSAGE = (
    "This question is outside the four Courses (GAIF, PEID, AITB, DTGS), so the Course Tutor cannot answer it. "
    "Try a question about one of those Courses."
)
RETRY_MESSAGE = "Something went wrong while preparing your answer. Please try again in a moment."
REFUSAL_MESSAGE = "The Course Material does not cover this question, so there is no answer to show."

load_dotenv()
TUTOR = tutor_setting()

st.set_page_config(page_title="Course Tutor")
st.title("Course Tutor")
st.caption("Ask a question about GAIF, PEID, AITB or DTGS. Answers come only from the Course Material and cite its Sections.")

question = st.text_area("Your question")


def course_label(code: str) -> str:
    return f"{code} ({COURSE_NAMES.get(code, code)})"


if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        result = ask(question.strip(), get_chat_model, tutor=TUTOR)

    if result is None or result.error:
        st.info(RETRY_MESSAGE, icon=":material/refresh:")
    elif result.course == OUT_OF_SCOPE:
        st.markdown("**Course:** Out of scope")
        if result.evidence:
            st.markdown(f"**Why:** “{markdown_safe(result.evidence)}”")
        st.info(OUT_OF_SCOPE_MESSAGE, icon=":material/explore_off:")
    elif result.is_refusal:
        # No answer from the Course Material, so no Course is named: the Refusal stands alone.
        st.warning(f"**Refusal.** {REFUSAL_MESSAGE}", icon=":material/block:")
    else:
        if result.tutor == AGENTIC_TUTOR:
            read = ", ".join(course_label(c) for c in dict.fromkeys(result.materials_read)) or "none"
            st.markdown(f"**Course Materials read:** {read}")
        else:
            st.markdown(f"**Course:** {course_label(result.course)}")
            st.markdown(f"**Why this Course:** “{markdown_safe(result.evidence)}”")
        st.markdown("**Answer**")
        st.markdown(markdown_safe(result.answer))
        if result.citations:
            st.caption("Cited Sections: " + ", ".join(result.citations))
        if result.invalid_citations:
            st.warning(
                "These cited Sections are not Sections of the Course Material read: "
                + ", ".join(result.invalid_citations),
                icon=":material/warning:",
            )
