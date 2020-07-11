''' 对基于模型方法生成的图像进行评估
'''

import os
import sys
import numpy as np
import pandas as pd
import cv2
import tifffile
import Utils

def getRawImages(root_path, img_types, npz_folder_path, save_to_npz=False):
    if save_to_npz:
        Utils.resetDir(npz_folder_path)

    standard_files = []
    all_files = []
    # {file_path : image_type}
    types = dict()

    ## 保存所有的图片到字典
    for img_type in img_types:
        dir_path = Utils.joinPath(root_path, img_type)
        file_names = os.listdir(dir_path)
        for file_name in file_names:
            file_path = Utils.joinPath(dir_path, file_name)
            all_files.append(file_path)
            types[file_path] = img_type
            if img_type=='standard':
                standard_files.append(file_path)

            # save image to npz files
            if save_to_npz:
                im = tifffile.imread(file_path)
                np.save(Utils.joinPath(npz_folder_path, file_path.replace('/','-')), im)

    return standard_files, all_files, types


class Matcher():
    def __init__(self):
        pass

    ## 准备相似度计算方法及对应函数
    def funcCreator(self, func_type, *args, **kwargs):
        if func_type=='histogram':
            def func(feature_a, feature_b):
                return cv2.compareHist(np.array(feature_a), np.array(feature_b), kwargs['method'])
            return func
        elif func_type=='moment':
            # 基于颜色矩的相似度计算函数
            def func(feature_a, feature_b):
                ''' calculate similaryty based on moment vector
                    Parameters:
                        feature_a,feature_b: numpy array of shape(4,)
                    Returns:
                        func: function
                '''
                #k_mins = kwargs['k_mins']
                #k_maxs = kwargs['k_maxs']
                #feature_a = (feature_a-k_mins)/(k_maxs-k_mins)
                #feature_b = (feature_b-k_mins)/(k_maxs-k_mins)

                assert(feature_a.shape==(4,) and feature_a.shape==(4,))
                return np.abs(feature_a-feature_b).mean()

            return func
        elif func_type=='signal_to_noise':
            def func(feature_a, feature_b):
                feature_a = feature_a[0]
                feature_b = feature_b[0]
                if feature_a>feature_b:
                    ratio = feature_a/feature_b
                else:
                    ratio = feature_b/feature_a
                #return 2/(1+np.exp(ratio-1))
                return ratio
            return func
        elif func_type=='glcm':
            metrics = kwargs['metrics']
            def func(feature_a, feature_b):
                if metrics=='1_norm_distance':
                    return np.sum(np.abs(feature_a-feature_b))
                elif metrics=='2_norm_distance':
                    # 2_norm_distance
                    return np.sum((feature_a-feature_b)**2)**0.5
                else:
                    sys.exit('error metrics for glcm')
            return func




    def getMethodResult(self, standard_files, img_type_dict, feature_dict, func, bigger_first):
        method_result = dict()
        for im_a_path in standard_files:
            feature_a = feature_dict[im_a_path]
            match_result = list()
            for (im_b_path, feature_b) in feature_dict.items():
                val = func(feature_a, feature_b)
                match_result.append(tuple((im_b_path, img_type_dict[im_b_path], val)))

            # sort
            match_result = sorted(match_result, key=lambda tup:tup[2], reverse=bigger_first)

            # add to dict
            method_result[im_a_path] = match_result

        return method_result

    def calAveragePos(self, match_result, method_name, top):
        method_result = match_result[method_name]
        # create dict: type_sum, type_cnt
        type_sum = dict()
        type_cnt = dict()

        for (im_a_path, match_result) in method_result.items():
            #  create file_stat_sum and file_stat_cnt
            file_stat_sum = dict()
            file_stat_cnt = dict()
            for idx, (im_b_path, im_b_type, dis) in enumerate(match_result[:top]):
                if im_b_type in file_stat_sum:
                    file_stat_sum[im_b_type] += (idx+1)
                    file_stat_cnt[im_b_type] += 1
                else:
                    file_stat_sum[im_b_type] = (idx+1)
                    file_stat_cnt[im_b_type] = 1

            # update type_sum and type_cnt
            for (im_type, avg_pos) in file_stat_sum.items():
                if im_type in type_sum:
                    type_sum[im_type] += file_stat_sum[im_type]/file_stat_cnt[im_type]
                    type_cnt[im_type] += 1
                else:
                    type_sum[im_type] = file_stat_sum[im_type]/file_stat_cnt[im_type]
                    type_cnt[im_type] = 1

        # calculate result
        ret = dict()
        for im_type, sum_of_avgpos in type_sum.items():
            ret[im_type] = type_sum[im_type] / type_cnt[im_type]

        # normalize
        for im_type, avgpos in ret.items():
            ret[im_type] = ret[im_type]/top

        return ret

#     def calculateAll(self):

    def calculatePos(self, img_types, match_result, method_names, tops):
        df = pd.DataFrame()
        for method_name in method_names:
            for top in tops:
                res = self.calAveragePos(match_result, method_name, top)
                series = pd.Series(res, index=img_types)
                col_name = '{}, top {}'.format(method_name, top)
                df[col_name] = series

        return df

    def calculateSimilarity(self,
                            standard_files,
                            types,
                            feature_dict,
                            img_types,
                            methods):
        df = pd.DataFrame()
        similarity_dict = {}
        for method_name, func, bigger_better in methods:
            type_sum = {}
            type_cnt = {}
            type_similarity = {}
            for im_a_path in standard_files:
                im_a_type = types[im_a_path]
                feature_a = feature_dict[im_a_path]
                im_sum = {}
                im_cnt = {}
                for (im_b_path, feature_b) in feature_dict.items():
                    im_b_type = types[im_b_path]
                    similarity = func(feature_a, feature_b)
                    if im_b_type in type_similarity:
                        type_similarity[im_b_type].append(similarity)
                    else:
                        type_similarity[im_b_type] = [similarity]

                    # update im_sum, im_cnt
                    if im_b_type in im_sum:
                        im_sum[im_b_type] += similarity
                        im_cnt[im_b_type] += 1
                    else:
                        im_sum[im_b_type] = similarity
                        im_cnt[im_b_type] = 1

                ## update type_sum, type_cnt
                # calculate averate
                im_result = {}
                for im_type, sum_of_similarity in im_sum.items():
                    im_result[im_type] = im_sum[im_type]/im_cnt[im_type]

                # update
                for im_type, avg_of_similarity in im_result.items():
                    if im_type in type_sum:
                        type_sum[im_type] += im_result[im_type]
                        type_cnt[im_type] += 1
                    else:
                        type_sum[im_type] = im_result[im_type]
                        type_cnt[im_type] = 1

            similarity_dict[method_name] = type_similarity
            series = pd.Series(type_sum, index=img_types)
            col_name = '{}: {}'.format(method_name, '>' if bigger_better else '<')
            df[col_name] = series

        return df, similarity_dict
