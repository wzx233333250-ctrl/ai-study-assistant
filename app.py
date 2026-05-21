import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量 (你的 API 密钥)
load_dotenv()

# 初始化 DeepSeek 客户端
try:
    client = OpenAI(
        api_key=os.environ.get("API_KEY"), 
        base_url="https://api.deepseek.com" 
    )
except Exception as e:
    st.error(f"初始化 API 客户端失败，请检查配置: {e}")

# --- 页面配置 ---
st.set_page_config(page_title="AI 大学生学习助手", page_icon="🎓", layout="wide")
# --- 🍎 注入苹果/包豪斯极简风 CSS ---
apple_bauhaus_css = """
<style>
    /* 1. 整体背景与字体：苹果常用的 San Francisco 字体族与高级灰白底色 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #FAFAFA; /* 极浅的高级灰，比纯白更护眼 */
        color: #1D1D1F; /* 苹果御用的深灰黑色 */
    }
    
    /* 2. 隐藏 Streamlit 默认的臃肿元素 (右上角菜单、底部水印、顶部彩条) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 3. 按钮的包豪斯化：去掉阴影，采用极简边框和微圆角 */
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
    
    /* 4. 对话气泡与输入框的优雅化 */
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
    
    /* 5. 分割线极简处理 */
    hr {
        border-top: 1px solid #E5E5EA;
        margin: 2em 0;
    }
</style>
"""
# 强制渲染这段 CSS 代码
st.markdown(apple_bauhaus_css, unsafe_allow_html=True)
# -----------------------------------
st.title("🎓 AI 大学生学习助手")
st.caption("聚合多 AI 能力，专为大学生打造的学习神器")

# --- 侧边栏 ---
st.sidebar.header("🤖 功能导航")
mode = st.sidebar.selectbox(
    "请选择功能：",
    ["📄 论文/文献分析 (DeepSeek)", "📸 拍照识题 (待开发)", "🌐 联网查文献 (待开发)", "💻 编程课辅助 (待开发)"]
)

# --- 主界面逻辑 ---
if mode == "📄 论文/文献分析 (DeepSeek)":
    st.header("📄 论文/文献分析")
    st.write("上传你的论文或文献，AI 将为你进行深度解读、提炼核心观点或解答疑问。")
    
    uploaded_file = st.file_uploader("上传文献 (当前暂支持 .txt 或 .md 格式)", type=["txt", "md"])
    user_question = st.text_input("你想针对这篇文献问什么？", placeholder="例如：请简要总结这篇文章的核心创新点。")
    
    if st.button("开始分析"):
        if uploaded_file is not None and user_question:
            with st.spinner("DeepSeek 正在飞速阅读并分析中，请稍候..."):
                try:
                    file_content = uploaded_file.read().decode("utf-8")
                    prompt = f"以下是一篇文献的内容：\n\n{file_content}\n\n问题：{user_question}"
                    
                    response = client.chat.completions.create(
                        model="deepseekv4flash", 
                        messages=[
                            {"role": "system", "content": "你是一个专业的学术助手，擅长严谨地分析论文和文献。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2 
                    )
                    
                    st.success("分析完成！")
                    st.markdown("### 🤖 DeepSeek 分析结果：")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"调用 API 时发生错误: {e}")
        else:
            st.warning("请确保已上传文献并输入了你的问题。")
else:
    st.header(mode)
    st.info("该功能正在全力开发中，敬请期待！当前请主要测试【📄 论文/文献分析】功能。")
