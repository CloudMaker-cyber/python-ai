import streamlit as st
import os
from openai import OpenAI

#设置页面配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    #布局
    layout="wide",
    #侧边栏状态
    initial_sidebar_state="auto",
    menu_items={}
)

#大标题
st.title("AI智能伴侣")

#logo
st.logo("./resources/touxiang.jpg")

#系统提示此
system_prompt = "你是一个历史老师，名字叫张老师，回答问题要严谨专业"
#创建与ai交互的对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

#消息输入框
prompt = st.chat_input("请输入你的问题：")
if prompt:
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    print("----------大模型返回结果：",response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)