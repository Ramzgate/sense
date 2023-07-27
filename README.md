# The Principal Path Method

The landscape of digital assets and blockchain technology has rapidly evolved, introducing concepts such as smart contracts, stablecoins, tokens, non-fungible tokens (NFTs), and other web3 technologies. These advancements have expanded the definition of assets, markets, and economies. Digital assets are no longer limited to payment tokens or stores of value; they now encompass works of art, virtual real estate, and entertainment assets.

These new assets pose challenges for financial reporting, both conceptual and methodological. One such challenge is _fair value_ pricing, the standard required by US and inrenational accounting standards (US GAAP and IFRS) for reporting value in financial reports.

Fair value pricing is a crucial aspect of the mark-to-market accounting method, which mandates that asset values should accurately reflect their current market prices, with regular adjustments made to account for prevailing market conditions. Under this accounting standard, the value of an asset is determined by its price on a specified **_principal market_**, which is typically the exchange where the asset is officially listed and traded (e.g., NYSE, Nasdaq, CBOT). The markets are local to some geographic regeon and are active a limited number of houers a day.  

In all markets, there  is a limited 

assets are exchanged against a sovereign fiat currency, and apart from potential currency conversions, fair value is derived from the price of the most recent transactions on the designated principal market. This ensures that assets are reported at their current market values, providing transparency and accuracy in financial reporting.

In the universe of digital assets, trading is global and happens across many different venues without a specific venue dominating any of the others. Moreover, most transactions are swaps of digital assets against other digital assets, this is true even if one of these assets is a stablecoin. Even for assets that trade against fiat currencies it is often the case that a small fraction of the volume is converted to fiat (on/off ramping) while the real drivers are digital to digital swaps. With such fragmented markets, it clearly becomes impossible to apply existing standards to reflect market realities.

The __Principal Path Method__ is to dynamically identify a principal market and once that market is obtained, source all price information from that market. The identification is a continuous process driven by volumes, market dynamics and freshness of data.

## The Principal Path Library
This
