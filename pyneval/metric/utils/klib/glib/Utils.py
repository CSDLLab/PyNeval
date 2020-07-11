# -*- coding: utf-8 -*-


"""Utility module
   This utility module provides some fundamental functions.
"""
import numpy as np
import math
import os
import sys
import shutil
from shutil import copyfile
from shutil import move
import pickle
import platform
import json
import time
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def dict2npy(data, out_path):
    assert(type(data)==dict)
    np.save(out_path, data)

def npy2dict(in_path):
    data = np.load(in_path).item()
    assert(type(data)==dict)
    return data

def dict2json(data, out_path):
    assert(type(data)==dict)
    with open(out_path, 'w') as fp:
        json.dump(data, fp)

def json2dict(in_path):
    with open(in_path, 'r') as fp:
        return json.load(fp)

def list2dict(list_data):
    return dict((val,idx) for idx,val in enumerate(list_data))

def reverseDict(dic_data):
    return {v:k for k,v in dic_data.items()}


class Timer():
    """ Timer util
    """
    def __init__(self):
        self.init_time = time.time()
        self.last_time = self.init_time
        self.now_time = self.init_time

    def __str__(self):
        return 'init time:{}, last time:{}'.format(self.init_time, self.last_time)

    def reset(self):
        self.init_time = time.time()
        self.last_time = self.init_time
        self.now_time = self.init_time

    def getTime(self):
        self.now_time = time.time()
        duration = self.now_time - self.last_time
        self.last_time = self.now_time
        return duration

    def getTotalTime(self,update_last_time=False):
        self.now_time = time.time()
        duration = self.now_time - self.init_time
        if update_last_time:
            self.last_time = self.now_time
        return duration

    def convertSecondsToStr(self, s):
        return time.strftime("%H小时:%M分:%S秒", time.gmtime(s))


class Mail(Timer):

    def __init__(self):
        super().__init__()

    def __str__(self):
        return 'My Mail class'

    def notifyMe(self,
                 subject,
                 content='官万先\r\n3110102860@zju.edu.cn',
                 mailto='3110102860@zju.edu.cn',
                 check_time=True):

        from_addr = "3110102860@zju.edu.cn"
        password = "163617"

        if check_time:
                time_to_last = self.convertSecondsToStr(self.getTime())
                time_to_begin = self.convertSecondsToStr(self.getTotalTime())
                content += '\r\n'
                content += '距离上次时间:'+time_to_last
                content += '\r\n'
                content += '距离开始时间:'+time_to_begin

        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = '官万先<%s>' % from_addr
        msg['To'] = mailto
        msg['Subject'] = Header(subject, 'utf-8').encode()

        smtp_server = "smtp.zju.edu.cn"
        server = smtplib.SMTP(smtp_server, 25)
        server.login(from_addr, password)
        server.sendmail(from_addr, [mailto], msg.as_string())
        server.quit()



def revertMat(M):
    return np.linalg.revertMat(M)



def copyFiles(src_dir, dst_dir, count, reset=False):
    if reset:
        resetDir(dst_dir)
    else:
        setDir(dst_dir)

    file_names = os.listdir(src_dir)
    total_cnt = len(file_names)
    idxs = np.arange(total_cnt)
    np.random.shuffle(idxs)

    real_count = np.min([total_cnt, count])
    for i in range(real_count):
        src_path = joinPath(src_dir,file_names[idxs[i]])
        dst_path = joinPath(dst_dir, file_names[idxs[i]])
        copyfile(src_path, dst_path)

    print('文件总数:{}, 拷贝数量:{}'.format(total_cnt, real_count))



def testDir(dir):
    '''Exit the program if dir not exist'''
    print(dir)
    if not os.path.exists(dir):
        sys.exit('Exit: %s not exist!'%(dir))

def setDir(dir):
    '''Create the dir if not exist'''
    if not os.path.exists(dir):
        os.makedirs(dir) # Like `make -p`, recursive create directory if needed

def resetDir(dir):
        shutil.rmtree(dir,ignore_errors=True)
        setDir(dir)

def datestamp():
    return time.strftime("%Y%m%d", time.localtime())

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S", time.localtime())

def hostname():
    return platform.node()

def generate_expid(model_name, extra_comment):
    exp_id = "%s-%s-%s" % (model_name, hostname(), timestamp())
    if extra_comment:
        exp_id = exp_id + '-' + extra_comment
    return exp_id

def saveData(data, path):
    """saveData, save variables into file
       :data: data stored in a list
       :path: string, file patth, ending with .pckl
    """
    f = open(path, 'wb')
    pickle.dump(data, f)
    f.close()

def loadData(path):
    """Load variables from a specified file"""
    f = open(path, 'rb')
    data = pickle.load(f)
    f.close()
    return data


def joinPath(path, *paths):
    return os.path.join(path, *paths)



def prepareTrain(args):
    if args.s : # start training new mode
        extra_comment = None
        if args.e:
            extra_comment = args.e[0]
        exp_id = Utils.generate_expid(model_name, extra_comment)
        exp_dir = '/'.join([FLAGS.all_stuff_dir,exp_id])
        Utils.resetDir(exp_dir)

        log_dir = '/'.join([exp_dir,FLAGS.log_dir])
        Utils.setDir(log_dir)

        checkpoint_dir= '/'.join([exp_dir,FLAGS.checkpoint_dir])
        Utils.setDir(checkpoint_dir)

        specified_checkpoint_dir= '/'.join([exp_dir,FLAGS.specified_checkpoint_dir])
        Utils.setDir(specified_checkpoint_dir)

        retrain = True
        continue_from_pre = False
    elif args.r: # restore and continue training model
        exp_id = args.r[0]
        exp_dir = '/'.join([FLAGS.all_stuff_dir,exp_id])
        Utils.testDir(exp_dir)

        log_dir = '/'.join([exp_dir,FLAGS.log_dir])
        Utils.testDir(log_dir)

        checkpoint_dir= '/'.join([exp_dir,FLAGS.checkpoint_dir])
        Utils.testDir(checkpoint_dir)

        specified_checkpoint_dir= '/'.join([exp_dir,FLAGS.specified_checkpoint_dir])
        Utils.setDir(specified_checkpoint_dir)

        retrain = True
        continue_from_pre = True
    else: # test model
        exp_id = args.t[0]
        exp_dir = '/'.join([FLAGS.all_stuff_dir,exp_id])
        Utils.testDir(exp_dir)

        log_dir = '/'.join([exp_dir,FLAGS.log_dir])
        Utils.testDir(log_dir)

        checkpoint_dir= '/'.join([exp_dir,FLAGS.checkpoint_dir])
        Utils.testDir(checkpoint_dir)

        specified_checkpoint_dir= '/'.join([exp_dir,FLAGS.specified_checkpoint_dir])
        Utils.setDir(specified_checkpoint_dir)

        retrain = False
        continue_from_pre = False
