#!/usr/lib/python

import openhab as openHAB
import socket
import logging as logger
import time
import datetime
import configparser

# Read in pi configurations
parser = configparser.RawConfigParser()
# parser.read(r'/home/pi/Dev/Central/venv/src/pi-config.ini')
# parser.read(r'C:/Users/Mark/PycharmProjects/CentralPi/venv/pi-config.ini')

# Gather data from openhab
base_url = 'http://localhost:8080/rest'
openhab = openHAB(base_url)

# Set log configuration
logger.basicConfig(filename='central.log', level=logger.DEBUG)

# Set up tcp socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def logEvent(eventType, eventMessage, functionName):
    if eventType == 'SUCCESS':
        logger.info(' -- ' + datetime.datetime.fromtimestamp(time.time()).strftime(
            '%Y-%m-%d %H:%M:%S') + ' --> ' + eventMessage + ' Function -> ' + functionName)
    elif eventType == 'ERROR':
        logger.debug(' -- ' + datetime.datetime.fromtimestamp(time.time()).strftime(
            '%Y-%m-%d %H:%M:%S') + ' --> ' + eventMessage + ' Function -> ' + functionName)
    elif eventType == 'WARNING':
        logger.warning(' -- ' + datetime.datetime.fromtimestamp(time.time()).strftime(
            '%Y-%m-%d %H:%M:%S') + ' --> ' + eventMessage + ' Function -> ' + functionName)


def getOpenhabItem(itemName):
    item = openhab.get_item(itemName)
    # if item is null log and return null
    if item.state == '':
        logEvent('ERROR', itemName + ' FAILED TO BE RETRIVED. ITEM WAS NULL.', 'getOpenhabItem')
        return 'NULL';
    # else if item is active log and return item
    elif item.state != '':
        logEvent('SUCCESS', itemName + ' SUCCESSFULLY RETRIVED.', 'getOpenhabItem')
        return item;


def toggleOpenhabItem(itemName):
    item = getOpenhabItem(itemName)
    # if item was retreived, toggle
    if item != 'NULL':
        # if item is ON toggle to OFF
        if item.state == 'ON':
            item.state = 'OFF'
            # check if item was toggled
            if item.state == 'OFF':
                # success
                logEvent('SUCCESS', itemName + ' SUCCESSFULLY TOGGLED TO \'OFF\'.', 'toggleOpenhabItem')
                return 'SUCCESS';
            else:
                # failure
                logEvent('ERROR', itemName + ' FAILED TOGGLED TO \'OFF\'.', 'toggleOpenhabItem')
                return 'FAIL';
        # if item is OFF toggle to ON
        elif item.state == 'OFF':
            item.state = 'ON'
            # check if item was toggled
            if item.state == 'ON':
                # success
                logEvent('SUCCESS', itemName + ' SUCCESSFULLY TOGGLED TO \'ON\'.', 'toggleOpenhabItem')
                return 'SUCCESS';
            else:
                # failure
                logEvent('ERROR', itemName + ' FAILED TO TOGGLED TO \'ON\'.', 'toggleOpenhabItem')
                return 'FAIL';
    else:
        return 'ITEM NULL';


# Returns the port of the raspberry pi by name
def getTcpPort(piName):
    section = 'Pi TCP Ports'
    if piName in parser.options(section):
        # log info event -> TCP PORT FOUND FOR ' + piName + '
        return (parser.get(section, piName))
    else:
        # log warning event -> TCP PORT NOT FOUND FOR + \'piName\'
        return 'NULL'


# Returns the ip address of the raspberry pi by name
def getIpAddress(piName):
    section = 'Pi IP Addresses'
    if piName in parser.options(section):
        logEvent('SUCCESS', 'IP ADDRESS FOUND FOR \'' + piName + '\'', 'getIpAddress')
        return (parser.get(section, piName))
    else:
        logEvent('ERROR', 'IP ADDRESS NOT FOUND FOR \'' + piName + '\'', 'getIpAddress')
        return 'NULL'


# Returns the name of the pi from the ip address
def getPiName(ip):
    section = 'Pi IP Addresses'
    for piName in parser.options(section):
        # if name ip matches return name
        if ip == getIpAddress(piName):
            logEvent('SUCCESS', 'PI NAME FOUND FOR \'' + ip + '\'', 'getPiName')
            return piName

    logEvent('ERROR', 'PI NAME NOT FOUND FOR \'' + ip + '\'', 'getPiName')
    return 'NULL'


def tcpListener():
    client.listen(1)
    logEvent('SUCCESS', 'LISTENING FOR TCP CONNECTIONS...', 'tcpListener')

    while True:
        # waiting for a connection
        connection, client_address = client.accept()
        # if connection is created
        if connection:
            try:
                # try to get name from ip
                piName = getPiName(client_address)
                if piName != 'NULL':
                    logEvent('SUCCESS', 'CONNECTION ESTABLISHED FROM ' + piName + ' (' + client_address + ')',
                             'tcpListener')
                else:
                    logEvent('SUCCESS', 'CONNECTION ESTABLISHED FROM ' + client_address, 'tcpListener')

                while True:
                    data = connection.recv(16)
                    if data:
                        print(data)
                    else:
                        # send confirmation back
                        logEvent('SUCCESS', 'CONFIRMATION RESPONSE SENT', 'tcpListener')
                        break

            # close connection
            finally:
                logEvent('SUCCESS', 'CONNECTION CLOSED', 'tcpListener')
                connection.close()


# Attempts to send a message via tcp
def sendMessage(piName, messageType, message):
    ip = getIpAddress(piName)
    port = getTcpPort(piName)
    print(ip)
    # successfully got ip and port
    if ip != 'NULL' & port != 'NULL':
        # client.connect((ip, port))
        client.connect(('localhost', 10000))
        # log event
        try:
            # format message
            m = '<' + messageType + '>\n'
            m += message
            sock.sendall(m)

            # Look for the confirmation response
            amount_received = 0
            amount_expected = 8

            while amount_received < amount_expected:
                response = sock.recv(16)
                amount_received += len(response)
                logEvent('SUCCESS', 'WAITING FOR RESPONSE FROM \'' + piName + '\'...', 'sendMessage')

            if response == 'SUCCESS':
                logEvent('SUCCESS', 'MESSAGE SEND SUCCESSFULLY TO \'' + piName + '\'', 'sendMessage')
            elif response == 'FAILURE':
                logEvent('ERROR', 'MESSAGE FAILED TO SEND TO \'' + piName + '\'', 'sendMessage')
            else:
                logEvent('ERROR', 'RESPONSE FROM \'' + piName + '\' NOT RECOGNIZABLE', 'sendMessage')

        finally:
            logEvent('SUCCESS', 'CONNECTION WITH \'' + piName + '\' CLOSED', 'sendMessage()')
            client.close()


def init():
    con = (getIpAddress('central'), getTcpPort('central'))
    client.bind(con)

#
# client.bind(('localhost', 10000))
# tcpListener()
# sendMessage('central', 'TEST', 'this is a test message!')

print("test again")
