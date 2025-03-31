import numpy as np
import matplotlib.pyplot as plt
from scipy.special import sici

T = 2.0 * 1e-3
w_g = 240 * 1e6 * 2 * np.pi
w_f = w_g + (1/2*T) * 2 * np.pi
SPEED_OF_LIGHT = 3e8


def calc_velocity_from_homo_hetero(heterodyne, homodyne):
    ratio = np.divide(heterodyne, homodyne, out=np.zeros_like(homodyne), where=homodyne != 0)
    ratio = np.clip(ratio, -1, 0.999)
    delta_w = ratio * (1 / T) / (ratio - 1)
    speed_of_light = 3e8

    velocity_map = 0.5 * delta_w * speed_of_light / w_g * 2 * np.pi
    velocity_map = np.clip(velocity_map, -30, 30)
    return velocity_map


def lerp(a, b, f):
    return a * (1-f) + b * f


def integrate_cos_analytic(v, l, homogeneous=True, order=0):
    phi = w_g * 2 * l / SPEED_OF_LIGHT
    w_delta = - 2 * (w_g / SPEED_OF_LIGHT) * v

    if homogeneous:
        a = (w_g - w_g - w_delta)
    else:
        print(w_f, w_g, w_delta)
        a = (w_f - w_g - w_delta)
    b = v / l

    def F(t):
        sin_value = np.sin(a * t + phi)
        cos_value = np.cos(a * t + phi)

        if order == 0 or b == 0:
            A = sin_value / a
            return A
        elif order == 1:
            A = sin_value / a
            A -= 2 * b * (a * t * sin_value + cos_value) / (a * a)
            return A
        elif order == 2:
            A = sin_value / a
            A -= 2 * b * (a * t * sin_value + cos_value) / (a * a)
            A += 3 * b * b * ((a*a*t*t-2) * sin_value + 2 * a * t * cos_value) / (a * a * a)
            return A
        else:
            si, ci = sici(a * (t + 1 / b))
            nominator = a * ci * np.sin(a / b - phi) - a * si * np.cos(a / b - phi) \
                        - b * np.cos(a * t + phi) / (b * t + 1)
            return nominator / (b * b)

    return (F(T) - F(0))


def plot_integrated_value_over_v():
    N = 200
    max_v = 2000
    xs = []
    result = {}
    l = 10

    for i in range(-N, N, 1):
        x = (i + 0.5) / N
        v = max_v * x #lerp(min_v, max_v, x)
        xs.append(v)
        heteros = [True, False]
        orders = [-1, 0, 1, 2]
        for hetero in heteros:
            for order in orders:
                hetero_name = "hetero" if hetero else "homo"
                order_name = "%d" % order
                name = "%s_%s" % (hetero_name, order_name)
                if name not in result:
                    result[name] = []
                y = integrate_cos_analytic(v, l, order=order, homogeneous=not hetero)
                result[name].append(y)

    for k, v in result.items():
        result[k] = np.asarray(v)


    # for order in [-1,0,1,2]:
    #     ratio = result["hetero_%d" % order] / result["homo_%d" % order]
    #     delta_w = ratio * (1 / T) / (ratio - 1)
    #     velocity = 0.5 * delta_w * SPEED_OF_LIGHT / w_g
    #     plt.plot(xs, velocity, label="%s" % order)

    plt.figure()
    plt.plot(xs, result["hetero_0"], label="0")
    plt.plot(xs, result["hetero_1"], label="1")
    plt.plot(xs, result["hetero_2"], label="2")
    plt.plot(xs, result["hetero_-1"], label="full")
    plt.legend()

    plt.figure()
    plt.plot(xs, result["hetero_0"] - result["hetero_-1"], label="0")
    plt.plot(xs, result["hetero_1"] - result["hetero_-1"], label="1")
    plt.plot(xs, result["hetero_2"] - result["hetero_-1"], label="2")
    plt.legend()

    plt.figure()
    plt.plot(xs, result["homo_0"], label="0")
    plt.plot(xs, result["homo_1"], label="1")
    plt.plot(xs, result["homo_2"], label="2")
    plt.plot(xs, result["homo_-1"], label="full")
    plt.legend()

    plt.figure()
    plt.plot(xs, result["homo_0"] - result["homo_-1"], label="0")
    plt.plot(xs, result["homo_1"] - result["homo_-1"], label="1")
    plt.plot(xs, result["homo_2"] - result["homo_-1"], label="2")
    plt.legend()

    plt.show()

