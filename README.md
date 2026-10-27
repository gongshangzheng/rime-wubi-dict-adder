# Rime 五笔词典管理工具（Emacs 插件）

把词条 + 五笔码追加到 Rime 用户词典，并提供词典体检命令。

## 环境要求

- Python 3.11+
- `pywubi`（由 `pyproject.toml` 声明，`uv sync` 一次装好）

```bash
cd ~/.emacs.d/modules/rime-wubi-dict-adder
uv sync          # 生成/更新 .venv 与 uv.lock
```

插件默认优先使用模块内 `.venv/bin/python`，不存在时回退 `python3`，因此通常**不需要**配 `rime-wubi-dict-adder-python-command`。

## Emacs 集成

```emacs-lisp
(use-package rime-wubi-dict-adder
  :load-path "~/.emacs.d/modules/rime-wubi-dict-adder"
  :config
  ;; 可选：自定义解释器 / 脚本 / 词典路径
  ;; (setq rime-wubi-dict-adder-python-command "/path/to/python")
  ;; (setq rime-wubi-dict-adder-user-dict "~/Library/Rime/wubi86_jidian_user.dict.yaml")
  ;; 可选：写入后让 Rime 重新部署（默认不做）
  ;; (setq rime-wubi-dict-adder-deploy-command
  ;;       '("/Library/Input Methods/Squirrel.app/Contents/MacOS/rime_deployer" "--build"))
  (define-key global-map (kbd "C-c r") #'rime-wubi-dict-adder-2-character-back)
  (define-key global-map (kbd "C-c w") #'rime-wubi-dict-adder-from-selected-region))
```

## 命令

| 命令 | 作用 |
|---|---|
| `rime-wubi-dict-adder-with-python` | 输入一个（或多个）词，追加其五笔码 |
| `rime-wubi-dict-adder-from-selected-region` | 把选区里的词（可多个，按空白分隔）一次加入 |
| `rime-wubi-dict-adder-2-character-back` | 加入光标前两个字 |
| `rime-wubi-dict-adder` | 手动指定词与码写入，不启动 Python |
| `rime-wubi-dict-adder-lint-dict` | **格式体检**（不用 Python）：缺 TAB、码非法、权重列非法，只报告不改 |
| `rime-wubi-dict-adder-check-dict` | **完整体检**（用 pywubi）：格式 + 用 pywubi 重算每个词条并与词典比对 + 重复词检测，报告里 `RET` 跳到对应行 |

### 两种体检怎么选

- `lint-dict`：秒出，纯格式规则，适合随时扫一眼。
- `check-dict`：会重算 5000+ 词条的码（实测约 40 ms），能发现「码写错/写短」「同一个词定义两次」这类内容错误，并给出建议码。

`check-dict` 的判定分级：

| 状态 | 级别 | 含义 |
|---|---|---|
| `format` | ERROR | 行内没有 TAB 分隔 |
| `invalid-code` | ERROR | 码不是 1–4 个小写字母 |
| `invalid-weight` | ERROR | 第三列（权重）不是数字 |
| `duplicate` | ERROR | 同一个词出现多次 |
| `mismatch` | ERROR | 与 pywubi 计算值不一致 |
| `shorter` | warn（**默认不显示**） | 是 pywubi 计算值的前缀。Rime 按前缀匹配，三码简写是有意的，故默认静音；`(setq rime-wubi-dict-adder-check-report-shorter t)` 或 `--report-shorter` 可打开 |
| `unverifiable` | warn | pywubi 无法为此词算出码（生僻字等） |

`z` 开头的码属于 Rime 的符号命名空间（如 `·⇥za`、`->⇥zr`），不做内容校验。

## 写入规则

- 已存在的词：直接返回，**不启动 Python**（词典索引按 mtime/size 缓存）。
- 新词：`call-process` 调 `dictAdder.py`，不经过 shell，因此词里含空格、`;`、`$` 之类不会被解释。
- **任一词非法则整批不写**：词为空/含空白/混入非汉字（pywubi 返回多段码）/生成的码不合法，都会报错并保持词典不变。
- 批量：一个选区里的多个词只启动一次 Python、扫一次词典、写一次文件。

## 命令行用法

```bash
# 添加
.venv/bin/python dictAdder.py 中国 测试词 -d ~/Library/Rime/wubi86_jidian_user.dict.yaml
# → [{"word": "中国", "code": "khlg", "status": "added"}, ...]

# 全量体检
.venv/bin/python dictAdder.py --check -d ~/Library/Rime/wubi86_jidian_user.dict.yaml
# → {"summary": {"lines": 5221, "entries": 5220, "errors": 5, "warnings": 3}, "findings": [...]}
```

两者都输出单行 JSON；退出码 0 表示无错误，1 表示有问题（写入模式下一词未写）。
