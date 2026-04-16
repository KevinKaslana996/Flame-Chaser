# Flame-Chaser

一个交通专业学生练手写的轨迹预测小工具。目前还很简陋，正在开发中。

## ✨ 项目简介

基于 SUMO 仿真数据，对车辆轨迹进行预测分析。本项目是我学习 Python、Git 和交通数据分析过程中的一个实践项目。

**当前状态：** 🚧 开发中，功能不稳定，代码质量随缘。

## 📁 目录结构

- `model/tracl.py`：核心代码，通过 TraCI 接口从 SUMO 仿真中提取车辆轨迹数据
- `data/`：SUMO 仿真路网和路径文件
- `.gitignore`：忽略缓存和虚拟环境文件

## 🚀 快速开始

### 环境依赖
- Python 3.x
- SUMO（已配置 TraCI）
- 其他依赖见 `requirements.txt`（如果有的话）

### 运行
```bash
python model/tracl.py
