"""The one screen: a question box and a button. Run with: streamlit run src/app.py"""
import streamlit as st

from course_material import COURSE_NAMES
from llm import get_chat_model
from tutor import answer_question

st.set_page_config(page_title="Course Tutor")
st.title("Course Tutor")
st.caption("Ask a question about GAIF, PEID, AITB or DTGS. Answers come only from the Course Material and cite its Sections.")

question = st.text_area("Your question")

if st.button("Ask") and question.strip():
    with st.spinner("Thinking..."):
        result = answer_question(question.strip(), get_chat_model())

    course_label = f"{result.course} ({COURSE_NAMES[result.course]})" if result.course in COURSE_NAMES else result.course
    st.markdown(f"**Course:** {course_label}")
    st.markdown(f"**Why this Course:** “{result.evidence}”")
    st.markdown("**Answer**")
    st.markdown(result.answer)
    if result.citations:
        st.caption("Cited Sections: " + ", ".join(result.citations))
