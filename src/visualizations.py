import dataset
import preprocessing

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import metrics

def plot_histogram(y_test, y_predict, bins=None, bin_labels=[]):
    fig, ax = plt.subplots(figsize=(10, 7))
    if bin_labels:
        ax.set_xticklabels([None] + bin_labels)


    sns.distplot(
        y_predict,
        ax=ax,
        hist=True,
        kde=False,
        hist_kws=dict(edgecolor="k", linewidth=1),
        bins=bins,
        label='y_predict'
    )
    sns.distplot(
        y_test,
        ax=ax,
        hist=True,
        kde=False,
        hist_kws=dict(edgecolor="k", linewidth=1),
        bins=bins,
        label='y_test'
    )
    ax.legend()
    plt.title('age distributions')
    plt.show()


def plot_grid(y_test, y_predict):
    min_age = int(y_predict[dataset.AGE_ATTRIBUTE].min())
    max_age = int(y_predict[dataset.AGE_ATTRIBUTE].max())
    time_range = [min_age, max_age]

    df_test = pd.DataFrame()
    df_test['y_predict'] = y_predict
    df_test['y_test'] = y_test

    fig = plt.figure()

    g = sns.JointGrid(
        df_test['y_predict'], df_test['y_test'], xlim=time_range, ylim=time_range)
    g.plot_joint(plt.hexbin, cmap="Purples", gridsize=30,
                 extent=time_range+time_range)

    g.ax_joint.plot(time_range, time_range, color='grey', linewidth=1.5)

    g.ax_marg_x.hist(df_test['y_predict'], color="tab:purple", alpha=.6)
    g.ax_marg_y.hist(df_test['y_test'], color="tab:purple",
                     alpha=.6, orientation="horizontal")

    g.set_axis_labels('Predicted ages in years', 'Target ages in years')

    plt.show()


def plot_log_loss(model):
    # retrieve performance metrics
    results = model.evals_result()
    epochs = len(results['validation_0']['merror'])

    # plot log loss
    fig, ax = plt.subplots(figsize=(12, 12))
    x_axis = range(0, epochs)
    ax.plot(x_axis, results['validation_0']['mlogloss'], label='Train')
    ax.plot(x_axis, results['validation_1']['mlogloss'], label='Test')
    ax.legend()

    plt.ylabel('Log Loss')
    plt.title('XGBoost Log Loss')
    plt.show()


def plot_classification_error(model):
    # retrieve performance metrics
    results = model.evals_result()
    epochs = len(results['validation_0']['merror'])

    # plot classification error
    fig, ax = plt.subplots(figsize=(12, 12))
    x_axis = range(0, epochs)
    ax.plot(x_axis, results['validation_0']['merror'], label='Train')
    ax.plot(x_axis, results['validation_1']['merror'], label='Test')
    ax.legend()

    plt.ylabel('Classification Error')
    plt.title('XGBoost Classification Error')
    plt.show()


def plot_confusion_matrix(y_test, y_predict, class_labels):
    cm = metrics.confusion_matrix(y_test, y_predict)
    plt.figure(figsize=[7, 6])
    norm_cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(norm_cm, annot=np.round(norm_cm, 2), fmt='g',
                xticklabels=class_labels, yticklabels=class_labels, cmap='bone')


def plot_feature_over_time(df, feature_selection=None):
    df = preprocessing.remove_outliers(df)
    df = df.drop(columns=['ID'])
    df[dataset.AGE_ATTRIBUTE] = preprocessing.custom_round(df[dataset.AGE_ATTRIBUTE])

    for feature, type in df.dtypes.iteritems():
        if feature_selection is not None and feature not in feature_selection:
            continue

        feature_df = df.copy()
        if type == 'object' or type == 'bool':
            feature_df = feature_df[[dataset.AGE_ATTRIBUTE, feature]] \
                .groupby([dataset.AGE_ATTRIBUTE, feature]) \
                .size() \
                .unstack(level=0) \
                .fillna(0)
            sns.heatmap(feature_df, cmap="Blues", cbar_kws={"shrink": .7})
        else:
            feature_df[feature] = feature_df[feature].clip(lower=feature_df[feature].quantile(0.005), upper=feature_df[feature].quantile(0.995))
            sns.relplot(data=feature_df, x=dataset.AGE_ATTRIBUTE, ci=99, y=feature, kind="line")
        #   sns.relplot(data=df, x=dataset.AGE_ATTRIBUTE, y=feature) #, line_kws={"color": "red"}, scatter_kws={'s':2})

        plt.show()


def plot_prediction_error_histogram(y_test, y_predict):
    error = (y_test.T - y_predict.T).T
    error.hist(bins = 40)
    plt.title('Histogram of prediction errors')