# 📌 优化 Mac 终端

## 🔥 痛点

- 主要是没高亮、 没提示

## 🚀 当前定制化

**Shell 层**

| 项目 | 当前配置 | 说明 |
|------|---------|------|
| Shell | zsh（Mac 默认） | 比 bash 更强的补全和插件生态 |
| 框架 | Oh My Zsh | 主题 + 插件管理，`source` 注入 zsh |
| 主题 | robbyrussell（默认） | 简洁，只显示路径 + git 分支 |

**插件**

| 插件 | 来源 | 作用 |
|------|------|------|
| git | Oh My Zsh 内置 | git 别名（`gst`=git status, `gco`=git checkout 等） |
| zsh-autosuggestions | 手动 clone | 输入时灰色提示历史命令，按 `→` 补全 |
| zsh-syntax-highlighting | 手动 clone | 命令实时语法高亮（对的绿色，错的红色） |
| maven | Oh My Zsh 内置 | mvn 别名 + 补全（`mvn!`=clean install） |

**CLI 工具替换**

| 老命令 | 新工具 | 安装方式 |
|-------|--------|---------|
| `ls` | eza | `brew install eza` |
| `cat` | bat | `brew install bat` |
| `find` | fd | `brew install fd` |
| `grep` | ripgrep | `brew install ripgrep` |
| `cd` | zoxide | `brew install zoxide` |

> `--icons` 参数暂未启用（需 Nerd Font，见 TODO）

**启动优化**

compinit 缓存：每天完整初始化一次，其余时间用 `-C` 跳过安全检查。启动 ~200ms。

**截图**

<img src="https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260604204235454.png" alt="image-20260604204235454" style="zoom:45%;" />

代码补全 ![image-20260605003603068](https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260605003603068.png)

报错提醒 ![image-20260605003636601](https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260605003636601.png)


## 🐚 Zsh

Mac 默认 Shell，替代了 bash。核心优势：更强的补全、插件生态、主题系统。

### Oh My Zsh

zsh 的配置框架，**不是独立程序**，是一组通过 `source` 注入 zsh 进程的脚本。

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

本质：git clone 到 `~/.oh-my-zsh/`，然后在 `.zshrc` 里 `source oh-my-zsh.sh`。

| 关系类比 | zsh 是 | Oh My Zsh 是 |
|---------|--------|-------------|
| 操作系统 | Windows 本体 | 主题包 + 驱动管理器 |
| 编辑器 | VS Code 本体 | 预装插件合集 |
| 汽车 | 引擎 | 内饰改装包 |

### 定制化建议

**必装插件**

Oh My Zsh 插件分两步：**下载**（git clone）+ **启用**（写入 plugins 数组）。只下载不启用不会生效。

```bash
# 第一步：下载插件到 Oh My Zsh 的 custom/plugins 目录

# zsh-autosuggestions：输入时灰色提示历史命令，按 → 键接受（类似 fish shell）
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# zsh-syntax-highlighting：实时语法高亮，命令正确变绿色，拼错变红色
git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

```bash
# 第二步：编辑 ~/.zshrc，在 plugins 数组里加上插件名
# 原来：plugins=(git)
# 改成：
plugins=(git zsh-autosuggestions zsh-syntax-highlighting)
```

> 新终端自动生效，或执行 `source ~/.zshrc` 立即生效。

**主题**

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
# ~/.zshrc → ZSH_THEME="powerlevel10k/powerlevel10k"
# p10k configure
```

| 主题 | 特点 |
|------|------|
| robbyrussell | Oh My Zsh 默认，只显示路径 + git 分支，零配置开箱即用 |
| agnoster | 信息丰富（路径、git、用户、时间），需安装 Powerline 字体才能正常显示符号 |
| powerlevel10k | zsh 专属，Shell 脚本实现，支持 Instant Prompt（启动秒开），交互式向导配置，可深度定制每一行显示什么 |
| starship | 独立二进制（Rust 编写），**跨 Shell**（zsh/bash/fish/PowerShell 共用同一套配置），异步渲染 prompt（不阻塞输入），配置写 TOML 文件 |

**框架替代方案**

| 方案 | 特点 | 适合谁 |
|------|------|--------|
| Oh My Zsh | 生态最大（300+ 插件），社区教程多，装完即用，但插件多时启动慢（全量 source） | 刚接触 zsh，想快速上手 |
| zinit | 异步加载插件（Turbo 模式），启动速度提升明显，支持按需加载（用到才初始化），学习成本稍高 | 在意启动速度，插件数量多 |
| 手写 .zshrc | 最轻量，只写自己需要的 alias/函数，无框架开销，启动 <50ms，但补全、主题需自己配 | 知道自己要什么的老手 |

