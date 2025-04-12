

# Linux 常识

## 基本概念

### 1. Linux 简介
- **定义**：Linux 是一个开源的类 Unix 操作系统内核，由 Linus Torvalds 于 1991 年创建。
- **发行版**：常见的 Linux 发行版包括 Ubuntu、CentOS、Debian、Red Hat 等。
- **特点**：
  - 开源、多用户、多任务。
  - 高稳定性，广泛用于服务器。

### 2. 文件系统
- **结构**：树状结构，以 `/` 为根目录。
- **重要目录**：
  - `/etc`：配置文件目录。
  - `/var`：变量数据（如日志）。
  - `/home`：用户主目录。
  - `/usr`：用户程序和数据。
- **文件类型**：普通文件（`-`）、目录（`d`）、符号链接（`l`）等。

### 3. 用户与权限
- **用户类型**：root（超级用户）、普通用户。
- **权限**：读（r）、写（w）、执行（x），用 `chmod` 修改（如 `chmod 755 file`）。
- **文件属性**：通过 `ls -l` 查看，例如 `drwxr-xr-x`。

### 4. 进程与服务
- **进程**：运行中的程序，PID 标识。
- **服务**：后台运行的进程，通常由 `systemd` 管理。

*（后续扩展：内核模块、网络栈等）*

---

## 基础命令

### 1. 文件与目录操作
- `ls`：列出目录内容。
  - 示例：`ls -l`（详细列表）、`ls -a`（显示隐藏文件）。
- `cd`：切换目录。
  - 示例：`cd /var/log`。
- `pwd`：显示当前路径。
- `mkdir`：创建目录。
  - 示例：`mkdir test_dir`。
- `rm`：删除文件或目录。
  - 示例：`rm -rf dir`（强制递归删除）。
- `cp`：复制文件或目录。
  - 示例：`cp file1 file2`。
- `mv`：移动或重命名文件。
  - 示例：`mv file1 /tmp/`。

### 2. 文件内容操作
- `cat`：查看文件内容。
  - 示例：`cat /etc/passwd`。
- `less`/`more`：分页查看文件。
- `tail`：查看文件末尾。
  - 示例：`tail -f log.txt`（实时跟踪）。
- `head`：查看文件开头。
- `grep`：搜索文件内容。
  - 示例：`grep "error" log.txt`。
- `echo`：输出内容。
  - 示例：`echo "hello" > file.txt`。

### 3. 系统管理
- `ps`：查看进程。
  - 示例：`ps aux`（所有进程）。
- `top`/`htop`：实时监控进程。
- `kill`：终止进程。
  - 示例：`kill -9 1234`（强制杀掉 PID 1234）。
- `df`：查看磁盘使用。
  - 示例：`df -h`（人类可读格式）。
- `du`：查看目录大小。
  - 示例：`du -sh /var`。
- `free`：查看内存使用。
  - 示例：`free -m`（以 MB 显示）。

### 4. 权限与用户
- `chmod`：修改权限。
  - 示例：`chmod 644 file.txt`。
- `chown`：修改文件所有者。
  - 示例：`chown user:group file.txt`。
- `whoami`：显示当前用户。
- `sudo`：以超级用户权限执行命令。

### 5. 网络相关
- `ping`：测试网络连通性。
  - 示例：`ping google.com`。
- `netstat`：查看网络状态。
  - 示例：`netstat -tuln`。
- `curl`：发送 HTTP 请求。
  - 示例：`curl http://example.com`。
- `ifconfig`/`ip`：查看网络配置。
- `lsof` : 查看打开文件的进程，包括端口。
  - 示例：lsof -i:80（查看占用 80 端口的进程）。

*（后续扩展：管道、重定向、脚本等）*

---

## 后端工程场景

### 1. 日志查看与分析
- **场景**：排查服务异常。
- **命令**：
  - `tail -f /var/log/app.log`：实时查看日志。
  - `grep "ERROR" /var/log/app.log`：过滤错误日志。
  - `awk '{print $1}' /var/log/app.log`：提取日志第一列。
- **扩展**：可用 `logrotate` 管理日志文件。

### 2. 服务部署与管理
- **场景**：部署 Java 应用。
- **命令**：
  - `systemctl start nginx`：启动 Nginx 服务。
  - `systemctl status app`：查看服务状态。
  - `nohup java -jar app.jar &`：后台运行 JAR 文件。
- **扩展**：编写 systemd 服务文件。

### 3. 性能监控
- **场景**：检查服务器负载。
- **命令**：
  - `top`：查看 CPU 和内存使用。
  - `iostat`：监控磁盘 I/O。
  - `vmstat`：系统资源统计。
- **扩展**：安装 `sar` 或 `Prometheus` 进行长期监控。

### 4. 文件传输与备份
- **场景**：同步代码或备份数据。
- **命令**：
  - `scp file.txt user@remote:/path/`：远程复制。
  - `rsync -av /src/ /backup/`：增量同步。
  - `tar -czvf backup.tar.gz /data/`：压缩备份。
- **扩展**：设置定时任务（`cron`）自动化。

### 5. 容器化与脚本
- **场景**：运行 Docker 或自动化任务。
- **命令**：
  - `docker ps`：查看运行中的容器。
  - `crontab -e`：编辑定时任务。
  - 示例脚本：
    ```bash
    #!/bin/bash
    echo "Backup at $(date)" >> /var/log/backup.log
    ```
- **扩展**：结合 `ansible` 管理多服务器。

*（后续扩展：安全配置、调试工具等）*

### 6. 查看占用端口号
- **场景**：后端服务启动失败，需检查端口（如 8080）是否被占用。
- **命令**：
  - **`netstat`**：
    - 示例：`netstat -tunlp | grep 8080`
    - 说明：`-t`（TCP）、`-u`（UDP）、`-n`（显示数字端口）、`-l`（监听状态）、`-p`（显示进程 ID 和名称）。
    - 输出：`tcp 0 0 0.0.0.0:8080 0.0.0.0:* LISTEN 1234/java`
  - **`ss`**：
    - 示例：`ss -tuln | grep 8080`
    - 说明：列出监听端口，输出更简洁。
    - 输出：`tcp LISTEN 0 128 0.0.0.0:8080 0.0.0.0:*`
  - **`lsof`**：
    - 示例：`lsof -i:8080`
    - 说明：显示占用 8080 端口的进程详细信息。
    - 输出：
      ```
      COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
      java    1234 user   12u  IPv4  56789      0t0  TCP *:8080 (LISTEN)
      ```
- **解决方法**：
  - 找到占用端口的进程 ID（PID），用 `kill -9 <PID>` 终止。
    - 示例：`kill -9 1234`。
  - 或调整服务端口，避免冲突。
- **扩展**：
  - 编写脚本自动化检查：
    ```bash
    #!/bin/bash
    PORT=8080
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "Port $PORT is occupied by PID $PID"
    else
        echo "Port $PORT is free"
    fi
    ```

---

## 其它常识

### Ctrl + C 后的过程

硬件动作事件 触发 信号 ->  操作系统触发中断信号 Sigint。
终端驱动程序识别终端，将它转换成一个信号。
操作系统接收到信号请求，查找当前终端的前台进程组。
将信号发给所有的进程。
用户空间捕捉进程，完成对对应的行为。
