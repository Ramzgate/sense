## Data organization

The _CryptoTick_ data should be setup in a subdirctory '_/trades/_' in the structure below. The entries 'binanace_11_22', 'kraken_5-11' corespond to compresed files delivers by _CryptoTick_, where the differnt directories under a exchnage corespnd to seperate installments. The subdiretories could overlap, in such cases is verified to be identical

```markdown
----trades/
        |binanace/
            |binance_11_22
            |binance_10_22
        |
        |coinbase/
            |coinbase1_11_22
            |coinbase2_5-12_22
            |
        |kraken/
            |kraken_5-11_22
```

```bash
...coinbase_11_22____20221101_____COINBASE_SPOT_BTC_USD.csv.gz
                   |_20221102   |_COINBASE_SPOT_AAVE_BTC.csv.gz
                   |_20221103   .
                   |_20221104   .
                   .            . 
                   .            |_COINBASE_SPOT_APE_USDT.csv.gz
                   .
                   |_20221130
```

