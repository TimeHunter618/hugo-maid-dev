---
title: Skill 蒸馏与能力萃取技术
description: 从能力识别到精准迁移，探索大语言模型特定能力的萃取、蒸馏与复用方法
date: 2025-11-08T10:00:00+08:00
lastmod: 2025-11-08T10:00:00+08:00
weight: 7
tags:
  - 大模型
  - 能力萃取
  - Skill蒸馏
  - Agent
  - 能力迁移
categories:
  - 人工智能
  - 技术分享
math: true
mermaid: true
photos:
  - https://d-sketon.top/img/backwebp/bg2.webp
---

## 引言

随着大语言模型（LLM）参数规模从数十亿增长到数千亿，一个核心矛盾日益凸显：**强大能力往往与庞大参数绑定，而实际部署迫切需要小而精的模型**。传统的知识蒸馏（Knowledge Distillation）试图将大模型的整体知识压缩到小模型中，但这种"全量压缩"的思路在面对复杂能力时往往力不从心——小模型在通用能力上尚可，但在代码生成、数学推理、工具使用等高阶能力上与大模型存在显著鸿沟。

**Skill 蒸馏**（Skill Distillation）或称**能力萃取**（Capability Extraction）提供了一种全新的思路：不再追求整体压缩，而是**精准识别、提取并迁移大模型的特定能力**到小模型中。例如，将 GPT-4 级别的代码生成能力蒸馏到 7B 参数的开源模型中，使其在编程任务上接近闭源大模型的水平。这种"定向萃取"的范式正在成为大模型落地的关键技术路径。

本文将从能力识别、数据构造、蒸馏训练、能力评估到能力组合，系统梳理 Skill 蒸馏与能力萃取的完整技术体系，并结合实践案例和前沿方向，帮助读者全面掌握这一技术。

## 概念定义与边界

### 什么是「Skill」

在 Skill 蒸馏的语境下，**Skill** 指的是模型在特定领域或任务上表现出的**结构化能力**。它不同于零散的知识片段，而是一套包含理解、推理、规划与执行的完整能力体系。例如，"代码生成"这一 Skill 不仅包含语法知识，还包含算法设计、调试推理、代码审查等子能力的协同。

#### Skill 的分类

我们可以将大语言模型的 Skill 大致分为以下几类：

| Skill 类别 | 能力描述 | 典型示例 | 评估基准 |
|-----------|---------|---------|---------|
| **推理能力** | 逻辑推理、多步推理、因果分析 | 数学证明、逻辑谜题 | GSM8K, MATH |
| **代码能力** | 代码生成、补全、调试、解释 | Python 编程、算法实现 | HumanEval, MBPP |
| **工具使用** | 调用 API、搜索引擎、代码执行 | Agent 任务、工具编排 | ToolBench, AgentBench |
| **多语言能力** | 跨语言理解与生成 | 翻译、跨语言问答 | XNLI, FLORES |
| **领域知识** | 专业领域的深度知识应用 | 医疗诊断、法律分析 | MedQA, LegalBench |
| **指令遵循** | 精确理解和执行复杂指令 | 格式约束、多步指令 | IFEval, MT-Bench |
| **创意写作** | 长文本生成、风格模仿 | 小说创作、文案撰写 | 自定义评估 |

理解 Skill 的分类有助于在蒸馏过程中**明确目标**：我们到底要萃取模型的哪种能力，以及如何衡量这种能力是否被成功迁移。

### Skill 蒸馏 vs 传统知识蒸馏

Skill 蒸馏与传统知识蒸馏虽然在形式上都涉及 Teacher-Student 范式，但在目标、方法和评估上有本质区别：

| 维度 | 传统知识蒸馏 | Skill 蒸馏 |
|------|------------|-----------|
| **核心目标** | 整体知识压缩，追求通用性能 | 特定能力精准迁移，追求专项性能 |
| **迁移内容** | 输出分布、中间特征、 logits | 推理过程、能力模式、行为策略 |
| **数据构造** | 通用数据集，无差别覆盖 | 能力定向数据，针对特定 Skill |
| **训练方法** | logit 蒸馏、特征对齐 | CoT 蒸馏、对比学习、RLHF |
| **评估方式** | 综合基准平均分 | 分项能力保真度、能力退化检测 |
| **能力冲突** | 不关注 | 需要处理多能力间的干扰 |
| **适用场景** | 模型压缩、部署加速 | 能力定制、专项增强 |

传统蒸馏好比"全量复印"，而 Skill 蒸馏更像"精准手术"——只提取所需的能力组织，避免无关信息的干扰。

### 能力萃取的概念

**能力萃取**（Capability Extraction）是 Skill 蒸馏的上游环节，强调从大模型中"分离"出特定能力的表征与行为模式，使其可被独立迁移和复用。这个过程类似于化学中的萃取操作：从混合物中选择性地溶解和分离目标成分。

```mermaid
graph LR
    A[大语言模型<br/>GPT-4 / Claude] --> B[能力萃取引擎]
    B --> C[代码能力]
    B --> D[推理能力]
    B --> E[工具使用能力]
    B --> F[领域知识能力]
    C --> G[小模型 A<br/>Code-7B]
    D --> H[小模型 B<br/>Math-7B]
    E --> I[小模型 C<br/>Agent-7B]
    F --> J[小模型 D<br/>Domain-7B]
    
    style A fill:#e1f5fe
    style B fill:#fff3e0
    style G fill:#e8f5e9
    style H fill:#e8f5e9
    style I fill:#e8f5e9
    style J fill:#e8f5e9
```

