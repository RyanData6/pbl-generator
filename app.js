/**
 * PBL 教学资源生成器 - 前端主逻辑
 */

const API_BASE = window.location.origin;

// 大模型服务商预设
const PROVIDER_PRESETS = {
    deepseek: { name: 'DeepSeek 深度求索', base_url: 'https://api.deepseek.com', models: ['deepseek-v4-flash', 'deepseek-chat', 'deepseek-reasoner'] },
    openai: { name: 'OpenAI', base_url: 'https://api.openai.com/v1', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'] },
    qwen: { name: '通义千问 (阿里云百炼)', base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', models: ['qwen-plus', 'qwen-max', 'qwen-turbo'] },
    zhipu: { name: '智谱 GLM', base_url: 'https://open.bigmodel.cn/api/paas/v4', models: ['glm-4-plus', 'glm-4', 'glm-4-flash'] },
    moonshot: { name: 'Kimi (月之暗面)', base_url: 'https://api.moonshot.cn/v1', models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'] },
    doubao: { name: '豆包 (火山方舟)', base_url: 'https://ark.cn-beijing.volces.com/api/v3', models: ['doubao-pro-32k', 'doubao-lite-32k'] },
    custom: { name: '自定义 (OpenAI 兼容)', base_url: '', models: [] },
};

// ==================== DOM 元素 ====================
const elements = {
    courseForm: document.getElementById('courseForm'),
    courseName: document.getElementById('courseName'),
    courseTopic: document.getElementById('courseTopic'),
    major: document.getElementById('major'),
    studentLevel: document.getElementById('studentLevel'),
    classHours: document.getElementById('classHours'),
    groupSize: document.getElementById('groupSize'),
    projectType: document.getElementById('projectType'),
    projectScenario: document.getElementById('projectScenario'),
    learningObjectives: document.getElementById('learningObjectives'),
    provider: document.getElementById('provider'),
    apiKey: document.getElementById('apiKey'),
    baseUrl: document.getElementById('baseUrl'),
    baseUrlGroup: document.getElementById('baseUrlGroup'),
    model: document.getElementById('model'),
    temperature: document.getElementById('temperature'),
    tempValue: document.getElementById('tempValue'),
    generateBtn: null, // 将在 DOMContentLoaded 中初始化
    downloadAllBtn: document.getElementById('downloadAllBtn'),
    progressArea: document.getElementById('progressArea'),
    progressText: document.getElementById('progressText'),
    progressCount: document.getElementById('progressCount'),
    progressFill: document.getElementById('progressFill'),
    resultContent: document.getElementById('resultContent'),
    tabsContainer: document.getElementById('tabsContainer'),
    tabsHeader: document.getElementById('tabsHeader'),
    tabsContent: document.getElementById('tabsContent'),
};

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    // 初始化生成按钮（需要在 DOM 加载完成后查询）
    elements.generateBtn = document.querySelector('.btn-primary');

    // Temperature 滑块实时显示值
    elements.temperature.addEventListener('input', (e) => {
        elements.tempValue.textContent = e.target.value;
    });

    // 服务商切换：自动填充 Base URL 和模型列表
    elements.provider.addEventListener('change', handleProviderChange);

    // 表单提交事件
    elements.courseForm.addEventListener('submit', handleGenerate);

    // 下载全部按钮
    elements.downloadAllBtn.addEventListener('click', handleDownloadAll);

    // 恢复访客上次保存的 API 配置
    restoreApiConfig();
});

/**
 * 服务商切换处理
 */
function handleProviderChange() {
    const provider = elements.provider.value;
    const preset = PROVIDER_PRESETS[provider];
    if (!preset) return;

    // 自定义：显示 Base URL 输入框，手动填写
    if (provider === 'custom') {
        elements.baseUrlGroup.style.display = 'block';
        elements.baseUrl.placeholder = 'https://api.example.com/v1';
        elements.baseUrl.value = '';
        elements.apiKey.placeholder = '请输入您的 API Key';
        fillModelOptions([], '');
        return;
    }

    // 预设服务商：自动填充 Base URL 和模型
    elements.baseUrlGroup.style.display = 'block';
    elements.baseUrl.value = preset.base_url;
    elements.apiKey.placeholder = '请输入您的 ' + preset.name + ' API Key';
    fillModelOptions(preset.models, preset.models[0]);
}

/**
 * 填充模型下拉选项
 */
function fillModelOptions(models, selected) {
    elements.model.innerHTML = '';
    if (models.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '请填写自定义模型名称';
        elements.model.appendChild(opt);
        return;
    }
    models.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        if (m === selected) opt.selected = true;
        elements.model.appendChild(opt);
    });
}

