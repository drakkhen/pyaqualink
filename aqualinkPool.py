#!/usr/bin/python
# coding=utf-8

import struct, sys, time, threading

from debugUtils import *
from aqualinkConf import *
from aqualinkInterface import *
from aqualinkPanel import *

########################################################################################################
# state of the pool and equipment
########################################################################################################
class Pool:
    # constructor
    def __init__(self, theState):
        self.title = ""
        self.date = ""
        self.time = ""

        # environment
        self.airTemp = 0
        self.poolTemp = 0
        self.spaTemp = 0
        self.waterTemp = 0

        # modes
        self.spaMode = False
        self.cleanMode = False
        self.fountainMode = False

        # equipment states
        self.filter = False
        self.cleaner = False
        self.spa = False
        self.heater = False
        self.poolLight = False
        self.spaLight = False

        self.state = theState
        self.panel = Panel(theState, self)

    def start(self):
        readThread = ReadThread(self.state, serialDevice, panelAddress, self, self.panel)
        readThread.start()

    def spaOn(self):
        self.panel.spaOn()

    def spaOff(self):
        self.panel.spaOff()

    def printState(self, delim="\n"):
        msg  = "Title:      "+self.title+delim
        msg += "Date:       "+self.date+delim
        msg += "Time:       "+self.time+delim
        msg += "Air:         %d°" %  (self.airTemp)+delim
        msg += "Pool:        %d°" %  (self.poolTemp)+delim
        msg += "Spa:         %d°" %  (self.spaTemp)+delim
        msg += "Filter:     "+self.printEquipmentState(self.filter)+delim
        msg += "Cleaner:    "+self.printEquipmentState(self.cleaner)+delim
        msg += "Spa:        "+self.printEquipmentState(self.spa)+delim
        msg += "Heater:     "+self.printEquipmentState(self.heater)+delim
        msg += "Pool light: "+self.printEquipmentState(self.poolLight)+delim
        msg += "Spa light:  "+self.printEquipmentState(self.spaLight)+delim
        return msg

    def printEquipmentState(self, equipment):
        return "ON" if equipment else "OFF"
                    
########################################################################################################
# message reading thread
########################################################################################################
class ReadThread(threading.Thread):
    # constructor
    def __init__(self, state, serialDevice, theAddr, thePool, thePanel):
        threading.Thread.__init__(self, target=self.readData)
        self.state = state
        self.pool = thePool
        self.panel = thePanel
        self.interface = Interface(serialDevice)
        self.addr = theAddr
        self.lastDest = '\x00'
        
    # data reading loop
    def readData(self):
        if debug: log("starting read thread")
        while self.state.running:
            if not self.state.running: break
            (dest, command, args) = self.interface.readMsg()
            if (dest == self.addr):# or (self.lastDest == self.addr): # messages that are related to this device
                if not monitorMode:                                 # send ACK if not passively monitoring
                    self.interface.sendMsg(masterAddress, cmdAck, ['\x8b', self.panel.button])
                    self.panel.button = btnNone
                self.panel.parseMsg(command, args)
            self.lastDest = dest
        del(self.interface)
        if debug: log("terminating read thread")

