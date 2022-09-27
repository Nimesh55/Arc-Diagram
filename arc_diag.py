import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import pandas as pd
from matplotlib.widgets import Cursor
import mplcursors

# Network data taken from this file
data_file = 'Data/data2.csv'

# previously clicked node details are stored in here
previously_selected_node = 0
previously_selected_arc = -1

# Properties in the window
graph_colour = "blue"
graph_selection_colour = "red"
graph_background_colour = "white"
clicked_line_color = "green"

# All the parameters required to the equations related to arcs are stored inside this
arc_equations = []

# Keeps record of weights for each node pairs used to make arcs
lines = {}


# Return required informations from file
def get_informations_from_file(file_name):
    df = pd.read_csv(file_name)
    num_of_rows, num_of_cols = df.shape
    node1, node2, weight = df.columns
    return num_of_rows, df[node1], df[node2], df[weight]


num_of_rows, sources, targets, weights = get_informations_from_file(data_file)


# Get nodes positions array
def get_nodes_positions(nodes_list):
    positions_of_nodes = {}
    x_pos = 0
    for node in nodes_list:
        positions_of_nodes[node] = x_pos
        x_pos += 1
    return positions_of_nodes


# Return sorted nodes list with positions array for given two nodes list
def get_sorted_list_of_nodes_with_positions(src_lst, tar_lst):
    nodes_list = src_lst.to_list()
    nodes_list.extend(tar_lst.to_list())
    nodes_list = list(set(nodes_list))
    nodes_list.sort()
    return nodes_list, get_nodes_positions(nodes_list)


nodes, positions_of_nodes = get_sorted_list_of_nodes_with_positions(sources, targets)
max_position = max(positions_of_nodes.values())


# Get weights for each line when there are duplicated node pairs in data
def get_lines_weights_for_duplicate_data(lines, sources, targets, weights):
    pairs = []
    for row in range(num_of_rows):
        if (sources[row], targets[row]) in pairs:
            lines[(sources[row], targets[row])] += weights[row]
        elif (targets[row], sources[row]) in pairs:
            lines[(targets[row], sources[row])] += weights[row]
        else:
            pairs.append((sources[row], targets[row]))
            lines[(sources[row], targets[row])] = weights[row]
    return lines


# Get weights for each line when there are no duplicated node pairs in data
def get_lines_weights_for_no_duplicate_data(lines, sources, targets, weights):
    for row in range(num_of_rows):
        lines[(sources[row], targets[row])] = weights[row]
    return lines


lines = get_lines_weights_for_no_duplicate_data(lines, sources, targets, weights)
nodes_count = len(nodes)

# Setup window
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(1, 1, 1)
ax.set_ylim(-5, nodes_count / 2 + 1)
ax.set_xlim(-1, nodes_count + 1)
fig.canvas.manager.set_window_title('Arc diagram')
ax.axis('off')

# Position the nodes in the graph
xs = [i for i in range(nodes_count)]
ys = [0] * nodes_count
points = ax.scatter(xs, ys, marker='o')

# Add annotation for cursor hovering events on nodes
cursor_for_points = mplcursors.cursor(points, hover=True)


@cursor_for_points.connect("add")
def on_add(sel):
    sel.annotation.set(text=nodes[sel.index])


# Add or change text related to node
def add_or_change_node_text(node_index, color, weight):
    node_index = int(node_index)
    label = nodes[node_index]

    ax.annotate(label,  # this is the text
                (node_index, 0),  # these are the coordinates to position the label
                textcoords="offset points",  # how to position the text
                xytext=(-4, -6),  # distance from text to points (x,y)
                rotation=90,
                va='top',
                fontsize=10,
                weight=weight,
                color=color,
                ha='left')  # horizontal alignment


# Draw arc
def draw_arc(src, des, color, id):
    x1 = positions_of_nodes[src]
    x2 = positions_of_nodes[des]
    arc = Arc(((x1 + x2) / 2, 0), abs(x2 - x1), abs(x2 - x1), 0, 0, 180, color=color,
              lw=lines[(src, des)] / max_position * 2, gid=id)
    ax.add_patch(arc)
    return (x1 + x2) / 2, abs(x1 - x2) / 2


# Check given cordinates on any arcs or not. If it is on the arc, return arc id
def check_point_on_arc_or_not(x_co, y_co):
    if y_co < 0:
        return -1
    for i in range(len(arc_equations)):
        h, r = arc_equations[i]
        value = y_co ** 2 + (x_co - h) ** 2
        line_half_width = 0.06 * weights[i] / max_position / 2
        if (r - line_half_width) ** 2 < value < (r + line_half_width) ** 2:
            return i
    return -1