/**
 * 保存访客 API 配置到 localStorage
 */
function saveApiConfig() {
    const config = {
        provider: elements.provider.value,
        apiKey: elements.apiKey.value.trim(),
        baseUrl: elements.baseUrl.value.trim(),
        model: elements.model.value,
    };
    localStorage.setItem('pbl_api_config', JSON.stringify(config));
}

/**
 * 恢复访客上次保存的 API 配置
 */
function restoreApiConfig() {
    try {
        const saved = JSON.parse(localStorage.getItem('pbl_api_config') || 'null');
        if (saved && saved.provider && PROVIDER_PRESETS[saved.provider]) {
            elements.provider.value = saved.provider;
            handleProviderChange();
            if (saved.apiKey) elements.apiKey.value = saved.apiKey;
            if (saved.baseUrl) elements.baseUrl.value = saved.baseUrl;
            if (saved.model && [...elements.model.options].some(o => o.value === saved.model)) {
                elements.model.value = saved.model;
            }
            return;
        }
    } catch (e) {
        // 配置损坏时忽略
    }
    // 无保存配置：按默认服务商渲染（自动填充 Base URL 和模型）
    handleProviderChange();
}

// ==================== 核心功能 ====================

/**
 * 处理生成请求
 */
async function handleGenerate(e) {
    e.preventDefault();

    // 表单验证
    if (!elements.courseName.value.trim()) {
        showError('请填写课程名称');
        elements.courseName.focus();
        return;
    }
    if (!elements.courseTopic.value.trim()) {
        showError('请填写课程主题');
        elements.courseTopic.focus();
        return;
    }

    // 获取选中的资源类型
    const resourceTypes = Array.from(
        document.querySelectorAll('.checkbox-item input[type="checkbox"]:checked')
    ).map(cb => cb.value);

    if (resourceTypes.length === 0) {
        showError('请至少选择一项教学资源');
        return;
    }

    // 构建请求数据
    const apiKey = elements.apiKey.value.trim();
    const baseUrl = elements.baseUrl.value.trim();

    // 所有访客必须填写自己的 API Key
    if (!apiKey) {
        showError('请先填写您的 API Key');
        elements.apiKey.focus();
        return;
    }

    const requestData = {
        course: {
            name: elements.courseName.value.trim(),
            topic: elements.courseTopic.value.trim(),
            major: elements.major.value,
            student_level: elements.studentLevel.value,
            class_hours: parseInt(elements.classHours.value),
            group_size: parseInt(elements.groupSize.value),
            project_type: elements.projectType.value,
            project_scenario: elements.projectScenario.value.trim() || null,
            learning_objectives: elements.learningObjectives.value.trim() || null,
        },
        resource_types: resourceTypes,
        model: elements.model.value,
        temperature: parseFloat(elements.temperature.value),
        api_key: apiKey,
        base_url: baseUrl || null,
    };

    // 保存访客 API 配置（仅保存在本机浏览器）
    saveApiConfig();

    // UI 状态切换
    setLoadingState(true);
    showProgress(0, resourceTypes.length, '正在准备生成...');
    hideResults();

    try {
        const response = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `请求失败 (${response.status})`);
        }

        const data = await response.json();
        showResults(data.results, requestData.course.name);
        showSuccess('教学资源生成完成！');
    } catch (error) {
        showError(`生成失败：${error.message}`);
        hideProgress();
    } finally {
        setLoadingState(false);
    }
}

