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

#初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

#展示聊天信息
for message in st.session_state.messages:#存储类型：{"role": "user或assistant", "content": prompt}
    st.chat_message(message["role"]).write(message["content"])



#系统提示词
system_prompt = "你是一个历史老师，名字叫张老师，回答问题要严谨专业"
#创建与ai交互的对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")

#消息输入框
prompt = st.chat_input("请输入你的问题：")
if prompt:
    st.chat_message("user").write(prompt)

#保存用户输入提示词
    st.session_state.messages.append({"role": "user", "content": prompt})
    #调用大模型
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    # #打印大模型返回结果(非流式输出)
    # print("----------大模型返回结果：",response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    #打印大模型返回结果(流式输出)
    response_message = st.empty()#创建一个空组件，用于展示大模型返回结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    #保存大模型回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})