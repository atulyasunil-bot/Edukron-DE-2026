"""
data_loader.py
---------------
Central place for reading the raw Home Credit CSV files.
All functions are decorated with st.cache_data so a file is read from disk
only once per session, no matter how many pages need it.
"""

import os
import pandas as pd
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _path(name: str) -> str:
    return os.path.join(DATA_DIR, name)


@st.cache_data(show_spinner="Loading application_train.csv ...")
def load_application_train() -> pd.DataFrame:
    return pd.read_csv(_path("application_train.csv"))


@st.cache_data(show_spinner="Loading application_test.csv ...")
def load_application_test() -> pd.DataFrame:
    return pd.read_csv(_path("application_test.csv"))


@st.cache_data(show_spinner="Loading bureau.csv ...")
def load_bureau() -> pd.DataFrame:
    return pd.read_csv(_path("bureau.csv"))


@st.cache_data(show_spinner="Loading bureau_balance.csv ...")
def load_bureau_balance() -> pd.DataFrame:
    return pd.read_csv(_path("bureau_balance.csv"))


@st.cache_data(show_spinner="Loading POS_CASH_balance.csv ...")
def load_pos_cash() -> pd.DataFrame:
    return pd.read_csv(_path("POS_CASH_balance.csv"))


def available_files() -> dict:
    """Returns which of the optional Home Credit tables are physically present."""
    names = [
        "application_train.csv",
        "application_test.csv",
        "bureau.csv",
        "bureau_balance.csv",
        "POS_CASH_balance.csv",
        "previous_application.csv",
        "installments_payments.csv",
        "credit_card_balance.csv",
    ]
    return {n: os.path.exists(_path(n)) for n in names}
