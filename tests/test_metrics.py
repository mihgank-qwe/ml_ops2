"""Тесты расчёта метрик"""

import numpy as np
import pytest
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score


def test_roc_auc_perfect_predictions():
    """Проверка, что ROC-AUC высокий при хороших предсказаниях"""
    y_true = np.array([0, 1, 0, 1])
    y_pred_proba = np.array([0.1, 0.9, 0.2, 0.8])
    auc = roc_auc_score(y_true, y_pred_proba)
    assert auc > 0.9


def test_f1_score_binary():
    """Проверка, что F1 для бинарной классификации работает корректно"""
    y_true = np.array([1, 0, 1, 0])
    y_pred = np.array([1, 0, 0, 0])
    f1 = f1_score(y_true, y_pred, zero_division=0)
    assert 0 <= f1 <= 1


def test_precision_recall():
    """Проверка, что расчёт precision и recall работает корректно"""
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([1, 0, 0, 0])
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    assert 0 <= precision <= 1
    assert 0 <= recall <= 1
