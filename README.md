<div align="center">
  <h1 align="center">RoboMimic Deploy</h1>
  <p align="center">
    <span> 🌎English </span> | <a href="README_zh.md"> 🇨🇳中文 </a>
  </p>
</div>

<p align="center">
  <strong>This is a repository for reinforcement learning implementation based on Unitree robots, supporting Unitree G1.</strong> 
</p>

## Installation and Configuration

## 1. Create a Virtual Environment

It is recommended to run training or deployment programs in a virtual environment. We suggest using Conda to create one.

### 1.1 Create a New Environment

Use the following command to create a virtual environment:
```bash
conda create -n robomimic python=3.8
```

### 1.2 Activate the Virtual Environment

```bash
conda activate robomimic
```

---

## 2. Install Dependencies

### 2.1 Install PyTorch
PyTorch is a neural network computation framework used for model training and inference. Install it with the following command:
```bash
conda install pytorch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 pytorch-cuda=12.1 -c pytorch -c nvidia
```

### 2.2 Install RoboMimic_Deploy

#### 2.2.1 Download
Clone the repository via git:

```bash
git clone https://github.com/ccrpRepo/RoboMimic_Deploy.git
```

#### 2.2.2 Install Components

Navigate to the directory and install:
```bash
cd RoboMimic_Deploy
pip install numpy==1.20.0
pip install onnx onnxruntime
```

#### 2.2.3 Install unitree_sdk2_python

```bash
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip install -e .
```
---
## Running the Code

## 1. Run Mujoco Simulation
```bash
python deploy_mujoco/deploy_mujoco.py
```

## 2. Policy Descriptions
- PassiveMode:   Damping protection mode
- FixedPose:     Position control to reset joint angles to default values
- LocoMode:      Control mode for stable walking
- Dance:         Charleston dance
- KongFu:        720-degree spinning kick (recommended only run in simulation)
- SkillCast:     Lower body and waist stabilization, upper body position-controlled to specific joint angles (typically executed before Mimic policy)
- SkillCooldown:  Lower body and waist continuous balancing, upper body reset to default joint angles (typically executed after Mimic policy)


---
## 3. 仿真操作说明
1. Connect an Xbox controller.
2. Run the simulation program:
```bash
python deploy_mujoco/deploy_mujoco.py
```
3. Press the ​​Start​​ button to enter position control mode.
4. Hold ​​R1 + A​​ to enter ​​LocoMode​​, then press BACKSPACE in the simulation to make the robot stand. Afterward, use the joystick to control walking.
5. Hold ​​R1 + X​​ to enter ​​Dance​​ mode—the robot will perform the Charleston. In this mode:
    - Press ​​L1​​ at any time to switch to damping protection mode.
    - Hold ​​R1 + A​​ to return to walking mode (not recommended).
    - Press ​​Start​​ to return to position control mode (not recommended).

6. The terminal will display a progress bar for the dance. After completion, press ​​R1 + A​​ to return to normal walking mode.
7. In ​​LocoMode​​, pressing ​​R1 + Y​​ triggers a 720-degree spinning kick—​​use only in simulation​​.

---
## 4. Real Robot Operation Instructions

1. Power on the robot and suspend it (e.g., with a harness).

2. Run the deploy_real program:
```bash
python deploy_real/deploy_real.py
```
3. Press the ​​Start​​ button to enter position control mode.
4. Subsequent operations are the same as in simulation.

---
## Important Notes
1. Deployment Recommendation​​:
- It is advised to deploy on a personal computer rather than the onboard Orin NX of the G1 robot.
- During testing, ​​LocoMode​​ and Mimic policies performed noticeably worse on the NX. The cause is currently unknown, feedback is welcome.

2. Mimic Policy Reliability​​:
- Success is not guaranteed, especially on slippery/sandy surfaces.
- If the robot loses control, immediately:
  Press ​​L1​​ to enter damping protection mode, or \
  Press ​​Select​​ to exit the control program.

3. 720-Degree Spinning Kick (R1+Y)​​:
- Strongly recommended for simulation only​​.
- If attempted on a real robot, ensure proper safety measures.
- The author assumes no responsibility for robot damage or injuries.