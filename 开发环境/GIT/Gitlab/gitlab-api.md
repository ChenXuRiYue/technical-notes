# 📌 gitlab - api

Gitlab 对外提供了一系列 api。该文档总结整理遇到的相关 API ，并且输出 prompt，python 工具。

## 📄 信息收集

### 🔖 获取所有项目

```python
import os
import requests
from urllib.parse import quote

GITLAB_URL = "https://git.sample.com/" # git 地址
TOKEN = "aaaaaaaaaaaaaaaaaaaa"         # token 令牌

headers = {"PRIVATE-TOKEN": TOKEN}
params = {"simple": True,							 # 简洁模式
          "per_page": 100,             # 每页 100 为峰值。需要分页拉完
          "with_shared": False,        # 排除共享项目
          "page": 1}                   # 页号
all_clone_urls = []

while True:
    resp = requests.get(f"{GITLAB_URL}/api/v4/groups/{namespace}/projects", headers=headers, params=params)
    projects = resp.json()
    if not projects:
        break
    for p in projects:
        all_clone_urls.append(p["http_url_to_repo"])
    params["page"] += 1

for url in sorted(all_clone_urls):
    print(url)
```

### 🔖 推送提交到 gitlab

```bash
curl --request POST \
  --url "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/merge_requests" \
  --header "PRIVATE-TOKEN: <YOUR_ACCESS_TOKEN>" \
  --header "Content-Type: application/json" \
  --data '{
    "source_branch": "feature/my-new-feature",
    "target_branch": "main",
    "title": "feat: add new feature",
    "description": "Automated MR via API",
    "remove_source_branch": true,
    "squash": false,
    "labels": "ai-generated,needs-review"
  }'
```



### 🔖 获取 merge 列表

- 上述提 merge 的 API 中，可以获取具有丰富信息的响应

```python
{
  "id": 12345678,
  "iid": 42,                # merge Id
  "project_id": 98765,
  "title": "feat: add login",
  "description": "...",
  "state": "opened",
  "source_branch": "feature/login",
  "target_branch": "main",
  "web_url": "https://gitlab.example.com/group/project/-/merge_requests/42"
}
```

- 或者一次拉取所有 merge List

```python
import requests
from urllib.parse import quote
from typing import List, Dict, Any

# --- 配置 ---
GITLAB_URL = "https://git.sample.com/"
PRIVATE_TOKEN = "aaaaaaaaaaaaaaaaaaaa"
GROUP_PATH = "your-top-group"

HEADERS = {"PRIVATE-TOKEN": PRIVATE_TOKEN}

MR_FILTERS = {
    "state": "opened",
    "labels": "ai-generated",
    "author_username": "ai-bot",
    "target_branch": "main",
    "per_page": 100,
}


# --- 工具函数 ---
def fetch_all_projects(group_path: str) -> List[Dict[str, Any]]:
    projects = []
    page = 1
    while True:
        resp = requests.get(
            f"{GITLAB_URL}/api/v4/groups/{quote(group_path, safe='')}/projects",
            headers=HEADERS,
            params={
                "include_subgroups": True,
                "with_shared": False,
                "per_page": 100,
                "page": page,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        projects.extend(data)
        page += 1
    return projects


def fetch_mr_urls(project_id: int) -> List[str]:
    urls = []
    page = 1
    while True:
        resp = requests.get(
            f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests",
            headers=HEADERS,
            params={**MR_FILTERS, "page": page},
        )
        resp.raise_for_status()
        mrs = resp.json()
        if not mrs:
            break
        urls.extend(mr["web_url"] for mr in mrs)
        page += 1
    return urls


# --- 主流程 ---
def main() -> None:
    projects = fetch_all_projects(GROUP_PATH)
    for proj in projects:
        urls = fetch_mr_urls(proj["id"])
        for url in urls:
            print(url)


if __name__ == "__main__":
    main()
```







## 🌳 生长思考

对发散的自由捕捉、精确化

## 💭 反复绊脚

记录回顾、使用文档时，遇到的困惑



## 🗺️ 修订记录

重要修订记录

## 🛠️ 实践经历

记录实践经历： demo + 工作经历 + 第三方优秀经验反思



## ⚙️ prompt

```markdown
# 背景
目前我正在打通 AI + Gitlab 的流程。我希望了解 gitlab 的 API。获取 gitlab 平台上的一些常见信息。
目前我聚焦于批量项目修改自动化问题
# 内容
- 怎么获取 gitlab 的所有可读项目列表
- 本地创建 merge 提交到 gitlab 上。避免在浏览器上操作。
- 怎么获取自己提出的所有 merge 列表
```

```markdown
# 背景
我是一名追求效率的学习者。我从事于Java后端开发工程师的工作。
我认为学习本质上就是 大量正确信息的消化 + 关键结论的感受 + 自由的发散。
依托这样的思想，我希望和你来进行一场talk。

我们的 talk 基于以下原则
1. 你是 该talk 主题下的专家
2. 我是一名在其他领域具有通用性技能的工程师，如 Java、传统算法、后端工程、C++ 语法、Go 语法等。拥有一定计算机基础的知识。
3. 我们是不同领域的擅长者，这是一场圆桌会议式的talk。就和索尔维会议一样，阿尔伯特·爱因斯坦与尼尔斯·玻尔之间的交流。
4. 以你的权重为主前提下，我希望我们相互的问询感兴趣的内容。这样可以推动 talk 的进度。
# talk 主题


# 思维链
1. 我对信息的要求是，你应该减少幻觉，即信息是足够正确的
2. 我总是对一件事物的是什么、从哪里来感到好奇。所以，你可以简略说明它的历史阶段以及发展哲学
3. 我一边和你 talk，一边做草稿笔记。因此你的言语足够开阔，具有阐述性的同时，也要让我容易从中记录归纳总结。但是请你不要直接给我总结笔记，因为我希望可以主动消化。

# 输入格式
我将会输入一个问题

# 输出格式
不需要特殊的模版。参照思维链
# 当前问题


# 问题阶段(记录了 talk 的过程，方便复用)


--------
以下内容是我方便复制粘贴模版，请你忽略
## 问题X：
### 问题描述：

### 关键结论：
```
