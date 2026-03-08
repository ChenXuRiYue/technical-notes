# 📌 Mac-终端

## 🔖 文件操作

⚙️ 创建文件

- `touch ~/.config/opencode/opencode.json`





## 🔖 进程管理

⚙️ 关闭端口应用程序

- `kill -9 $(lsof -ti :8080)`
  - `kill -9` 强制杀死
  - `$()` 占位符
  - `lsof -ti :8080` 查找占用 8080 端口号的 pid （process id 进程 ID）
    - `-t` 仅见模式 `(Terse mode)`
    - `-i` 表示查看网络接口 `Internet`
- `lsof -ti :8080 | xargs kill -9`
  - `|` 管道符
    - 将前一个命令的标准输出，直接变为后一个命令的标准输入
  - `xargs kill -9`
    - `xargs` 从标准输入构建并执行命令。它读取管道传来的内容，将其作为参数追加到后面的命令