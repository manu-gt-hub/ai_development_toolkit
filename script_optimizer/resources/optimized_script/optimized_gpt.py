import pandas as pd
import numpy as np

def preprocess_dataframe(df):
    """
    Preprocess the DataFrame by converting date columns, sorting,
    and calculating financial indicators.

    Parameters:
    df (pd.DataFrame): Input DataFrame containing financial data with 'date' and 'close' columns.

    Returns:
    pd.DataFrame: Preprocessed DataFrame with additional columns for daily return, 
                  cumulative return, moving averages, volatility, and signals.
    """
    try:
        # Convert 'date' column to datetime format and sort by date
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # Calculate daily return as percentage change
        df['daily_return'] = df['close'].pct_change()

        # Calculate cumulative return
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1

        # Calculate moving averages
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()

        # Calculate 20-day volatility (standard deviation of daily returns)
        df['volatility_20'] = df['daily_return'].rolling(window=20).std()

        # Determine bullish or bearish market conditions
        df['ma_signal'] = np.where(df['ma_20'] > df['ma_50'], 'bullish', 'bearish')

        # Identify moving average crossover signals
        df['ma_crossover'] = df['ma_20'] > df['ma_50']
        df['ma_crossover_signal'] = df['ma_crossover'].astype(int).diff()

        # Assign trend based on crossover signals
        df['trend'] = np.select(
            [
                df['ma_crossover_signal'] == 1,  # Golden cross
                df['ma_crossover_signal'] == -1  # Death cross
            ],
            [
                'golden_cross',
                'death_cross'
            ],
            default='no_signal'
        )

        # Drop rows with NaN values and reset index
        df = df.dropna().reset_index(drop=True)

        return df

    except Exception as e:
        print(f"An error occurred while processing the DataFrame: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Sample usage:
# df = pd.DataFrame({'date': [...], 'close': [...]})
# processed_df = preprocess_dataframe(df)