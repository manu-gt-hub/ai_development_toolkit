import pandas as pd
import numpy as np

def preprocess_dataframe(df):
    """
    Converts the 'date' column to datetime, sorts by date, and resets the index.

    :param df: Pandas DataFrame containing at least a 'date' column.
    :return: Pandas DataFrame with the 'date' column converted and sorted.
    """
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date').reset_index(drop=True)

def calculate_financial_indicators(df):
    """
    Calculates various financial indicators on the DataFrame.

    :param df: Pandas DataFrame that must contain the 'close' column.
    :return: Modified DataFrame with new financial indicators added.
    """
    df['daily_return'] = df['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    return df

def calculate_moving_averages(df):
    """
    Calculates moving averages and their derived signals.

    :param df: Pandas DataFrame that must contain the 'close column.
    :return: DataFrame with moving averages and moving average signals added.
    """
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['volatility_20'] = df['daily_return'].rolling(window=20).std()
    df['ma_crossover'] = df['ma_20'] > df['ma_50']
    df['ma_crossover_signal'] = df['ma_crossover'].astype(int).diff()
    return df

def determine_market_trend(df):
    """
    Determines market trend based on moving average crossovers.

    :param df: Pandas DataFrame with 'ma_crossover_signal' column.
    :return: DataFrame with trend signal added.
    """
    df['trend'] = np.select(
        [df['ma_crossover_signal'] == 1, df['ma_crossover_signal'] == -1],
        ['golden_cross', 'death_cross'],
        default='no_signal'
    )
    return df

def process_stock_data(df):
    """
    Process stock data by performing preprocessing, financial calculation, and trend determination.

    :param df: DataFrame with stock data, expects 'date' and 'close' columns.
    :return: Processed DataFrame.
    """
    try:
        df = preprocess_dataframe(df)
        df = calculate_financial_indicators(df)
        df = calculate_moving_averages(df)
        df = determine_market_trend(df)
        return df.dropna().reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"Error processing stock data: {e}")

def example_usage():
    """
    Example usage of the process_stock_data function with sample data.
    """
    data = {
        'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04'],
        'close': [100, 101, 102, 103],
    }
    df = pd.DataFrame(data)
    processed_df = process_stock_data(df)
    print(processed_df)

if __name__ == "__main__":
    example_usage()