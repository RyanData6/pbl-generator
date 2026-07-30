"""
PBL 教学资源生成器
面向高职本科数据科学类专业
"""
import streamlit as st
from openai import OpenAI
import time

# 页面配置
st.set_page_config(
    page_title="PBL 教学资源生成器",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 DeepSeek 客户端
@st.cache_resource
def get_client():
    return OpenAI(
        api_key="sk-e527575201544bf2a0884a54d05c99a0",
        base_url="https://api.deepseek.com"
    )

client = get_client()

# 侧边栏配置
with st.sidebar:
    st.title("⚙️ 配置")
    
    model = st.selectbox(
        "选择模型",
        ["deepseek-v4-flash", "deepseek-chat", "deepseek-reasoner"],
        index=0
    )
    
    temperature = st.slider(
        "创造性 (temperature)",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1
    )
    
    st.divider()
    st.markdown("""
    **使用说明**
    1. 填写课程基本信息
    2. 选择要生成的资源类型
    3. 点击生成按钮
    4. 查看并下载结果
    """)

# 主界面
st.title("🎓 PBL 教学资源生成器")
st.caption("面向高职本科 · 数据科学类专业方向")

# 课程信息输入
st.header("📖 课程信息")

col1, col2 = st.columns(2)

with col1:
    course_name = st.text_input(
        "课程名称",
        placeholder="例如：Python 数据分析",
        value=""
    )
    
    course_topic = st.text_input(
        "课程主题/章节",
        placeholder="例如：数据清洗与预处理",
        value=""
    )
    
    target_major = st.selectbox(
        "专业方向",
        [
            "数据科学与大数据技术",
            "人工智能技术应用",
            "计算机应用技术（数据方向）",
            "软件技术（数据方向）",
            "统计学（数据方向）"
        ]
    )

with col2:
    class_hours = st.number_input(
        "计划课时",
        min_value=1,
        max_value=64,
        value=8
    )
    
    group_size = st.number_input(
        "小组人数",
        min_value=2,
        max_value=8,
        value=4
    )
    
    student_level = st.selectbox(
        "学生层次",
        ["高职本科（应用型本科）"]
    )

# PBL 项目设计
st.header("🎯 PBL 项目设计")

project_type = st.selectbox(
    "项目类型",
    [
        "数据分析实战项目",
        "数据可视化项目",
        "机器学习应用项目",
        "数据库设计与开发项目",
        "数据采集与处理项目",
        "综合数据科学项目"
    ]
)

project_scenario = st.text_area(
    "项目情境描述（可选）",
    placeholder="描述一个真实的业务场景，例如：某电商企业需要对用户行为数据进行分析，以提升用户留存率...",
    height=100
)

learning_objectives = st.text_area(
    "学习目标（可选，不填则由 AI 自动生成）",
    placeholder="例如：\n1. 掌握 pandas 数据清洗的核心方法\n2. 能够独立完成数据质量评估报告\n3. 培养团队协作与项目管理能力",
    height=100
)

# 资源类型选择
st.header("📦 选择要生成的教学资源")

resource_types = {
    "项目设计文档": "生成包含驱动问题、项目背景、学习目标、预期成果、里程碑、知识技能清单的完整项目设计文档",
    "学习指导材料": "生成项目任务书、分阶段任务清单、学习路径图、资源推荐清单、学习策略建议",
    "探究支持工具": "生成研究问题引导单、信息收集模板、数据分析框架、实验设计方案、思维导图建议",
    "协作工具": "生成小组分工协议、协作规则与流程、进度跟踪表、会议记录模板、代码协作规范",
    "脚手架材料": "生成知识提示卡、常见问题解答、代码示例片段、案例参考、易错点提醒",
    "评价工具": "生成过程性评价量规、终结性评价量规、自评表、互评表、反思日志模板",
    "成果展示模板": "生成项目报告模板、演示文稿模板、数据作品集格式要求、展示答辩流程、展示技巧提示",
    "教师指南": "生成教学实施建议、引导提问策略、常见困难应对方案、差异化教学建议、课程思政融入点、教学资源准备清单"
}

selected_resources = []
cols = st.columns(2)
for idx, (resource_name, description) in enumerate(resource_types.items()):
    with cols[idx % 2]:
        if st.checkbox(f"📋 {resource_name}", key=f"chk_{resource_name}"):
            selected_resources.append((resource_name, description))

# 生成按钮
st.divider()
generate_btn = st.button(
    "🚀 生成教学资源",
    type="primary",
    use_container_width=True
)

# 生成逻辑
if generate_btn:
    # 验证输入
    if not course_name or not course_topic:
        st.error("请填写课程名称和课程主题！")
        st.stop()
    
    if not selected_resources:
        st.warning("请至少选择一项要生成的教学资源！")
        st.stop()
    
    # 构建系统提示
    system_prompt = """你是一位资深的高职本科数据科学类专业教师，擅长 PBL（项目式学习）教学设计。

你的设计需要：
1. 贴近高职本科学生的知识水平和认知特点
2. 注重实践应用，对接企业真实需求
3. 体现数据科学类专业特色
4. 内容结构清晰、可操作性强
5. 融入课程思政元素

**输出格式要求（必须严格遵守）：**
- 必须使用标准 Markdown 格式
- 使用 # ## ### 等标题层级组织内容结构
- 使用 - 或 1. 2. 3. 创建列表
- 使用表格展示量规、清单等结构化信息
- 使用 **加粗** 强调重点内容
- 使用代码块 ```python 展示代码示例
- 使用 > 引用重要提示
- 使用 --- 分隔不同章节
- 确保层次分明，便于阅读和下载"""
    
    # 构建用户提示
    context = f"""## 课程信息
- **课程名称**：{course_name}
- **课程主题/章节**：{course_topic}
- **专业方向**：{target_major}
- **学生层次**：{student_level}
- **计划课时**：{class_hours}
- **小组人数**：{group_size}
- **项目类型**：{project_type}
"""
    
    if project_scenario:
        context += f"- **项目情境**：{project_scenario}\n"
    
    if learning_objectives:
        context += f"- **学习目标**：\n{learning_objectives}\n"
    
    # 存储结果
    if "generated_results" not in st.session_state:
        st.session_state.generated_results = {}
    
    # 生成每个资源
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (resource_name, description) in enumerate(selected_resources):
        status_text.text(f"正在生成 {resource_name}...")
        progress_bar.progress((idx) / len(selected_resources))
        
        user_prompt = f"{context}\n\n{description}"
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                stream=False
            )
            
            result = response.choices[0].message.content
            st.session_state.generated_results[resource_name] = result
            
        except Exception as e:
            st.error(f"生成 {resource_name} 时出错：{str(e)}")
            st.session_state.generated_results[resource_name] = f"生成失败：{str(e)}"
    
    progress_bar.progress(1.0)
    status_text.text("生成完成！")
    st.session_state.results_ready = True
    st.rerun()