能力萃取的关键挑战在于：能力在大模型中并非以独立模块的形式存在，而是**交织在模型的参数空间中**。如何将特定能力"解耦"出来，是整个技术体系的核心难题。

## Skill 蒸馏技术全景

Skill 蒸馏的完整流程可以概括为五个阶段，每个阶段都有其核心任务和技术挑战：

```mermaid
graph TD
    A[能力识别与分析] --> B[蒸馏数据构造]
    B --> C[蒸馏训练]
    C --> D[能力评估]
    D --> E[能力增强与组合]
    E -->|迭代优化| A
    
    A --> A1[能力探测]
    A --> A2[能力归因]
    A --> A3[边界测试]
    
    B --> B1[定向数据生成]
    B --> B2[数据增强]
    B --> B3[质量控制]
    
    C --> C1[能力定向微调]
    C --> C2[CoT 蒸馏]
    C --> C3[对比式蒸馏]
    C --> C4[RLHF 蒸馏]
    
    D --> D1[保真度评估]
    D --> D2[泛化评估]
    D --> D3[退化检测]
    
    E --> E1[迭代萃取]
    E --> E2[能力组合]
    E --> E3[能力路由]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

下面我们将逐一深入每个阶段的技术细节。

## 能力识别与分析

### 能力探测

**能力探测**（Capability Probing）是 Skill 蒸馏的第一步：在蒸馏之前，我们需要明确 Teacher 模型到底具备哪些能力，以及这些能力的强度如何。

#### 探测数据集设计

一个有效的探测数据集需要满足以下要求：

1. **覆盖性**：覆盖目标能力的各个子维度
2. **区分度**：能够区分不同能力水平的模型
3. **纯净性**：尽量减少其他能力的干扰

例如，要探测模型的数学推理能力，可以设计如下分层探测集：

```python
import json
from typing import List, Dict

def build_math_probe_dataset(levels: List[str]) -> Dict[str, List[Dict]]:
    """构建分层数学推理探测数据集
    
    Args:
        levels: 能力层级列表，如 ['basic', 'intermediate', 'advanced', 'expert']
    
    Returns:
        分层探测数据集
    """
    probe_templates = {
        'basic': {
            'desc': '基础算术运算',
            'examples': [
                {'question': '计算 15 + 27 × 3', 'answer': 96, 'skill': 'arithmetic'},
                {'question': '求 144 的平方根', 'answer': 12, 'skill': 'arithmetic'},
            ]
        },
        'intermediate': {
            'desc': '代数与方程求解',
            'examples': [
                {'question': '解方程 2x² + 5x - 3 = 0', 'answer': 'x = 1/2 或 x = -3', 'skill': 'algebra'},
                {'question': '化简 (a+b)³', 'answer': 'a³+3a²b+3ab²+b³', 'skill': 'algebra'},
            ]
        },
        'advanced': {
            'desc': '多步推理与应用题',
            'examples': [
                {
                    'question': '一列火车以60km/h速度行驶，2小时后另一列火车从同一站点以80km/h同向出发，几小时后追上？',
                    'answer': '6小时', 'skill': 'word_problem'
                },
            ]
        },
        'expert': {
            'desc': '竞赛级数学证明',
            'examples': [
                {
                    'question': '证明：对于任意正整数 n，n³ - n 能被 6 整除',
                    'answer': 'n³-n = n(n-1)(n+1) = (n-1)n(n+1)，三个连续整数之积必被6整除',
                    'skill': 'proof'
                },
            ]
        }
    }
    
    dataset = {}
    for level in levels:
        if level in probe_templates:
            dataset[level] = probe_templates[level]['examples']
    
    return dataset

# 构建探测集
probe_data = build_math_probe_dataset(['basic', 'intermediate', 'advanced', 'expert'])
print(json.dumps(probe_data, ensure_ascii=False, indent=2))
```

通过对 Teacher 模型在探测集上的表现进行分析，我们可以绘制出**能力雷达图**，直观展示模型在各能力维度上的分布，从而确定蒸馏的优先目标。

### 能力归因分析

确定了模型具备某种能力后，下一个关键问题是：**这种能力存储在模型的哪些参数中？** 这就是能力归因分析（Capability Attribution）要解决的问题。

#### 注意力归因分数

研究表明，Transformer 模型中的特定注意力头（Attention Head）与特定能力高度相关。我们可以用注意力归因分数来量化每个注意力头对特定能力的贡献：

$$
A_{h}^{(l)} = \frac{1}{N} \sum_{i=1}^{N} \sum_{t=1}^{T_i} \alpha_{h,t}^{(l)} \cdot \mathbb{1}[y_i = \hat{y}_i]
$$

其中：
- $A_{h}^{(l)}$ 是第 $l$ 层第 $h$ 个注意力头的归因分数
- $N$ 是测试样本数
- $T_i$ 是第 $i$ 个样本的序列长度
- $\alpha_{h,t}^{(l)}$ 是该注意力头在第 $t$ 个 token 上的注意力权重
- $\mathbb{1}[y_i = \hat{y}_i]$ 是指示函数，模型预测正确时为 1

通过归因分析，我们可以识别出与目标能力强相关的**关键注意力头和层**，为后续的定向蒸馏提供指导。例如，研究发现某些层的注意力头专门负责代码语法理解，而另一些层负责逻辑推理。

#### 层级重要性分析

除了注意力头级别，我们还可以分析模型层级对能力的重要性。一种常用方法是**逐层消融实验**：逐层禁用某一层的输出，观察目标能力的变化程度：

$$
I^{(l)} = \text{Score}_{full} - \text{Score}_{\backslash l}
$$

其中 $I^{(l)}$ 是第 $l$ 层的重要性分数，$\text{Score}_{\backslash l}$ 表示禁用第 $l$ 层后的能力评分。重要性分数越高，说明该层对目标能力的贡献越大。

### 能力边界测试

能力边界测试旨在确定模型特定能力的**上限和边界**：在什么复杂度下能力开始失效？在什么场景下能力无法泛化？

边界测试通常采用**难度递增**的策略，逐步增加任务的复杂度，直到模型能力出现断崖式下降。例如，对于代码生成能力，可以从单行代码 → 简单函数 → 复杂算法 → 多文件项目逐步递增。

通过边界测试，我们可以绘制出**能力衰减曲线**，明确蒸馏时需要覆盖的难度范围，避免蒸馏后的模型只在简单任务上有效。

## 蒸馏数据构造

数据是 Skill 蒸馏的核心。高质量的定向数据决定了蒸馏效果的上限。

### 能力定向数据生成

与传统蒸馏使用通用数据不同，Skill 蒸馏需要**针对特定能力生成高质量训练数据**。这通常通过让 Teacher 模型（如 GPT-4）在特定能力领域生成大量带高质量推理过程的数据来实现。

```python
import openai
import json
from typing import List, Dict
from dataclasses import dataclass, asdict

