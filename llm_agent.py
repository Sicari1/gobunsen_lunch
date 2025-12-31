# llm_agent.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.tools import DuckDuckGoSearchRun # 검색 도구 임포트
from langchain_core.tools import Tool
import config as cfg

def get_agent(df):
    llm = ChatOpenAI(
        model=cfg.MODEL_NAME, 
        temperature=0, 
        api_key=st.secrets["openai"]["api_key"]
    )
    
    # 1. 검색 도구 생성
    search = DuckDuckGoSearchRun()
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="현재 날씨, 실시간 정보 등이 필요할 때 유용합니다."
        )
    ]

    # 2. 에이전트 생성 (extra_tools 추가)
    return create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type="openai-functions",
        allow_dangerous_code=True,
        extra_tools=tools  # 도구 장착!
    )