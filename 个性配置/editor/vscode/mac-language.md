# Mac-language

# C++

## **Mac Pro 配置 GCC 环境**

### **mac 配置 clang**

目标是配置简单的 C++ 运行环境。可以一键运行在终端中输入输出，方便竞赛以及补题。

插件：
**Code Runner**
**C/C++ Clang Command Adapter**
**CodeLLDB 
[配置文件-c++.md](配置文件-c++.md) **

**vs code: 任务系统 task**
[配置文件-c++.md](配置文件-c++.md) 

```markdown
# 背景
我是一名竞赛爱好者，我刚换了一台 mac。但是我并不熟悉 mac 竞赛环境的配置。我希望摸索 vscode  C++ 简单代码的运行环境：
使得它可以满足以下效果：
1. 一键即运行
2. vscode 终端中输入输出。

# 待解决问题：
```

配置上比较简单：

配置如上执行流：并且对编译并运行设置为默认模式模式，使用 control shift B 可以快速编译并运行

**Task.json**

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

**可以编译成功、但是智能检查依然报错**

<img src="https://raw.githubusercontent.com/ChenXuRiYue/image-cloud/main/typora/image-20250728205445028.png" alt="image-20250728205445028" style="zoom:50%;" />

<u>c_cpp_properties.json</u>

```json
{
    "configurations": [
        {
            "name": "Mac",
            "includePath": [
                "${workspaceFolder}/**"
            ],
            "defines": [],
            "compilerPath": "/usr/bin/clang++",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "macos-clang-arm64"
        }
    ],
    "version": 4
}

```

如上即使配置了C++17 限制，依然会对 C++11 引入的 tuple 报警。

~~未解决~~：

最后全部关闭，像刷 leetcode 白板一样完成简单单文件内容填写
