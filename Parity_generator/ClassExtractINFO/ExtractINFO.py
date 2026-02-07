import pandas as pd


class ExtractINFO:
    def __init__(self, INFO_path: str, sheet_name=""):
        self.INFO_path = INFO_path
        self.sheet_name = sheet_name

    def _read_info(self):
        info_df = pd.read_excel(self.INFO_path, header=None)
        info_df.dropna(how='all', axis=0, inplace=True)  # Remove empty rows
        # info_df.dropna(how='all', axis=1, inplace=True)  # Remove empty columns - commented out to keep all columns from header

        info_df.columns = info_df.iloc[0]  # Set the first row as header
        info_df.columns = info_df.columns.fillna('')  # Fill NaN in header with empty string
        info_df = info_df[1:]
        info_df = info_df.fillna('')
        info_df = info_df.astype(str)

        info_dict = info_df.to_dict(orient='records')[0]

        return info_dict

    def _read_info_multi(self):
        if self.sheet_name:
            info_df = pd.read_excel(self.INFO_path, sheet_name=self.sheet_name, header=None)
        else:
            info_df = pd.read_excel(self.INFO_path, header=None)
        info_df.dropna(how='all', axis=0, inplace=True)  # Remove empty rows
        # info_df.dropna(how='all', axis=1, inplace=True)  # Remove empty columns - commented out to keep all columns from header

        info_df.columns = info_df.iloc[0]  # Set the first row as header
        info_df.columns = info_df.columns.fillna('')  # Fill NaN in header with empty string
        info_df = info_df[1:]
        info_df = info_df.fillna('')
        info_df = info_df.astype(str)

        info_dict_list = [row.to_dict() for index, row in info_df.iterrows()]
        return info_dict_list