# 显示结果
if st.session_state.get("results_ready"):
    st.divider()
    st.header("📄 生成结果")
    
    results = st.session_state.get("generated_results", {})
    
    if results:
        # 创建标签页
        tabs = st.tabs(list(results.keys()))
        
        for tab, resource_name in zip(tabs, results.keys()):
            with tab:
                st.markdown(results[resource_name])
                
                # 下载按钮
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 下载 Markdown",
                        data=results[resource_name].encode("utf-8"),
                        file_name=f"PBL_{resource_name}_{course_name}.md",
                        mime="text/markdown",
                        key=f"dl_md_{resource_name}"
                    )
                with col2:
                    st.download_button(
                        label="📥 下载纯文本",
                        data=results[resource_name].encode("utf-8"),
                        file_name=f"PBL_{resource_name}_{course_name}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{resource_name}"
                    )
        
        # 全部下载
        st.divider()
        all_content = "\n\n---\n\n".join(
            f"# {resource_name}\n\n{results[resource_name]}"
            for resource_name in results.keys()
        )
        
        st.download_button(
            label="📦 下载全部资源（Markdown）",
            data=all_content.encode("utf-8"),
            file_name=f"PBL_全部资源_{course_name}.md",
            mime="text/markdown",
            use_container_width=True
        )
