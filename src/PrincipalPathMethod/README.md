### Historical Data File Organization

The historical data should be setup in a subdirctory `trades/` in the structure below.
- Within `trades/` there are seperate subdirectories for each exchange `binance/`, `coinbase/`,`kraken/`, etc.
- Each exchange directory will contain further subdirectories by installments of compressed file deliveries from the provider, `binance_11_22/`, `binance_10_22/`, etc.
- It is important to note that if there is overlap between installments, redundant files will be ignored.

With this structure historical data will be read to memory for further processing. 
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

