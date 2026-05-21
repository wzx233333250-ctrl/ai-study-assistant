import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from pypdf import PdfReader

# 1. 加载配置与初始化 AI
load_dotenv()
try:
    client = OpenAI(
        api_key=os.environ.get("API_KEY"), 
        base_url="https://api.deepseek.com" 
    )
except Exception as e:
    st.error(f"初始化失败: {e}")

# 2. 页面基础设置
st.set_page_config(page_title="AI 大学生学习助手", page_icon="🎓", layout="wide")

# 3. 🍎 注入苹果/包豪斯极简风 CSS
apple_bauhaus_css = """
<style>
    /* 整体背景与字体：高级灰白底色，苹果字体 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #FAFAFA;
        color: #1D1D1F;
    }
    
    /* 隐藏 Streamlit 默认的杂乱元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 按钮的包豪斯化：极简边框和微圆角 */
    .stButton > button {
        background-color: #FFFFFF;
        color: #1D1D1F;
        border: 1px solid #D2D2D7;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        box-shadow: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #F5F5F7;
        border-color: #86868B;
        color: #000000;
    }
    
    /* 对话气泡与输入框的优雅化 */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5EA;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    [data-testid="stChatInput"] {
        border-radius: 12px;
        border: 1px solid #D2D2D7;
    }
</style>
"""
st.markdown(apple_bauhaus_css, unsafe_allow_html=True)

# 4. 侧边栏导航
st.sidebar.header("🤖 功能导航")
mode = st.sidebar.selectbox(
    "请选择功能：",
    ["📄 论文/文献分析 (DeepSeek)", "📸 拍照识题 (待开发)", "🌐 联网查文献 (待开发)"]
)

# 5. 核心逻辑：带记忆的对话模式
if mode == "📄 论文/文献分析 (DeepSeek)":
    st.title("🎓 论文与文献阅读助理")
    
    # 初始化记忆
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "paper_context" not in st.session_state:
        st.session_state.paper_context = ""

    # 上传与解析区
    st.markdown("### 1. 准备文献")
    uploaded_file = st.file_uploader("上传 PDF 或文本格式的文献：", type=["txt", "md", "pdf"])
    
    if uploaded_file is not None:
        if st.button("📥 提取并解析文献"):
            with st.spinner("正在提取文献内容..."):
                try:
                    file_content = ""
                    if uploaded_file.name.endswith(".pdf"):
                        pdf_reader = PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                file_content += text + "\n"
                    else:
                        file_content = uploaded_file.read().decode("utf-8")
                    
                    st.session_state.paper_context = file_content[:8000]
                    st.success("文献解析成功！请在下方输入框开始对话。")
                    st.session_state.messages = [] # 清空旧对话
                except Exception as e:
                    st.error(f"解析失败: {e}")

    st.divider()
    st.markdown("### 2. 深度探讨")

    # 渲染历史聊天气泡
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 底部聊天输入框
    if prompt := st.chat_input("请输入您关于这篇文献的问题..."):
        if not st.session_state.paper_context:
            st.warning("⚠️ 请先在上方上传并点击【提取并解析文献】按钮！")
        else:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 组装上下文给 AI
            api_messages = [{"role": "system", "content": f"你是一个严谨的学术助手。以下是文献内容：\n\n{st.session_state.paper_context}\n\n请根据文献回答问题。"}]
            for msg in st.session_state.messages:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

            # 调用大模型并显示
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                with st.spinner("思考中..."):
                    try:
                        response = client.chat.completions.create(
                            model="deepseekv4flash",
                            messages=api_messages,
                            temperature=0.3
                        )
                        full_response = response.choices[0].message.content
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        st.error(f"请求报错: {e}")
else:
    st.info("该功能正在全力开发中，敬请期待！")
