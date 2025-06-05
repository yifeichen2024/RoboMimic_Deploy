import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from common.path_config import PROJECT_ROOT
from common.ctrlcomp import *
from FSM.FSM import *
from typing import Union
import numpy as np
import time
import os
import yaml

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_, unitree_hg_msg_dds__LowState_
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowCmd_, unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_ as LowCmdHG
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowCmd_ as LowCmdGo
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as LowStateHG
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_ as LowStateGo
from unitree_sdk2py.utils.crc import CRC

from common.command_helper import create_damping_cmd, create_zero_cmd, init_cmd_hg, init_cmd_go, MotorMode
from common.rotation_helper import get_gravity_orientation_real, transform_imu_data
from common.remote_controller import RemoteController, KeyMap

def send_cmd(cmd: Union[LowCmdGo, LowCmdHG]):
    cmd.crc = CRC().Crc(cmd)
    lowcmd_publisher_.Write(cmd)

def LowStateHgHandler(msg: LowStateHG):
    low_state = msg
    mode_machine_ = low_state.mode_machine
    remote_controller.set(low_state.wireless_remote)
    
def wait_for_low_state():
    while low_state.tick == 0:
        time.sleep(0.02)
    print("Successfully connected to the robot.")
        
def zero_torque_state():
    print("Enter zero torque state.")
    print("Waiting for the start signal...")
    while not remote_controller.is_button_released(KeyMap.start):
        create_zero_cmd(low_cmd)
        send_cmd(low_cmd)
        time.sleep(control_dt)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    mujoco_yaml_path = os.path.join(current_dir, "config", "real.yaml")
    with open(mujoco_yaml_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        net = config["net"]
        num_joints = config["num_joints"]
        lowcmd_topic = config["lowcmd_topic"]
        lowstate_topic = config["lowstate_topic"]
        control_dt = config["control_dt"]
        error_over_time = config["error_over_time"]
        
    ChannelFactoryInitialize(0, net)
    
    remote_controller = RemoteController()
    low_cmd = unitree_hg_msg_dds__LowCmd_()
    low_state = unitree_hg_msg_dds__LowState_()
    mode_pr_ = MotorMode.PR
    mode_machine_ = 0
    lowcmd_publisher_ = ChannelPublisher(lowcmd_topic, LowCmdHG)
    lowcmd_publisher_.Init()

    # inital connection
    lowstate_subscriber = ChannelSubscriber(lowstate_topic, LowStateHG)
    lowstate_subscriber.Init(LowStateHgHandler, 10)
    
    # wait for the subscriber to receive data
    wait_for_low_state()
    
    init_cmd_hg(low_cmd, mode_machine_, mode_pr_)
    
    policy_output_action = np.zeros(num_joints, dtype=np.float32)
    kps = np.zeros(num_joints, dtype=np.float32)
    kds = np.zeros(num_joints, dtype=np.float32)
    qj = np.zeros(num_joints, dtype=np.float32)
    dqj = np.zeros(num_joints, dtype=np.float32)
    quat = np.zeros(4, dtype=np.float32)
    ang_vel = np.zeros(3, dtype=np.float32)
    gravity_orientation = np.array([0,0,-1], dtype=np.float32)
    
    state_cmd = StateAndCmd(num_joints)
    policy_output = PolicyOutput(num_joints)
    FSM_controller = FSM(state_cmd, policy_output)
    
    running = True
    counter_over_time = 0
    while(not remote_controller.is_button_pressed(KeyMap.L1) and running):
        try:
            if(counter_over_time >= error_over_time):
                raise ValueError("counter_over_time >= error_over_time")
            
            loop_start_time = time.time()
            
            if remote_controller.is_button_released(KeyMap.select):
                state_cmd.skill_cmd = FSMCommand.PASSIVE
            if remote_controller.is_button_released(KeyMap.start):
                state_cmd.skill_cmd = FSMCommand.POS_RESET
            if remote_controller.is_button_released(KeyMap.A) and remote_controller.is_button_pressed(KeyMap.R1):
                state_cmd.skill_cmd = FSMCommand.LOCO
            if remote_controller.is_button_released(KeyMap.X) and remote_controller.is_button_pressed(KeyMap.R1):
                state_cmd.skill_cmd = FSMCommand.SKILL_1
            if remote_controller.is_button_released(KeyMap.Y) and remote_controller.is_button_pressed(KeyMap.R1):
                state_cmd.skill_cmd = FSMCommand.SKILL_2
            
            for i in range(num_joints):
                qj[i] = low_state.motor_state[i].q
                dqj[i] = low_state.motor_state[i].dq

            # imu_state quaternion: w, x, y, z
            quat = low_state.imu_state.quaternion
            ang_vel = np.array([low_state.imu_state.gyroscope], dtype=np.float32)
            
            gravity_orientation = get_gravity_orientation_real(quat)
            
            state_cmd.q = qj.copy()
            state_cmd.dq = dqj.copy()
            state_cmd.gravity_ori = gravity_orientation.copy()
            state_cmd.ang_vel = ang_vel.copy()
            
            FSM_controller.run()
            policy_output_action = policy_output.actions.copy()
            kps = policy_output.kps.copy()
            kds = policy_output.kds.copy()
            
            # Build low cmd
            for i in range(len(num_joints)):
                low_cmd.motor_cmd[i].q = policy_output_action[i]
                low_cmd.motor_cmd[i].qd = 0
                low_cmd.motor_cmd[i].kp = kps[i]
                low_cmd.motor_cmd[i].kd = kds[i]
                low_cmd.motor_cmd[i].tau = 0
                
            # send the command
            create_damping_cmd(low_cmd) # only for debug
            send_cmd(low_cmd)
            
            loop_end_time = time.time()
            delta_time = loop_end_time - loop_start_time
            if(delta_time < control_dt):
                time.sleep(control_dt - delta_time)
                counter_over_time = 0
            else:
                print("control loop over time.")
                counter_over_time += 1
            pass
        except ValueError as e:
            print("CATCHED ERROR!!!")
            
            
    create_damping_cmd(low_cmd)
    send_cmd(low_cmd)
    print("Exit")
    
    