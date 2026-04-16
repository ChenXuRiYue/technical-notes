# 📌 cc-Switch

## 📝 文档以及仓库

**github：** https://github.com/farion1231/cc-switch/blob/main/README_ZH.md

## 🌳 发散

这个项目的技术栈就是 Tauri2 + react + rust。可以学习借鉴一下

## ❓遇到一些问题

- 没权限修改配置文件需要

  一个开启权限的脚本：

  ```sh
  #!/bin/bash
  
  # CC-Switch 权限设置脚本
  # 此脚本用于修复 CC-Switch 相关配置文件夹的权限问题
  
  echo "开始为 CC-Switch 相关配置文件夹授予权限..."
  
  # 获取当前用户名
  CURRENT_USER=$(whoami)
  echo "当前用户: $CURRENT_USER"
  
  # 定义可能的 CC-Switch 和相关配置目录
  CONFIG_DIRS=(
      "/Users/$CURRENT_USER/.claude"
      "/Users/$CURRENT_USER/.gemini" 
      "/Users/$CURRENT_USER/Library/Application Support/CC-Switch"
      "/Users/$CURRENT_USER/Library/Application Support/Claude"
      "/Users/$CURRENT_USER/Library/Application Support/Gemini"
      "/Users/$CURRENT_USER/.config/claude"
      "/Users/$CURRENT_USER/.config/gemini"
  )
  
  # 为每个可能的配置目录设置权限
  for dir in "${CONFIG_DIRS[@]}"; do
      if [ -d "$dir" ]; then
          echo "正在处理目录: $dir"
          
          # 修改目录权限
          chmod 755 "$dir"
          
          # 修改目录所有权
          sudo chown -R "$CURRENT_USER:staff" "$dir"
          
          # 处理目录下的所有文件
          find "$dir" -type f -exec chmod 644 {} \;
          find "$dir" -type d -exec chmod 755 {} \;
          
          echo "  ✓ $dir 权限设置完成"
      else
          echo "  - $dir 不存在，跳过"
      fi
  done
  
  # 特别处理临时文件问题
  GEMINI_DIR="/Users/$CURRENT_USER/.gemini"
  if [ -d "$GEMINI_DIR" ]; then
      echo "处理 $GEMINI_DIR 中的临时文件..."
      # 删除可能存在的临时文件
      find "$GEMINI_DIR" -name "*.tmp.*" -delete 2>/dev/null || true
      echo "  ✓ 临时文件清理完成"
  fi
  
  # 检查 CC-Switch 应用权限 (需要用户手动设置)
  echo ""
  echo "注意：您还需要为 CC-Switch 应用程序添加系统权限："
  echo "1. 打开 '系统偏好设置' -> '安全性与隐私' -> '隐私' 选项卡"
  echo "2. 在左侧列表中选择 '全盘访问权限'"
  echo "3. 点击左下角的锁图标解锁"
  echo "4. 点击 '+' 添加 CC-Switch 应用程序"
  echo "5. 重启 CC-Switch 应用程序"
  
  echo ""
  echo "权限设置完成！"
  echo "请重启 CC-Switch 应用程序以使更改生效。"
  ```

  使用说明：

  1. 保存为： `fix_cc_switch_permissions.sh`
  2. 赋予执行权限
    ```bash
    chmod +x fix_cc_switch_permissions.sh
    ```
  3. 运行脚本
  
  ```bash
  ./fix_cc_switch_permissions.sh
  ```
  
  