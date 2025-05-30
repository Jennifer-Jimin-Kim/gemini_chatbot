"""
Research Partner Chatbot
------------------------
신경과학 및 의학 연구를 위한 AI 기반 연구 동료 챗봇입니다.
Google의 Gemini 1.5 Flash 모델을 사용하여 지능적인 연구 지원을 제공합니다.
"""

import streamlit as st
import google.generativeai as genai
from typing import List, Dict

# Constants
INITIAL_GREETING = """안녕하세요. 저는 연구 도우미 Gemini 입니다. 
먼저 간단한 정보를 입력해 주시면, 더 나은 연구 지원을 제공해 드릴 수 있습니다."""

SYSTEM_PROMPT = """당신은 신경과학과 의학 분야의 전문 연구 동료입니다.
당신의 역할은 다음과 같습니다:
1. 연구 논의에 지적이고 협력적인 지원을 제공
2. 관련 과학 문헌과 연구 논문을 제안
3. 연구 아이디어를 발전시키고 개선하는 데 도움
4. 건설적인 비평과 대안적 관점을 제시
5. 전문적이면서도 지원적인 톤을 유지

항상 다음과 같은 방식으로 응답해주세요:
- 과학적 개념에 대한 깊은 이해를 보여주기
- 비판적 사고와 학문적 엄격성을 장려하기
- 구체적이고 실행 가능한 제안을 제공하기
- 적절한 경우 관련 과학 문헌을 참조하기"""

# Page Configuration
def initialize_page():
    """Streamlit 페이지 설정 및 레이아웃 초기화"""
    st.set_page_config(
        page_title="연구 동료 챗봇",
        page_icon="🤖",
        layout="centered"
    )
    
    st.title("🤖 연구 동료 챗봇")
    st.markdown("""
    당신의 연구, 브레인스토밍, 학술 작문을 지원하는 AI 기반 연구 동료입니다.
    
    **주요 기능:**
    - 연구 아이디어 개발
    - 관련 문헌 제안
    - 비판적 분석
    - 학술 작문 지원
    """)

# User Information Management
def initialize_user_info():
    """사용자 정보 초기화"""
    if "user_info" not in st.session_state:
        st.session_state.user_info = {
            "name": None,
            "field": None,
            "is_initialized": False
        }

def get_user_info():
    """사용자 정보 입력 받기"""
    if not st.session_state.user_info["is_initialized"]:
        with st.form("user_info_form"):
            st.subheader("👤 연구자 정보")
            name = st.text_input("이름을 입력해주세요")
            field = st.text_input("주요 연구 분야를 입력해주세요 (예: 신경과학, 의학, 생명공학 등)")
            submitted = st.form_submit_button("시작하기")
            
            if submitted and name and field:
                st.session_state.user_info["name"] = name
                st.session_state.user_info["field"] = field
                st.session_state.user_info["is_initialized"] = True
                st.rerun()
        return False
    return True

# Chat History Management
def initialize_chat_history():
    """채팅 기록 초기화"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        if st.session_state.user_info["is_initialized"]:
            welcome_message = f"""안녕하세요, {st.session_state.user_info['name']}님. 
저는 연구 도우미 Gemini 입니다. {st.session_state.user_info['field']} 분야의 연구를 지원해 드리겠습니다.

어떤 연구 주제에 대해 논의해 보고 싶으신가요? 
혹시 현재 진행 중인 연구가 있거나, 새로운 연구 아이디어를 탐색하고 싶으신지 알려주시면, 
제가 가진 전문 지식을 활용하여 지원해 드릴 수 있도록 하겠습니다. 
구체적인 질문이나 아이디어를 제시해 주시면 더욱 구체적인 도움을 드릴 수 있습니다."""
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})

def display_chat_history():
    """채팅 기록 표시"""
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])

# Gemini API Integration
def initialize_gemini():
    """Gemini API 초기화"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error("Gemini API 초기화에 실패했습니다. API 키를 확인해주세요.")
        st.stop()

def format_chat_history(messages: List[Dict]) -> str:
    """API 요청을 위한 채팅 기록 포맷팅"""
    return "\n".join([
        f"{'사용자' if msg['role'] == 'user' else '어시스턴트'}: {msg['content']}"
        for msg in messages
    ])

# Main Application
def main():
    """메인 애플리케이션 함수"""
    # 컴포넌트 초기화
    initialize_page()
    initialize_user_info()
    
    # 사용자 정보 입력 확인
    if not get_user_info():
        return
    
    initialize_chat_history()
    model = initialize_gemini()
    
    # 채팅 기록 표시
    display_chat_history()
    
    # 채팅 입력
    user_input = st.chat_input("💡 연구 아이디어, 논문 주제, 질문을 입력하세요…")
    
    if user_input:
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)
        
        try:
            # 응답 생성
            chat_history = format_chat_history(st.session_state.messages)
            response = model.generate_content(chat_history)
            
            # 어시스턴트 응답 추가 및 표시
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            with st.chat_message("assistant"):
                st.write(response.text)
                
        except Exception as e:
            st.error(f"응답 생성 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()
