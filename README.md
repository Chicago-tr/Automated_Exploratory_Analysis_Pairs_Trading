# Cointegrated-Series-Tester
A script to automate testing all combinations of a list of equities for cointegration using the CADF test. Statistically significant results/pairs are saved to dictionaries and printed.


### Motivation
More often than not assets, particularly equities, behave like a geometric Brownian motion which makes them unsuitable for a stand-alone mean-reverting strategy. However, sometimes linear combinations of time series (equity prices in our case) can be found that are stationary. This means, among other things, that the combination's time series has a constant mean and variance over time. Series for which such a linear combination exists are said to be cointegrated. The CADF test allows one to check if such a combination exists between two time series. 

This script provides an easy way to run the CADF test against all combinations of a list of different price time series with only statistically significant results being saved.


### How it works

Given a path to data files and a list of the file names (without file extension), a nested loop is utilized to iterate over all possible pairs of the time series contained in the list.

```python
if __name__ == '__main__':

    csv_path = 'PATH TO DATA FILES'
    symbols = ['LIST OF FILE NAMES']

    cadf_results = cadf_analysis(csv_path, symbols)
```
```python
def cadf_analysis(path, symbols):
    """
    Parameters
    ----------
    path (str) : path to location of data files
    symbols (list) : list of ticker symbols to be analyzed, name of symbols
    should be without file extension. ex: 'APPL'

    Returns
    -------
    Three dictionaries with tuples of symbols as keys and cadf test results
    as values.
    """

    symbol_list = [x + '.csv' for x in symbols]
    usuable_pairs_1 = {}
    usuable_pairs_5 = {}
    usuable_pairs_10 = {}

    for i in range(len(symbol_list)):

        symbol = symbol_list[i]

        for k in range(len(symbol_list)):
            symbol2 = symbol_list[k]
            if symbol == symbol2:
                pass
```
For each pair a pandas DataFrame is created and an Ordinary Least Squares regression is run with model residuals added as a column to the DataFrame. Using these residuals the CADF test is then run.

```python
            else:

                csv_tup = (symbol, symbol2)

                price_df = create_df(path, csv_tup)

                residuals = run_ols(price_df, symbol, symbol2)

                cadf = create_cadf(residuals)
```

The results are then checked for statistical significance. First the p-value is checked against the .05 threshold. Then whether the calculated test statistic is more negative than either the 1%, 5%, or 10% critical value. If one of these tests is passed the pair will be saved as a key in a dictionary with the CADF test results as the value. There exists a separate dictionary for each level that pairs can pass at and a pair will only be added to the level of highest confidence.

```python

                if cadf[1] < .05:                       

                    if cadf[4]['1%'] > cadf[0]:
                        usuable_pairs_1[csv_tup] = cadf

                    elif cadf[4]['5%'] > cadf[0]:
                        usuable_pairs_5[csv_tup] = cadf

                    elif cadf[4]['10%'] > cadf[0]:
                        usuable_pairs_10[csv_tup] = cadf
```


Pairs that displayed a cointegrated relationship are then printed and the dictionaries are returned for potential further analysis.

```python

    print('\nAT 1% LEVEL:', usuable_pairs_1.keys())

    print('\nAT 5% LEVEL:', usuable_pairs_5.keys())

    print('\nAT 10% LEVEL:', usuable_pairs_10.keys())

    return (usuable_pairs_1, usuable_pairs_5, usuable_pairs_10)
```

