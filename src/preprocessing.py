import logging
from datetime import date
from collections import Counter

import utils
import dataset
import visualizations

import pandas as pd
import numpy as np
from sklearn import model_selection, preprocessing
from imblearn.under_sampling import RandomUnderSampler

logger = logging.getLogger(__name__)


def remove_other_attributes(df):
    return df.drop(columns=dataset.OTHER_ATTRIBUTES)


def keep_other_attributes(df):
    # Remove all buildings that do not have one of our four variables (age/type/floor/height).
    df = df.dropna(subset=dataset.OTHER_ATTRIBUTES+[dataset.AGE_ATTRIBUTE])
    df = df[df[dataset.TYPE_ATTRIBUTE] != 'Indifférencié']

    # Encode 'usage type', which is a categorical variable, into multiple dummy variables.
    df = utils.dummy_encoding(df, dataset.TYPE_ATTRIBUTE)
    return df


def normalize_features(df_train, df_test):
    scaler = preprocessing.MinMaxScaler()
    feature_columns = list(set(df_train.columns) - set(dataset.AUX_VARS) - set(dataset.TARGET_ATTRIBUTES))
    df_train[feature_columns] = scaler.fit_transform(df_train[feature_columns])
    df_test[feature_columns] = scaler.transform(df_test[feature_columns])
    return df_train, df_test


def drop_unimportant_features(df):
    return df[dataset.SELECTED_FEATURES + [dataset.AGE_ATTRIBUTE] + dataset.AUX_VARS]


def remove_buildings_pre_2000(df):
    return df[df[dataset.AGE_ATTRIBUTE] >= 2000]


def remove_buildings_pre_1850(df):
    return df[df[dataset.AGE_ATTRIBUTE] >= 1850]


def remove_buildings_pre_1950(df):
    return df[df[dataset.AGE_ATTRIBUTE] >= 1950]


def remove_buildings_between_1930_1990(df):
    return df[~df[dataset.AGE_ATTRIBUTE].between(1930, 1990)]


def remove_outliers(df):
    df = df[df[dataset.AGE_ATTRIBUTE] > 1900]
    df = df[df[dataset.AGE_ATTRIBUTE] < 2020]
    return df


def undersample_skewed_distribution(df):
    rus = RandomUnderSampler(random_state=dataset.GLOBAL_REPRODUCIBILITY_SEED)
    X, y = utils.split_target_var(df)
    undersampled_X, undersampled_y = rus.fit_resample(X, y)

    visualizations.plot_histogram(undersampled_y, y, bins=utils.age_bins(undersampled_y))
    logger.info(f'Downsampling distribution results in: {sorted(Counter(undersampled_y[dataset.AGE_ATTRIBUTE]).items())}')

    undersampled_df = pd.concat([undersampled_X, undersampled_y], axis=1, join="inner")
    return undersampled_df


def categorize_age_EHS(df):
    df[dataset.AGE_ATTRIBUTE] = pd.cut(
        df[dataset.AGE_ATTRIBUTE], dataset.EHS_AGE_BINS, labels=dataset.EHS_AGE_LABELS).cat.codes
    return df


def categorize_age(df):
    bins = utils.age_bins(df, bin_size=5)
    labels = bins[:-1]

    df[dataset.AGE_ATTRIBUTE] = pd.cut(
        df[dataset.AGE_ATTRIBUTE], bins, labels=labels).cat.codes
    return df


def round_age(df):
    df[dataset.AGE_ATTRIBUTE] = utils.custom_round(df[dataset.AGE_ATTRIBUTE])
    return df


def add_noise_feature(df):
    df["feature_noise"] = np.random.normal(size=len(df))
    return df


def split_80_20(df):
    return model_selection.train_test_split(df, test_size=0.2, random_state=dataset.GLOBAL_REPRODUCIBILITY_SEED)


def split_50_50(df):
    return model_selection.train_test_split(df, test_size=0.5, random_state=dataset.GLOBAL_REPRODUCIBILITY_SEED)


def split_by_region(df):
    # We aim to cross-validate our results using five French sub-regions 'departement' listed below.
    # one geographic region for validation, rest for testing
    region_names = ['Haute-Vienne', 'Hauts-de-Seine',
                    'Aisne', 'Orne', 'Pyrénées-Orientales']
    df_test = df[df.departement == region_names[dataset.GLOBAL_REPRODUCIBILITY_SEED % len(region_names)]]
    df_train = df[~df.index.isin(df_test.index)]
    return df_train, df_test


def filter_french_medium_sized_cities_with_old_center(df):
    city_names = ['Valence', 'Aurillac', 'Oyonnax', 'Aubenas', 'Vichy', 'Montluçon', 'Montélimar', 'Bourg-en-Bresse']
    # city_names = ['Valence', 'Oyonnax', 'Bourg-en-Bresse'] # very similar in terms of building age structure
    return df[df['city'].isin(city_names)]


def split_and_filter_by_french_medium_sized_cities_with_old_center(df):
    city_names = ['Valence', 'Aurillac', 'Oyonnax', 'Aubenas', 'Vichy', 'Montluçon', 'Montélimar', 'Bourg-en-Bresse']
    test_city = city_names[dataset.GLOBAL_REPRODUCIBILITY_SEED % len(city_names)]
    city_names.remove(test_city)
    df_test = df[df['city'] == test_city]
    df_train = df[df['city'].isin(city_names)]
    return df_train, df_test


def split_by_city(df):
    cities = sorted(df['city'].unique())
    df_test = df[df['city'] == cities[dataset.GLOBAL_REPRODUCIBILITY_SEED % len(cities)]]
    df_train = df[~df.index.isin(df_test.index)]
    return df_train, df_test