@dataclass
class SkillDataPoint:
    """能力定向数据点"""
    skill_type: str          # 能力类型: code/math/tool/...
    difficulty: str          # 难度: easy/medium/hard/expert
    instruction: str         # 指令/问题
    reasoning: str           # 推理过程 (CoT)
    response: str            # 最终回答
    quality_score: float     # 质量评分

def generate_skill_directed_data(
    skill_type: str,
    num_samples: int,
    teacher_model: str = "gpt-4",
    difficulty_levels: List[str] = None
) -> List[SkillDataPoint]:
    """使用 Teacher 模型生成能力定向训练数据
    
    Args:
        skill_type: 目标能力类型
        num_samples: 生成样本数
        teacher_model: Teacher 模型名称
        difficulty_levels: 难度层级
    
    Returns:
        能力定向数据集
    """
    if difficulty_levels is None:
        difficulty_levels = ["easy", "medium", "hard", "expert"]
    
    skill_prompts = {
        "code": "你是一个编程专家。请生成一道编程题目，并给出详细的解题思路和Python代码实现。要求：1)题目有实际应用场景 2)解题思路清晰 3)代码包含注释 4)附带测试用例",
        "math": "你是一个数学教育家。请生成一道数学推理题，并给出详细的逐步推理过程。要求：1)题目需要多步推理 2)推理过程严谨 3)最终给出明确答案",
        "tool": "你是一个Agent设计专家。请设计一个需要使用外部工具（搜索、计算器、代码执行等）的复杂任务，并给出完整的工具调用推理链。要求：1)任务贴近实际 2)推理链完整 3)每步说明调用哪个工具及原因",
    }
    
    system_prompt = skill_prompts.get(skill_type, skill_prompts["code"])
    dataset = []
    samples_per_level = num_samples // len(difficulty_levels)
    
    for difficulty in difficulty_levels:
        difficulty_hint = {
            "easy": "题目难度：入门级，适合初学者",
            "medium": "题目难度：中等，需要一定基础",
            "hard": "题目难度：困难，需要深入理解",
            "expert": "题目难度：专家级，需要创造性思维",
        }[difficulty]
        
        full_prompt = f"{system_prompt}\n\n{difficulty_hint}\n\n请以JSON格式输出：{{\"instruction\": \"...\", \"reasoning\": \"...\", \"response\": \"...\"}}"
        
        for _ in range(samples_per_level):
            try:
                resp = openai.chat.completions.create(
                    model=teacher_model,
                    messages=[
                        {"role": "system", "content": "你是一个高质量数据生成器。"},
                        {"role": "user", "content": full_prompt},
                    ],
                    temperature=0.8,  # 适当提高温度增加多样性
                )
                content = resp.choices[0].message.content
                parsed = json.loads(content)
                
                data_point = SkillDataPoint(
                    skill_type=skill_type,
                    difficulty=difficulty,
                    instruction=parsed.get("instruction", ""),
                    reasoning=parsed.get("reasoning", ""),
                    response=parsed.get("response", ""),
                    quality_score=0.0,  # 待后续质量评估
                )
                dataset.append(data_point)
            except Exception as e:
                print(f"生成失败: {e}")
                continue
    
    return dataset

