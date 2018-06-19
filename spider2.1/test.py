# coding=utf-8
from datetime import datetime
from datetime import timedelta
import os
import shutil
import execjs
import redis



def get_date_list():
    endday = datetime.now()
    day = timedelta(days=-(6*30))
    startday = (endday + day).strftime('%Y%m%d')
    timespan = timedelta(days=1)
    daylist = []
    while True:
        day = endday = (endday - timespan)
        sday = day.strftime("%Y%m%d")
        daylist.append(sday)
        if sday == startday:
            break
    return daylist


def startEndList(daylist, mset):
    res = {m:[] for m in mset}
    for d in daylist:
        res[d[0:6]].append(int(d))
    print res
    res = {k:[str(max(v)), str(min(v))] for k, v in res.items()}
    print res


def rmdir():
    ld = os.listdir('./')
    for d in ld:
        rd = [
                './' + d + '/verifycode/',
                './' + d + '/sample/', 
                './' + d +'/logs'
                ]
                
        for i in rd:
            if os.path.exists(i):
                for d in  os.listdir(i):
                    print i + d + '     已删除'
                # print i 
                shutil.rmtree(i)
                os.mkdir(i)  

if __name__ == '__main__':

    # daylist = get_date_list()
    # mset = set([d[:6] for d in daylist])
    # print mset
    # print startEndList(daylist, mset) 
    rmdir()
    # test()