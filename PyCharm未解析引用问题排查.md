# PyCharm "未解析引用" 问题排查记录

## 现象

PyCharm 中 Python 代码大面积报"未解析引用"（import 飘红），但实际运行完全正常，第三方包都已安装。

---

## 根因

**Windows 用户名是中文"唐诗涵"**，venv 路径形如 `C:\Users\唐诗涵\Desktop\python\.venv`，包含中文字符。

PyCharm 在添加 / 重检 venv 解释器时，会运行 venv 里的 `python` 让其打印 `sys.path`，内容通过**管道**传给 PyCharm。

问题就出在这一步：

- Python 3.14 在中文 Windows locale 下默认用 **GBK** 编码输出管道内容
- PyCharm 按 **UTF-8** 解码
- `"唐诗涵"` 的 GBK 字节 `CC C6 CA AB BA AD` 被按 UTF-8 解读成乱码 `??ʫ??`
- 该路径在磁盘上不存在，被 PyCharm 的 `PythonSdkUpdater` 判为 "Bogus sys.path entry" 丢弃
- 最终写进 `jdk.table.xml` 的 SDK 配置里，`<classPath>` 的 `<roots>` **少了 `.venv` 和 `.venv/Lib/site-packages`**
- 所有第三方 import 因此无法被解析

> 运行正常的根本原因：运行时 `sys.path` 由 Python 自己计算，不依赖 PyCharm 的 SDK roots 配置。

---

## 解决方法

两步必须配合，缺一不可：

### 1. 设置系统环境变量（用户级）

```bash
setx PYTHONUTF8 1
```

作用：让 Python 强制用 UTF-8 输出（[PEP 540](https://peps.python.org/pep-0540/)），从根本上避免 GBK → UTF-8 乱码。Python 3.15 起这会是默认行为，安全可逆。

查看是否生效：新开终端执行 `python -c "import sys; print(sys.stdout.encoding)"`，输出 `utf-8` 即生效。

### 2. 重启 PyCharm 并重建解释器

- **完全退出** PyCharm（让新的环境变量被新进程继承）
- 重启后，进入 `Settings → Project → Python Interpreter`，**删除原来那个 venv 解释器**
- 重新添加 venv 解释器，使 `jdk.table.xml` 重新生成正确的 SDK roots

---

## 验证方法

成功标志：

- 检查 `%APPDATA%\JetBrains\PyCharm2025.3\config\options\jdk.table.xml`，找到对应 SDK 的 `<classPath>`，里面的 `<roots>` 列表应包含 site-packages 项，形如：
  ```xml
  <root url="file://$USER_HOME$/Desktop/python/.venv/Lib/site-packages" type="SOURCES" />
  ```
- PyCharm 中飘红的 `import` 全部恢复正常

失败标志：

- 在 PyCharm `Help → Show Log in Explorer` 查看 `idea.log`，再次出现 `Bogus sys.path entry C:\Users\??ʫ??\...`，说明环境变量没继承到位，PyCharm 需要完全退出再重启

---

## 排查过程中尝试过但失败的方案（踩坑记录）

- ❌ `Invalidate Caches`：治标不治本，重建索引后很快又飘红
- ❌ 删掉 SDK 条目再重建：无环境变量时，每次重建都会再次乱码丢弃
- ❌ `Mark as Sources` 手动把 site-packages 打成 Sources：SDK roots 重算时复发
- ❌ 终端 `pip install` 重装：包本来就没问题，问题在 PyCharm 配置层面

---

## 根本性建议

- **长期方案**：新项目优先放在**纯 ASCII 路径**下，例如 `D:\code\myproject`，彻底回避此问题
- **临时方案**：保留 `PYTHONUTF8=1` 用户变量，不影响现有项目
- **副作用须知**：`PYTHONUTF8=1` 在老旧 `cmd` 窗口直接 `print("中文")` 可能反而乱码（cmd 不一定支持 UTF-8 输出），但 PyCharm / Windows Terminal / VS Code 都正常
- **撤销方法**：`setx PYTHONUTF8 ""` 或在"系统属性 → 高级 → 环境变量"的用户变量区域删除 `PYTHONUTF8` 这一行

---

## 排查时间线

- **2026-09-09**：从误诊"装错环境"→"索引过期"→"删重建"→最终在 `idea.log` 抓到 `Bogus sys.path entry` 乱码，并用 `xxd` 字节级比对 GBK vs UTF-8 字节确认根因；设 `PYTHONUTF8=1` + 重启 PyCharm + 重建解释器后修复