# Change arc colour
def change_patch_color(n, color):
    ax.patches[n].set_color(color)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.show()


# change color of the lines that are starting or ending from given point
def change_line_colors_for_point(point, color):
    node_index = list(positions_of_nodes.values()).index(point)
    node_name = list(positions_of_nodes.keys())[node_index]

    index_lst = sources.index[sources == node_name].tolist()
    index_lst.extend(targets.index[targets == node_name].tolist())
    for index in index_lst:
        ax.patches[index].set_color(color)
        h, r = arc_equations[index]
        text_color = color
        weight = 'regular'
        if text_color == graph_colour:
            text_color = graph_background_colour
            weight = 'bold'
        ax.annotate(weights[index], (h, r), xytext=(0, 6), rotation=0, textcoords="offset points", fontsize=10,
                    ha='left', va='bottom', color=text_color, weight=weight)
    plt.show()


# When user click on a node, change line colors related to selected node.
def click_on_node(event):
    global previously_selected_node
    x1, y1 = event.xdata, event.ydata
    x_co = round(x1, 1)
    y_co = round(y1, 0)
    if int(y_co) == 0 and x_co.is_integer():
        # Change line colours
        change_line_colors_for_point(previously_selected_node, graph_colour)
        change_line_colors_for_point(x_co, graph_selection_colour)
        # Change points colours
        ax.scatter(previously_selected_node, 0, marker='o', color=graph_colour)
        ax.scatter(x_co, 0, marker='o', color=graph_selection_colour)
        # Change node text styles
        add_or_change_node_text(previously_selected_node, graph_background_colour, "bold")
        add_or_change_node_text(previously_selected_node, graph_colour, "regular")
        add_or_change_node_text(x_co, graph_background_colour, "regular")
        add_or_change_node_text(x_co, graph_selection_colour, "bold")

        previously_selected_node = x_co
    else:
        change_line_colors_for_point(previously_selected_node, graph_colour)
        add_or_change_node_text(previously_selected_node, graph_colour, "regular")
        add_or_change_node_text(previously_selected_node, graph_background_colour, "bold")
        add_or_change_node_text(previously_selected_node, graph_colour, "regular")
        ax.scatter(previously_selected_node, 0, marker='o', color=graph_colour)


# When user click on a point in arc
def click_on_arc(event):
    global previously_selected_arc
    x_coordinate, y_coordinate = event.xdata, event.ydata
    arc_id = check_point_on_arc_or_not(x_coordinate, y_coordinate)
    from_node = ""
    to_node = ""
    line_weight = 0
    if previously_selected_arc > 0:
        ax.patches[previously_selected_arc].set_color(graph_colour)
        previously_selected_arc = -1
    if arc_id >= 0:
        from_node = sources[arc_id]
        to_node = targets[arc_id]
        line_weight = weights[arc_id]
        ax.patches[arc_id].set_color(clicked_line_color)
        previously_selected_arc = arc_id

    # Clear the previously created box in the graph
    delete_textstr = "Nodes  :- {f_node} - {t_node}\nWeight :- {w}".format(
        f_node="Delete this text from node for next time",
        t_node="Delete this text from node for next time",
        w=line_weight)
    props_del = dict(boxstyle='square', facecolor='white', edgecolor='white', alpha=1, linewidth=2.0)
    ax.text(0.03, 0.95, delete_textstr, transform=ax.transAxes, fontsize=10, color='white',
            verticalalignment='top', bbox=props_del)

    # Create next details box according to the position clicked in the canvas
    textstr = "Nodes  :- {f_node} - {t_node}\nWeight :- {w}".format(f_node=from_node, t_node=to_node, w=line_weight)
    props = dict(boxstyle='round', facecolor='lightsteelblue', edgecolor='navy', alpha=0.5)
    ax.text(0.03, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)


# Cursor in window
cursor = Cursor(ax, horizOn=False, vertOn=False)

# Draw arcs according to the data in lines
gid = 0
for src, des in lines:
    h, r = draw_arc(src, des, graph_colour, gid)
    arc_equations.append((h, r))
    gid += 1

# Add names in nodes
for x_co in xs:
    add_or_change_node_text(x_co, 'blue', 'regular')

# Add events
fig.canvas.mpl_connect('button_press_event', click_on_node)
fig.canvas.mpl_connect('button_press_event', click_on_arc)

fig.tight_layout()

plt.show()
