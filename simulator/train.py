from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv

from simulator.BlockchhainGymEnv import BlockchainCustomEnv
from sb3_contrib import RecurrentPPO
from stable_baselines3.common.evaluation import evaluate_policy
import numpy as np
import pandas as pd

from simulator.BlockchhainGymEnvWithCustomDataset import BlockchainCustomEnvWithCustomDataset

# import optuna


# def make_env():
#     env = BlockchainCustomEnv(
#         transaction_coefficient=0.8500582486876478,
#         waiting_time_coefficient=0.8119021197691496,
#         pending_transaction_coefficient=0.7869582013882934
#     )
#     return env
#
#
# vec_env = DummyVecEnv([make_env] * 8)

env = BlockchainCustomEnv(
        transaction_coefficient=0.8500582486876478,
        waiting_time_coefficient=0.8119021197691496,
        pending_transaction_coefficient=0.7869582013882934
    )

model = RecurrentPPO(
    "MlpLstmPolicy",
    env,
    verbose=1,
    tensorboard_log="./ppo_SimulatorBlockchainEnv_tensorboard/",
    n_steps=8192,
)
# model.learn(total_timesteps=250000)
# model.save("ppo_SimulatorBlockchainEnv_250000")


# loading model
model = RecurrentPPO.load("ppo_SimulatorBlockchainEnv_250000")



# customDataset

df = pd.read_csv("sample_transactions.csv")

env_custom_dataset = BlockchainCustomEnvWithCustomDataset(
        transaction_coefficient=0.8500582486876478,
        waiting_time_coefficient=0.8119021197691496,
        pending_transaction_coefficient=0.7869582013882934,
        transactions_data=df
)


# Enjoy trained agent
# obs = env.reset()
# for i in range(5000):
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
#     env.render()


# transaction_size = random.randint(1, 100)
# transaction_data = "Transaction " + str(random.randint(1, 100) + 1)




obs = env_custom_dataset.reset()

waiting_time = []

# loop through the rows using iterrows()
for index, row in df.iterrows():
    print(row['transaction_size'], row['transaction_data'])
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env_custom_dataset.step(action)
    w_time = list(info)[0]
    if w_time > 0:
        waiting_time.append(w_time)
    env_custom_dataset.render()


# average waiting time
print("Average waiting time: ", np.sum(waiting_time))

print("Blockchain length", len(env.blockchain.chain))




# Evaluate the agent
# mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=20, warn=False)
#
# print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")


# Trained model



# def objective(trial):
#     # Define the hyperparameters to tune
#     transaction_coefficient_train = trial.suggest_uniform("transaction_coefficient", -1, 1)
#     waiting_time_coefficient_train = trial.suggest_uniform("waiting_time_coefficient", -1, 1)
#     pending_transaction_coefficient_train = trial.suggest_uniform("pending_transaction_coefficient", -1, 1)
#
#     def make_env():
#         env = BlockchainCustomEnv(
#             transaction_coefficient=transaction_coefficient_train,
#             waiting_time_coefficient=waiting_time_coefficient_train,
#             pending_transaction_coefficient=pending_transaction_coefficient_train
#         )
#         env = Monitor(env, filename="./ppo_SimulatorBlockchainEnv_tensorboard/")
#         return env
#
#     vec_env = DummyVecEnv([make_env] * 1)
#
#     model = PPO(
#         "MlpPolicy",
#         vec_env,
#         verbose=1,
#     )
#     model.learn(total_timesteps=25000)
#
#
#     # predict the mean reward
#
#     obs = vec_env.reset()
#
#     total_reward = []
#
#     for i in range(1000):
#         action, _states = model.predict(obs)
#         observation, reward, done, info = vec_env.step(action)
#         total_reward.append(reward)
#
#     mean_reward = np.mean(total_reward)
#
#     return mean_reward
#
#
# study = optuna.create_study(
#     direction="maximize",
#     storage="sqlite:///db.sqlite3",
#     study_name="ppo_SimulatorBlockchainEnv"
# )
# study.optimize(objective, n_trials=100)
# print(f"Best value: {study.best_value} (params: {study.best_params})")
#
#
# transaction_coefficient = study.best_params["transaction_coefficient"]
# waiting_time_coefficient = study.best_params["waiting_time_coefficient"]
# pending_transaction_coefficient = study.best_params["pending_transaction_coefficient"]
#
# print("transaction_coefficient: ", transaction_coefficient)
# print("waiting_time_coefficient: ", waiting_time_coefficient)
# print("pending_transaction_coefficient: ", pending_transaction_coefficient)
