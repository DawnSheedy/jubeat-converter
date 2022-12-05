import resources.adpcmwave as adpcmwave
import numpy
import struct
import resources.wavfile as wavfile


import resources.helper as helper

helper.check_ffmpeg()

def parse_bin(input_filename, output_filename):
    with open(input_filename,"rb") as f:
        data = f.read()

    if data[0:4].decode('ascii') != "BMP\0":
        print("Not a BMP audio file")
        exit(1)

    data_size, loop_start, loop_end = struct.unpack(">III", data[0x04:0x10])
    channels, bits = struct.unpack("<HH", data[0x10:0x14])
    rate, = struct.unpack(">I", data[0x14:0x18])

    is_looped = True if loop_start > 0 or loop_end > 0 else False

    if is_looped:
        loops = [(loop_start, loop_end)]
        print("Found loop offsets: start = %d, end = %d" % (loop_start, loop_end))

        # foobar2000 plugin (rename .wav to .wavloop): http://slemanique.com/software/foo_input_wave_loop.html
        print("Loop information will be stored in a SMPL chunk for playback in players that have support for SMPL loops")
    else:
        loops = None

    data = bytearray(data[0x20:])
    output = adpcmwave.decode_data(data, rate, channels, bits)
    output = numpy.ndarray((int(len(output) // 2 // channels), channels), numpy.int16, output, 0)
    wavfile.write(output_filename, rate, output, loops=loops)
