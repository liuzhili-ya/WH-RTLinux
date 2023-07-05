#!/usr/bin/env python3

#encoding=utf-8
__author__ = 'addy.ke@rock-chips.com'

import traceback
import os
import sys
import threading
import time
import math
import getopt

version = 'Upgrade Tool v1.49'

def printCmd(cmd):
    print('Command: %s' % cmd)

def toolName():
    fd = os.popen('uname -s')
    line = fd.read().split()[0]
    fd.close()

    if line in ('Darwin'):
        return 'sudo ./bin/flash.mac'

    fd = os.popen('uname -m')
    line = fd.read().split()[0]
    fd.close()
    return 'sudo ./bin/flash.%s' % line

def queryFlashMode():
    cmd = '%s LD' % toolName()
    fd = os.popen(cmd)
    line = fd.read()
    if line.find("Mode=Loader") >= 0:
        print('loader')
    elif line.find("Mode=Maskrom") >= 0:
        print('maskrom')
    else:
        print("none")

class flashTool:
    def __init__(self, system, board):
        if len(board) == 0:
            self.imagePath = '../Images'
        else:
            self.imagePath = '../Images-%s' % board
        if len(system) == 0:
            self.paramName = 'parameter.txt'
        else:
            self.paramName = 'parameter-%s.txt' % system
        self.tool = toolName()

    def flashEncFile(self, param):
        p = param.split(',')
        if len(p) == 1 or p[1].find('none') >= 0:
            cmd = '%s KDB-W-SN ./files/%s' % (self.tool, p[0])
        else:
            cmd = '%s KDB-W-SN ./files/%s %s' % (self.tool, p[0], p[1])
        return cmd

    def flashReboot(self):
        return '%s rd ' % self.tool

    def flashLoader(self):
        return '%s UL %s/MiniLoaderAll.bin' % (self.tool, self.imagePath)

    def flashParameter(self):
        return '%s DI -p %s/%s' % (self.tool, self.imagePath, self.paramName)

    def flashOne(self, part):
        if part in ('uboot', 'trust'):
            return '%s DI -%s %s/%s.img %s/%s' % (self.tool, part, self.imagePath, part, self.imagePath, self.paramName)
        else:
            return '%s DI -%s %s/%s.img' % (self.tool, part, self.imagePath, part)

def help(argv):
    text = 'Usage: ' + argv[0] + 'options [PARAMTER]\n'
    text += '\n'
    text += 'Options:\n'
    text += '  -h, --help                        Print help information\n'
    text += '  -v, --version                     Print version\n'
    text += '  -q, --query                       Query device flash mode\n'
    text += '  -e, --enc encFile                 Flash kdb enc file\n'
    text += '  -b, --board boardName             Specify board name\n'
    text += '  -a, --android parts               Flash android images\n'
    text += '  -l, --linux parts                 Flash linux images\n'
    text += '  -d, --dual parts                  Flash dual systems images\n'
    text += '\n'
    text += 'Parameter:\n'
    text += '  encFile: file and id split by a commas, such as: BND-TB-RK1808M0-500-0-10dcb6901287.kdb.enc,TM018083200300011\n'
    text += '  boardName: such as prod, prox, m0, s0, smart, rv1126 ...\n'
    text += '  parts: partitions split by a commas, include: uboot, trust, boot_linux, rootfs, boot, misc, system, vendor, oem ...\n'
    text += '\n'
    text += 'e.g.\n'
    text += '  ' + argv[0] + ' -q\n'
    text += '  ' + argv[0] + ' -e BND-TB-RK1808M0-500-0-10dcb6901287.kdb.enc,TM018083200300011\n'
    text += '  ' + argv[0] + ' -b m0 -l uboot,trust,boot_linux,rootfs\n'
    text += '  ' + argv[0] + ' -b prod -a uboot,turst,boot,misc,system,vendor\n'
    text +='\n'

    print(text)

#if os.geteuid() != 0:
#    print 'This program must be run as root!'
#    sys.exit()

try:
    options,args = getopt.getopt(sys.argv[1:], 'hvqe:b:a:l:d:', ['help', 'version', 'query', 'enc=', 'board=', 'anroid=', 'linux=', 'dual='])

except getopt.GetoptError:
    help(sys.argv)
    sys.exit()

if len(options) == 0:
    help(sys.argv)
    sys.exit()

system = ''
board = ''
enc = ''
parts = ''

for option, param in options:
    if option in ('-h', '--help'):
        help(sys.argv)
        sys.exit()
    if option in ('-v', '--version'):
        print(version)
        sys.exit()
    if option in ('-q', '--query'):
        queryFlashMode()
        sys.exit()

for option, param in options:
    if option in ('-b', '--board'):
        board = param
    if option in ('-e', '--enc'):
        enc = param
    if option in ('-l', '--linux'):
        system = 'linux'
        parts = param
        if parts.find("all") >= 0:
            parts = 'uboot,trust,boot_linux,rootfs'
    if option in ('-a', '--android'):
        system = 'android'
        parts = param
        if parts.find("all") >= 0:
            parts = 'uboot,trust,misc,boot,recovery,system,vendor,oem'
    if option in ('-d', '--dual'):
        system = 'dual'
        parts = param
        if parts.find("all") >= 0:
            parts = 'uboot,trust,misc,boot,recovery,system,vendor,oem,boot_linux,rootfs'

cmds = []
tool = flashTool(system, board)
if len(enc) != 0:
    cmds.append(tool.flashEncFile(enc))
    cmds.append(tool.flashReboot())
else:
    partList = parts.split(',')
    cmds.append(tool.flashLoader()) 
    cmds.append(tool.flashParameter()) 
    for part in partList:
        cmds.append(tool.flashOne(part))
    cmds.append(tool.flashReboot())

for cmd in cmds:
    printCmd(cmd)
    os.system(cmd)
