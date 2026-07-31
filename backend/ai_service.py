"""大模型 AI 服务（访客自带 API Key，无内置 Key）"""
import os
from openai import OpenAI

# 注意：本系统不内置任何 API Key，所有访客必须填写自己的 Key
# 以下仅作为兜底环境变量（可为空）
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# 常见大模型服务商预设（访客可快速选择）
PROVIDER_PRESETS = {
    "deepseek": {
        "name": "DeepSeek 深度求索",
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-v4-flash", "deepseek-chat", "deepseek-reasoner"],
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    },
    "qwen": {
        "name": "通义千问 (阿里云百炼)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-plus", "qwen-max", "qwen-turbo"],
    },
    "zhipu": {
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-plus", "glm-4", "glm-4-flash"],
    },
    "moonshot": {
        "name": "Kimi (月之暗面)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    },
    "doubao": {
        "name": "豆包 (火山方舟)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": ["doubao-pro-32k", "doubao-lite-32k"],
    },
    "custom": {
        "name": "自定义 (OpenAI 兼容)",
        "base_url": "",
        "models": [],
    },
}

# 资源类型对应的详细提示词
RESOURCE_PROMPTS = {
    "项目设计文档": """生成包含以下内容的完整项目设计文档：
1. 驱动问题（Driving Question）- 开放性的核心问题
2. 项目背景与情境描述 - 真实业务场景
3. 学习目标 - 知识目标、技能目标、素养目标（各3-5条）
4. 项目预期成果 - 最终交付物清单及质量要求
5. 项目里程碑 - 分阶段任务与时间节点
6. 所需知识与技能清单 - 前置知识、核心知识点""",

    "学习指导材料": """生成以下学习指导材料：
1. 项目任务书 - 明确的任务描述、交付要求、评分标准概述
2. 分阶段任务清单 - 每个阶段的具体任务、完成标准、建议时间
3. 学习路径图 - 从起点到终点的知识技能路线图
4. 资源推荐清单 - 推荐的书籍、在线课程、文档、数据集、工具等
5. 学习策略建议 - 针对高职本科学生的学习方法指导""",

    "探究支持工具": """生成以下探究支持工具：
1. 研究问题引导单 - 5-8个引导性问题
2. 信息收集模板 - 数据来源记录表、数据质量评估表
3. 数据分析框架 - EDA → 特征工程 → 建模 → 评估
4. 实验/调研设计方案模板 - 假设提出、变量定义、方法选择
5. 思维导图建议 - 核心概念的思维导图结构""",

    "协作工具": """生成以下协作工具：
1. 小组分工协议模板 - 角色定义、职责说明
2. 协作规则与流程 - 沟通机制、决策流程、冲突解决策略
3. 进度跟踪表 - 甘特图式任务跟踪表
4. 会议记录模板 - 站会/周会记录格式
5. 代码协作规范 - Git工作流建议、代码审查清单""",

    "脚手架材料": """生成以下脚手架材料：
1. 知识提示卡 - 5-8张核心知识点提示卡
2. 常见问题解答（FAQ）- 10个学生可能遇到的问题及解答
3. 代码示例片段 - 关键技术的Python代码示例
4. 案例参考 - 1-2个类似项目的简要案例分析
5. 易错点提醒 - 常见错误及避免方法""",

    "评价工具": """生成以下评价工具：
1. 过程性评价量规 - 针对学习过程的评分量规表格
2. 终结性评价量规 - 针对最终成果的评分量规表格
3. 自评表 - 学生自我反思评价表
4. 互评表 - 组间互评标准与评分表
5. 反思日志模板 - 引导学生反思学习过程的结构化模板""",

    "成果展示模板": """生成以下成果展示模板：
1. 项目报告模板 - 结构化的项目报告大纲
2. 演示文稿模板 - PPT结构建议
3. 数据作品集格式要求 - 代码仓库组织、README规范
4. 展示/答辩流程说明 - 时间分配、评分规则、提问环节指南
5. 展示技巧提示 - 面向高职本科学生的演讲技巧建议""",

    "教师指南": """生成以下教师指南：
1. 教学实施建议 - 课堂组织形式、时间安排、教学节奏建议
2. 引导提问策略 - 不同阶段的引导性问题示例
3. 常见困难应对方案 - 学生可能遇到的技术困难及应对策略
4. 差异化教学建议 - 针对不同水平学生的分层指导策略
5. 课程思政融入点 - 数据伦理、职业道德等思政元素建议
6. 教学资源准备清单 - 需要提前准备的软硬件环境"""
}

SYSTEM_PROMPT = """你是一位资深的高职本科数据科学类专业教师，擅长PBL（项目式学习）教学设计。

你的设计需要：
1. 贴近高职本科学生的知识水平和认知特点
2. 注重实践应用，对接企业真实需求
3. 体现数据科学类专业特色
4. 内容结构清晰、可操作性强
5. 融入课程思政元素

**输出格式要求（必须严格遵守）：**
- 必须使用标准Markdown格式
- 使用 # ## ### 等标题层级组织内容结构
- 使用 - 或 1. 2. 3. 创建列表
- 使用表格展示量规、清单等结构化信息
- 使用 **加粗** 强调重点内容
- 使用代码块 ```python 展示代码示例
- 使用 > 引用重要提示
- 使用 --- 分隔不同章节
- 确保层次分明，便于阅读和下载"""


def get_client(api_key: str = None, base_url: str = None):
    """获取 OpenAI 客户端（API Key 必须由访客提供）"""
    if not api_key:
        raise ValueError("缺少 API Key，请填写您自己的 API Key")
    return OpenAI(
        api_key=api_key,
        base_url=base_url or "https://api.deepseek.com"
    )


def build_user_prompt(course_data: dict, resource_type: str) -> str:
    """构建用户提示词"""
    context = f"""## 课程信息
- **课程名称**：{course_data['name']}
- **课程主题/章节**：{course_data['topic']}
- **专业方向**：{course_data['major']}
- **学生层次**：{course_data['student_level']}
- **计划课时**：{course_data['class_hours']}
- **小组人数**：{course_data['group_size']}
- **项目类型**：{course_data['project_type']}
"""

    if course_data.get('project_scenario'):
        context += f"- **项目情境**：{course_data['project_scenario']}\n"

    if course_data.get('learning_objectives'):
        context += f"- **学习目标**：\n{course_data['learning_objectives']}\n"

    resource_instruction = RESOURCE_PROMPTS.get(resource_type, f"生成{resource_type}")

    return f"{context}\n\n{resource_instruction}"


def generate_resource(course_data: dict, resource_type: str, model: str = "deepseek-v4-flash", temperature: float = 0.7, api_key: str = None, base_url: str = None) -> str:
    """调用大模型 API 生成资源（支持访客自带 API 配置）"""
    client = get_client(api_key, base_url)
    user_prompt = build_user_prompt(course_data, resource_type)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"API调用失败：{str(e)}")