> 建议路径：Oh My Zsh 入门 → 用熟后迁移到 zinit 或手写 .zshrc

### 未来可预见的场景

| 场景 | 痛点 | 可能的定制方向 |
|------|------|--------------|
| 多项目切换频繁 | 反复 cd、记住不同项目的工具链 | zoxide 智能跳转 + 项目级 .envrc（direnv） |
| 服务器运维 | SSH 进去环境全丢、断连丢进度 | tmux 会话保持 + 远程 .zshrc 同步（dotfiles 管理） |
| Git 操作密集 | 频繁敲长命令、分支管理混乱 | 自定义 git 函数 + fzf 分支选择器 |
| 日志/数据排查 | grep 慢、输出无结构 | ripgrep + bat 高亮 + jq 格式化 |
| 终端启动变慢 | 装了太多工具，每次开终端等半秒 | zinit 异步加载 / 懒加载 nvm 等重型初始化 |
| 团队协作 | 每个人终端配置不同，新人上手慢 | dotfiles 仓库化（chezmoi / stow） |

## 🔧 现代 CLI 工具

独立于 Shell 框架，用更快更好看的工具替换老命令。与 Oh My Zsh **没有关系**——它们是独立的二进制程序，只是碰巧在 `.zshrc` 里用 alias 映射。

```bash
brew install eza bat fd ripgrep zoxide btop delta tldr
```

```bash
# .zshrc 中注册别名
alias ls="eza --icons --group-directories-first"
alias ll="eza -la --icons --group-directories-first --git"
alias cat="bat --style=plain"
alias find="fd"
alias grep="rg"
eval "$(zoxide init zsh)"
alias cd="z"
```

| 老命令 | 新工具 | 改进点 |
|-------|--------|-------|
| `ls` | **eza** | 支持颜色、图标、Git 状态标记，目录排前面，`--tree` 可看目录树 |
| `cat` | **bat** | 自带行号、语法高亮、Git diff 标记，自动识别文件类型，本质是 `cat + less + highlight` |
| `find` | **fd** | 语法比 find 简洁（`fd xxx` 即可），默认忽略 .gitignore 里的文件，速度快 |
| `grep` | **ripgrep** | Rust 实现，速度极快，自动跳过二进制文件和 .gitignore 目录，正则默认开启 |
| `cd` | **zoxide** | 记住你去过哪，`z 项目名` 模糊匹配跳转，不用记完整路径，类似 autojump 但更快 |
| `diff` | **delta** | 语法高亮 diff，行内差异标色，支持 side-by-side，git diff 自动走 delta |
| `man` | **tldr** | 跳过冗长的 man 手册，直接给常用命令的示例，`tldr tar` 比 `man tar` 实用得多 |

