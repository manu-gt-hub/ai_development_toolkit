import pandas as pd
import numpy as np

def preprocess_data(dataframe):
    """
    Preprocess the stock data by converting dates, sorting, and calculating various returns and moving averages.

    Parameters:
    dataframe (pd.DataFrame): DataFrame containing stock data with 'date' and 'close' columns.

    Returns:
    pd.DataFrame: Processed DataFrame with additional columns for daily returns, cumulative returns,
                  moving averages, volatility, and trend signals.
    """
    try:
        # Convert 'date' column to datetime
        dataframe['date'] = pd.to_datetime(dataframe['date'])
        
        # Sort values by date and reset index
        dataframe = dataframe.sort_values('date').reset_index(drop=True)

        # Calculate daily return
        dataframe['daily_return'] = dataframe['close'].pct_change()

        # Calculate cumulative return
        dataframe['cumulative_return'] = (1 + dataframe['daily_return']).cumprod() - 1

        # Calculate moving averages
        dataframe['ma_20'] = dataframe['close'].rolling(window=20).mean()
        dataframe['ma_50'] = dataframe['close'].rolling(window=50).mean()

        # Calculate volatility
        dataframe['volatility_20'] = dataframe['daily_return'].rolling(window=20).std()

        # Determine moving average signals
        dataframe['ma_signal'] = np.where(dataframe['ma_20'] > dataframe['ma_50'], 'bullish', 'bearish')

        # Identify crossover and generate crossover signals
        dataframe['ma_crossover'] = dataframe['ma_20'] > dataframe['ma_50']
        dataframe['ma_crossover_signal'] = dataframe['ma_crossover'].astype(int).diff()

        # Determine trend based on crossover signals
        dataframe['trend'] = np.select(
            [dataframe['ma_crossover_signal'] == 1, dataframe['ma_crossover_signal'] == -1],
            ['golden_cross', 'death_cross'],
            default='no_signal'
        )

        # Drop NaN values and reset index
        dataframe = dataframe.dropna().reset_index(drop=True)

        return dataframe

    except Exception as e:
        print(f"An error occurred while processing data: {e}")
        return None

# Example test cases
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'close': [100, 102, 101]
    })

    # Preprocess the sample data
    processed_data = preprocess_data(sample_data)
    print(processed_data)