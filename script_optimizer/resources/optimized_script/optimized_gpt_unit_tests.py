import pandas as pd
import numpy as np

def preprocess_financial_data(df):
    """
    Preprocesses a DataFrame containing financial data, including calculating returns,
    moving averages, volatility, and trading signals.

    Parameters:
        df (pd.DataFrame): DataFrame containing financial data with at least 'date' and 'close' columns.

    Returns:
        pd.DataFrame: A DataFrame with computed fields such as daily return, cumulative return,
                      moving averages, volatility, and trading signals.
    """
    try:
        # Convert 'date' column to datetime format and sort DataFrame by date
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # Calculate daily returns and cumulative returns
        df['daily_return'] = df['close'].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1

        # Calculate moving averages and volatility
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()
        df['volatility_20'] = df['daily_return'].rolling(window=20).std()

        # Generate trading signals based on moving average crossovers
        df['ma_signal'] = np.where(df['ma_20'] > df['ma_50'], 'bullish', 'bearish')
        df['ma_crossover'] = df['ma_20'] > df['ma_50']
        df['ma_crossover_signal'] = df['ma_crossover'].astype(int).diff()

        # Identify trends based on crossover signals
        df['trend'] = np.select(
            [
                df['ma_crossover_signal'] == 1,
                df['ma_crossover_signal'] == -1
            ],
            [
                'golden_cross',
                'death_cross'
            ],
            default='no_signal'
        )

        # Drop rows with NaN values and reset index
        df = df.dropna().reset_index(drop=True)

    except Exception as e:
        print(f"Error processing the DataFrame: {e}")
    
    return df


# Unit Tests
def test_preprocess_financial_data():
    """Unit test for preprocess_financial_data function."""
    # Test with a sample DataFrame
    sample_data = {
        'date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05'],
        'close': [100, 102, 101, 103, 105]
    }
    df = pd.DataFrame(sample_data)
    result = preprocess_financial_data(df)

    # Assert the output contains expected columns
    expected_columns = {'date', 'close', 'daily_return', 'cumulative_return', 'ma_20', 'ma_50', 
                        'volatility_20', 'ma_signal', 'ma_crossover', 'ma_crossover_signal', 'trend'}
    assert expected_columns.issubset(result.columns), "Missing expected columns in the result DataFrame."
    
    # Assert no NaN values are present in the resulting DataFrame
    assert result.isna().sum().sum() == 0, "Resulting DataFrame should contain no NaN values."

# If needed, can run the test by uncommenting the next line
# test_preprocess_financial_data()