# exptrack_jd166

**找出实验管理与追踪工程师·投机解码的命中率里互相矛盾的两处并排列出。**

`exptrack_jd166` —— 在同一个输入里两两比对，检测实验管理与追踪工程师·投机解码的命中率相关的矛盾表述，把冲突双方原样并排呈现

- 零依赖，Python 3.10+ 标准库即可运行
- 单文件，`exptrack_jd166.py` 拷走就能用
- 不联网、不写文件

## 对应的岗位

- 目标岗位：**华为 · 资深实验管理与追踪工程师**
- 技能主线：MLOps、Python、Ray
- 领域标签：MLOps
- 研究方向：实验管理与追踪工程师·投机解码的命中率

工具里的规则表就是照着上面这条岗位要求建的——每条规则都挂在技能线或领域标签上，命中时能指回具体要求。

<!-- ipos:install -->
## 安装

零依赖，Python 3.10+ 即可：

```bash
pip install wangliwesi-exptrack_jd166
```

装完直接用命令名调用：

```bash
exptrack_jd166 --help
```

也可以不用安装，直接把 `exptrack_jd166.py` 拷走用——它只依赖标准库。

## 为什么需要它

不替用户猜哪一句是本意，只把矛盾双方并排摆出来，由人决定取舍

它遵守下面几条自己定的规矩：

1. **只报告能定位到具体位置的结论**，不做语义猜测。
2. **规则表公开**，每条命中都能对应到岗位要求的一条明示规则。
3. **输入为空或格式不对时明确报错**，不静默返回空结果。

## 用法

```bash
python exptrack_jd166.py --file input.txt
python exptrack_jd166.py --text "示例内容"
python exptrack_jd166.py --file input.txt --json
```

加 `--json` 可以拿到机器可读的结果，便于接到流水线里。

## 已知局限

- 一致性靠字面差异判定，语义等价但写法不同会误报。
- 不解析跨文档的引用关系。

## 跑测试

```bash
python test_exptrack_jd166.py
```

测试用独立的断言与临时数据，不污染工作目录。

## 来源与参考

- Python 标准库文档：<https://docs.python.org/3/>
- GitHub 仓库：<https://github.com/wangliwesi/exptrack_jd166>

---

## 关于作者

wangliwesi 做实验管理与追踪工程师·投机解码的命中率相关的问题，方向对标华为的资深实验管理与追踪工程师岗位。这个工具先替你回答一个具体问题，再谈别的。

- 个人主页：<https://wangliwesi.github.io>
- 仓库：<https://github.com/wangliwesi/exptrack_jd166>

## 许可

MIT，见 [LICENSE](LICENSE)。
