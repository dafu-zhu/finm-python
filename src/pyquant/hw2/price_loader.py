from typing import Optional

import yfinance as yf
import polars as pl
import pandas as pd
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    filename='data_loader.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger('yfinance').setLevel(logging.CRITICAL)


class PriceLoader:
    """
    Load S&P 500 prices from Yahoo Finance
    """
    def __init__(self, tickers: list = None):
        self.tickers = tickers
        self.prices = None

    def get_sp500_tickers(self):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        table = pd.read_html(url, header=0, storage_options=headers)[0]
        tickers = table['Symbol'].str.replace('.', '-')
        self.tickers = tickers.to_list()

        return self.tickers

    def get_prices(self, start_date: str, end_date: str, batch_size: int = 10) -> pl.DataFrame:
        if not self.tickers:
            self.get_sp500_tickers()

        num_batch = len(self.tickers) // 10 + 1
        result = None
        cnt = 0

        # Fetch data in batches
        for i in tqdm(range(num_batch), desc='Fetching', unit='batch'):
            batch = self.tickers[i * batch_size : (i + 1) * batch_size]
            pd_batch = yf.download(
                batch, start=start_date, end=end_date,
                auto_adjust=True, progress=False)['Close']
            pl_df = pl.DataFrame(pd_batch.reset_index())

            # Drop the column with all null values
            pl_prices = pl_df[[s.name for s in pl_df if not (s.null_count() == pl_df.height)]].lazy()

            # Tickers that actually collected
            tickers = pl_prices.collect().select(pl.exclude('Date')).columns
            cnt += len(tickers)

            diff = list(set(batch) - set(tickers))
            if diff:
                logging.error(f"Symbol {diff} failed to load")
            logging.info(f"Batch {i + 1}: Loaded {len(tickers)}/{len(batch)} tickers")

            # Join based on the 'Date' column
            if result is None:
                result = pl_prices
            else:
                result = result.join(pl_prices, on="Date", how="full", coalesce=True)

        logging.info(f"Total {cnt} tickers loaded successfully")
        self.prices = result.collect()

        return self.prices

    def write_parquet(self, path: Path):
        self.prices.write_parquet(path)

    def load_parquet(self, path: Path):
        self.prices = pl.read_parquet(path)
        return self.prices
    


if __name__ == "__main__":
    loader = PriceLoader()
    prices = loader.get_prices('2005-01-01', '2025-01-01')
    parquet_path = Path('../../..') / 'data' / 'raw' / 'sp500.parquet'
    loader.write_parquet(parquet_path)