from stable_baselines3.common.vec_env import DummyVecEnv

from simulator.BlockchhainGymEnv import BlockchainCustomEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor


def make_env():
    env = BlockchainCustomEnv()
    env = Monitor(env, filename="./ppo_SimulatorBlockchainEnv_tensorboard/")
    return env


vec_env = DummyVecEnv([make_env] * 8)

model = PPO(
    "MlpPolicy",
    vec_env,
    verbose=1,
    tensorboard_log="./ppo_SimulatorBlockchainEnv_tensorboard/"
)
model.learn(total_timesteps=2500000)
model.save("ppo_SimulatorBlockchainEnv")
