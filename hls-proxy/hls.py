import os
import sys
import subprocess

SERVER_HOSTNAME         = os.environ['SERVER_HOSTNAME']
STREAMER_HOSTNAME       = os.environ['STREAMER_HOSTNAME']
OUTPUT_DIRECTORY        = os.environ['OUTPUT_DIRECTORY']
SERVER_PATH             = os.environ['SERVER_PATH']
OUTPUT_INDEX_FILE_NAME  = os.environ['OUTPUT_INDEX_FILE_NAME']
OUTPUT_TS_FILE_PATTERN  = os.environ['OUTPUT_TS_FILE_PATTERN']
SEGMENT_LEN             = 12 # Seconds

SOUT_CONFIG_TEMPLATE = '\
#std {{\
    access = livehttp {{\
        seglen = {seg_len},\
        delsegs = true,\
        numsegs = 10,\
        index = {out_dir}/{idx_file},\
        index-url = http://{host_name}/{host_path}/{ts_pattern}\
    }},\
    mux = ts{{\
        use-key-frames\
    }},\
    dst = {out_dir}/{ts_pattern}\
}}'

def sout_config(local_path, server_path):
    raw = SOUT_CONFIG_TEMPLATE.format(
        seg_len=SEGMENT_LEN,
        out_dir=local_path,
        idx_file=OUTPUT_INDEX_FILE_NAME,
        host_name=SERVER_HOSTNAME,
        host_path=server_path,
        ts_pattern=OUTPUT_TS_FILE_PATTERN
    )
    # Removing whitespaces because of VLC's weird parsing rules
    return ''.join(raw.split())

VLC_COMMAND = lambda port, local_path, server_path: [
    'vlc',
    '-I', 'dummy',
    '--play-and-exit',
    '--live-caching', '300',
    'http://{}:{}'.format(STREAMER_HOSTNAME, port),
    '--sout', sout_config(local_path, server_path)
]

class Proxy:

    def __init__(self, port):
        self.process = None
        self.port = port

    def start(self):
        subdir = '{}'.format(self.port)
        local_path = os.path.join(OUTPUT_DIRECTORY, subdir)
        server_path = os.path.join(SERVER_PATH, subdir)

        if not os.path.exists(local_path):
            os.makedirs(local_path)

        command = VLC_COMMAND(
            self.port,
            local_path,
            server_path
        )

        self.process = subprocess.Popen(
            command,
            stdout=sys.stderr.fileno(),
            stderr=subprocess.PIPE,
        )

    def alive(self):
        if self.process is None:
            return False
        return self.process.poll() is None

    def to_json(self):
        return {
            'port': self.port
        }

    def __del__(self):
        if self.alive():
            self.process.kill()

    def __hash__(self):
        return hash(self.port)

    def __eq__(self, other):
        return self.port == other.port

    def __ne__(self, other):
        return not self.__eq__(other)
