# Dockerfile 笔记

## 一、概述

1. **定义**：Dockerfile 是一个文本文件，其中包含了一系列指令，用于自动化构建 Docker 镜像。通过 Dockerfile，可以描述镜像的基础环境、安装的软件、配置信息以及运行的命令等，是创建自定义 Docker 镜像的核心工具。

2. **作用**：

- **标准化镜像构建**：确保在不同的环境中，镜像的构建过程是一致的，避免因环境差异导致的构建问题。

- **版本控制**：类似于代码的版本控制，通过修改 Dockerfile 并记录版本，可以方便地管理镜像的不同版本。

- **提高效率**：自动化构建过程减少了手动配置的工作量，提高了镜像创建的效率。

- **团队协作**：团队成员可以共享 Dockerfile，方便协作开发和部署应用。

## 二、使用 Dockerfile

1. **基本步骤**：

- **创建 Dockerfile**：在项目目录中创建一个名为 Dockerfile 的文本文件（注意大小写）。

- **编写指令**：根据应用的需求，在 Dockerfile 中编写一系列指令，指定基础镜像、安装软件、复制文件等操作。

- **构建镜像**：在包含 Dockerfile 的目录中，打开终端，运行 docker build 命令来构建镜像。例如：docker build -t myimage:latest.，其中 -t 用于指定镜像的名称和标签，. 表示当前目录（Dockerfile 所在目录）。

- **运行容器**：使用 docker run 命令基于构建好的镜像启动容器。例如：docker run -d myimage:latest，-d 表示以守护进程模式运行容器。

1. **最佳实践**：

- **选择合适的基础镜像**：尽量选择官方提供的基础镜像，如 ubuntu、alpine、python 等，以确保镜像的稳定性和安全性。同时，根据应用的需求选择合适的版本。

- **分层构建**：将不同的操作分成多个步骤，每个步骤对应一个镜像层。这样可以利用 Docker 的层缓存机制，提高后续构建的速度。例如，将安装软件和复制应用代码分开，先安装软件，再复制代码。

- **清理临时文件**：在构建过程中，可能会产生一些临时文件，如安装包、编译中间文件等。使用 RUN 指令在安装完成后清理这些临时文件，以减小镜像的体积。

- **设置工作目录**：使用 WORKDIR 指令设置容器内的工作目录，方便后续的文件操作和命令执行。

- **添加注释**：在 Dockerfile 中添加注释，解释每个指令的作用和目的，提高代码的可读性。

## 三、Dockerfile 语法命令

1. **FROM**：

- **作用**：指定基础镜像，后续的指令将基于该镜像进行构建。一个 Dockerfile 中必须有且只能有一个 FROM 指令作为第一条指令（多阶段构建除外）。

- **示例**：FROM ubuntu:latest，表示使用最新版本的 Ubuntu 作为基础镜像。

2. **MAINTAINER**：

- **作用**：指定镜像的维护者信息，如姓名和邮箱地址。虽然该指令在 Docker 官方文档中已被标记为过时，推荐使用 LABEL 指令来替代，但在一些旧的 Dockerfile 中仍然可能会看到。

- **示例**：MAINTAINER John Doe <[johndoe@example.com](mailto:johndoe@example.com)>。

3. **RUN**：

- **作用**：在构建镜像的过程中，在容器内执行命令。每条 RUN 指令都会创建一个新的镜像层。

- **示例**：RUN apt-get update && apt-get install -y python3，表示更新软件包列表并安装 Python 3。

4. **COPY**：

- **作用**：将本地文件或目录复制到镜像中的指定位置。

- **示例**：COPY requirements.txt /app/，表示将当前目录下的 requirements.txt 文件复制到镜像中 /app/ 目录下。

5. **ADD**：

- **作用**：与 COPY 类似，也是将本地文件或目录复制到镜像中，但 ADD 还具有一些额外的功能，如自动解压 tar 文件、处理远程 URL 等。不过，由于 ADD 的行为相对复杂，可能会导致一些意外情况，因此推荐优先使用 COPY。

- **示例**：ADD app.tar.gz /app/，如果 app.tar.gz 是一个压缩文件，该指令会将其解压到 /app/ 目录下。

6. **WORKDIR**：

- **作用**：设置容器内的工作目录，后续的 RUN、CMD、ENTRYPOINT 等指令将在该目录下执行。

- **示例**：WORKDIR /app，表示将工作目录设置为 /app。

7. **CMD**：

- **作用**：指定容器启动时默认执行的命令。一个 Dockerfile 中只能有一个 CMD 指令，如果有多个，只有最后一个会生效。

- **示例**：CMD ["python3", "[app.py](http://app.py)"]，表示容器启动时运行 python3 [app.py](http://app.py) 命令。

8. **ENTRYPOINT**：

- **作用**：指定容器启动时执行的可执行文件或命令，与 CMD 配合使用。ENTRYPOINT 定义了容器的主程序，CMD 可以作为参数传递给 ENTRYPOINT。

- **示例**：ENTRYPOINT ["python3"]，CMD ["[app.py](http://app.py)"]，等价于 python3 [app.py](http://app.py)。

9. **EXPOSE**：

- **作用**：声明容器运行时监听的端口，用于告知 Docker 该容器需要对外提供哪些服务。但 EXPOSE 指令本身并不会真正地打开端口，还需要在运行容器时使用 -p 或 -P 选项进行端口映射。

- **示例**：EXPOSE 80，表示容器监听 80 端口。

10. **ENV**：

- **作用**：设置环境变量，这些环境变量在容器运行时可以被应用程序访问。

- **示例**：ENV APP_VERSION 1.0，可以在容器内通过 echo $APP_VERSION 查看环境变量的值。

11. **VOLUME**：

- **作用**：创建一个挂载点，用于将容器内的数据持久化存储或与宿主机共享数据。

- **示例**：VOLUME /data，表示在容器内创建一个 /data 挂载点。

12. **USER**：

- **作用**：指定在容器内运行后续指令和启动应用程序的用户。可以提高容器的安全性，避免以 root 用户运行应用。

- **示例**：USER myuser，表示后续指令以 myuser 用户身份执行。

13. **ARG**：

- **作用**：定义构建时的参数，这些参数可以在 docker build 命令中通过 --build-arg 选项传递。

- **示例**：ARG VERSION=latest，在构建时可以使用 docker build --build-arg VERSION=1.0.0. 来覆盖默认值。