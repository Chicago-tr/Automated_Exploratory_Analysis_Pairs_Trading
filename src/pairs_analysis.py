#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import cadf_tester as ct
import pandas as pd
import numpy as np
import os


def create_df(path, symbol):
    """
    Parameters
    ----------
    path : string, path to location of data files
    symbol : the name of the csv data file

    Returns
    -------
    df : The time series as a DataFrame ordered chronologically
    """

    df = pd.read_csv(os.path.join(path, symbol),index_col=0,parse_dates=True)
    df = df.replace({'\$':''}, regex = True)
    df = df.sort_values(by='timestamp')

    return df


def calc_spread(series_one, series_two, hedge_ratio):
    """
    Parameters
    ----------
    series_one : A Pandas DF column or series of values
    series_two : A Pandas DF column or series of values
    hedge_ratio : Float, The hedge ratio given by running the OLS when finding pairs

    Returns
    -------
    spread : Pandas Series of the spread

    """
    spread = series_two - series_one * hedge_ratio

    return spread


def create_zscore(spread):
    """
    Parameters
    ----------
    spread : A Pandas Series of the spread between two securities

    Returns
    -------
    Pandas Series of Z-score values
    """

    return (spread - spread.mean())/ np.std(spread)



if __name__ == '__main__':

    csv_path = 'PATH HERE'
    symbols = ['DVN_daily','VLO_daily','HES_daily',
                'ENB_daily','SHEL_daily','BP_daily','TTE_daily',
                'OXY_daily','EOG_daily','COP_daily','CVX_daily','XOM_daily']


    cadf_results = ct.cadf_analysis(csv_path, symbols)

    one_percent_results = cadf_results[0]

    #We'll take just the pairs and their hedge ratios
    pairs = list(one_percent_results.keys())

    pairs_copy = pairs[:]
    plots = []

    for i in range(len(pairs)):


        hes_df = create_df(csv_path, pairs[i][0])
        vlo_df = create_df(csv_path, pairs[i][1])


        spread = calc_spread(hes_df['close'], vlo_df['close'], pairs[i][2])
        zscore = create_zscore(spread)


        plt.plot(zscore)
        plt.axhline(zscore.mean(), color='black')
        plt.axhline(1.0, color='green')
        plt.axhline(-1.0, color='red')
        plt.title(f"{pairs[i][0]} x {pairs[i][1]}")
        plt.legend(['Z-score', 'Mean', '+1', '-1'])

        plots.append(plt.gcf())
        plt.show()

    with PdfPages('Pairs_Analysis_Results.pdf') as pdf:
        for plot in plots:
            pdf.savefig(plot, bbox_inches='tight')