> **TODO**：eza 的 `--icons` 需要 Nerd Font，网络问题暂未安装。后续从 [Nerd Fonts Releases](https://github.com/ryanoasis/nerd-fonts/releases/latest) 下载 `FiraCode.zip`，解压安装后在终端 app 中切换字体，再加回 `--icons` 参数。

### fzf 模糊搜索

```bash
brew install fzf
$(brew --prefix)/opt/fzf/install
```

```bash
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:500 {}'"
```

| 快捷键 | 功能 |
|-------|------|
| `Ctrl+R` | 模糊搜历史命令 |
| `Ctrl+T` | 模糊搜文件 |
| `Alt+C` | 模糊搜目录并 cd |


## 🧩 终端技术架构

```
终端模拟器（PTY 渲染）  ←→  Shell（命令解释）  ←→  CLI 工具（功能执行）
     ANSI 转义序列             .zshrc + 插件             stdin/stdout 管道
```

三层独立可替换，各自暴露清晰接口：

| 层次 | 接口 | 开发者增强方向 |
|------|------|--------------|
| 终端模拟器 | ANSI 转义、键盘事件、窗口协议 | 选 iTerm2/Kitty，自定义配色字体快捷键 |
| Shell | .zshrc、插件 API、补全系统、钩子函数 | Oh My Zsh + 语法高亮 + 自动建议 |
| CLI 工具 | stdin/stdout、exit code、环境变量 | eza/bat/fd/ripgrep 替换老命令 |
| 工作流 | 别名、函数、热键 | fzf 模糊搜索 + zoxide 智能跳转 |

**关键概念**

| 概念 | 是什么 | 一句话理解 |
|------|--------|-----------|
| **终端 (Terminal)** | 物理硬件盒子（VT100），有键盘和屏幕 | 用户与计算机之间的"打字机" |
| **终端模拟器 (Emulator)** | 模拟物理终端的软件（iTerm2、Terminal.app） | 软件版的硬件终端 |
| **PTY (伪终端)** | 内核提供的虚拟串口对（master/slave） | 模拟器和 Shell 之间的"管道" |
| **ANSI 转义序列** | `\033[31m` 这样的控制字节 | 给终端的"指令"：变红、加粗、清屏 |
| **stdin/stdout/stderr** | 进程的三个标准流 | 键盘输入 / 正常输出 / 错误输出 |
| **Shell** | 命令解释器（zsh/bash） | 读命令 → 解析 → 执行 → 返回结果 |
| **$PATH** | 冒号分隔的目录列表 | Shell 去哪些目录找可执行文件 |
| **管道 `\|`** | 前一个进程的 stdout → 后一个进程的 stdin | 命令拼接的基础设施 |

核心理解：终端本质是 **PTY 双向字节流**，不理解"命令"只理解字节。定制就是在每层的接口上注入增强。

> 参考：[The TTY demystified](https://www.linusakesson.net/programming/thetty/) — 经典文章，解释 Linux/Unix TTY 子系统的来龙去脉

### 集成示例：以 zsh 为例

**安装 zsh 本质上做了什么？**

```bash
brew install zsh
```

| 步骤 | 做了什么 | 文件位置 |
|------|---------|---------|
| 1. 下载编译 | 把 zsh 二进制放到系统目录 | `/opt/homebrew/bin/zsh` |
| 2. 注册为合法 Shell | 写入 shells 白名单 | `/etc/shells` |
| 3. 设为默认（可选） | 修改用户的 login shell | `chsh -s /opt/homebrew/bin/zsh` |

终端启动时的调用链：

```
用户打开 iTerm2 → 读系统配置 → fork+exec("/bin/zsh") → zsh 启动 → 读 .zshrc → 进入交互循环
```

**Oh My Zsh 生态管理**

Oh My Zsh 不是独立程序，是**寄生在 zsh 进程内的一组 .zsh 脚本**，通过 `source` 注入：

```
~/.oh-my-zsh/
├── oh-my-zsh.sh        ← 框架入口，被 .zshrc source
├── plugins/
│   ├── git/            ← git 别名、函数
│   ├── docker/         ← docker 补全
│   └── zsh-autosuggestions/  ← 第三方插件（git clone 进来的）
└── themes/
    └── powerlevel10k/
```

插件加载本质：`git clone` 脚本到 `$ZSH_CUSTOM/plugins/` → Oh My Zsh 启动时 `source` 它们。

**安装终端工具的通用模式**

```
1. 获取二进制    → brew install / git clone / curl 下载
2. 注册到系统    → /etc/shells（Shell）/ $PATH（CLI 工具）/ .zshrc（插件）
3. 启动时加载    → Shell 读 .zshrc → source 插件 → 别名/函数/补全生效
```

| 安装对象 | 本质操作 | 注册位置 |
|---------|---------|---------|
| Shell (zsh) | 放二进制 + 注册到 /etc/shells | `/etc/shells` |
| Oh My Zsh | git clone 框架 + 写入 .zshrc | `~/.oh-my-zsh/` |
| 插件 | git clone 脚本到插件目录 | `$ZSH_CUSTOM/plugins/` |
| CLI 工具 (eza) | brew install 放二进制到 $PATH | `$PATH` 内 |

### 层间关系：完全独立的软件

终端生态每一层都是**独立软件**，只面向系统接口层做开发，层与层之间**零代码耦合**：

```
Terminal.app          zsh              bash              fish
    │                  │                │                │
    │  PTY 字节流      │                │                │
    ├──────────────────┤                │                │
    │  完全不知道对方的存在，只通过 PTY 传字节              │
    └──────────────────┴────────────────┴────────────────┘
```

类比：

| 关系 | 协议/接口 | 特点 |
|------|----------|------|
| 终端 ↔ Shell | PTY + ANSI | 各自独立，只靠字节流通信 |
| 浏览器 ↔ 服务器 | HTTP | 各自独立，只靠协议通信 |
| 插头 ↔ 插座 | 电气标准 | 各自独立，只靠物理规格兼容 |

zsh 团队不需要改 Terminal.app，Terminal.app 也不需要知道 zsh。只要双方遵守 PTY + ANSI 约定就能协作。Oh My Zsh 更彻底——它甚至没有自己的进程，只是被 `source` 进 zsh 进程里运行的脚本集合。


## 💡 生成推荐



## 🌳 生长思考

Q1：Mac 中对终端采取什么样的定制化？怎么理解 Mac 中的终端技术？

## 💭 反复绊脚

**zsh / Oh My Zsh / CLI 工具 三者关系分不清**

容易把它们当成一个东西，因为都在 `.zshrc` 里配置。实际是三层独立的关系：

```
zsh        = 地基（解析执行命令的引擎）
Oh My Zsh  = 装修（主题、补全、别名，source 进 zsh 的脚本）
CLI 工具   = 家具（eza/bat/ripgrep 等独立二进制，跟 zsh 无关）
```

类比：zsh 是 Android，Oh My Zsh 是 MIUI，CLI 工具是微信。MIUI 和微信没有关系，只是碰巧装在同一台手机上。

**启动速度调优：compinit 是大头**

装完插件后感觉终端变慢，用 `zprof` 定位：

```bash
# 直接跑一行出报告
zsh -c 'zmodload zsh/zprof; source ~/.zshrc; zprof' | head -20
```

| 函数 | 耗时 | 占比 | 说明 |
|------|------|------|------|
| compinit | 410ms | 85% | zsh 补全系统初始化（扫描所有补全定义） |
| compdef | 118ms | 24% | 注册 807 个补全定义（被调了 807 次） |
| compdump | 97ms | 20% | 加载补全缓存文件 |
| _omz_source | 52ms | 10% | Oh My Zsh 插件加载 |

**解法**：compinit 每天只完整跑一次，其余时间用缓存跳过安全检查：

```zsh
autoload -Uz compinit
if [[ -n ${ZDOTDIR:-$HOME}/.zcompdump(#qN.mh+24) ]]; then
  compinit          # 缓存超过 24 小时，完整重建
else
  compinit -C       # -C 跳过安全检查，直接用缓存
fi
```

优化后 compinit 从 410ms → 21ms，整体启动从 ~350ms → ~200ms。

> **经验**：`zprof` 是 zsh 内置的性能分析工具，定位启动瓶颈非常直观。遇到"终端变慢"先 profile，不要盲猜。

## 调研

### 痛点参考

| 痛点 | 现状 | 期望 |
| ---- | ---- | ---- |
| 命令输出无颜色 | `ls` `cat` `grep` 纯白文本，信息密度低 | 颜色区分、语法高亮 |
| 目录跳转靠手打 | `cd a/b/c/d` 逐级输入 | `z 项目名` 一步到位 |
| 历史命令难搜 | `Ctrl+R` 只能逐条翻 | 模糊搜索，即时预览 |
| 找文件慢 | `find . -name "*.java"` 语法冗长 | `fd xxx` 简洁快速 |
| diff 难读 | 原生 diff 无颜色，行内差异不标 | 语法高亮 + 行内对比 |
| 切换目录不记得路径 | 频繁 `cd` 来回跳 | 智能记忆，按习惯跳转 |
| 终端启动慢 | nvm/rbenv 初始化阻塞 | 懒加载，按需触发 |

### Shell 配置

**安装 Oh My Zsh**

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

**必装插件**

```bash
# ~/.zshrc → plugins=(git zsh-autosuggestions zsh-syntax-highlighting z extract sudo)

git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-syntax-highlighting ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

**主题（Powerlevel10k）**

```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
# ~/.zshrc → ZSH_THEME="powerlevel10k/powerlevel10k"
# p10k configure
```

🪏 主题对比

| 主题          | 特点                                |
| ------------- | ----------------------------------- |
| robbyrussell  | 默认，简洁                          |
| agnoster      | 信息丰富，需 Powerline 字体         |
| powerlevel10k | 最快，可高度定制，Instant Prompt    |
| starship      | 跨 Shell，Rust 实现                 |

### 现代 CLI 工具

**一键安装**

```bash
brew install eza bat fd ripgrep zoxide btop delta tldr
```

**注册别名（.zshrc）**

```bash
alias ls="eza --icons --group-directories-first"
alias ll="eza -la --icons --group-directories-first --git"
alias cat="bat --style=plain"
alias find="fd"
alias grep="rg"
alias top="btop"
eval "$(zoxide init zsh)"
alias cd="z"
```

**eza 颜色配置（.zshrc）**

```bash
# 目录默认灰色（避免亮蓝色刺眼）
export EZA_COLORS="di=0"
```

🪏 工具替换对照

| 老命令  | 新工具      | 改进点                        |
| ------- | ----------- | ----------------------------- |
| `ls`    | **eza**     | 颜色、图标、Git 状态          |
| `cat`   | **bat**     | 行号、语法高亮                |
| `find`  | **fd**      | 语法简洁、忽略 .gitignore     |
| `grep`  | **ripgrep** | 更快、忽略二进制              |
| `cd`    | **zoxide**  | `z 项目名` 即跳转            |
| `diff`  | **delta**   | 语法高亮 diff                 |
| `man`   | **tldr**    | 精简版 man，直给示例          |

### fzf 模糊搜索

**安装**

```bash
brew install fzf
$(brew --prefix)/opt/fzf/install
```

**.zshrc 配置**

```bash
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=numbers --line-range=:500 {}'"
```

🪏 核心快捷键

| 快捷键   | 功能             |
| -------- | ---------------- |
| `Ctrl+R` | 模糊搜历史命令   |
| `Ctrl+T` | 模糊搜文件       |
| `Alt+C`  | 模糊搜目录并 cd  |

### Git 别名与函数

**自定义别名**

```bash
alias gaa="git add --all"
alias gcm="git commit -m"
alias gpf="git push --force-with-lease"
alias gundo="git reset --soft HEAD~1"
```

**常用函数**

```bash
mkcd() { mkdir -p "$1" && cd "$1"; }
port() { lsof -i :"$1" -P -n -l; }
killp() { ps aux | grep "$1" | grep -v grep | awk '{print $2}' | xargs kill -9; }
```

### iTerm2 配置

**为什么用 iTerm2 替代 Terminal.app**

| 功能 | Terminal.app | iTerm2 |
|------|-------------|--------|
| Nerd Font 图标 | 支持有限 | ✅ 完美支持 |
| 分屏 | ❌ | ✅ `Cmd+D` |
| 热键窗口 | ❌ | ✅ `Cmd+`` 一键呼出 |
| 搜索高亮 | 基础 | ✅ 强大 |
| 自动补全 | ❌ | ✅ |
| 配色主题 | 少 | ✅ 丰富 |
| 半透明背景 | ❌ | ✅ |

**安装**

```bash
brew install --cask iterm2
```

**设置为默认终端**

iTerm2 → Settings → General → 勾选 `Set iTerm2 as default terminal`

**字体配置（Nerd Font 图标）**

1. 安装字体：`brew install --cask font-fira-code-nerd-font`
2. iTerm2 设置：`Settings → Profiles → Text → Font` → 选择 `FiraCode Nerd Font`
3. 勾选 **Use ligatures**（编程连字）

**必改设置**

| 设置项       | 路径                              | 推荐值                   |
| ------------ | --------------------------------- | ------------------------ |
| 热键窗口     | Keys → Hotkey                     | `Cmd+`` ``，呼出/隐藏   |
| 垂直分屏     | Keys → Key Bindings               | `Cmd+D`                  |
| 半透明背景   | Profiles → Window → Transparency  | 15-20%                   |
| 状态栏       | Profiles → Session → Status bar   | 启用                     |

**推荐配色**

| 方案         | 特点         |
| ------------ | ------------ |
| Dracula      | 对比度高     |
| Catppuccin   | 柔和护眼     |
| Tokyo Night  | 偏紫色调     |

![image-20260605191343816](https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260605191343816.png)



### 启动速度优化

**测量**

```bash
time zsh -i -c exit
```

**懒加载 nvm（启动最大杀手）**

```bash
export NVM_LAZY_LOAD=true
```

**懒加载 rbenv 等**

```bash
rbenv() {
  unfunction rbenv
  eval "$(command rbenv init -)"
  rbenv "$@"
}
```

🪏 优化效果

| 优化手段           | 提速效果     |
| ------------------ | ------------ |
| 懒加载 nvm         | 减少 200ms+  |
| 懒加载 rbenv/pyenv | 减少 100ms+  |
| 减少插件数量       | 每个 10-50ms |

### 生成推荐参考

| 推荐 | 说明 | 解决什么 |
| ---- | ---- | -------- |
| Starship 主题 | 跨 Shell，比 p10k 更轻量 | 已有 p10k 可跳过 |
| zinit 替代 Oh My Zsh | 异步加载，启动更快 | 插件多时启动慢 |
| tmux | 终端复用，远程不断连 | 服务器操作场景 |
| Warp 终端 | AI 辅助，块状输出 | 新体验，非必需 |
