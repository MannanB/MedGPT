import streamlit as st
import requests

def call_api(query, prev):
    pnew = []
    for p in prev:
        pnew.append([p[0], p[1], str(p[2])])
    return requests.post("http://localhost:8000/query", json={"query": query, "previous": prev}).json()


def show_messages(text):
    messages_str = [
        f"{m['role']}: {m['content']}" for m in st.session_state["messages"][1:]
    ]
    text.text_area("Messages", value=str("\n".join(messages_str)), height=400)


base_prompt = [{"role": "Doctor", "content": "Ask me anything"}]

if "previous" not in st.session_state:
    st.session_state["previous"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = base_prompt

st.header("MedGPT")

text = st.empty()
show_messages(text)

prompt = st.text_input("Prompt", value="Enter your message here...")

if st.button("Send"):
    with st.spinner("Generating response..."):
        st.session_state["messages"] += [{"role": "Patient", "content": prompt}]
        
        resp = call_api(prompt, st.session_state["previous"])
        st.session_state["messages"] += [
            {"role": "Doctor", "content": resp["response"]}
        ]
        st.session_state["previous"] = resp["previous"]
        show_messages(text)

if st.button("Clear"):
    st.session_state["messages"] = base_prompt
    st.session_state["previous"] = []
    show_messages(text)

js = f"""
<script>
    function scroll(dummy_var_to_force_repeat_execution){{
        var textAreas = parent.document.querySelectorAll('.stTextArea textarea');
        for (let index = 0; index < textAreas.length; index++) {{
            textAreas[index].scrollTop = textAreas[index].scrollHeight;
        }}
    }}
    scroll({len(st.session_state['messages'])})
</script>
"""

st.components.v1.html(js)