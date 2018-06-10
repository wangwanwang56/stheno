# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from numbers import Number

import numpy as np
from numpy.testing import assert_allclose
from plum import Dispatcher

from stheno.graph import GP, Graph
from stheno.input import Observed
from stheno.kernel import EQ
from stheno.mean import FunctionMean, ZeroMean, Mean, OneMean, \
    PosteriorCrossMean, PosteriorMean
# noinspection PyUnresolvedReferences
from . import eq, neq, lt, le, ge, gt, raises, call, ok, eprint


def test_corner_cases():
    yield raises, NotImplementedError, lambda: Mean()(1.)
    x = np.random.randn(10, 2)
    yield ok, np.allclose(ZeroMean()(x), ZeroMean()(Observed(x)))


def test_basic_arithmetic():
    dispatch = Dispatcher()

    @dispatch(Number)
    def f1(x): return np.array([[x ** 2]])

    @dispatch(object)
    def f1(x): return np.sum(x ** 2, axis=1)[:, None]

    @dispatch(Number)
    def f2(x): return np.array([[x ** 3]])

    @dispatch(object)
    def f2(x): return np.sum(x ** 3, axis=1)[:, None]

    m1 = FunctionMean(f1)
    m2 = FunctionMean(f2)
    m3 = ZeroMean()
    x1 = np.random.randn(10, 2)
    x2 = np.random.randn()

    yield ok, np.allclose((m1 * m2)(x1), m1(x1) * m2(x1)), 'prod'
    yield ok, np.allclose((m1 * m2)(x2), m1(x2) * m2(x2)), 'prod 2'
    yield ok, np.allclose((m1 + m3)(x1), m1(x1) + m3(x1)), 'sum'
    yield ok, np.allclose((m1 + m3)(x2), m1(x2) + m3(x2)), 'sum 2'
    yield ok, np.allclose((5. * m1)(x1), 5. * m1(x1)), 'prod 3'
    yield ok, np.allclose((5. * m1)(x2), 5. * m1(x2)), 'prod 4'
    yield ok, np.allclose((5. + m1)(x1), 5. + m1(x1)), 'sum 3'
    yield ok, np.allclose((5. + m1)(x2), 5. + m1(x2)), 'sum 4'


def test_posterior_mean():
    pcm = PosteriorCrossMean(None, None, None, None, None, None)
    yield eq, str(pcm), 'PosteriorCrossMean()'

    gp = GP(EQ(), graph=Graph())
    pm = PosteriorMean(gp, None, None, None)
    yield eq, str(pm), 'PosteriorMean()'


def test_function_mean():
    m1 = 5 * OneMean() + (lambda x: x ** 2)
    m2 = (lambda x: x ** 2) + 5 * OneMean()
    m3 = (lambda x: x ** 2) + ZeroMean()
    m4 = ZeroMean() + (lambda x: x ** 2)
    x = np.random.randn(10, 1)

    yield ok, np.allclose(m1(x), 5 + x ** 2)
    yield ok, np.allclose(m2(x), 5 + x ** 2)
    yield ok, np.allclose(m3(x), x ** 2)
    yield ok, np.allclose(m4(x), x ** 2)

    def my_function(x): pass

    yield eq, str(FunctionMean(my_function)), 'my_function'


def test_selected_mean():
    m = 5 * OneMean() + (lambda x: x ** 2)
    x = np.random.randn(10, 3)

    yield assert_allclose, m.select(1, 2)(x), m(x[:, [1, 2]])


def test_shifting():
    m = 5 * OneMean() + (lambda x: x ** 2)
    x = np.random.randn(10, 3)

    yield assert_allclose, m.shift(5)(x), m(x - 5)


def test_stretching():
    m = 5 * OneMean() + (lambda x: x ** 2)
    x = np.random.randn(10, 3)

    yield assert_allclose, m.stretch(5)(x), m(x / 5)


def test_input_transform():
    m = 5 * OneMean() + (lambda x: x ** 2)
    x = np.random.randn(10, 3)

    yield assert_allclose, m.transform(lambda x: x - 5)(x), m(x - 5)
