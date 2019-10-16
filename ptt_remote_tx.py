#!/usr/bin/env python3
#
# Python PTT remote (TX) by barf <stuart@macintosh>
#

import os
import sys
stdout_parking = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = stdout_parking
import time
import zmq
import pickle
import argparse

DEBUG = False
if DEBUG: from IPython import embed

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Push-to-talk remote control by barf <stuart@macintosh.nz>')
    parser.add_argument('HOST', help='FQDN or IP address of PTT remote RX host')
    parser.add_argument('PORT', help='port number of PTT remote RX host')

    args = parser.parse_args()
    host_ip = args.HOST
    host_port = args.PORT

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.sndhwm = 8
    print("Connecting…")
    socket.connect("tcp://%s:%s" % (host_ip, host_port))
    print("Connected")

    pygame.init()
    clock = pygame.time.Clock()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for stick in joysticks:
        stick.init()

    done = False
    while not done:
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
           
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print('type: %s\tdict: %s' % (event.type, event.dict))
                if DEBUG: embed()
                socket.send(pickle.dumps([event.type, event.dict, time.time()]))
            if event.type == pygame.JOYBUTTONUP:
                print('type: %s\tdict: %s' % (event.type, event.dict))
                if DEBUG: embed()
                socket.send(pickle.dumps([event.type, event.dict, time.time()]))

            if DEBUG: print('type: %s\tdict: %s' % (event.type, event.dict))

        # time.sleep(10)
        clock.tick(30)

    # if DEBUG: embed()
    pygame.quit()