# 使用示例
# dataset = generate_skill_directed_data("code", num_samples=1000)
# print(f"生成 {len(dataset)} 条代码能力数据")
```

上述代码展示了如何系统性地使用 Teacher 模型生成分层、分难度的能力定向数据。关键设计点包括：**难度分层**确保数据覆盖从易到难的全谱系，**温度调节**平衡数据质量与多样性，**结构化输出**便于后续质量控制。

### 数据增强策略

#### 思维链数据增强

思维链（Chain-of-Thought, CoT）数据是 Skill 蒸馏的核心资产。除了直接让 Teacher 生成 CoT，还可以通过以下策略增强：

1. **多路径 CoT**：对同一问题生成多条不同的推理路径，增加推理多样性
2. **CoT 重写**：将 Teacher 的 CoT 用不同风格重写（简洁版、详细版、类比版）
3. **反向推理**：从答案出发逆向构造推理链，增强推理的鲁棒性

#### 困难样本挖掘

困难样本对能力提升至关重要。可以通过以下方式挖掘：

```python
def mine_hard_examples(
    student_model_predictions: List[Dict],
    difficulty_threshold: float = 0.5
) -> List[Dict]:
    """从 Student 模型的预测中挖掘困难样本
    
    困难样本定义：Student 模型预测错误或置信度低的样本
    
    Args:
        student_model_predictions: Student 模型的预测结果
        difficulty_threshold: 困难度阈值
    
    Returns:
        困难样本列表
    """
    hard_examples = []
    for pred in student_model_predictions:
        is_correct = pred['predicted'] == pred['ground_truth']
        confidence = pred.get('confidence', 0.0)
        
        # 预测错误 或 置信度低 → 困难样本
        if not is_correct or confidence < difficulty_threshold:
            pred['hardness'] = 1.0 - confidence if is_correct else 1.0
            hard_examples.append(pred)
    
    # 按困难度排序
    hard_examples.sort(key=lambda x: x['hardness'], reverse=True)
    return hard_examples
```

挖掘到的困难样本会被重新送入 Teacher 模型生成高质量 CoT，然后加入训练集进行针对性强化。这种**"发现弱点 → 定向补强"**的迭代策略是提升蒸馏效果的关键。

#### 负样本构造

负样本在对比式蒸馏中尤为重要。好的负样本应该"似是而非"——表面合理但实际错误，帮助 Student 学会区分正确和错误的能力表达：

- **推理错误型**：推理过程中某一步出现逻辑错误
- **格式错误型**：推理正确但输出格式不符合要求
- **幻觉型**：推理中引入了不存在的事实或函数

### 数据质量控制

#### 一致性检验

对 Teacher 生成的数据，需要验证其正确性。常用方法包括：

1. **自一致性**（Self-Consistency）：让 Teacher 多次生成同一问题的答案，取多数一致的结果
2. **执行验证**：对代码类数据，实际运行代码验证输出
3. **交叉验证**：用不同 Teacher 模型生成，对比一致性

#### 多样性保证

数据多样性直接影响蒸馏后模型的泛化能力。我们可以用以下公式度量数据集的多样性：

$$
D(\mathcal{S}) = -\sum_{i=1}^{M} p_i \log p_i, \quad p_i = \frac{n_i}{N}
$$

其中 $\mathcal{S}$ 是数据集，$M$ 是语义聚类的数量，$n_i$ 是第 $i$ 个聚类中的样本数，$N$ 是总样本数。$D(\mathcal{S})$ 越大表示数据多样性越高。当多样性不足时，可以通过追加生成或重采样来补充。

## Skill 蒸馏训练方法

### 能力定向微调

能力定向微调（Skill-Directed SFT）是最基础的 Skill 蒸馏方法：使用能力定向数据对 Student 模型进行监督微调。

#### 损失函数设计

标准 SFT 使用交叉熵损失，但在 Skill 蒸馏中，我们需要**对不同能力组件赋予不同权重**：

$$
\mathcal{L}_{skill\_sft} = \sum_{i=1}^{N} \sum_{t=1}^{T_i} w_t \cdot \text{CE}(y_{i,t}, \hat{y}_{i,t})
$$

其中 $w_t$ 是第 $t$ 个 token 的权重。对于 CoT 数据，我们通常对推理过程部分的 token 赋予更高权重：

$$
w_t = \begin{cases} \alpha & \text{if token}_t \in \text{reasoning part} \\ 1 & \text{if token}_t \in \text{other parts} \end{cases}
$$

其中 $\alpha > 1$ 是推理增强系数，引导模型更关注推理过程的学习。

### CoT 蒸馏

CoT 蒸馏是 Skill 蒸馏中最核心的方法之一。其核心思想是：不仅蒸馏最终答案，更蒸馏**推理过程本身**。

```mermaid
graph LR
    subgraph Teacher
        T1[问题输入] --> T2[推理步骤 1]
        T2 --> T3[推理步骤 2]
        T3 --> T4[推理步骤 3]
        T4 --> T5[最终答案]
    end
    
    subgraph Student 学习过程
        S1[问题输入] --> S2[学习推理步骤 1]
        S2 --> S3[学习推理步骤 2]
        S3 --> S4[学习推理步骤 3]
        S4 --> S5[生成最终答案]
    end
    
    T2 -.->|蒸馏| S2
    T3 -.->|蒸馏| S3
    T4 -.->|蒸馏| S4
    
    style T2 fill:#fff3e0
    style T3 fill:#fff3e0
    style T4 fill:#fff3e0
    style S2 fill:#e8f5e9
    style S3 fill:#e8f5e9
    style S4 fill:#e8f5e9
