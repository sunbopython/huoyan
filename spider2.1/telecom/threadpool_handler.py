# coding=utf-8
import Queue

from threadpool import ThreadPool
from threadpool import NoResultsPending



class VerifycodeError(Exception):
    # 验证码错误异常
    pass
    
class TelecomSiteError(Exception):
    # 电信网站错误异常
    pass


class ThraedPool_ExcRes(ThreadPool):
    # 使线程池遇到异常则跳出并关闭

    def poll(self, block=False):
        # 设置一个异常标志
        self.exc_flag = False
        while True:
            if not self.workRequests:
                raise NoResultsPending
            elif block and not self.workers:
                raise NoWorkersAvailable
            try:
                request, result = self._results_queue.get(block=block)
                # if request.exception and request.exc_callback:
                #     request.exc_callback(request, result)
                # 存在异常，执行回调，清空工作线程，告知wait()跳出循环
                if request.exception and request.exc_callback:
                    request.exc_callback(request, result)
                    self.dismissWorkers(len(self.workers))
                    self.exc_flag = True
                    raise NoResultsPending
                if request.callback and not \
                       (request.exception and request.exc_callback):
                    request.callback(request, result)
                del self.workRequests[request.requestID]
            except Queue.Empty:
                break