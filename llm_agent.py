# llm_agent.py
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import config as cfg

def get_agent(df):
    llm = ChatOpenAI(
        model=cfg.MODEL_NAME, 
        temperature=0, 
        api_key=st.secrets["openai"]["api_key"]
    )
    return create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type="openai-functions",
        allow_dangerous_code=True 
    )