```

CoT 蒸馏的损失函数在标准 SFT 损失基础上，增加了对推理链一致性的约束：

$$
\mathcal{L}_{cot} = \mathcal{L}_{sft} + \lambda \cdot \mathcal{L}_{reasoning\_consist}
$$

其中推理一致性损失 $\mathcal{L}_{reasoning\_consist}$ 可以定义为 Student 和 Teacher 推理过程的 KL 散度：

$$
\mathcal{L}_{reasoning\_consist} = \text{KL}\left(p_{student}(\mathbf{r}|\mathbf{x}) \| p_{teacher}(\mathbf{r}|\mathbf{x})\right)
$$

其中 $\mathbf{r}$ 是推理过程序列，$\mathbf{x}$ 是输入。$\lambda$ 是平衡系数，控制推理一致性约束的强度。

实践表明，CoT 蒸馏相比直接 SFT 能显著提升 Student 的推理能力，尤其是在数学和代码等需要多步推理的任务上。

### 对比式能力蒸馏

对比式能力蒸馏（Contrastive Skill Distillation）的核心思想是：让 Student 模型学会区分**"好的能力表达"**和**"坏的能力表达"**，而不仅仅是模仿 Teacher。

通过构造正样本（Teacher 的高质量输出）和负样本（低质量或错误输出），对比损失函数为：

$$
\mathcal{L}_{contrast} = -\log \frac{\exp\left(\text{sim}(h_s, h^+)/\tau\right)}{\exp\left(\text{sim}(h_s, h^+)/\tau\right) + \sum_{j=1}^{K} \exp\left(\text{sim}(h_s, h_j^-)/\tau\right)}
$$

其中：
- $h_s$ 是 Student 模型的隐层表示
- $h^+$ 是正样本（Teacher 输出）的隐层表示
- $h_j^-$ 是第 $j$ 个负样本的隐层表示
- $\text{sim}(\cdot, \cdot)$ 是相似度函数（如余弦相似度）
- $\tau$ 是温度参数
- $K$ 是负样本数量

对比式蒸馏的优势在于：它不仅教会 Student "做什么"，还教会它"不做什么"，从而获得更清晰的能力边界。这在工具使用能力蒸馏中尤为重要——Student 需要学会何时调用工具、何时不调用。

### RLHF-based 能力蒸馏

RLHF-based 能力蒸馏将 Teacher 模型作为**奖励模型**（Reward Model），通过强化学习引导 Student 模型发展目标能力。

```mermaid
graph TD
    A[Student 模型] -->|生成输出| B[输出候选]
    B --> C[Teacher 模型<br/>作为奖励模型]
    C -->|评分| D[奖励信号]
    D --> E[PPO 训练]
    E -->|更新参数| A
    
    F[能力定向提示词] --> A
    G[KL 散度约束<br/>防止偏离过远] --> E
    
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#e1f5fe
```

RLHF 蒸馏的优化目标为：

$$
\max_{\theta} \mathbb{E}_{\mathbf{y} \sim \pi_\theta(\cdot|\mathbf{x})} \left[ R_\phi(\mathbf{x}, \mathbf{y}) \right] - \beta \cdot \text{KL}\left(\pi_\theta(\cdot|\mathbf{x}) \| \pi_{ref}(\cdot|\mathbf{x})\right)
$$

其中：
- $R_\phi(\mathbf{x}, \mathbf{y})$ 是 Teacher 模型给出的奖励分数
- $\pi_\theta$ 是 Student 模型的策略
- $\pi_{ref}$ 是参考策略（通常是 SFT 后的 Student）
- $\beta$ 是 KL 惩罚系数，防止 Student 偏离参考策略过远

Teacher 作为奖励模型时，可以采用多种评分策略：

1. **成对比较**：让 Teacher 比较两个 Student 输出的优劣，训练偏好模型
2. **绝对评分**：让 Teacher 对 Student 输出直接打分（1-5 分）
3. **细粒度评分**：让 Teacher 对推理过程的每一步进行评分

### 多能力联合蒸馏

实际应用中，我们往往需要同时蒸馏多种能力到同一模型中。但多能力蒸馏面临**能力冲突**问题：优化一种能力可能损害另一种能力（类似灾难性遗忘）。

| 策略 | 方法 | 优点 | 缺点 |
|------|------|------|------|
| **顺序蒸馏** | 逐个能力依次蒸馏 | 实现简单 | 严重遗忘问题 |
| **混合蒸馏** | 将多能力数据混合训练 | 遗忘较轻 | 能力间可能互相干扰 |
| **加权混合** | 按能力重要性分配数据比例 | 平衡性好 | 需要调参 |
| **参数隔离** | 不同能力使用不同 LoRA 模块 | 无冲突 | 模块间切换开销 |
| **课程蒸馏** | 按难度递增顺序蒸馏 | 渐进式提升 | 训练时间较长 |
| **对抗蒸馏** | 引入对抗样本平衡多能力 | 冲突最小化 | 训练不稳定 |

对于参数隔离策略，可以为每种能力训练独立的 LoRA 适配器，推理时根据任务类型动态加载：

```python
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import AutoModelForCausalLM
import torch

class MultiSkillModel:
    """多能力模型：为每种能力维护独立的 LoRA 适配器"""
    
    def __init__(self, base_model_name: str, skill_names: list):
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name, torch_dtype=torch.float16
        )
        self.skill_names = skill_names
        self.skill_adapters = {}
        
        # 为每种能力配置 LoRA
        for skill in skill_names:
            lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                lora_dropout=0.05,
            )
            skill_model = get_peft_model(self.base_model, lora_config)
            self.skill_adapters[skill] = skill_model
    
    def inference(self, input_text: str, skill: str):
        """根据指定能力路由到对应的适配器"""
        if skill not in self.skill_adapters:
            raise ValueError(f"未知能力: {skill}")
        
        model = self.skill_adapters[skill]
        model.eval()
        # 推理逻辑...
        return model.generate(input_text)
