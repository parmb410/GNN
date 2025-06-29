# -*- coding: utf-8 -*-
"""plotter

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ocdhQa_GtJZ2Znb3MNTNfpEb0W3XQqws
"""

import os
import matplotlib.pyplot as plt

def plot_metrics(history_dict, save_dir="plots"):
    os.makedirs(save_dir, exist_ok=True)

    def plot_single(metric_name):
        plt.figure()
        for label, values in history_dict.items():
            if metric_name in values:
                plt.plot(values[metric_name], label=label)
        plt.title(f"{metric_name} over Epochs")
        plt.xlabel("Epoch")
        plt.ylabel(metric_name)
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{save_dir}/{metric_name}.png")
        plt.close()

    for metric in ["train_acc", "valid_acc", "target_acc", "class_loss", "dis_loss"]:
        plot_single(metric)