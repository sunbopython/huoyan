#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time,os,signal
import logging
import logging.config

logging.config.fileConfig('gsxt/gsxtlogger.conf')

class DriverClean():
    def __init__(self,status,ts,pid,br):
        self.logger = logging.getLogger()
        self.status = status
        self.ts = ts
        self.pid = pid
        self.br = br
        self.term = 0

    def clean(self):
        while True:
            if self.term == 1:
                return
            if self.status == 1:
                time.sleep(1)
                continue
            if time.time() - self.ts <= 30:
                # print time.time()-self.ts
                time.sleep(1)
                continue
            break
        try:
            self.br.quit()
            self.logger.info("webdriver has been killed!")
        except Exception as e:
            self.logger.error( 'killpg error')
            self.logger.error(e)


    def setstatus(self,status):
        self.status = status

    def setts(self,ts):
        self.ts = ts

    def setterm(self,term):
        self.term = term
