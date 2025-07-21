# 基于 Hexo + github + cloudfare 搭建个人博客

## 原理及概念：

1 . Hexo: 

2 . github 提供的服务：

Github pages 为了促进开源文化：通过免费提供静态网站托管服务。



## 实现

### 1. Node.js npm 安装

### 2. git 安装

### 3. hexo 安装

```
npm install -g hexo-cli
hexo -v
```



### 4. 创建 github pages 的项目

限定仓库名： 用户名.github.io



### 5 . hexo 项目根目录下

安装相关依赖：

```
npm install hexo --save
npm install hexo-deployer-git --save
```

更改 Hexo 部署配置：
```
deploy:
  type: git
  repo: git@github.com:你的GitHub用户名/你的GitHub用户名.github.io.git
  branch: main
```

### 可能遇到的问题：

1. ssh 配置不成功。框架使用的是 ssh 推送方式，需要配置好 和 github 的 ssh 公钥



## NEXT

### 博客内容更新部署

```
hexo clean    -- 清空缓冲区
hexo generate -- 创建静态文件
hexo serve    -- 本地运行
hexo deploy   -- 远程部署
```





## 个性化配置

主题仓库：[Themes | Hexo](https://hexo.io/themes/)
