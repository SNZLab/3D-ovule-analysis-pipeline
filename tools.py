import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from scipy import stats as st
from configparser import ConfigParser
import statsmodels.stats.multicomp as mc

# Classes and functions

# Read file, e.g., database.ini, containing all credentials required for connecting to the database
def config(filename='db.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


# Connect to the database
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return cur


def group(df, gr):
    new_df = df.groupby(gr)
    return new_df


def sum_by_var(df, var, name='n'):
    new_df = df[var].sum().reset_index(name=name)
    return new_df


def count_unique(df, var, name='n'):
    new_df = df[var].value_counts().sort_index(ascending=True).reset_index(name=name)
    return new_df


class StatsForGraphs():
    def __init__(self, df, var, value):
        self.df = df
        self.var = var
        self.value = value

    def compute_stats(self):
        mean = np.empty((0,1))
        std = np.empty((0,1))

        for item in self.df[self.var].unique():
            mean = np.append(mean, self.df[self.df[self.var] == item][self.value].mean())
            std = np.append(std, self.df[self.df[self.var] == item][self.value].std())
        return mean, std


class Unpaired_ttest():
    def __init__(self, df, var, categories, value):
        self.df = df
        self.var = var
        self.categories = categories
        self.value = value
    
    def perform_ttest(self):
        a = self.df.loc[self.df[self.var] == self.categories[0], self.value].to_numpy()
        b = self.df.loc[self.df[self.var] == self.categories[1], self.value].to_numpy()
        ttest = st.ttest_ind(a=a, b=b, equal_var=True)

        if ttest.pvalue >= 0.05:
            asterisk = 'ns'
        elif ttest.pvalue < 0.05 and ttest.pvalue >= 0.01:
            asterisk = '*'
        elif ttest.pvalue < 0.01 and ttest.pvalue >= 0.001:
            asterisk = '**'
        elif ttest.pvalue < 0.001 and ttest.pvalue >= 0.0001:
            asterisk = '***'
        else:
            asterisk = '****'
        return asterisk
    
    def graph_annotate(self, asterisk, col, h):
        categories = self.df[self.var].unique()
        idx1, idx2 = np.where(categories == self.categories[0])[0][0], np.where(categories == self.categories[1])[0][0]
        y1 = self.df[self.df[self.var] == self.categories[0]][self.value].max() + h
        y2 = self.df[self.df[self.var] == self.categories[1]][self.value].max() + h
        plt.plot([idx1, idx1, idx2, idx2], [y1, y1+(y2-y1)+h, y2+h, y2], lw=1.5, color=col)
        plt.text((idx1+idx2)*.5, np.max([y1,y2])+h, asterisk, ha='center', va='bottom', color=col)


class MultipleComparison_ttest():
    def __init__(self, df, var, value, method):
        self.df = df
        self.var = var
        self.value = value
        self.method = method

    def perform_ttest(self):
        comp1 = mc.MultiComparison(self.df[self.value], self.df[self.var])
        _, _, a2 = comp1.allpairtest(st.ttest_ind, alpha=0.05, method=self.method)
        pairs = a2[a2['pval_corr'] >= 0.0001][['group1','group2']]
        pvalues = a2[a2['pval_corr'] >= 0.0001]['pval_corr']

        asterisk = []
        for p in pvalues:
            if p >= 0.05:
                asterisk.append('ns')
            elif p < 0.05 and p >= 0.01:
                asterisk.append('*')
            elif p < 0.01 and p >= 0.001:
                asterisk.append('**')
            elif p < 0.001 and p >= 0.0001:
                asterisk.append('***')
            else:
                asterisk.append('****')
        return pairs, pvalues, asterisk
    
    def graph_annotate(self, pairs, asterisk, col, h):
        max = self.df.groupby(self.var).max()[self.value].reset_index(name='max')
        for idx, pair in enumerate(pairs):
            categories = self.df[self.var].unique()
            idx1, idx2 = np.where(categories == pair[0])[0][0], np.where(categories == pair[1])[0][0]
            y1 = max.loc[max[self.var]==pair[0], 'max'] + h
            y2 = max.loc[max[self.var]==pair[1], 'max'] + h
            max.loc[max[self.var]==pair[0], 'max'] = np.max([y1,y2]) + h
            max.loc[max[self.var]==pair[1], 'max'] = np.max([y1,y2]) + h
            plt.plot([idx1, idx1, idx2, idx2], [np.max([y1,y2]), np.max([y1,y2])+0.5*h, np.max([y1,y2])+0.5*h, np.max([y1,y2])], lw=1.5, color=col)
            plt.text((idx1+idx2)*.5, np.max([y1,y2])+0.5*h, asterisk[idx], ha='center', va='bottom', color=col)


class Multiple_ttest():
    def __init__(self, df, var, value, pairs):
        self.df = df
        self.var = var
        self.value = value
        self.pairs = pairs
    
    def perform_ttest(self):
        asterisk = []
        for pair in self.pairs:
            a = self.df.loc[self.df[self.var] == pair[0], self.value].to_numpy()
            b = self.df.loc[self.df[self.var] == pair[1], self.value].to_numpy()
            ttest = st.ttest_ind(a=a, b=b, equal_var=True)

            if ttest.pvalue >= 0.05:
                asterisk.append('ns')
            elif ttest.pvalue < 0.05 and ttest.pvalue >= 0.01:
                asterisk.append('*')
            elif ttest.pvalue < 0.01 and ttest.pvalue >= 0.001:
                asterisk.append('**')
            elif ttest.pvalue < 0.001 and ttest.pvalue >= 0.0001:
                asterisk.append('***')
            else:
                asterisk.append('****')
        return asterisk
    
    def graph_annotate(self, asterisk, col, h):
        max = self.df.groupby(self.var).max()[self.value].reset_index(name='max')
        for idx, pair in enumerate(self.pairs):
            categories = self.df[self.var].unique()
            idx1, idx2 = np.where(categories == pair[0])[0][0], np.where(categories == pair[1])[0][0]
            y1 = max.loc[max[self.var]==pair[0], 'max'] + h
            y2 = max.loc[max[self.var]==pair[1], 'max'] + h
            max.loc[max[self.var]==pair[0], 'max'] = np.max([y1,y2]) + h
            max.loc[max[self.var]==pair[1], 'max'] = np.max([y1,y2]) + h
            plt.plot([idx1, idx1, idx2, idx2], [np.max([y1,y2]), np.max([y1,y2])+0.5*h, np.max([y1,y2])+0.5*h, np.max([y1,y2])], lw=1.5, color=col)
            plt.text((idx1+idx2)*.5, np.max([y1,y2])+0.5*h, asterisk[idx], ha='center', va='bottom', color=col)


class OneWayAnova():
    def __init__(self, df, var, value, category):
        self.df = df
        self.var = var
        self.value = value
        self.categories = category
    
    def perform_anova(self):
        input = []
        for category in self.categories:
            input.append(self.df.loc[self.df[self.var] == category, self.value].to_numpy())
        
        anova = st.f_oneway(*input)
        return anova.statistic, anova.pvalue
    

class MathTextSciFormatter(ticker.Formatter):
    def __init__(self, fmt="%1.2e"):
        self.fmt = fmt
    def __call__(self, x, pos=None):
        s = self.fmt % x
        decimal_point = '.'
        positive_sign = '+'
        tup = s.split('e')
        significand = tup[0].rstrip(decimal_point)
        sign = tup[1][0].replace(positive_sign, '')
        exponent = tup[1][1:].lstrip('0')
        if exponent:
            exponent = '10^{%s%s}' % (sign, exponent)
        if significand and exponent:
            s =  r'%s{\times}%s' % (significand, exponent)
        else:
            s =  r'%s%s' % (significand, exponent)
        return "${}$".format(s)
