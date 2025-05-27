import pandas as pd
import numpy as np

def process_stock_data(dataframe):
    """
    Processes stock data to calculate returns, moving averages, volatility,
    and signals based on moving average crossovers.

    Parameters:
        dataframe (pd.DataFrame): A DataFrame containing 'date' and 'close' columns.

    Returns:
        pd.DataFrame: The processed DataFrame with additional columns for daily return, 
        cumulative return, moving averages, volatility, and signals.
    
    Raises:
        ValueError: If the required columns are not present in the DataFrame.
    """
    # Check for necessary columns
    required_columns = ['date', 'close']
    if not all(col in dataframe.columns for col in required_columns):
        raise ValueError("DataFrame must contain 'date' and 'close' columns.")
    
    try:
        # Convert 'date' column to datetime and sort DataFrame
        dataframe['date'] = pd.to_datetime(dataframe['date'])
        dataframe = dataframe.sort_values('date').reset_index(drop=True)

        # Calculate daily and cumulative returns
        dataframe['daily_return'] = dataframe['close'].pct_change()
        dataframe['cumulative_return'] = (1 + dataframe['daily_return']).cumprod() - 1

        # Calculate moving averages
        dataframe['ma_20'] = dataframe['close'].rolling(window=20).mean()
        dataframe['ma_50'] = dataframe['close'].rolling(window=50).mean()

        # Calculate volatility
        dataframe['volatility_20'] = dataframe['daily_return'].rolling(window=20).std()

        # Identify bullish/bearish signals based on moving averages
        dataframe['ma_signal'] = np.where(dataframe['ma_20'] > dataframe['ma_50'], 'bullish', 'bearish')

        # Detect moving average crossovers
        dataframe['ma_crossover'] = dataframe['ma_20'] > dataframe['ma_50']
        dataframe['ma_crossover_signal'] = dataframe['ma_crossover'].astype(int).diff()

        # Define trend signals based on crossovers
        dataframe['trend'] = np.select(
            [dataframe['ma_crossover_signal'] == 1, dataframe['ma_crossover_signal'] == -1],
            ['golden_cross', 'death_cross'],
            default='no_signal'
        )

        # Drop rows with NaNs and reset index
        dataframe = dataframe.dropna().reset_index(drop=True)

        return dataframe

    except Exception as e:
        raise RuntimeError(f"An error occurred while processing the data: {e}")

# Basic unit tests
if __name__ == "__main__":
    import unittest

    class TestProcessStockData(unittest.TestCase):
        def setUp(self):
            # Sample data for testing
            data = {
                'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05'],
                'close': [100, 102, 101, 103, 105]
            }
            self.df = pd.DataFrame(data)

        def test_process_stock_data(self):
            result = process_stock_data(self.df)
            self.assertIn('daily_return', result.columns)
            self.assertIn('cumulative_return', result.columns)
            self.assertIn('ma_20', result.columns)
            self.assertIn('ma_50', result.columns)
            self.assertIn('volatility_20', result.columns)
            self.assertIn('ma_signal', result.columns)
            self.assertIn('trend', result.columns)

        def test_missing_columns(self):
            df_invalid = pd.DataFrame({'date': ['2021-01-01'], 'open': [100]})
            with self.assertRaises(ValueError):
                process_stock_data(df_invalid)

if __name__ == "__main__":
    unittest.main()