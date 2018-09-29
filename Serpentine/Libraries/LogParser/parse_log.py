import sys
import json

def read_binary(log_name):
    with open(log_name, 'rb') as f:
        bytes = f.read()
    bits = []
    for byte in bytes:
        bits.append(bin(byte)[2:].zfill(8))
    return bits

def parse(bits):
    MAP_WIDTH = int(bits[-2], 2)
    MAP_HEIGHT = int(bits[-1], 2)

    tile_count = 0
    turn_count = -1

    rterr, bterr, gterr, pterr = {}, {}, {}, {}
    rbody, bbody, gbody, pbody = {}, {}, {}, {}
    runit, bunit, gunit, punit = {}, {}, {}, {}

    for bit in bits[:-2]:
        if tile_count % (MAP_WIDTH * MAP_HEIGHT) == 0:
            tile_count = 0
            turn_count += 1
            rterr[turn_count] = []
            bterr[turn_count] = []
            gterr[turn_count] = []
            pterr[turn_count] = []
            rbody[turn_count] = []
            bbody[turn_count] = []
            gbody[turn_count] = []
            pbody[turn_count] = []
            runit[turn_count] = (-1, -1)
            bunit[turn_count] = (-1, -1)
            gunit[turn_count] = (-1, -1)
            punit[turn_count] = (-1, -1)

        magic_tuple = (tile_count // MAP_WIDTH, tile_count - MAP_WIDTH * (tile_count // MAP_WIDTH))

        if bit[5:] == '010':
            rterr[turn_count].append(magic_tuple)
        elif bit[5:] == '011':
            bterr[turn_count].append(magic_tuple)
        elif bit[5:] == '100':
            gterr[turn_count].append(magic_tuple)
        elif bit[5:] == '101':
            pterr[turn_count].append(magic_tuple)

        if bit[1:3] == '10':
            if bit[3:5] == '00':
                rbody[turn_count].append(magic_tuple)
            elif bit[3:5] == '01':
                bbody[turn_count].append(magic_tuple)
            elif bit[3:5] == '10':
                gbody[turn_count].append(magic_tuple)
            elif bit[3:5] == '11':
                pbody[turn_count].append(magic_tuple)

        elif bit[1:3] == '01':
            if bit[3:5] == '00':
                runit[turn_count] = magic_tuple
            elif bit[3:5] == '01':
                bunit[turn_count] = magic_tuple
            elif bit[3:5] == '10':
                gunit[turn_count] = magic_tuple
            elif bit[3:5] == '11':
                punit[turn_count] = magic_tuple

        tile_count += 1

    return {'red': {'terr': rterr, 'body': rbody, 'unit': runit},
            'blue': {'terr': bterr, 'body': bbody, 'unit': bunit},
            'green': {'terr': gterr, 'body': gbody, 'unit': gunit},
            'purple': {'terr': pterr, 'body': pbody, 'unit': punit}}


def bin_to_json(log_directory, target_directory):
     with open(target_directory, 'w') as f:
         f.write(json.dumps(parse(read_binary(log_directory))))

if __name__ == "__main__":
    bin_to_json(sys.argv[1], sys.argv[2])
    try:
        bin_to_json(sys.argv[1], sys.argv[2])
    except:
        if len(sys.argv) != 3:
            print('Invalid args: format = python parse_log.py log_directory target_directory')
        else:
            print('Invalid file name: check your file names')
