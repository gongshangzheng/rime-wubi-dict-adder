# Rime 五笔词典管理工具（Emacs 插件）

基于 Python 的五笔输入法词典管理工具，提供 Emacs 集成支持。

## 环境要求

- Python 3.7+ 环境
- pywubi 包

安装依赖：
```bash
pip install pywubi
```

## Emacs 集成

`rime-wubi-dict-adder.el` 文件提供了 Emacs 集成的词典管理功能。

### 推荐配置

使用 `use-package` 配置：

```emacs-lisp
(use-package rime-wubi-dict-adder
  :ensure nil
  :load-path "~/path/to/directory/containing-el-file/"
  :config
  (setq rime-wubi-dict-adder-python-command "/path/to/python")  ; 如果 python 不在 PATH 中需要设置
  (setq rime-wubi-dict-adder-user-dict "~/.config/ibus/rime/wubi86_jidian.user.dict.yaml")
  (setq rime-wubi-dict-adder-script-path "dictAdder.py")
  (define-key global-map (kbd "C-c W") 'rime-wubi-dict-adder-with-python)
  (define-key global-map (kbd "C-c w") 'rime-wubi-dict-adder-from-selected-region))
 
```

请根据您的系统环境调整路径配置。此配置示例：
1. 从本地目录加载插件
2. 设置 Python 路径（可选，当 python 不在环境变量时需配置）
3. 将主要功能绑定到 C-c w 快捷键
