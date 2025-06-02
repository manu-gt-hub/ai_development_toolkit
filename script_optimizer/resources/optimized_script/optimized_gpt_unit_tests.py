import pandas as pd
import numpy as np
import unittest

def prepare_data(df):
    """
    Convert date column to datetime, and sort the dataframe based on date.
    
    :param df: DataFrame with at least a 'date' and 'close' column
    :return: DataFrame sorted by date
    """
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date').reset_index(drop=True)

def calculate_returns(df):
    """
    Compute daily and cumulative returns.
    
    :param df: DataFrame with 'close' prices
    :return: DataFrame with 'daily_return' and 'cumulative_return' added
    """
    df['daily_return'] = df['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    return df

def moving_averages_and_volatility(df):
    """
    Calculate moving averages and volatility for the 'close' prices.
    
    :param df: DataFrame with 'close' prices that contains 'daily_return'
    :return: DataFrame with moving averages and volatility
    """
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    df['volatility_20'] = df['daily_return'].rolling(window=20).std()
    return df

def generate_signals(df):
    """
    Generate trading signals based on moving average crossovers.
    
    :param df: DataFrame with moving averages 'ma_20' and 'ma_50'
    :return: DataFrame with trading signals
    """
    df['ma_crossover'] = df['ma_20'] > df['ma_50']
    df['ma_crossover_signal'] = df['ma_crossover'].astype(int).diff()
    df['trend'] = np.select(
        [df['ma_crossover_signal'] == 1, df['ma_crossover_signal'] == -1],
        ['golden_cross', 'death_cross'],
        default='no_signal'
    )
    return df

def process_stock_data(df):
    """
    Process the input dataframe through a series of transformations to add 
    financial analytics like returns, moving averages, and trading signals.
    
    :param df: Input DataFrame expected to have columns: 'date', 'close'
    :return: Processed DataFrame
    """
    df = prepare_data(df)
    df = calculate_returns(df)
    df = moving_averages_and_volatility(df)
    df = generate_signals(df)
    return df.dropna().reset_index(drop=True)

class TestFinancialFunctions(unittest.TestCase):
    def test_prepare_data(self):
        df = pd.DataFrame({
            'date': ['2021-01-02', '2021-01-01'],
            'close': [100, 101]
        })
        result = prepare_data(df)
        self.assertTrue(result.iloc[0]['date'] < result.iloc[1]['date'])

    def test_calculate_returns(self):
        df = pd.DataFrame({'close': [100, 102]})
        result = calculate_returns(df)
        self.assertAlmostEqual(result.loc[1, 'daily_return'], 0.02)

    def test_moving_averages_and_volatility(self):
        df = pd.DataFrame({'close': np.random.rand(100)})
        df = calculate_returns(df)
        result = moving_averages_and_volatility(df)
        self.assertIn('ma_20', result)
        self.assertIn('volatility_20', result)

    def test_generate_signals(self):
        df = pd.DataFrame({
            'ma_20': [1, 2],
            'ma_50': [2, 1]
        })
        result = generate_signals(df)
        self.assertEqual(result.loc[1, 'trend'], 'golden_cross')

    def test_process_stock_data(self):
        df = pd.DataFrame({
            'date': ['2021-01-01', '2021-01-02'],
            'close': [100, 105]
        })
        result = process_stock_data(df)
        self.assertIn('cumulative_return', result)
        self.assertIn('trend', result)

if __name__ == "__main__":
    unittest.main()