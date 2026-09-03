import string
import math

class MyFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        if 'm' in format_spec:
            my_format_spec = format_spec.replace('m', 'e')
            return super().format_field(value, my_format_spec).replace('e', 'E').replace('+0', '').replace('-0', '-').replace('+', '')
        else:
            return super().format_field(value, format_spec)

def to_atp_format(resistance, n_chars=6):
    fmt = MyFormatter()

    flag = math.floor(math.log10(resistance))
    # print(flag)

    if flag > 9:
        r = fmt.format('{:2.1m}', resistance)

    if flag in {5, 6, 7, 8, 9}:
        r = fmt.format('{:2.2m}', resistance)

    elif flag in {4}:
        r = '{:6.0f}.'.format(resistance)

    elif flag in {3}:
        r = '{:5.1f}'.format(resistance)

    elif flag in {2}:
        r = '{:5.2f}'.format(resistance)

    elif flag in {1}:
        r = '{:5.3f}'.format(resistance)

    elif flag in {0}:
        r = '{:5.4f}'.format(resistance)

    elif flag in {-1, -2, -3, -4, -5}:
        z1 = '{:5.5f}'.format(resistance)
        r = z1[1:].rstrip("0")

    elif flag in {-6, -7, -8, -9}:
        r = fmt.format('{:2.1m}', resistance)

    elif flag < -9:
        r = fmt.format('{:2.0m}', resistance)

    return r.rjust(n_chars)

    # tower_R = float(input('Insert R: '))
    # # new_resistance = to_atp_format(tower_R, 2, 6)
    # #
    # new_resistance = '{:2.1E}'.format(tower_R)