def hide_labels():
    ax = plt.gca()
    ax.xaxis.set_ticklabels([], minor=True)
    ax.yaxis.set_ticklabels([], minor=True)
    ax.xaxis.set_ticklabels([], minor=False)
    ax.yaxis.set_ticklabels([], minor=False)

def plot_integrated_value_over_l():
    N = 200
    max_l = 10
    xs = []
    result = {}
    v = 10

    for i in range(1, N):
        x = (i + 0.5) / N
        l = max_l * x #lerp(min_v, max_v, x)
        xs.append(l)
        heteros = [True, False]
        orders = [-1, 0, 1, 2]
        for hetero in heteros:
            for order in orders:
                hetero_name = "hetero" if hetero else "homo"
                order_name = "%d" % order
                name = "%s_%s" % (hetero_name, order_name)
                if name not in result:
                    result[name] = []
                y = integrate_cos_analytic(v, l, order=order, homogeneous=not hetero)
                result[name].append(y)

    for k, v in result.items():
        result[k] = np.asarray(v)

    # for order in [-1,0,1,2]:
    #     ratio = result["hetero_%d" % order] / result["homo_%d" % order]
    #     delta_w = ratio * (1 / T) / (ratio - 1)
    #     velocity = 0.5 * delta_w * SPEED_OF_LIGHT / w_g
    #     plt.plot(xs, velocity, label="%s" % order)

    plt.figure()
    plt.plot(xs, result["hetero_0"], label="0")
    plt.plot(xs, result["hetero_1"], label="1")
    plt.plot(xs, result["hetero_2"], label="2")
    plt.plot(xs, result["hetero_-1"], label="full")
    hide_labels()
    plt.tight_layout()
    plt.savefig("hetero_over_l.svg", dpi=1200, bbox_inches="tight")

    # plt.legend()

    plt.figure()
    plt.plot(xs, result["hetero_0"] - result["hetero_-1"], label="0")
    plt.plot(xs, result["hetero_1"] - result["hetero_-1"], label="1")
    plt.plot(xs, result["hetero_2"] - result["hetero_-1"], label="2")
    hide_labels()
    plt.tight_layout()
    plt.savefig("hetero_diff_over_l.svg", dpi=1200, bbox_inches="tight")

    # plt.legend()

    plt.figure()
    plt.plot(xs, result["homo_0"], label="0")
    plt.plot(xs, result["homo_1"], label="1")
    plt.plot(xs, result["homo_2"], label="2")
    plt.plot(xs, result["homo_-1"], label="full")
    hide_labels()
    plt.tight_layout()
    plt.savefig("homo_over_l.svg", dpi=1200, bbox_inches="tight")
    # plt.legend()

    plt.figure()
    plt.plot(xs, result["homo_0"] - result["homo_-1"], label="0")
    plt.plot(xs, result["homo_1"] - result["homo_-1"], label="1")
    plt.plot(xs, result["homo_2"] - result["homo_-1"], label="2")

    hide_labels()
    plt.tight_layout()
    plt.savefig("homo_diff_over_l.svg", dpi=1200, bbox_inches="tight")

    # plt.legend()

    # plt.show()

    plt.figure()
    plt.plot(xs, calc_velocity_from_homo_hetero(result["hetero_0"] , result["homo_0"]), label="0")
    plt.plot(xs, calc_velocity_from_homo_hetero(result["hetero_1"] , result["homo_1"]), label="1")
    plt.plot(xs, calc_velocity_from_homo_hetero(result["hetero_2"] , result["homo_2"]), label="2")
    plt.plot(xs, calc_velocity_from_homo_hetero(result["hetero_-1"] , result["homo_-1"]), label="full")

    # hide_labels()
    plt.tight_layout()
    plt.savefig("velocity.svg", dpi=1200, bbox_inches="tight")


    # plt.legend()

    plt.show()

if __name__ == "__main__":
    plot_integrated_value_over_l()