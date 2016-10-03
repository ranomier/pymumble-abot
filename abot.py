#!/usr/bin/env python
"""
TITLE:  abot
AUTHOR: Ranomier (ranomier@fragomat.net)
DESC:   a simple bot that receives sound from a sound device (for me jack audio kit)
"""

import argparse
import sys

from thrd_party import pymumble
import pyaudio
__version__ = "0.0.3"


def main():
    """swallows parameter. TODO: move functionality away"""
    parser = argparse.ArgumentParser(description='Alsa input to mumble')
    parser.add_argument("-H", "--host", dest="host", type=str, required=True,
                        help="A hostame of a mumble server")

    parser.add_argument("-u", "--user", dest="user", type=str, required=True,
                        help="Username you wish, Default=abot")

    parser.add_argument("-p", "--password", dest="password", type=str, default=None,
                        help="Password if server requires one")

    parser.add_argument("-s", "--setperiodsize", dest="periodsize", type=int, default=256,
                        help="Lower values mean less delay. WARNING:Lower values could be unstable")

    parser.add_argument("-b", "--bandwidth", dest="bandwidth", type=int, default=96000,
                        help="Bandwith of the bot (in bytes/s). Default=96000")

    args = parser.parse_args()

    if args.password:
        abot = pymumble.Mumble(args.host, args.user, password=args.password)
    else:
        abot = pymumble.Mumble(args.host, args.user)
    abot.set_application_string("abot (%s)" % __version__)
    abot.set_codec_profile("audio")
    abot.start()
    abot.is_ready()
    abot.set_bandwidth(args.bandwidth)

    p_in = pyaudio.PyAudio()

    stream = p_in.open(input=True,
                       channels=1,
                       format=pyaudio.paInt16,
                       rate=pymumble.constants.PYMUMBLE_SAMPLERATE,
                       frames_per_buffer=args.periodsize)

    while True:
        data = stream.read(args.periodsize)
        if not data:
            print("no data, exiting loop")
            break
        abot.sound_output.add_sound(data)
    stream.close()
    return 0



if __name__ == "__main__":
    sys.exit(main())
