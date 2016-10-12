#!/usr/bin/env python
"""
TITLE:  abot
AUTHOR: Ranomier (ranomier@fragomat.net)
DESC:   a simple bot that receives sound from a sound device (for me jack audio kit)
"""

import argparse
import sys
from threading import Thread
from time import sleep
from collections import UserDict
from pprint import pprint
import warnings

from thrd_party import pymumble
import pyaudio
__version__ = "0.0.4"

class Runner(UserDict):
    """ TODO """
    def __init__(self, run_dict, args_dict=None):
        super().__init__(run_dict)
        self.change_args(args_dict)
        self.run()

    def change_args(self, args_dict):
        """ TODO """
        for name in self.keys():
            if name in args_dict:
                self[name]["args"] = args_dict[name]["args"]
                self[name]["kwargs"] = args_dict[name]["kwargs"]
            else:
                self[name] = ()


    def run(self):
        """ TODO """
        for name, cdict in self.items():
            print("generating process for:", name)
            self[name]["process"] = Thread(target=cdict["func"],
                                           args=cdict["args"],
                                           kwargs=cdict["kwargs"])
            print("starting process for:", name)
            self[name]["process"].start()


class MumbleRunner(Runner):
    def __init__(self, mumble_object, args_dict):
        self.mumble = mumble_object
        super().__init__(self._config(), args_dict)

    def _config(self):
        raise NotImplementedError("please inherit and implement")



class Audio(MumbleRunner):
    """ TODO """
    def _config(self): 
        return {"input": {"func": self.__input_loop, "process": None},
                "output": {"func": self.__output_loop, "process": None}}

    def calculate_volume(self, thread_name):
        try:
            db = self[thread_name]["db"]
            self["vol_vector"] = 10 ** (db/20)
        except KeyError:
            self["vol_vector"] = 1


    def __output_loop(self, periodsize):
        """ TODO """
        return None

    def __input_loop(self, periodsize):
        """ TODO """
        p_in = pyaudio.PyAudio()
        stream = p_in.open(input=True,
                           channels=1,
                           format=pyaudio.paInt16,
                           rate=pymumble.constants.PYMUMBLE_SAMPLERATE,
                           frames_per_buffer=periodsize)
        while True:
            data = stream.read(periodsize)
            if not data:
                print("no data, exiting loop")
                break
            self.mumble.sound_output.add_sound(data)
        stream.close()
        return True

    def input_vol(self, dbint):
        self.run_dict = None



def main():
    """swallows parameter. TODO: move functionality away"""
    parser = argparse.ArgumentParser(description='Alsa input to mumble')
    parser.add_argument("-H", "--host", dest="host", type=str, required=True,
                        help="A hostame of a mumble server")

    parser.add_argument("-u", "--user", dest="user", type=str, required=True,
                        help="Username you wish, Default=abot")

    parser.add_argument("-p", "--password", dest="password", type=str, default="",
                        help="Password if server requires one")

    parser.add_argument("-s", "--setperiodsize", dest="periodsize", type=int, default=256,
                        help="Lower values mean less delay. WARNING:Lower values could be unstable")

    parser.add_argument("-b", "--bandwidth", dest="bandwidth", type=int, default=96000,
                        help="Bandwith of the bot (in bytes/s). Default=96000")

    parser.add_argument("-c", "--certificate", dest="certfile", type=str, default=None,
                        help="Path to an optional openssl certificate file")

    parser.add_argument("-C", "--channel", dest="channel", type=str, default=None,
                        help="channel name as string")

    args = parser.parse_args()

    abot = pymumble.Mumble(args.host, args.user, certfile=args.certfile, password=args.password)

    abot.set_application_string("abot (%s)" % __version__)
    abot.set_codec_profile("audio")
    abot.start()
    abot.is_ready()
    abot.set_bandwidth(args.bandwidth)
    try:
        abot.channels.find_by_name(args.channel).move_in()
    except pymumble.channels.UnknownChannelError as err:
        print("Tried to connect to channel:", args.channel, ". Got this Error:")
        print(str(err))


    audio = Audio(abot, {"output": {"args": (args.periodsize, ),
                                    "kwargs": None},
                         "input": {"args": (args.periodsize, ),
                                   "kwargs": None}
                        }
                 )
    while True:
        pprint(audio)
        sleep(100)

    #stream = p_in.open(input=True,
    #                   channels=1,
    #                   format=pyaudio.paInt16,
    #                   rate=pymumble.constants.PYMUMBLE_SAMPLERATE,
    #                   frames_per_buffer=args.periodsize)




if __name__ == "__main__":
    sys.exit(main())
