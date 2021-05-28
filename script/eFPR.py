import os
import time
import sys

import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from argparse import ArgumentParser
from os.path import isdir

mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = 'DejaVu Sans'
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14


def is_valid_path(parser, p_file):
    p_file = os.path.abspath(p_file)
    if not os.path.exists(p_file):
        parser.error("The path %s does not exist!" % p_file)
    else:
        return p_file


def is_valid_file(parser, p_file):
    p_file = os.path.abspath(p_file)
    if not os.path.exists(p_file):
        parser.error("The file %s does not exist!" % p_file)
    else:
        return p_file


def get_parser():
    parser = ArgumentParser()

    parser.add_argument("-d",
                        dest="INPUT_DIR",
                        help="Shuffle Directory",
                        type=lambda x: is_valid_path(parser, x))
    parser.add_argument("-o",
                        dest="OUTPUT_DIR",
                        help="Path of directory output")
    parser.add_argument("-p",
                        dest="PERCENT",
                        help="Percent of eFPR accepted (default: 0.0001)",
                        type=float,
                        default=0.0001)

    return parser


def main():
    print("\n--------------------------------------------------------------")
    print("eFPR.py: Example of a small script to explore null distribution ")
    print("and return a cutoff. This program was written by Eric Audemard")
    print("For more information, contact: eric.audemard@umontreal.ca")
    print("----------------------------------------------------------------\n")

    global args
    args = get_parser().parse_args()

    df_res = None
    input_dir = args.INPUT_DIR
    for dir_name in os.listdir(input_dir):
        path_dir = os.path.join(input_dir, dir_name)
        if isdir(path_dir):
            file_path = os.path.join(path_dir, 'predictive_capability.xls')
            print("read: " + file_path)
            tmp = pd.read_csv(file_path, sep="\t")
            if df_res is None:
                df_res = tmp
            else:
                df_res = df_res.append(tmp)

    df_res.dropna(inplace=True)
    cutoff = np.quantile(
        df_res["kernel_mcc"].values,
        1 - args.PERCENT
    )
    df_res_not_filtred = df_res[df_res["kernel_mcc"] > cutoff]

    print("# of MCC: " + str(df_res.shape[0]))
    print("cutoff for an eFPR < " + str(args.PERCENT) + ": " + str(round(cutoff, 2)))
    print("# of MCC > cutoff: " + str(df_res_not_filtred.shape[0]))

    title = "threshold = " + str(round(cutoff, 2)) + ", eFPR < " + str(args.PERCENT)
    sns_plot = sns.violinplot(x=df_res["kernel_mcc"]).set_title(title)
    plt.axvline(cutoff, color='r', ls='--')

    fig_dir = os.path.join(args.OUTPUT_DIR)
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)
    fig_file = os.path.join(fig_dir, "null_distribution.pdf")
    sns_plot.figure.savefig(fig_file)
    plt.close('all')


main()
