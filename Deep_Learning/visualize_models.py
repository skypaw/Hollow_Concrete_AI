import ezdxf
from ezdxf.addons import odafc
from numpy import linspace
import numpy as np


def draw(doc, i, a, h, as1, a1, r, l, base_x, base_y):
    a, h, as1, a1, r, l = a * 100, h * 100, as1 * 100 ** 2, a1 * 100, r * 100, l * 100

    # print(a, h, as1, a1, r, l)

    as_r = (as1 / (2 * np.pi)) ** 0.5

    msp = doc.modelspace()

    msp.add_text(f'{int(i)}').set_pos((base_x - a, base_y))

    points_rectangle = [(base_x, base_y), (base_x, base_y + h), (base_x + a, base_y + h), (base_x + a, base_y),
                        (base_x, base_y)]
    points_circle = [(base_x + a / 2, base_y + h / 2), r]
    points_reinforcement = [(base_x + a1, base_y + a1), as_r]
    points_reinforcement_2nd = [(base_x + a - a1, base_y + a1), as_r]

    msp.add_lwpolyline(points_rectangle)

    msp.add_circle(points_reinforcement[0], points_reinforcement[1])
    msp.add_circle(points_reinforcement_2nd[0], points_reinforcement_2nd[1])

    msp.add_radius_dim(center=(base_x + a1, base_y + a1), radius=round(as_r, 2), angle=360 - 45, dimstyle='EZ_RADIUS',
                       override={'dimtoh': 1}).render()

    msp.add_linear_dim(base=(base_x + a / 2, base_y - 2), p1=(base_x, base_y), p2=(base_x + a, base_y),
                       angle=0).render()
    msp.add_linear_dim(base=(base_x + a + 2, base_y + h / 2), p1=(base_x + a, base_y),
                       p2=(base_x + a, base_y + h), angle=90).render()

    if l == 0:
        msp.add_circle(points_circle[0], points_circle[1])
        msp.add_radius_dim(center=(base_x + a / 2, base_y + h / 2), radius=round(r, 2), angle=45, dimstyle='EZ_RADIUS',
                           override={'dimtoh': 1}).render()
    else:

        msp.add_arc(center=(base_x + a / 2, base_y + h / 2 + l / 2), radius=round(r, 2), start_angle=360, end_angle=180)
        msp.add_arc(center=(base_x + a / 2, base_y + h / 2 - l / 2), radius=round(r, 2), start_angle=180, end_angle=360)

        msp.add_lwpolyline(
            [(base_x + a / 2 - r, base_y + h / 2 - l / 2), (base_x + a / 2 - r, base_y + h / 2 + l / 2)])
        msp.add_lwpolyline(
            [(base_x + a / 2 + r, base_y + h / 2 - l / 2), (base_x + a / 2 + r, base_y + h / 2 + l / 2)])

        msp.add_linear_dim(base=(base_x + a / 2 - r + 2, base_y + h / 2),
                           p1=(base_x + a / 2 - r, base_y + h / 2 - l / 2),
                           p2=(base_x + a / 2 - r, base_y + h / 2 + l / 2), angle=90).render()

        msp.add_radius_dim(center=(base_x + a / 2, base_y + h / 2 + l / 2), radius=round(r, 2), angle=45,
                           dimstyle='EZ_RADIUS',
                           override={'dimtoh': 1}).render()


def visualize_models():
    dimensions_csv = np.genfromtxt("/full_data.csv",
                                   delimiter=",")

    max_a = max(dimensions_csv[:, 1]) * 100 * 2
    max_h = max(dimensions_csv[:, 2]) * 100 * 2

    models = len(dimensions_csv)
    rows = int(np.ceil(models ** 0.5))

    print(max_a, max_h, models, rows, rows ** 2)

    draw_iterator = 0

    base_x = 0
    base_y = 0

    doc = ezdxf.new('R2010')
    try:
        for i in range(rows):
            for j in range(rows * 2):
                if draw_iterator + 1 in dimensions_csv[:, 0]:
                    draw(doc, dimensions_csv[draw_iterator, 0], dimensions_csv[draw_iterator, 1],
                         dimensions_csv[draw_iterator, 2],
                         dimensions_csv[draw_iterator, 3], dimensions_csv[draw_iterator, 4],
                         dimensions_csv[draw_iterator, 5],
                         dimensions_csv[draw_iterator, 6], base_x, base_y)
                else:
                    break

                base_x += max_a
                if j == rows * 2 - 1:
                    base_x = 0

                print(draw_iterator)
                draw_iterator += 1

            base_y += max_h

        doc.saveas('models_visualization.dxf')
    except:
        print("daasdf")
    finally:
        doc.saveas('models_visualization.dxf')


if __name__ == '__main__':
    # draw(1, 0.1, 0.15, 2.3e-4, 0.02, 0.03, 0.05, 50, 50)
    visualize_models()
    # convert()
