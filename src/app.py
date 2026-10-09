"""The one screen: a question box and a button. Run with: streamlit run src/app.py"""
import streamlit as st

from course_material import COURSE_NAMES
from llm import get_chat_model
from screen import ask, markdown_safe
from tutor import OUT_OF_SCOPE

OUT_OF_SCOPE_MESSAGE = (
    "This question is outside the four Courses (GAIF, PEID, AITB, DTGS), so the Course Tutor cannot answer it. "
    "Try a question about one of those Courses."
)
RETRY_MESSAGE = "Something went wrong while preparing your answer. Please try again in a moment."

st.set_page_config(page_title="Course Tutor")
st.title("Course Tutor")
st.caption("Ask a question about GAIF, PEID, AITB or DTGS. Answers come only from the Course Material and cite its Sections.")

question = st.text_area("Your question")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        result = ask(question.strip(), get_chat_model)

    if result is None or result.error:
        st.info(RETRY_MESSAGE, icon=":material/refresh:")
    elif result.course == OUT_OF_SCOPE:
        st.markdown("**Course:** Out of scope")
        st.markdown(f"**Why:** “{markdown_safe(result.evidence)}”")
        st.info(OUT_OF_SCOPE_MESSAGE, icon=":material/explore_off:")
    else:
        st.markdown(f"**Course:** {result.course} ({COURSE_NAMES.get(result.course, result.course)})")
        st.markdown(f"**Why this Course:** “{markdown_safe(result.evidence)}”")
        if result.is_refusal:
            st.warning(f"**Refusal.** {markdown_safe(result.answer.strip())}", icon=":material/block:")
        else:
            st.markdown("**Answer**")
            st.markdown(markdown_safe(result.answer))
            if result.citations:
                st.caption("Cited Sections: " + ", ".join(result.citations))
            if result.invalid_citations:
                st.warning(
                    f"These cited Sections are not Sections of the {result.course} Course Material: "
                    + ", ".join(result.invalid_citations),
                    icon=":material/warning:",
                )
