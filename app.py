import streamlit as st
import sys
import os

# Ensure src is in the path for internal imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.assistant import run_assistant

def main():
    st.set_page_config(page_title="GROUNDED Policy Assistant")

    st.markdown(
        """
        <style>
        .title-text {
            color: navy;
            font-family: sans-serif;
            font-weight: bold;
        }
        .evidence-box {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            background-color: #fafafa;
            color: #333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h1 class="title-text">GROUNDED</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="title-text" style="color: #444; font-size: 1.5rem;">Policy Answer Assistant</h2>', unsafe_allow_html=True)
    st.markdown("---")

    question = st.text_input("Ask a policy question")

    col1, col2 = st.columns(2)
    with col1:
        determination_date = st.text_input("Determination date", placeholder="YYYY-MM-DD (Optional)")
    with col2:
        change_date = st.text_input("Change-of-circumstance date", placeholder="YYYY-MM-DD (Optional)")

    if st.button("Ask Policy"):
        if not question.strip():
            st.warning("Please enter a policy question.")
            return

        with st.spinner("Searching policy..."):
            try:
                # Treat empty string as None
                d_date = determination_date.strip() if determination_date.strip() else None
                c_date = change_date.strip() if change_date.strip() else None

                response = run_assistant(
                    question=question.strip(),
                    determination_date=d_date,
                    change_date=c_date
                )

                status = response.get("status")

                if status == "ANSWERED":
                    st.markdown("### Answer")
                    
                    if response.get("generation_mode") == "fallback":
                        st.caption("Grounded response")

                    st.write(response.get("answer"))

                    source = response.get("source", [])
                    if source:
                        st.markdown("### Source")
                        for s in source:
                            st.markdown(f"**§{s['clause_id']}** — {s['source_doc']}")
                    
                    policy = response.get("policy", {})
                    applicable = policy.get("applicable", [])
                    if applicable:
                        st.markdown("### Policy evidence")
                        for item in applicable:
                            st.markdown(f"""
                            <div class="evidence-box">
                                <strong>Clause: {item['clause_id']}</strong><br/>
                                <em>Source: {item['source_doc']}</em><br/><br/>
                                {item['text']}
                            </div>
                            """, unsafe_allow_html=True)

                elif status == "NEEDS_DATE":
                    st.warning(response.get("answer"))
                
                elif status == "ABSTAIN":
                    st.error(response.get("answer"))
                
                elif status == "AI_UNAVAILABLE":
                    st.error(response.get("answer", "AI API is currently unavailable. Please try again later."))
                
                else:
                    st.info(response.get("answer", "Unknown response status."))

            except Exception as e:
                st.error("AI_UNAVAILABLE: An error occurred communicating with the AI service.")
                st.exception(e)

if __name__ == "__main__":
    main()
