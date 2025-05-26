#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import pandas as pd
import os


def create_df(path, symbols):
    """
    Parameters
    ----------
    path : string, path to location of data files
    symbols : tuple, containing the name of two csv data files

    Returns
    -------
    close_df : DataFrame of the price data for 2 securities
    """

    first_df = pd.read_csv(os.path.join(path, symbols[0]),index_col=0,parse_dates=True)
    first_df = first_df.replace({'\$':''}, regex = True)


    second_df = pd.read_csv(os.path.join(path, symbols[1]),index_col=0,parse_dates=True)
    second_df = second_df.replace({'\$':''}, regex = True)


    close_data = [first_df['Close/Last'].astype(float), second_df['Close/Last'].astype(float)]



    titles = [symbols[0], symbols[1]]
    close_df = pd.concat(close_data, axis=1, keys= titles)

    close_df = close_df.ffill()

    return close_df



def run_ols(close_df, symbol, symbol2):
    """
    Parameters
    ----------
    close_df : DataFrame of close prices for symbol and symbol2
    symbol : string, first symbol
    symbol2 : string, second symbol

    Returns
    -------
    close_df : the close_df DataFrame with an added column for the model
    Residuals
    """

    Y = close_df[symbol]
    x = close_df[symbol2]
    x = sm.add_constant(x)

    try:
        model = sm.OLS(Y, x)
    except:
       raise Exception('\nMissingDataError, Datasets are probably different lengths')

    results = model.fit()


    coef = results.params.iloc[1]
    # print('Hedge Ratio: %s' % coef)


    close_df['Residuals'] = results.resid
    return close_df, coef


def create_cadf(close_df):
    """
    Parameters
    ----------
    close_df : DataFrame containing Residuals from OLS model

    Returns
    -------
    cadf : Tuple containing results of the cadf test
    """

    cadf = ts.adfuller(close_df['Residuals'],1)
    return cadf


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
            else:

                csv_tup = (symbol, symbol2)

                price_df = create_df(path, csv_tup)

                residuals, coef = run_ols(price_df, symbol, symbol2)

                csv_tup = (symbol, symbol2, coef)       #Add the hedge ratio

                cadf = create_cadf(residuals)

                if cadf[1] < .05:                       #testing the p-value

                    if cadf[4]['1%'] > cadf[0]:
                        usuable_pairs_1[csv_tup] = cadf

                    elif cadf[4]['5%'] > cadf[0]:
                        usuable_pairs_5[csv_tup] = cadf

                    elif cadf[4]['10%'] > cadf[0]:
                        usuable_pairs_10[csv_tup] = cadf

    print('\nAT 1% LEVEL:', usuable_pairs_1.keys())

    print('\nAT 5% LEVEL:', usuable_pairs_5.keys())

    print('\nAT 10% LEVEL:', usuable_pairs_10.keys())

    return (usuable_pairs_1, usuable_pairs_5, usuable_pairs_10)








if __name__ == '__main__':

    csv_path = 'PATH TO DATA FILES'
    symbols = ['LIST OF FILE NAMES']

    cadf_results = cadf_analysis(csv_path, symbols)
