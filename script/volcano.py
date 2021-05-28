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

    parser.add_argument("-i",
                        dest="INPUT_FILE",
                        help="path to prodective_capability.xls file",
                        type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-o",
                        dest="OUTPUT_DIR",
                        help="Path of directory output")
    parser.add_argument("-t",
                        dest="THRESHOLD",
                        help="To fix a threshold (Default: None)",
                        type=float,
                        default=None)
    parser.add_argument("--anno",
                        dest="ANNO",
                        help="To use gene_name as features ids (Default: None)",
                        type=lambda x: is_valid_file(parser, x),
                        default=None)
    parser.add_argument("--pvalue",
                        dest="PVALUE",
                        help="Display volcano using pvalue (Default: MCC)",
                        action='store_true')

    parser.set_defaults(PVALUE=False)

    return parser


def main():
    print("\n--------------------------------------------------------------")
    print("volcano.py: Example of a small script to display a volcano plot.")
    print("This program was written by Eric Audemard")
    print("For more information, contact: eric.audemard@umontreal.ca")
    print("----------------------------------------------------------------\n")

    global args
    args = get_parser().parse_args()

    df_res = pd.read_csv(args.INPUT_FILE, sep="\t", index_col="id")

    if args.THRESHOLD is not None and args.PVALUE is None:
        args.THRESHOLD = -np.log10(args.THRESHOLD)

    if args.ANNO is not None:
        df_anno = pd.read_csv(args.ANNO, sep="\t", index_col="gene_id")
        df_res = pd.concat([df_res, df_anno], axis=1)
        df_res.set_index('gene_name', inplace=True)

    y_label = "kernel_mcc"
    if args.PVALUE is True:
        y_label = "-log10(pvalue)"
        df_res["t_pv"] = - np.log10(df_res["t_pv"])
        df_res.rename(columns={"t_pv": y_label}, inplace=True)

    df_res.dropna(inplace=True)
    df_res.sort_values(by=[y_label], ascending=False, inplace=True)

    sns_plot = sns.scatterplot(data=df_res, x="l2fc", y=y_label)

    plt.tight_layout()

    if args.THRESHOLD is not None:
        plt.axhline(args.THRESHOLD, ls='--', color='r')

        df_res_pos = df_res[df_res["l2fc"] > 0]
        df_res_pos = df_res_pos[df_res_pos[y_label] >= args.THRESHOLD]

        for line in range(0, min(5, df_res_pos.shape[0])):
            sns_plot.text(
                df_res_pos.l2fc.iloc[line] - 1, df_res_pos.kernel_mcc.iloc[line],
                df_res_pos.index[line], horizontalalignment='left'
            )

        df_res_neg = df_res[df_res["l2fc"] < 0]
        df_res_neg = df_res_neg[df_res_neg[y_label] >= args.THRESHOLD]
        for line in range(0, min(5, df_res_neg.shape[0])):
            sns_plot.text(
                df_res_neg.l2fc.iloc[line]+0.01, df_res_neg.kernel_mcc.iloc[line],
                df_res_neg.index[line], horizontalalignment='left'
            )

    fig_dir = os.path.join(args.OUTPUT_DIR)
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    fig_file = os.path.join(fig_dir, "volcano_mcc.pdf")
    if args.PVALUE is True:
        if args.THRESHOLD is None:
            fig_file = os.path.join(fig_dir, "volcano_pvalue.pdf")
        else:
            fig_file = os.path.join(fig_dir, "volcano_pvalue_threshold.pdf")
    else:
        if args.THRESHOLD is None:
            fig_file = os.path.join(fig_dir, "volcano_mcc.pdf")
        else:
            fig_file = os.path.join(fig_dir, "volcano_mcc_threshold.pdf")

    sns_plot.figure.savefig(fig_file)
    plt.close('all')


main()
