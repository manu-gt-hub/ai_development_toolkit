import pandas as pd
import pandas as pd

def functtion(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    df['daily_return'] = df['close'].pct_change()

    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1

    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()

    df['volatility_20'] = df['daily_return'].rolling(window=20).std()

    df['ma_signal'] = np.where(df['ma_20'] > df['ma_50'], 'bullish', 'bearish')

    df['ma_crossover'] = df['ma_20'] > df['ma_50']
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

    df = df.dropna().reset_index(drop=True)

    return df
