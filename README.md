# theBigBangTheory
DSCI510_project
Package used:
BeautifulSoup from bs4, requests, json, pandas, sys, csv, os , seaborn, and statsmodels.api. All imported before running the code. Most of them are normal packages for cs510 class, but the way to install statsmodels.api is to use pip to install it:

	pip install statsmodels

If you have not installed pip, please follow this instruction:
https://pip.pypa.io/en/stable/installation/ 
--------------------------------------------------------------------
How to run the program:
 1. bbt.py
    It calls the default_function(). This function needs no parameter. It will recollect all the data again and update the data.csv file. It takes about 10 - 15 minutes to run and would print the first 10 rows of the data frame containing all the 17 features.
  2. bbt.py --lineplot
    Each time you run it, it calls the lineplot() function and prints the graph of the one selected feature vs. time.
  3.bbt.py – describe
    It calls the describe() to give detailed description of every feature : count, mean, standard deviation, minimum, 25 percentile, 50 percentile (median), 75 percentile, and maximum. 
  4.bbt.py – regression
    It calls the regression() function to give a linear regression report over all features. In the report, it is worth to note that those with p values < 0.05 are significant features, which has a larger possibility to be a factor for the final IMDb rating of the Big Bang Theory.
  5.bbt.py --statics
    It calls the static_function() and prints the first 10 rows of the data in the static file.

