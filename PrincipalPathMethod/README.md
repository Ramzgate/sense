### Historical Data File Organization

The _CryptoTick_ data should be setup in a subdirctory `trades/` in the structure below.

Directories `binance/`, `coinbase/`, `kraken/` corespond to exchanges. Subdirectories `binanace_11_22/`, `binance_10_22/`, ...  corespond to installments of compresed file delivers by _CryptoTick. In case of overlap between installments redundant files are ignored.

```markdown
----trades/
        |binanace/
            |binance_11_22/
            |binance_10_22/
            |...
        |coinbase/
            |coinbase1_11_22/
                |20221101/
                    |COINBASE_SPOT_BTC_USD.csv.gz
                    |COINBASE_SPOT_AAVE_BTC.csv.gz
                    |COINBASE_SPOT_APE_USDT.csv.gz
                    |...
                |20221102/
                |20221103/
                |20221104/
                |...
                |20221130/
            |coinbase2_5-12_22/
        |kraken/
            |kraken_5-11_22/
        |...
```

