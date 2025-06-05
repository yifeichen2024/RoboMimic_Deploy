<div align="center">
  <h1 align="center">RoboMimic Deploy</h1>
  <p align="center">
    <a href="README.md">🌎 English</a> | <span>🇨🇳 中文</span>
  </p>
</div>

<p align="center">
  🎮🚪 <strong>RoboMimic Deploy 是一个基于状态切换机制的机器人多策略部署框架，目前包含的策略适用于宇树G1机器人(29dof)</strong> 🚪🎮
</p>

## 安装配置

## 1. 创建虚拟环境

建议在虚拟环境中运行训练或部署程序，推荐使用 Conda 创建虚拟环境。

### 1.1 创建新环境

使用以下命令创建虚拟环境：

```bash
conda create -n robomimic python=3.8
```

### 1.2 激活虚拟环境

```bash
conda activate robomimic
```

---

## 2. 安装依赖

### 2.1 安装 PyTorch

PyTorch 是一个神经网络计算框架，用于模型训练和推理。使用以下命令安装：

```bash
conda install pytorch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 pytorch-cuda=12.1 -c pytorch -c nvidia
```

### 2.2 安装 RoboMimic_Deploy

#### 2.2.1 下载

通过 Git 克隆仓库：

```bash
git clone https://github.com/ccrpRepo/RoboMimic_Deploy.git
```

#### 2.2.2 安装组件

进入目录并安装：

```bash
cd RoboMimic_Deploy
pip install numpy==1.20.0
pip install onnx onnxruntime
```
#### 2.2.3 安装unitree_sdk2_python

```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```
---
## 运行代码

## 1. 运行Mujoco仿真代码
```bash
python deploy_mujoco/deploy_mujoco.py
```
---
## 2. Policy 说明
- PassiveMode:   阻尼保护模式
- FixedPose:     位控恢复至默认关节值
- LocoMode:      用于稳定行走的控制模式
- Dance:         查尔顿斯舞
- KongFu:        720度回旋踢（建议只在仿真中运行）
- SkillCast:     下肢+腰部稳定站立，上肢位控至特定关节角，一般在执行Mimic策略前执行
- SkillCooldown:  下肢+腰部持续平衡，上肢恢复至默认关节角，一般在执行Mimic策略后执行

---
## 3. 仿真操作说明

1. 连接Xbox手柄
2. 运行仿真程序：
```bash
python deploy_mujoco/deploy_mujoco.py
```
3. Start键进入位控模式
4. 同时按住R1+A，进入LocoMode，并按下`BACKSPACE`在仿真中使机器人站立，之后能通过摇杆控制机器人行走
5. 同时按住R1+X，进入Dance，机器人开始跳查尔顿斯舞，在该模式下，可以随时按下L1进入阻尼保护模式，也可以按住R1+A恢复行走模式（不推荐），或按Start进入位控模式（不推荐）
6. 终端会显示舞蹈的进度条，结束后可按下R1+A恢复至正常行走模式
7. 在LocoMode模式下还可以按R1+Y让机器人720度回旋踢，只推荐在仿真中使用
---
## 4. 真机操作说明
1. 开机后将机器人吊起来
2. 运行deploy_real程序：
```bash
python deploy_real/deploy_real.py
```
3. Start键进入位控模式
4. 后续操作与仿真中一致

---
## 注意事项
1. 建议部署在自己的个人电脑上，而不是G1的机载Orin NX上，作者测试时部署在NX上，LocoMode和各个Mimic策略的效果都有明显下降，目前不清楚原因，欢迎大家积极反馈；
2. Mimic策略不保证百分百的成功率，尤其在湿滑/沙地等地面上，若机器人出现失控的情况，请马上按下L1键进入阻尼保护模式，或按下Select键直接退出控制程序；
3. 720度回旋踢的动作（R1+Y）只建议在仿真中运行，如果非要在真机运行，请做好充分的保护措施，若出现机器人损坏或人员受伤等情况，作者不负任何责任。



