"""The one screen: a question box and a button. Run with: streamlit run src/app.py"""
import streamlit as st

from course_material import COURSE_NAMES
from llm import get_chat_model
from tutor import OUT_OF_SCOPE, answer_question

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
        model = get_chat_model()
        try:
            result = answer_question(question.strip(), model)
        except Exception:
            result = None

    if result is None or result.error:
        st.info(RETRY_MESSAGE, icon=":material/refresh:")
    elif result.course == OUT_OF_SCOPE:
        st.markdown("**Course:** Out of scope")
        st.markdown(f"**Why:** “{result.evidence}”")
        st.info(OUT_OF_SCOPE_MESSAGE, icon=":material/explore_off:")
    else:
        st.markdown(f"**Course:** {result.course} ({COURSE_NAMES.get(result.course, result.course)})")
        st.markdown(f"**Why this Course:** “{result.evidence}”")
        if result.is_refusal:
            st.warning(f"**Refusal.** {result.answer.strip()}", icon=":material/block:")
        else:
            st.markdown("**Answer**")
            st.markdown(result.answer)
            if result.citations:
                st.caption("Cited Sections: " + ", ".join(result.citations))
            if result.invalid_citations:
                st.warning(
                    "These cited Sections do not exist in the Course Material: "
                    + ", ".join(result.invalid_citations),
                    icon=":material/warning:",
                )
