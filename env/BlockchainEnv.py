import glob
import random
from datetime import datetime

import dask
import gym
import numpy as np
import pandas as pd
from fastparquet import ParquetFile
from gym import spaces
import math

DURATION = 1 * 60 * 60 * 24  # 1 day
EPISODE_END = 60 * 60 * 24 * 20  # 10 days


def get_transaction_per_second(picklePath: str, start_timestamp: int, end_timestamp: int,
                               time_col: str = 'x') -> pd.DataFrame:
    # Get the list of pickle file names
    pickle_files = glob.glob(picklePath)
    dfs = []
    # convert timestamp to datetime
    start_timestamp = pd.to_datetime(start_timestamp, unit='s')
    end_timestamp = pd.to_datetime(end_timestamp, unit='s')
    # Iterate over the pickle files
    for file_name in pickle_files:
        # Read the current file using dask.delayed()
        df = dask.delayed(pd.read_pickle)(file_name)
        filtered_df = df[(df[time_col] >= start_timestamp) & (df[time_col] <= end_timestamp)]
        dfs.append(filtered_df)
    # Concatenate all the dask dataframe
    final_df = dask.compute(*dfs)
    final_df = pd.concat(final_df)
    return final_df


def sum_fees(transactions_data, block_size):
    current_size = 0
    total_fee = 0
    counted_transactions = 0

    last_size = 0
    last_fee = 0
    for index, row in transactions_data.iterrows():
        if current_size < block_size:
            last_size = row['size']
            last_fee = row['fee']

            current_size += row['size']
            total_fee += row['fee']
            counted_transactions = counted_transactions + 1
        else:
            current_size -= last_size
            total_fee -= last_fee
            counted_transactions = counted_transactions - 1
            break
    uncounted_transactions = transactions_data.shape[0] - counted_transactions
    return total_fee, uncounted_transactions


def read_transactions_new(start_timestamp, end_timestamp, directory):
    #     extract only date from start_timestamp and end_timestamp
    start_date = datetime.fromtimestamp(int(start_timestamp)).strftime('%Y-%m-%d')
    end_date = datetime.fromtimestamp(int(end_timestamp)).strftime('%Y-%m-%d')
    # print(start_date)
    # print(end_date)
    #     if start date and end date are same then read only one file
    start_date = start_date.replace('-', '')
    end_date = end_date.replace('-', '')
    if start_date == end_date:
        # print("Same date")
        # format start_date to a single string without the -

        # df = dask.delayed(pd.read_table)(f"{directory}/blockchair_bitcoin_transactions_{start_date}.tsv.gz")
        try:

            df = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_{start_date}.parquet")
            df = df.to_pandas()
        except:
            df = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_20170101.parquet")
            df = df.to_pandas()




    else:
        #         if start date and end date are different then read the two files and concat them
        # print("Different date")
        # df1 = dask.delayed(pd.read_table)(f"{directory}/blockchair_bitcoin_transactions_{start_date}.tsv.gz")
        # df2 = dask.delayed(pd.read_table)(f"{directory}/blockchair_bitcoin_transactions_{end_date}.tsv.gz")
        # df = dask.delayed(pd.concat)([df1, df2], axis=0)

        try:

            df1 = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_{start_date}.parquet")
            df2 = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_{end_date}.parquet")

            df = pd.concat([df1.to_pandas(), df2.to_pandas()], axis=0)
        except:
            df1 = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_20170101.parquet")
            df2 = ParquetFile(f"{directory}/blockchair_bitcoin_transactions_20170102.parquet")
            df = pd.concat([df1.to_pandas(), df2.to_pandas()], axis=0)

    # result = df.compute()
    df.sort_values(by='fee', ascending=False, inplace=True)
    return df


def read_transactions(start_timestamp, end_timestamp, directory):
    files = glob.glob(f"{directory}/*.gz")
    dfs = [dask.delayed(pd.read_table)(f) for f in files]
    df = dask.delayed(pd.concat)(dfs, axis=0)
    df = df.assign(time=dask.delayed(pd.to_datetime)(df['time']))
    start_time = datetime.fromtimestamp(int(start_timestamp))
    end_time = datetime.fromtimestamp(int(end_timestamp))
    df = df[(df['time'] >= start_time) & (df['time'] <= end_time)]
    result = df.compute()
    result.sort_values(by='fee', ascending=False, inplace=True)
    del df
    return result


def search_by_timestamp(path, timestamp):
    df = pd.read_csv(path)
    # Convert the timestamp to a datetime format
    date = pd.to_datetime(timestamp, unit='s')
    # Filter the data based on the date
    df['index'] = pd.to_datetime(df['index'])
    filtered_data = df[df['index'].dt.date == date.date()]
    return filtered_data