/**
 * 显示生成结果
 */
function showResults(results, courseName) {
    hideProgress();
    elements.resultContent.style.display = 'none';
    elements.tabsContainer.style.display = 'flex';
    elements.downloadAllBtn.style.display = 'inline-flex';

    // 清空旧内容
    elements.tabsHeader.innerHTML = '';
    elements.tabsContent.innerHTML = '';

    // 存储结果供下载使用
    window.currentResults = results;
    window.currentCourseName = courseName;

    const resourceNames = Object.keys(results);

    // 创建标签按钮和内容面板
    resourceNames.forEach((name, index) => {
        // 标签按钮
        const tabBtn = document.createElement('button');
        tabBtn.className = `tab-button${index === 0 ? ' active' : ''}`;
        tabBtn.textContent = name;
        tabBtn.dataset.target = `panel-${index}`;
        tabBtn.addEventListener('click', () => switchTab(tabBtn));
        elements.tabsHeader.appendChild(tabBtn);

        // 内容面板
        const panel = document.createElement('div');
        panel.className = `tab-panel${index === 0 ? ' active' : ''}`;
        panel.id = `panel-${index}`;

        const result = results[name];
        if (result.error) {
            panel.innerHTML = `
                <div class="markdown-content">
                    <h3 style="color: var(--danger-color);">生成失败</h3>
                    <p>${result.error}</p>
                </div>
            `;
        } else {
            const markdownHtml = marked.parse(result.content);
            panel.innerHTML = `
                <div class="markdown-content">${markdownHtml}</div>
                <button class="btn-secondary download-btn" onclick="downloadSingle('${name}')">
                    下载 Markdown
                </button>
            `;
        }

        elements.tabsContent.appendChild(panel);
    });
}

/**
 * 切换标签页
 */
function switchTab(activeBtn) {
    // 更新按钮状态
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    activeBtn.classList.add('active');

    // 更新面板状态
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    const targetPanel = document.getElementById(activeBtn.dataset.target);
    if (targetPanel) targetPanel.classList.add('active');
}

/**
 * 下载单个资源
 */
function downloadSingle(resourceName) {
    const result = window.currentResults[resourceName];
    if (!result || result.error) return;

    const blob = new Blob([result.content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PBL_${resourceName}_${window.currentCourseName}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * 下载全部资源
 */
function handleDownloadAll() {
    if (!window.currentResults) return;

    const allContent = Object.entries(window.currentResults)
        .filter(([_, v]) => !v.error)
        .map(([name, v]) => `# ${name}\n\n${v.content}`)
        .join('\n\n---\n\n');

    const blob = new Blob([allContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PBL_全部资源_${window.currentCourseName}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==================== UI 状态管理 ====================

function setLoadingState(loading) {
    elements.generateBtn.disabled = loading;
    if (loading) {
        elements.generateBtn.innerHTML = '<span class="loading"></span> 生成中...';
    } else {
        elements.generateBtn.innerHTML = '生成教学资源';
    }
}

function showProgress(current, total, text) {
    elements.progressArea.style.display = 'block';
    elements.progressText.textContent = text;
    elements.progressCount.textContent = `${current}/${total}`;
    const percent = total > 0 ? (current / total) * 100 : 0;
    elements.progressFill.style.width = `${percent}%`;
}

function hideProgress() {
    elements.progressArea.style.display = 'none';
}

function hideResults() {
    elements.tabsContainer.style.display = 'none';
    elements.downloadAllBtn.style.display = 'none';
    elements.resultContent.style.display = 'none';
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
}

/**
 * Toast 提示
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // 样式
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '14px 20px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '10000',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        transform: 'translateX(120%)',
        transition: 'transform 0.3s ease',
        background: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
    });

    document.body.appendChild(toast);

    // 动画显示
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
    });

    // 自动消失
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
