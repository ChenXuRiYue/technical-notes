# 📌 Begin

## 🔗 资料

- [tauri](https://v2.tauri.app/zh-cn/start/create-project/) 官方文档



## 🪵 创建项目



```shell
cargo install create-tauri-app --locked

cargo create-tauri-app
```

运行：

```cargo
cd tauri-app
cargo tauri dev
```



## 🪵 使用 Tauri CLI 手动创建

基于已有前端项目创建。

- 为项目创建新的目录，初始化前端（就像目前仅在开发前端项目一样）

  ```shell
  mkdir tauri-app
  cd tauri-app
  npm create vite@latest .
  ```

- 使用包管理器安装 Tauri CLI 工具

  ```
  cargo install tauri-cli --version "^2.0.0" --locked

- 目录下初始化 Tauri

  ```rust
  cargo tauri init
  ```

- 运行检查 Tauri 应用

  ```shell
  cargo tauri dev
  ```

  

## 🪵 项目结构

```txt
.
├── package.json
├── index.html
├── src/
│   ├── main.js
├── src-tauri/
│   ├── Cargo.toml
│   ├── Cargo.lock
│   ├── build.rs
│   ├── tauri.conf.json
│   ├── src/
│   │   ├── main.rs
│   │   └── lib.rs
│   ├── icons/
│   │   ├── icon.png
│   │   ├── icon.icns
│   │   └── icon.ico
│   └── capabilities/
│       └── default.json
```



# 🧸 DEMO

- 菜单
  - 插件管理
  - AI 管理
- Git 仓库管理
  - 数据统计

----

### 🔖 环境搭建

- 创建项目

```
cargo create-tauri-app
```

命令行输入相关参数

- 创建一个 React 前端的项目。安装依赖

```
npm install
```

- 启动项目

```
cargo tauri dev
```

![image-20260126234456745](https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/global/image-20260126234456745.png)



















