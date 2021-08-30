#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/17
# @Author  : github.com/guofei9987

# @Time    : 2021/8/29
# @Author  : zhanghan
import copy
import os
import numpy as np
import multiprocessing as mp


def get_default_x0(parameters):
    res = []
    for para in parameters:
        res.append(parameters[para]["default"])
    return res

def set_default_x0(parameters, x_new_default):
    it = 0
    for para in parameters:
        parameters[para]["default"] = x_new_default[it]
        it += 1

class SimulatedAnnealingBase():
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
    def __init__(self, func, gold_swc_tree, metric_method, 
                 metric_config, optimize_config,**kwargs):
        assert optimize_config["optimize"]["SA"]["Tmax"] > optimize_config["optimize"]["SA"]["Tmin"] > 0, 'Tmax > Tmin > 0'


        self.func = func
        self.T_max = optimize_config["optimize"]["SA"]["Tmax"]  # initial temperature
        self.T_min = optimize_config["optimize"]["SA"]["Tmin"]  # end temperature
        self.L = optimize_config["optimize"]["SA"]["L"]  # num of iteration under every temperature（also called Long of Chain）
        # stop if best_y stay unchanged over max_stay_counter times (also called cooldown time)
        self.max_stay_counter = optimize_config["optimize"]["SA"]["maxStayCounter"]
        self.q = optimize_config["optimize"]["SA"]["q"]
        parameters = optimize_config["trace"]["parameters"]
        self.n_dims = len(parameters)
        
        self.best_x = parameters  # initial solution
        self.best_y = self.func(gold_tree=gold_swc_tree, metric_method=metric_method, config=get_default_x0(parameters),
                                metric_config=metric_config, optimize_config=optimize_config,
                                test_name="test_init", lock=None)[1]
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
        self.T = self.T * self.q

    def isclose(self, a, b, rel_tol=1e-09, abs_tol=1e-30):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    def run(self, gold_swc_tree, metric_method, metric_config, optimize_config):
        x_current, y_current = self.best_x, self.best_y
        stay_counter = 0
        CPU_CORE_NUM = 15
        while True:
            # loop L times under the same Temperature
            i = 0
            print("[Info: ]x current = {}".format(get_default_x0(x_current)))

            while i < int(self.L):
                pool = mp.Pool(processes=CPU_CORE_NUM)
                res_x, res_y = [], []
                lock = mp.Manager().Lock()
                for j in range(CPU_CORE_NUM):
                    x_new = self.get_new_x(x_current)
                    print("[Info: ]x new = {}".format(get_default_x0(x_new)))
                    res_y.append(
                        pool.apply_async(self.func, args=tuple([gold_swc_tree, 
                        metric_method, get_default_x0(x_new), metric_config, optimize_config, os.path.join("tmp", "tmp_res_{}".format(j)), lock]))
                    )
                    res_x.append(get_default_x0(x_new))
                print("[Info: ]i/L = {}/{}".format(i, self.L))
                pool.close()
                pool.join()
                for it in range(len(res_x)):
                    i += 1
                    x_new_default, y_new = res_y[it].get()
                    # Metropolis
                    df = y_new - y_current
                    if df < 0 or np.exp(-df / self.T) > np.random.rand():
                        set_default_x0(x_current, x_new_default)
                        y_current = y_new
                        print("[Info: ] Jump success")
                        if y_new < self.best_y:
                            print("[Info: ] Update success")
                            self.best_x = copy.deepcopy(x_new_default)
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


class SAFast(SimulatedAnnealingBase):
    '''
    u ~ Uniform(0, 1, size = d)
    y = sgn(u - 0.5) * T * ((1 + 1/T)**abs(2*u - 1) - 1.0)

    xc = y * (upper - lower)
    x_new = x_old + xc

    c = n * exp(-n * quench)
    T_new = T0 * exp(-c * k**quench)
    '''
    def __init__(self, gold_swc_tree, metric_method, metric_config, optimize_config, func, **kwargs):
        # nit parent class
        super().__init__(func=func, gold_swc_tree=gold_swc_tree, metric_method=metric_method,
                         metric_config=metric_config, optimize_config=optimize_config, **kwargs)
        self.m, self.n, self.quench = kwargs.get('m', 1), kwargs.get('n', 1), kwargs.get('quench', 1)
        # upper and down are range of the parameters.
        self.lower, self.upper = kwargs.get('lower', -10), kwargs.get('upper', 10)
        self.c = self.m * np.exp(-self.n * self.quench)

    def get_new_x(self, x):
        """randomly search for a new x point"""
        x_new = copy.deepcopy(x)
        for para in x_new:
            if x_new[para]["type"] == "number":
                ran = np.random.uniform(-1, 1)
                l, r = x_new[para]['range'][0], x[para]['range'][1]
                xc = np.sign(ran) * self.T * ((1 + 1.0 / self.T) ** np.abs(ran) - 1.0)

                x_new_default = x[para]['default']/3 + xc * (r-l)/3
                x_new_default += (l+r)/3
                x_new[para]["default"] = x_new_default
            if x_new[para]["type"] == "integer":
                ran = np.random.uniform(-1, 1)
                l, r = x_new[para]['range'][0], x[para]['range'][1]
                xc = np.sign(ran) * self.T * ((1 + 1.0 / self.T) ** np.abs(ran) - 1.0)

                x_new_default = x[para]['default']/3 + xc * (r-l)/3
                x_new_default += (l+r)/3
                x_new[para]["default"] = int(np.round(x_new_default))
            if x_new[para]["type"] == "boolean":
                ran = np.random.uniform(-1, 1)
                l, r = 0, 1
                if x[para]['default'] == False:
                    x0 = 0
                else:
                    x0 = 1
                xc = np.sign(ran) * self.T * ((1 + 1.0 / self.T) ** np.abs(ran) - 1.0)

                x_new_default = x0/3 + xc * (r-l)/3
                x_new_default += (l+r)/3
                if int(np.round(x_new_default)) == 0:
                    x_new_default = False
                else:
                    x_new_default = True

                x_new[para]["default"] = x_new_default
        return x_new

    def cool_down(self):
        self.T = self.T_max * np.exp(-self.c * self.iter_cycle ** self.quench)

# SA_fast is the default
SA = SAFast
