#!/usr/bin/env python

from thrd_party import pymumble
import alsaaudio
import argparse
__version__ = "0.0.2"

parser = argparse.ArgumentParser(description='Alsa input to mumble')
parser.add_argument("-H", "--host", dest="host", type=str, required=True,
                    help="A hostame of a mumble server")

parser.add_argument("-u", "--user", dest="user", type=str, required=True,
                    help="Username you wish")

parser.add_argument("-p", "--password", dest="password", type=str, default=None,
                    help="Password if server requires one")

parser.add_argument("-s", "--setperiodsize", dest="periodsize", type=int, default=256,
                    help="Lower values mean less delay. WARNING: Lower values could be unstable")

parser.add_argument("-b", "--bandwidth", dest="bandwidth", type=float, default=96000,
                    help="Bandwith of the bot (in bytes/s). Default value=96000")

args = parser.parse_args()

if args.password:
    abot = pymumble.Mumble(args.host, args.user, password=args.password)
else:
    abot = pymumble.Mumble(args.host, args.user)
abot.set_application_string("abot (%s)" % __version__)
abot.set_codec_profile("audio")
abot.set_bandwidth(args.bandwidth)
abot.start()
abot.is_ready()

a_in = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE)
a_in.setchannels(1)
a_in.setperiodsize(args.periodsize)
a_in.setrate(pymumble.constants.PYMUMBLE_SAMPLERATE)

while True:
    length, data = a_in.read()
    if not data:
        print("no data, exiting loop")
        break
    abot.sound_output.add_sound(data)