```

## 能力评估体系

蒸馏效果的评估是 Skill 蒸馏中容易被忽视但至关重要的环节。传统评估只看综合分数，而 Skill 蒸馏需要**多维度、分能力**的精细化评估。

### 评估维度

Skill 蒸馏的评估应覆盖以下三个核心维度：

**1. 能力保真度（Fidelity）**

衡量 Student 在目标能力上与 Teacher 的接近程度：

$$
\text{Fidelity} = \frac{\text{Score}_{student}^{skill}}{\text{Score}_{teacher}^{skill}} \times 100\%
$$

保真度越高，说明能力迁移越成功。实践中，70-80% 的保真度通常已经具备实用价值。

**2. 能力泛化（Generalization）**

衡量蒸馏后的能力是否能在**分布外**（OOD）数据上泛化：

$$
\text{Generalization} = \frac{\text{Score}_{student}^{OOD}}{\text{Score}_{student}^{ID}} \times 100\%
$$

其中 ID（In-Distribution）是训练数据同分布的测试集，OOD 是分布外测试集。泛化率过低说明蒸馏可能只是"记住"了训练数据而非真正获得了能力。

**3. 能力强度（Strength）**

衡量蒸馏后能力的绝对水平，通常用通过率或准确率表示：

$$
\text{Strength} = \frac{\text{正确样本数}}{\text{总样本数}} \times 100\%
$$

### 评估基准

| 能力类型 | 评估基准 | 评估指标 | 说明 |
|---------|---------|---------|------|
| 代码生成 | HumanEval | Pass@1 / Pass@10 | 函数级代码正确性 |
| 代码生成 | MBPP | Pass@1 | 基础编程能力 |
| 代码生成 | CodeContests | Pass@k | 竞赛级编程 |
| 数学推理 | GSM8K | Accuracy | 小学数学应用题 |
| 数学推理 | MATH | Accuracy | 竞赛级数学 |
| 工具使用 | ToolBench | Success Rate | 工具调用成功率 |
| 工具使用 | AgentBench | Success Rate | Agent 任务完成率 |
| 指令遵循 | IFEval | Strict / Loose | 指令约束遵守率 |
| 多语言 | XNLI | Accuracy | 跨语言推理 |
| 综合能力 | MT-Bench | Score (1-10) | 多轮对话综合评估 |

### 能力退化检测

Skill 蒸馏的一个重要风险是：**在增强目标能力的同时，其他能力可能退化**。因此，蒸馏后必须进行能力退化检测。

退化检测的方法是：在蒸馏前后，用一套**通用能力评估集**测试模型，对比各项能力的变化：

$$
\Delta_{skill_j} = \text{Score}_{after}^{skill_j} - \text{Score}_{before}^{skill_j}
$$

如果 $\Delta_{skill_j} < -\epsilon$（$\epsilon$ 为退化容忍阈值），则说明能力 $j$ 发生了显著退化，需要通过数据混合或正则化等手段进行修复。

```python
def detect_capability_regression(
    before_scores: Dict[str, float],
    after_scores: Dict[str, float],
    threshold: float = 0.03
) -> Dict[str, dict]:
    """检测能力退化
    
    Args:
        before_scores: 蒸馏前各能力评分
        after_scores: 蒸馏后各能力评分
        threshold: 退化告警阈值
    
    Returns:
        各能力的变化情况
    """
    results = {}
    for skill, before_score in before_scores.items():
        after_score = after_scores.get(skill, 0.0)
        delta = after_score - before_score
        results[skill] = {
            'before': before_score,
            'after': after_score,
            'delta': delta,
            'status': '退化' if delta < -threshold else ('提升' if delta > threshold else '持平')
        }
    return results

# 示例：检测代码能力蒸馏后的各项能力变化
before = {'code': 0.35, 'math': 0.52, 'instruction': 0.71, 'multilingual': 0.68, 'safety': 0.95}
after  = {'code': 0.72, 'math': 0.50, 'instruction': 0.69, 'multilingual': 0.65, 'safety': 0.94}

regression = detect_capability_regression(before, after)
for skill, info in regression.items():
    print(f"{skill}: {info['before']:.2f} → {info['after']:.2f} ({info['status']}, Δ={info['delta']:+.2f})")
