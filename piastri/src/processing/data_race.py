import pandas as pd

class DataRace:
    def __init__(self):
        self.df_race_raw = None
        self.df_race_processed = None
        self.df_race_final = None

    def __get_df_race_raw(self):
        # Your logic to produce the raw dataframe
        self.df_race_raw = pd.DataFrame()  # Replace with actual logic
        return self.df_race_raw

    def __get_df_race_processed(self, df_race_raw, year, some_int):
        # Your logic to process the raw dataframe using year and some_int
        self.df_race_processed = pd.DataFrame()  # Replace with actual logic
        return self.df_race_processed

    def get_df_race_final(self, year, some_int):
        # Automatically call the intermediate steps
        df_race_raw = self.__get_df_race_raw()
        df_race_processed = self.__get_df_race_processed(df_race_raw, year, some_int)
        # Your logic to produce the final dataframe
        self.df_race_final = pd.DataFrame()  # Replace with actual logic
        return self.df_race_final