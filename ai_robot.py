import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json


#保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_date = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果sessions目录不存在，就创建一个
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=2)

#生成会话名字函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#加载所有会话列表信息
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])

    return session_list

#加载当前会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            #读取信息
            with open(f"sessions/{session_name}.json","r",encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败")

#删除会话
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            #如果删除当前会话，需要更新列表信息
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除失败")



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
#会话名称
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()


#展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
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
    #会话信息
    st.header("会话信息")

    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            #加载会话信息    三元运算符来判断当前加载的所有会话中哪个是打开的，就标红
            if st.button(session,width="stretch",icon="📄",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()

        with col2:
            #删除按键
            if st.button("",width="stretch",icon="❌",key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    #新建会话
    if st.button("新建会话",width="stretch",icon = "🖊"):
        #保存当前会话
        save_session()
        #保存新建会话信息（需要重置st.session_state.messages和st.session_state.current_session)
        if st.session_state.messages:        #如果存在会话信息,才能新建
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()        #重新运行页面,保证新页面能渲染出来



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
    save_session()