# 输出示例:
# code: 0.35 → 0.72 (提升, Δ=+0.37)
# math: 0.52 → 0.50 (持平, Δ=-0.02)
# instruction: 0.71 → 0.69 (持平, Δ=-0.02)
# multilingual: 0.68 → 0.65 (退化, Δ=-0.03)
# safety: 0.95 → 0.94 (持平, Δ=-0.01)
```

上述示例中，代码能力大幅提升（+0.37），但多语言能力出现退化（-0.03），需要在后续迭代中加入少量多语言数据进行修复。

## 实践案例

### 代码能力蒸馏

本案例展示如何将 GPT-4 的代码生成能力蒸馏到 7B 参数的开源模型（如 CodeLlama-7B 或 Qwen-7B）。

#### 数据构造

1. **种子问题收集**：从 LeetCode、Codeforces 等平台收集 5000 道编程题
2. **CoT 数据生成**：用 GPT-4 为每道题生成详细的解题思路 + 代码实现 + 测试用例
3. **数据清洗**：执行生成的代码，过滤掉无法通过测试用例的样本
4. **难度分层**：按通过率和代码复杂度分为 easy/medium/hard/expert 四级

#### 训练配置

| 配置项 | 值 |
|-------|-----|
| Base 模型 | Qwen-7B |
| 训练方法 | LoRA (r=64, alpha=128) |
| 学习率 | 2e-4 |
| Batch Size | 64 (有效) |
| 训练轮数 | 3 |
| CoT 权重 $\alpha$ | 2.0 |
| 数据量 | ~15,000 条 |
| 最大序列长度 | 4096 |

#### 效果对比

| 评估基准 | Base 模型 (Qwen-7B) | 蒸馏后 | GPT-4 (Teacher) | 保真度 |
|---------|--------------------|-------|-----------------|-------|
| HumanEval Pass@1 | 35.4% | 68.2% | 85.1% | 80.1% |
| MBPP Pass@1 | 42.1% | 71.5% | 83.2% | 85.9% |
| CodeContests Pass@1 | 8.2% | 22.6% | 32.1% | 70.4% |
| 代码解释准确率 | 51.3% | 76.8% | 91.5% | 83.9% |
| 代码调试成功率 | 28.7% | 58.3% | 78.9% | 73.9% |

蒸馏后的 7B 模型在代码能力上达到了 GPT-4 的 70-86%，而参数量仅为 GPT-4 的极小部分，充分验证了 Skill 蒸馏的有效性。

### 数学推理能力蒸馏

数学推理能力的蒸馏核心在于 CoT 数据的质量。以 GSM8K 和 MATH 为目标基准：

#### CoT 数据生成策略

采用**渐进式 CoT 生成**策略，参考 WizardMath 的方法：

1. 从基础数学题出发，通过**深度进化**（Deepen Evolving）逐步增加题目难度
2. 让 Teacher 模型为每道题生成多条推理路径，通过**自一致性投票**筛选最优路径
3. 对推理过程进行**步骤级质量标注**，标记每个推理步骤的正确性和必要性

#### 蒸馏效果

| 评估基准 | Base 模型 | 蒸馏后 | Teacher (GPT-4) |
|---------|----------|-------|-----------------|
| GSM8K | 38.5% | 72.3% | 92.0% |
| MATH | 12.1% | 35.6% | 52.9% |
| SVAMP | 45.2% | 78.1% | 89.5% |

关键发现：CoT 蒸馏对 GSM8K（小学数学）的提升显著（+33.8%），但对 MATH（竞赛级数学）的提升相对有限（+23.5%），说明高难度能力的蒸馏需要更多数据和更精细的方法。

### 工具使用能力蒸馏

工具使用能力（Agent 能力）的蒸馏是当前最前沿的方向之一。目标是将大模型的工具调用、任务规划、多步执行能力迁移到小模型。

```mermaid
graph TD
    subgraph Teacher Agent
        TA1[任务理解] --> TA2[工具选择]
        TA2 --> TA3[参数构造]
        TA3 --> TA4[工具调用]
        TA4 --> TA5[结果解析]
        TA5 --> TA6[下一步规划]
        TA6 -->|循环| TA2
    end
    
    subgraph 蒸馏数据
        D1[任务-工具调用轨迹]
        D2[工具选择推理]
        D3[参数构造示例]
        D4[错误恢复策略]
    end
    
    subgraph Student Agent
        SA1[任务理解] --> SA2[工具选择]
        SA2 --> SA3[参数构造]
        SA3 --> SA4[工具调用]
        SA4 --> SA5[结果解析]
        SA5 --> SA6[下一步规划]
        SA6 -->|循环| SA2
    end
    
    TA1 -.->|蒸馏| D1
    TA2 -.->|蒸馏| D2
    TA3 -.->|蒸馏| D3
    TA4 -.->|蒸馏| D4
    D1 -.->|训练| SA1
    D2 -.->|训练| SA2
    D3 -.->|训练| SA3
    D4 -.->|训练| SA4
    
    style TA1 fill:#e1f5fe
    style SA1 fill:#e8f5e9
```

工具使用能力蒸馏的特殊之处在于：需要蒸馏的不仅是单步决策，还包括**多步轨迹规划**和**错误恢复**能力。实践表明，在蒸馏数据中加入 Teacher 的错误恢复轨迹（即工具调用失败后如何调整策略），能显著提升 Student Agent 的鲁棒性。

## 能力增强与组合

### 迭代能力萃取

单轮蒸馏往往无法达到理想效果，**迭代能力萃取**通过多轮"蒸馏-评估-补强"的循环逐步增强模型能力：

```mermaid
graph LR
    A[第 1 轮蒸馏] --> B[能力评估]
    B --> C{达标?}
    C -->|否| D[困难样本挖掘]
    D --> E[定向数据补充]
    E --> F[第 2 轮蒸馏]
    F --> B
    C -->|是| G[蒸馏完成]
    
    style A fill:#e1f5fe
    style F fill:#e1f5fe
    style G fill:#e8f5e9
