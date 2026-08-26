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
#伴侣昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
#伴侣性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼开朗的东北姑娘"

#展示聊天信息
for message in st.session_state.messages:#存储类型：{"role": "user或assistant", "content": prompt}
    st.chat_message(message["role"]).write(message["content"])



#系统提示词
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。：
        规则：
        1. 每次只回1条消息
        2. 禁止任何场景或状态描述性文字
        3. 匹配用户的语言
        4. 回复简短，像微信聊天一样
        5. 有需要的话可以用❤☆等emoji表情
        6. 用符合伴侣性格的方式对话
        7. 回复的内容，要充分体现伴侣的性格特征
        伴侣性格：
        - %s
        你必须严格遵守上述规则来回复用户。
        """


#创建与ai交互的对象
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")


#左侧的侧边栏-with：streamlit中上下文管理器
with st.sidebar:
    st.subheader("伴侣设置")
    #昵称
    nick_name = st.text_input("伴侣名称",placeholder="请输入伴侣名称", value = st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    #性格
    nature = st.text_area("伴侣性格", placeholder="请输入伴侣性格", value = st.session_state.nature)
    if nature:
        st.session_state.nature = nature


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
            {"role": "system", "content": system_prompt%(st.session_state.nick_name, st.session_state.nature)},
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