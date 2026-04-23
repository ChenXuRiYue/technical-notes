# VS Code Mac 开发环境配置

## C++ 开发环境

#### 背景

Mac 上使用 VS Code 配置 C++ 简单运行环境，满足：
1. 一键编译运行（`Ctrl+Shift+B`）
2. VS Code 终端中输入输出
3. 适合竞赛刷题场景

#### 必备插件

- **Code Runner** - 一键运行
- **C/C++ Clang Command Adapter** - 智能提示
- **CodeLLDB** - 调试支持

#### 配置文件说明

VS Code 使用 `.vscode` 文件夹中的 JSON 文件来管理项目的编译、运行、调试和智能提示等行为。

| 文件                    | 功能                 | 是否调试用 | 是否编译用 | 是否必须 |
| ----------------------- | -------------------- | ---------- | ---------- | -------- |
| `tasks.json`            | 定义编译/运行任务    | ❌          | ✅          | ✅ 通常需要 |
| `launch.json`           | 调试器配置           | ✅          | ❌          | ❌ 仅调试时需要 |
| `c_cpp_properties.json` | 智能提示和编译器设置 | ❌          | ❌（辅助）  | ✅ 用于补全和跳转 |

#### 实际工作流

1. **写代码**（`main.cpp`）
2. **VS Code 使用 `c_cpp_properties.json` 提供代码补全和跳转**
3. **按下 `Ctrl+Shift+B`，VS Code 执行 `tasks.json` 中的编译并运行任务**
4. **按下 `F5`，VS Code 根据 `launch.json` 启动调试器开始调试**

#### 配置模板

##### ✅ `.vscode/tasks.json`

包含三个任务：默认的"生成并运行"、"生成活动文件"（仅编译）、"运行程序"（仅运行）。

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "生成并运行",
      "type": "shell",
      "command": "sh",
      "args": [
        "-c",
        "clang++ -std=c++17 -g ${file} -o ${fileDirname}/${fileBasenameNoExtension} && cd ${fileDirname} && ./$(basename ${file} .cpp)"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "new"
      },
      "problemMatcher": []
    },
    {
      "type": "cppbuild",
      "label": "生成活动文件",
      "command": "/usr/bin/clang++",
      "args": [
        "-fcolor-diagnostics",
        "-fansi-escape-codes",
        "-g",
        "-std=c++17",
        "${file}",
        "-o",
        "${fileDirname}/${fileBasenameNoExtension}"
      ],
      "options": {
        "cwd": "${fileDirname}"
      },
      "problemMatcher": ["$gcc"],
      "group": {
        "kind": "build",
        "isDefault": false
      },
      "detail": "编译器: /usr/bin/clang++"
    },
    {
      "label": "运行程序",
      "type": "shell",
      "command": "sh",
      "args": [
        "-c",
        "cd ${fileDirname} && ./$(basename ${file} .cpp)"
      ],
      "group": {
        "kind": "none",
        "isDefault": false
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    }
  ]
}
```

##### ✅ `.vscode/launch.json`

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "C++ Debug",
      "type": "cppdbg",
      "request": "launch",
      "program": "${fileDirName}/${fileBasenameNoExtension}",
      "args": [],
      "stopAtEntry": false,
      "cwd": "${fileDir}",
      "environment": [],
      "externalConsole": false,
      "MIMode": "lldb"
    }
  ]
}
```

##### ✅ `.vscode/c_cpp_properties.json`

```json
{
  "configurations": [
    {
      "name": "Mac",
      "includePath": ["${workspaceFolder}/**"],
      "defines": [],
      "macFrameworkPath": ["/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks"],
      "compilerPath": "/usr/bin/clang++",
      "cStandard": "c17",
      "cppStandard": "c++17",
      "intelliSenseMode": "macos-clang-arm64"
    }
  ],
  "version": 4
}
```

#### 注意事项

- **智能检查报错问题**：即使配置了 C++17，可能仍对某些标准库报错（如 tuple）。如果不需要智能提示，可以像 LeetCode 白板一样直接关闭。
- 如果使用 `g++`，将 `compilerPath` 改为 `/usr/local/bin/g++`（需先安装 GCC）
- 使用第三方库（如 OpenCV）需要在 `c_cpp_properties.json` 中添加头文件路径