```

每一轮迭代中，重点在于**发现模型的薄弱环节**并针对性补强。例如，Orca 的渐进式学习方法就是典型的迭代萃取：从简单的解释 traces 开始，逐步过渡到复杂的推理策略。

### 能力组合

将多种 Skill 蒸馏到同一模型是实现通用型小模型的关键路径：

```mermaid
graph TD
    A[Base 模型 7B] --> B[代码能力蒸馏]
    A --> C[数学能力蒸馏]
    A --> D[工具使用蒸馏]
    
    B --> E[代码 LoRA]
    C --> F[数学 LoRA]
    D --> G[Agent LoRA]
    
    E --> H[能力融合]
    F --> H
    G --> H
    
    H --> I[多能力小模型<br/>Code+Math+Agent]
    
    J[能力路由器] -->|代码任务| E
    J -->|数学任务| F
    J -->|Agent任务| G
    
    style H fill:#fff3e0
    style I fill:#e8f5e9
    style J fill:#fce4ec
```

能力组合有两种主要策略：

1. **参数融合**：将不同能力的 LoRA 适配器合并，需要处理能力间的参数冲突
2. **动态路由**：保持各能力适配器独立，推理时由路由器选择加载哪个适配器

### 能力路由

当单个小模型无法同时承载多种能力时，**能力路由**（Skill Routing）提供了一种分布式方案：将不同 Skill 路由到不同的小模型，由一个轻量级路由器进行调度。

路由器的核心是一个分类器，根据输入特征预测应激活哪个 Skill 模型：

$$
P(skill_j | \mathbf{x}) = \text{softmax}(\mathbf{W}_r \cdot \text{Enc}(\mathbf{x}))
$$

其中 $\mathbf{W}_r$ 是路由器的参数，$\text{Enc}(\mathbf{x})$ 是输入编码。路由器的训练数据可以来自 Teacher 模型在各能力上的表现分布。

## 前沿方向

### 自动化 Skill 发现

当前 Skill 的识别主要依赖人工经验和领域知识，未来趋势是**自动化发现模型中的潜在能力**。通过无监督的能力探测和聚类分析，自动识别模型中尚未被显式训练但已经具备的"涌现能力"，为蒸馏提供新的目标。

### 跨模型能力迁移

目前的 Skill 蒸馏主要在同一架构族内进行（如 LLaMA 系列）。跨架构的能力迁移——例如将 GPT-4 的能力迁移到 Mistral 架构——面临更大的挑战，因为不同架构的隐空间表示不同。基于表示对齐（Representation Alignment）的跨模型蒸馏是一个有前景的方向。

### 能力可解释性

理解 Skill 在模型中"存储在哪里、如何运作"对于精准蒸馏至关重要。结合机械可解释性（Mechanical Interpretability）研究，未来有望实现**能力级别的精确定位和提取**——像外科手术一样精确地提取特定能力对应的参数子集。

### Skill 库与复用

随着 Skill 蒸馏技术的成熟，未来可能形成**标准化的 Skill 库**：各种经过蒸馏和验证的能力模块以即插即用的方式存在，开发者可以像搭积木一样组合所需能力。这将极大降低定制化模型的开发成本，推动大模型的普及应用。

## 结语

Skill 蒸馏与能力萃取技术代表了从"模型压缩"到"能力工程"的范式转变。它不再追求将大模型整体缩小，而是精准地提取和迁移我们所需的那部分能力，使小模型在特定领域达到接近大模型的水平。

从技术演进的角度看，Skill 蒸馏的发展趋势是：**从人工到自动化、从单一到组合、从粗粒度到精细化**。随着能力探测、归因分析和自动化蒸馏技术的不断进步，我们有望在未来看到更多高质量的专项小模型，它们在各自领域内媲美甚至超越通用大模型，同时保持极低的部署成本。

对于实践者而言，掌握 Skill 蒸馏技术的关键在于：**明确目标能力、构造高质量定向数据、选择合适的蒸馏方法、建立精细化评估体系**。这条路径虽然需要更多的工程投入，但换来的是更高效、更经济、更可控的模型能力定制。

## 参考文献

1. Fu Y, Peng L, Sachidananda V, et al. Specializing Smaller Language Models towards Multi-Step Reasoning[C]. International Conference on Machine Learning (ICML), 2023.
2. Magister L C, White C, Harvill J, et al. Teaching Small Language Models to Reason[C]. Annual Meeting of the Association for Computational Linguistics (ACL), 2023.
3. Mukherjee S, Arora A, Guan J, et al. Orca: Progressive Learning from Complex Explanation Traces of GPT-4[J]. arXiv preprint arXiv:2306.02707, 2023.
4. Xu Y, Li Z, Zhang J, et al. A Survey on Knowledge Distillation of Large Language Models[J]. arXiv preprint arXiv:2402.13116, 2024.
5. Luo H, Sun P, Li C, et al. WizardMath: Empowering Mathematical Reasoning for Large Language Models via Reinforced Evol-Instruct[J]. arXiv preprint arXiv:2308.09783, 2023.
6. Mukherjee S, Mitra A, Jawahar G, et al. Orca 2: Teaching Small Language Models How to Reason[J]. arXiv preprint arXiv:2311.11045, 2023.
7. Hsieh C P, Sun S, Kriman S, et al. Distilling Step-by-Step! Outperforming Larger Language Models with Less Training Data and Smaller Model Sizes[C]. Findings of ACL, 2023.
8. Wang Y, Kordi Y, Mishra S, et al. Self-Instruct: Aligning Language Models with Self-Generated Instructions[C]. ACL, 2023.
9. Taori S, Gulrajani I, Zhang T, et al. Stanford Alpaca: An Instruction-following LLaMA Model[J]. GitHub repository, 2023.
10. Chiang W L, Li Z, Lin Z, et al. Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90% ChatGPT Quality[J]. Blog post, 2023.
