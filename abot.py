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
import collections
#from pprint import pprint
#import warnings

from thrd_party import pymumble
import pyaudio
__version__ = "0.0.4"

class Runner(collections.UserDict):
    """ TODO """
    def __init__(self, run_dict, args_dict=None):
        self.is_ready = False
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
                self[name]["args"] = None
                self[name]["kwargs"] = None


    def run(self):
        """ TODO """
        for name, cdict in self.items():
            print("[run] generating process for:", name)
            self[name]["process"] = Thread(name=name,
                                           target=cdict["func"],
                                           args=cdict["args"],
                                           kwargs=cdict["kwargs"])
            print("[run] starting process for:", name)
            self[name]["process"].start()
            print("[run] ", name, "started")
        print("[run] all done")
        self.is_ready = True

    def status(self):
        """ TODO """
        if self.is_ready:
            result = []
            for meta in self.keys():
                ntuple = collections.namedtuple("thread_info", ("name", "alive"))
                result.append(ntuple(meta["process"].name, meta["process"].is_alive()))
            return result
        else:
            return list()

    def stop(name=""):
        raise NotImplementedError("Sorry")


class MumbleRunner(Runner):
    def __init__(self, mumble_object, args_dict):
        self.mumble = mumble_object
        super().__init__(self._config(), args_dict)

    def _config(self):
        raise NotImplementedError("please inherit and implement")

class BaseAudio(MumbleRunner):
    """Configures a MumbleRunner. Input only. Via pyaudio"""
    def _config(self):
        return {"input": {"func": self.__input_loop, "process": None},
                "output": {"func": self.__output_loop, "process": None}}

    def __output_loop(self):
        raise NotImplementedError("please inherit and implement")
    def __input_loop(self):
        raise NotImplementedError("please inherit and implement")

class Audio(BaseAudio):
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
            self.mumble.sound_output.add_sound(data)
        stream.close()
        return True

    def input_vol(self, dbint):
        self.run_dict = None

class AudioPipe(BaseAudio):
    def __output_loop(self, periodsize):
        return None

    def __input_loop(self, periodsize, path):
        while True:
            with open(path) as fifo_fd:
                while True:
                    data = fifo_fd.read(periodsize)
                    self.mumble.sound_output.add_sound(data)


class Parser(MumbleRunner):
    pass

def prepare_mumble(host, user, password="", certfile=None,
                   codec_profile="audio", bandwidth=96000, channel=None):
    """Will configure the pymumble object and return it"""

    abot = pymumble.Mumble(host, user, certfile=certfile, password=password)

    abot.set_application_string("abot (%s)" % __version__)
    abot.set_codec_profile(codec_profile)
    abot.start()
    abot.is_ready()
    abot.set_bandwidth(bandwidth)
    if channel:
        try:
            abot.channels.find_by_name(channel).move_in()
        except pymumble.channels.UnknownChannelError:
            print("Tried to connect to channel:", "'" + channel + "'. ", "Got this Error:")
            print("Available Channels:")
            print(abot.channels)
            sys.exit(1)
    return abot


def main(preserve_thread=True):
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
                        help="Channel name as string")

    parser.add_argument("-f", "--fifo", dest="fifo_path", type=str, default=None,
                        help="Read from FIFO (EXPERMENTAL)")

    args = parser.parse_args()


    abot = prepare_mumble(args.host, args.user, args.password, args.certfile,
                          "audio", args.bandwidth, args.channel)
    if args.fifo_path:
        audio = AudioPipe(abot, {"output": {"args": (args.periodsize, ),
                                            "kwargs": None},
                                 "input": {"args": (args.periodsize, args.fifo_path),
                                           "kwargs": None}
                                }
                         )
    else:
        audio = Audio(abot, {"output": {"args": (args.periodsize, ),
                                        "kwargs": None},
                             "input": {"args": (args.periodsize, ),
                                       "kwargs": None}
                            }
                     )
    if preserve_thread:
        while True:
            print(audio.status())
            sleep(10)

if __name__ == "__main__":
    sys.exit(main())
