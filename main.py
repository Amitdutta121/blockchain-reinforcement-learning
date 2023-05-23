import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from env.BlockchainEnv import BlockchainEnv



# env = BlockchainEnv()

env = make_vec_env(BlockchainEnv, n_envs=8)

# obs = env.reset()

# while True:
# action = 751816
# obs, rewards, dones, info = env.step(action)
# print("rewards", rewards)
# # env.render()


# Save a checkpoint every 1000 steps
# checkpoint_callback = CheckpointCallback(
#     save_freq=100,
#     save_path="./logs/",
#     name_prefix="rl_model",
#     save_replay_buffer=True,
#     save_vecnormalize=True,
# )

model = PPO(
    "MlpPolicy",
    env,
    n_steps=64,
    verbose=1,
    batch_size=64 * 1,
    tensorboard_log="./ppo_BlockchainEnv_tensorboard/"
)

model.learn(
        total_timesteps=10,
        # callback=checkpoint_callback,
        reset_num_timesteps=True,
        tb_log_name="PPO",
    )

# TIMESTEPS = 10
#
# for i in range(1, 1000):
#     model.learn(
#         total_timesteps=100000,
#         # callback=checkpoint_callback,
#         reset_num_timesteps=True,
#         tb_log_name="PPO",
#     )
#     model.save(f"ppo_{TIMESTEPS * i}_BlockchainEnv")


# test_rewards = []
#
# obs = env.reset()
# while True:
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     print("action", action)
#     print("rewards", rewards)
#     test_rewards.append(rewards)
#     print("obs", obs)
#     print("dones", dones)
#     print("info", info)
#     env.render()


# conn.close()


# new_df = pd.read_pickle("./env/blockchaindata/state/transactions-per-second_0.pkl")
# print(new_df.head(10))

# sample_df = get_transaction_per_second("./env/blockchaindata/state/transactions-per-second_*.pkl", 1641031200, 1641031200, 'x')
# print(sample_df.head(10))


# import gym
#
# from stable_baselines3 import PPO
# from stable_baselines3.common.env_util import make_vec_env
#
# # Parallel environments
# env = make_vec_env("CartPole-v1", n_envs=4)
#
# model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=25000)
# model.save("ppo_cartpole")
#
# del model # remove to demonstrate saving and loading
#
# model = PPO.load("ppo_cartpole")
#
# obs = env.reset()
# while True:
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     env.render()
