import pandas as pd
import numpy as np

def process_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert 'date' column to datetime format, sort by date in ascending order.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with sorted 'date' column.
    """
    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by 'date' column in ascending order
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily returns, cumulative returns, and moving averages.

    Args:
        df (pd.DataFrame): Input DataFrame with 'close' column.

    Returns:
        pd.DataFrame: DataFrame with additional columns.
    """
    # Calculate daily returns
    df['daily_return'] = df['close'].pct_change()
    
    # Calculate cumulative returns
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    
    # Calculate moving averages (MA) of 20 and 50 days
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    
    return df

def calculate_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate volatility of daily returns for moving averages (MA) of 20 and 50 days.

    Args:
        df (pd.DataFrame): Input DataFrame with 'daily_return' column.

    Returns:
        pd.DataFrame: DataFrame with additional columns.
    """
    # Calculate volatility of daily returns
    df['volatility_20'] = df['daily_return'].rolling(window=20).std()
    
    return df

def generate_signal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate buy/sell signals based on moving averages (MA).

    Args:
        df (pd.DataFrame): Input DataFrame with 'ma_20' and 'ma_50' columns.

    Returns:
        pd.DataFrame: DataFrame with 'ma_signal' column.
    """
    # Generate buy/sell signals
    df['ma_signal'] = np.where(df['ma_20'] > df['ma_50'], 'bullish', 'bearish')
    
    return df

def generate_trend_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trend signals based on moving averages (MA) crossover.

    Args:
        df (pd.DataFrame): Input DataFrame with 'ma_crossover' column.

    Returns:
        pd.DataFrame: DataFrame with 'trend' column.
    """
    # Generate trend signals
    df['ma_crossover'] = df['ma_20'].rolling(window=1).gt(df['ma_50'].rolling(window=1))
    df['ma_crossover_signal'] = df['ma_crossover'].astype(int).diff()
    
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
    
    return df

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with missing values and reset index.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    # Remove rows with missing values
    df = df.dropna()
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process date column, calculate returns, volatility, and generate signals.

    Args:
        df (pd.DataFrame): Input DataFrame with 'close' column.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    # Process date column
    df = process_date_column(df)
    
    # Calculate returns
    df = calculate_returns(df)
    
    # Calculate volatility
    df = calculate_volatility(df)
    
    # Generate signals
    df = generate_signal(df)
    df = generate_trend_signals(df)
    
    # Clean DataFrame
    df = clean_dataframe(df)
    
    return df

# Example usage:
df = pd.DataFrame({
    'close': [100, 110, 120, 130, 140],
    'date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05']
})

df = process_data(df)

print(df)