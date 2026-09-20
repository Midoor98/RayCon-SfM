<p align="center">
  <img src="docs/assets/hero-v0.1.png" alt="RayCon-SfM v0.1.0 public preview — concept artwork" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/Midoor98/RayCon-SfM/releases/tag/v0.1.0"><img alt="Version v0.1.0" src="https://img.shields.io/badge/preview-v0.1.0-8b7cff?style=flat-square" /></a>
  <img alt="C++17" src="https://img.shields.io/badge/C%2B%2B-17-4cc9f0?style=flat-square" />
  <img alt="Python 3.10 or later" src="https://img.shields.io/badge/Python-3.10%2B-80e8cf?style=flat-square" />
  <img alt="Synthetic examples included" src="https://img.shields.io/badge/data-synthetic-25334d?style=flat-square" />
</p>

<h1 align="center">RayCon-SfM</h1>
<p align="center"><strong>Structure from Motion</strong><br />运动恢复结构（SfM）</p>
<p align="center"><a href="#quick-start">Quick start</a> · <a href="#preview">Preview</a> · <a href="#roadmap">Roadmap</a> · <a href="docs/INPUTS.md">Input formats</a> · <a href="CHANGELOG.md">Changelog</a></p>

RayCon-SfM 是一个运动恢复结构（SfM）项目，按版本逐步开放代码。首个公开版本先开放配套工具；下一版本计划提供 SfM 系统试运行代码、示例配置与启动脚本。 `v0.1.0` 提供两套可以独立运行的 C++17 / Python 工具、可再生合成样例、图像预览和本地检查脚本。

> **Public preview**：当前 `v0.1.0` 开放配套工具与合成样例，SfM 系统试运行入口计划在下一版本提供。 封面是概念插画；下面的预览图来自本仓库合成数据的实际输出。

## Available in v0.1

| Module | Available in v0.1.0 |
| --- | --- |
| Organize | 通过图连通分量整理成对特征关联，确定性排序与编号 |
| Validate | 去除重复边，剔除同图冲突与视图不足的分量 |
| Export | 输出特征轨迹 JSON、可见性 CSV 和拒绝记录 |
| C++ + Python | 标准库实现，无私有依赖；附两种实现的输出交叉检查 |

## Quick start

### C++ preview

需要 C++17 编译器、CMake 3.16 及以上版本。默认构建包含检查工具，因此也需要 Python 3.10 及以上版本。

```bash
git clone https://github.com/Midoor98/RayCon-SfM.git
cd RayCon-SfM
bash run_cpp.sh
```

输出位于新的 `result/cpp-*` 目录。查看版本与参数：

```bash
./build/raycon_sfm_preview --version
./build/raycon_sfm_preview --help
```

### Python preview

只使用 Python 标准库，无需安装额外包：

```bash
bash run.sh
bash run.sh --version
```

两个入口均可传入 `--input` 和 `--output`，指定的输出目录必须尚不存在。完整字段与坐标约定见 [Input formats](docs/INPUTS.md)。不需要 Python 的纯 C++ 构建可使用 `-DBUILD_TESTING=OFF`。

## Preview

![RayCon-SfM synthetic data preview](docs/assets/demo-preview.png)

16 条轨迹来自程序生成的特征关联，8 个图像编号不代表真实图像重建或相机注册结果。 这张图不表示定位或重建精度。

生成样例、运行 C++ 并重绘预览：

```bash
python3 scripts/make_example.py
bash run_cpp.sh --input data/showcase_matches.csv --output result/my-preview
python3 -m pip install -r requirements-preview.txt
python3 scripts/render_preview.py --input result/my-preview/tracks.json
```

`matplotlib` 仅用于重绘预览；普通运行与测试不依赖它。再次运行时为 `--output` 换一个新目录。封面来源与生成提示见 [Artwork](docs/ARTWORK.md)。

## Roadmap

| Target | Planned public content | Status |
| --- | --- | --- |
| September 2026 · v0.1.0 | C++ / Python 工具、合成数据、导出样例、预览图 | Available |
| October 2026 | 完善数据接口、示例配置和配套工具文档 | Planned |
| November 2026 | 准备 SfM 系统试运行入口与测试样例 | Planned |
| **December 2026 · v0.2 preview** | **计划发布 SfM 试运行代码、示例配置和启动脚本** | **Tentative** |

下一版本以 SfM 系统试运行为目标，暂定于 2026 年 12 月开放；具体功能、支持数据和运行要求以对应 GitHub Release 为准。

## Build & checks

```bash
bash scripts/check.sh
```

检查涵盖 Python 单元测试、C++ Release 构建、两种实现的输出一致性、非法输入、已有结果保护以及版本标识。当前在 Ubuntu / GCC 环境核验；仓库不包含平台专属编译产物。

```text
cpp/                 C++17 source and small CSV utilities
src/                 Python implementation
data/                Synthetic fixtures only
scripts/             Checks, fixture generation and preview rendering
tests/               Unit tests and C++/Python cross-checks
docs/                Input reference and visual assets
CMakeLists.txt       Standalone C++ build
VERSION              Public preview version
```

## Feedback

使用 [Issues](https://github.com/Midoor98/RayCon-SfM/issues) 报告复现步骤、输入格式问题或公开工具的改进建议。请用合成或可公开的数据描述问题。
