## Historical Data File Organization

The `CryptoTick` data should be setup in a subdirctory `_/trades/_` in the structure below.

The entries `binanace_11_22`, `kraken_5-11` corespond to compresed files delivers by _CryptoTick_, where the differnt directories under a exchnage corespnd to seperate installments. 

The subdiretories could overlap, in such cases is verified to be identical

```markdown
----trades/
        |binanace/
            |binance_11_22
            |binance_10_22
            |...
        |coinbase/
            |coinbase1_11_22
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
            |coinbase2_5-12_22
        |...
        |kraken/
            |kraken_5-11_22
```

