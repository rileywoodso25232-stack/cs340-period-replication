# 本地上游源码

在仓库根目录运行 `python scripts/fetch_upstream.py`，
获取 `config/upstream.json` 指定提交版本的 PERIOD。

下载后的 `PERIOD/` 目录已被 Git 忽略。
不要提交其中嵌套的 Git 仓库或下载的依赖。
保留的原始许可证位于 `licenses/PERIOD-MIT.txt`。
