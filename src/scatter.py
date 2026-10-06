import sys

import matplotlib.pyplot as plt

plt.switch_backend('Agg')

data_file = sys.argv[1]
out_file = sys.argv[2]
title = sys.argv[3]
x_label = sys.argv[4]
y_label = sys.argv[5]

x_values = []
y_values = []
with open(data_file) as source:
    for line in source:
        values = line.split()
        x_values.append(float(values[0]))
        y_values.append(float(values[1]))

fig, ax = plt.subplots()
ax.scatter(x_values, y_values)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.set_title(title)

plt.savefig(out_file, bbox_inches='tight')
