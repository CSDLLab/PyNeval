#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/17
# @Author  : github.com/guofei9987
import copy
import os
import numpy as np
import multiprocessing as mp
from sko.base import SkoBase
from sko.operators import mutation

CPU_CORE_NUM = 15


class SimulatedAnnealingBase(SkoBase):
    """
    DO SA(Simulated Annealing)

    Parameters
    ----------------
    func : function
        The func you want to do optimal
    n_dim : int
        number of variables of func
    x0 : array, shape is n_dim
        initial solution
    T_max :float
        initial temperature
    T_min : float
        end temperature
    L : int
        num of iteration under every temperature（Long of Chain）

    Attributes
    ----------------------


    Examples
    -------------
    See https://github.com/guofei9987/scikit-opt/blob/master/examples/demo_sa.py
    """

    def __init__(self, func, x0, T_max=100, T_min=1e-7, L=300, max_stay_counter=150, **kwargs):
        assert T_max > T_min > 0, 'T_max > T_min > 0'

        self.func = func
        self.T_max = T_max  # initial temperature
        self.T_min = T_min  # end temperature
        self.L = int(L)  # num of iteration under every temperature（also called Long of Chain）
        # stop if best_y stay unchanged over max_stay_counter times (also called cooldown time)
        self.max_stay_counter = max_stay_counter

        self.n_dims = len(x0)

        self.best_x = np.array(x0)  # initial solution
        self.best_y = self.func(self.best_x, "test_init")[1]
        self.T = self.T_max
        self.iter_cycle = 0
        self.generation_best_X, self.generation_best_Y = [self.best_x], [self.best_y]
        # history reasons, will be deprecated
        self.best_x_history, self.best_y_history = self.generation_best_X, self.generation_best_Y

    def get_new_x(self, x):
        u = np.random.uniform(-1, 1, size=self.n_dims)
        x_new = x + 20 * np.sign(u) * self.T * ((1 + 1.0 / self.T) ** np.abs(u) - 1.0)
        return x_new

    def cool_down(self):
        self.T = self.T * 0.7

    def isclose(self, a, b, rel_tol=1e-09, abs_tol=1e-30):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def run(self):
        x_current, y_current = self.best_x, self.best_y
        stay_counter = 0
        while True:
            # loop L times under the same Temperature
            i = 0
            while i < self.L:
                pool = mp.Pool(processes=CPU_CORE_NUM)
                res_y = []
                res_x = []
                lock = mp.Manager().Lock()
                for j in range(CPU_CORE_NUM):
                    x_new = self.get_new_x(x_current)
                    for k in range(len(x_new)):
                        x_new[k] = max(x_new[k], 0)
                        x_new[k] = min(x_new[k], 1)
                    res_y.append(
                        pool.apply_async(self.func, args=tuple([x_new, os.path.join("tmp", "tmp_res_{}".format(j)), lock]))
                    )
                    res_x.append(x_new)

                print("[Info: ]i/L = {}/{}".format(i, self.L))
                pool.close()
                pool.join()
                for it in range(len(res_x)):
                    i += 1
                    x_new, y_new = res_y[it].get()
                    # Metropolis
                    df = y_new - y_current
                    if df < 0 or np.exp(-df / self.T) > np.random.rand():
                        x_current, y_current = x_new, y_new
                        print("[Info: ] Jump success")
                        if y_new < self.best_y:
                            print("[Info: ] Update success")
                            self.best_x = copy.deepcopy(x_new)
                            self.best_y = y_new
                        break
            print("[Info: ] best x = {}".format(self.best_x))
            print("[Info: ] best y = {}".format(self.best_y))

            print("[Info: ] iter_cycle = {} T = {} stay_counter = {}".format(
                self.iter_cycle, self.T, stay_counter
            ))
            print("[Info: ]origin minimalScoreAuto = {}\n"
                  "        minimalScoreSeed = {}".format(
                self.best_x[0], self.best_x[1]
            ))
            self.iter_cycle += 1
            self.cool_down()
            self.generation_best_Y.append(self.best_y)
            self.generation_best_X.append(self.best_x)

            # if best_y stay for max_stay_counter times, stop iteration
            if self.isclose(self.best_y_history[-1], self.best_y_history[-2]):
                stay_counter += 1
            else:
                stay_counter = 0

            if self.T < self.T_min:
                stop_code = 'Cooled to final temperature'
                break
            if stay_counter > self.max_stay_counter:
                stop_code = 'Stay unchanged in the last {stay_counter} iterations'.format(stay_counter=stay_counter)
                break

        return self.best_x, self.best_y

    fit = run


class SAFast(SimulatedAnnealingBase):
    '''
    u ~ Uniform(0, 1, size = d)
    y = sgn(u - 0.5) * T * ((1 + 1/T)**abs(2*u - 1) - 1.0)

    xc = y * (upper - lower)
    x_new = x_old + xc

    c = n * exp(-n * quench)
    T_new = T0 * exp(-c * k**quench)
    '''

    def __init__(self, func, x0, T_max=100, T_min=1e-7, L=300, max_stay_counter=150, **kwargs):
        # nit parent class
        super().__init__(func, x0, T_max, T_min, L, max_stay_counter, **kwargs)
        self.m, self.n, self.quench = kwargs.get('m', 1), kwargs.get('n', 1), kwargs.get('quench', 1)
        # upper and down are range of the parameters.
        self.lower, self.upper = kwargs.get('lower', -10), kwargs.get('upper', 10)
        self.c = self.m * np.exp(-self.n * self.quench)

    def get_new_x(self, x):
        """randomly search for a new x point"""
        r = np.random.uniform(-1, 1, size=self.n_dims)
        xc = np.sign(r) * self.T * ((1 + 1.0 / self.T) ** np.abs(r) - 1.0)
        x_new = x + xc * (self.upper - self.lower)
        return x_new

    def cool_down(self):
        self.T = self.T_max * np.exp(-self.c * self.iter_cycle ** self.quench)


# SA_fast is the default
SA = SAFast