# def search_by_timestamp_by_x(path, timestamp):
#     df = pd.read_csv(path)
#     # Convert the timestamp to a datetime format
#     date = pd.to_datetime(timestamp, unit='s')
#     # Filter the data based on the date
#     df['x'] = pd.to_datetime(df['x'])
#     filtered_data = df[df['x'].dt.date == date.date()]
#     return filtered_data
#
#     def get_transaction_from_database(self, start_timestamp, end_timestamp):
#         # Create a cursor object
#         cursor = self.conn.cursor()
#
#         # Define the SQL query
#         sql = '''SELECT * FROM transactions WHERE time BETWEEN %s AND %s'''
#
#         # Execute the query and retrieve the data
#         cursor.execute(sql, (start_timestamp, end_timestamp))
#         rows = cursor.fetchall()
#
#         # Convert the data to a pandas dataframe
#         df = pd.DataFrame(rows,
#                           columns=['block_id', 'time', 'size', 'input_total_usd', 'output_total',
#                                    'output_total_usd',
#                                    'fee', 'fee_usd', 'fee_per_kb', 'fee_per_kb_usd', 'id'])
#
#         # Close the cursor and connection
#         cursor.close()
#
#         return df
class BlockchainEnv(gym.Env):
    """A Blockchain simulation env for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(BlockchainEnv, self).__init__()

        # set content time 2016:01:01 00:00:00
        self.current_time = 1480982400
        self.starting_time = 1480982400
        self.block_size = random.randint(0, 1000000)

        # action space
        # self.action_space = spaces.Box(low=np.array([0]), high=np.array([1000000]), dtype=np.float32)
        # self.action_space = spaces.Discrete(1000000)
        self.action_space = spaces.Box(low=0.0000001, high=1, shape=(1,), dtype=np.float32)

        # observation space
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)

        # reward
        self.reward = 0

        self.state_data = pd.read_csv("./env/blockchaindata/networkstate/final_state.csv")

    # def filter_data_by_group_in_dataframe(self, start_timestamp, end_timestamp):
    #     #     extract only date from timestamp
    #
    #     cc1 = datetime.fromtimestamp(int(start_timestamp)).date()
    #     cc2 = datetime.fromtimestamp(int(end_timestamp)).date()
    #
    #     start_date = str(cc1.year)+"-"+str(cc1.month)+"-"+str(cc1.day)
    #     end_date = str(cc2.year)+"-"+str(cc2.month)+"-"+str(cc2.day)
    #     df1 = self.transaction_dump.get_group(start_date)
    #     df2 = self.transaction_dump.get_group(end_date)
    #     df = pd.concat([df1, df2], axis=0)
    #     return df

    def search_state_data_by_timestamp(self, start_timestamp):
        start_date = datetime.fromtimestamp(int(start_timestamp)).strftime('%Y-%m-%d')

        df = self.state_data[self.state_data['Datetime'] == start_date]

        return df

        # print(start_date)

    def step(self, action):
        # sum fees of last 10 min
        print("action========================", action[0])
        actual_action = math.floor(action[0] * 10000000)
        print("actual_action", actual_action)
        total_fee_of_included_transactions, uncounted_transactions = sum_fees(read_transactions_new(
            self.current_time - DURATION, self.current_time,
            "./env/blockchaindata/dump/transaction_dump_parquet"
        ), actual_action)

        # print("total_fee_of_included_transactions", total_fee_of_included_transactions)
        # print("uncounted_transactions", uncounted_transactions)

        reward = total_fee_of_included_transactions - (1 / actual_action) * uncounted_transactions

        # print("reward", reward)
        # add 10 min to current time
        self.current_time += DURATION

        # generate state data
        obs = self._next_observation()

        episode_end = int(self.starting_time) + int(864000)

        # done if current time is 1 hour after start time
        done = self.current_time >= episode_end

        if done:
            print("=====================  EPISIDE STATUS =====================", done)
        return obs, reward, done, {}

    def render(self, mode="human"):
        pass

    def _next_observation(self):
        # print("self.current_time", self.current_time)
        # main_value = \
        #     get_transaction_per_second("./env/blockchaindata/state/transactions-per-second_*.pkl", self.current_time,
        #                                self.current_time, 'x')['y'].values[0]
        # print("main_value", main_value)
        # difficulty = \
        # search_by_timestamp("./env/blockchaindata/networkstate/difficulty.csv", self.current_time)['y'].values[0]
        # mempool_growth = \
        # search_by_timestamp("./env/blockchaindata/networkstate/mempool_growth.csv", self.current_time)['y'].values[0]
        # n_transactions = \
        # search_by_timestamp("./env/blockchaindata/networkstate/n-transactions.csv", self.current_time)['y'].values[0]
        # output_volume = search_by_timestamp("./env/blockchaindata/networkstate/output-volume.csv", self.current_time)['y'].values[0]
        # utxo_count = search_by_timestamp_by_x("./env/blockchaindata/networkstate/utxo-count.csv", self.current_time)['y'].values[0]
        # print("utxo_count",utxo_count)

        searched_data = self.search_state_data_by_timestamp(self.current_time)

        # print(searched_data.values[0])

        frame = np.array([
            searched_data.values[0][2],
            searched_data.values[0][3],
            searched_data.values[0][4],
            searched_data.values[0][5],
        ])

        print(frame)

        # print(frame)

        # normalize array
        # normalizedData = frame / np.linalg.norm(frame)

        # print("normalizedData", normalizedData)

        return frame
        # pass

    def reset(self):
        # print("reset called")

        # set current_time to a random time between 1480982400 and 2020:01:01 01:00:00
        generated_timestamp = random.randint(1480982400, 1577836800)

        self.current_time = generated_timestamp
        self.starting_time = generated_timestamp

        self.block_size = random.randint(0, 1000000)
        return self._next_observation()
