import re
import numpy as np
import random


def get_coordinates(pl_file_name, node_name):
    """
	@gk
	This function takes as input a pl-file's name and a node's name
	and returns an int-type list of the coordinates.
	list's form : [x-coordinate, y-coordinate]
	:param pl_file_name:
	:param node_name:
	:return:
	"""
    coordinates = []
    with open(pl_file_name) as f:
        for num, line in enumerate(f):
            if node_name in line:
                data = line.split()
                if node_name == data[0]:
                    coordinates.append(float(data[1]))
                    coordinates.append(float(data[2]))
                    break
    return coordinates


def get_non_terminal_nodes_list(file_name):
    """
	@gt
	this function takes in as a parameter a .nodes file,
	after checking if the line contains node information
	it checks if the node of that line is characterized as a terminal one
	and if it is not, it appends it in a list
	:param file_name: str
	:return non_terminal_list: list[str, str,..., str]
	"""
    non_terminal_list = []
    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    node_info = line.split()
                    if len(node_info) == 3:
                        non_terminal_list.append(node_info[0])

    return non_terminal_list


def get_coordinates_net(net_file, net_name):
    """
	@gk
	This function takes as input a .nets file's name and the name of a net
	and returns a dictionary of nodes and their coordinates
	dictionary's form: {'node's name': ['x','y'], ...}
	:param net_file: str
	:param net_name: str
	:return net: dict{'str': ['str','str']}
	"""
    pl_file = net_file.replace('.nets', '.pl')
    net = {}
    net_name_number = int(net_name.replace('n', ''))
    nodes_in_net_num = 0
    node_names = []
    data = []
    pos = 0
    counter = -1
    with open(net_file) as nf:
        for num, line in enumerate(nf, 0):
            if "NetDegree" in line:
                counter += 1
                if counter == net_name_number:
                    pos = num
                    data = line.split()
                    nodes_in_net_num = data[2]

    with open(net_file) as nf:
        for num, line in enumerate(nf, 0):
            if pos < num <= pos + int(nodes_in_net_num):
                data = line.split()
                node_names.append(data[0])

    data.clear()
    with open(pl_file) as p:
        for num, line in enumerate(p):
            if num == 0 or '#' in line or line == '\n':
                continue
            else:
                data.append(line.split())

    for i in node_names:
        for j in data:
            if i == j[0]:
                net[i] = [j[1]]
                net[i].append(j[2])

    return net


def return_nets_for_node(file_name, search_node):
    """
	@gt
	this function takes in as a parameter the name of the benchmark the user
	wants to search and a node
	returns all nets the node is part of
	:param file_name: str
	:param search_node: str
	:return nets_in: list[str, str,..., str]
	"""

    nets = {}
    counter = 0
    nets_in = []

    with open(file_name + ".nets") as f:
        num_of_nodes = -1
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if "NetDegree" in line:
                    num_of_nodes = int(line.split()[2])
                    net_name = "n" + str(counter)
                    counter += 1
                    nets[net_name] = []
                elif re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    num_of_nodes -= 1
                    nets[net_name].append(line.split()[0])
            if num_of_nodes == 0:
                if search_node not in nets[net_name]:
                    del nets[net_name]
                else:
                    nets_in.append(net_name)

    return nets_in


def place_node(file_name, node, new_x, new_y):
    """
	@gt
	this function takes in as a parameter a benchmark and a list of nodes
	places these nodes in a random position inside the chip
	does same function to every node if "all" is given instead of a list
	:param file_name: str
	:param node_list: list[str, str,......, str]/"all"
	:return
	"""

    place = {}
    rows = {}
    counter = 0

    with open(file_name + ".scl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if line.split()[0] == "Coordinate":
                    starting_height = int(line.split()[2])
                    if starting_height not in rows.keys():
                        rows[starting_height] = []
                if line.split()[0] == "Height":
                    height = int(line.split()[2])
                if line.split()[0] == "Sitespacing":
                    sitespacing = line.split()[2]
                if line.split()[0] == "SubrowOrigin":
                    starting_x = int(line.split()[2])
                    ending_x = int(starting_x) + int(sitespacing) * int(line.split()[5])
                    rows[starting_height].append(starting_x)
                    rows[starting_height].append(ending_x)

    key_list = []
    for key in rows:
        key_list.append(key)
    key_list.sort()

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if line.split()[0] == node:
                    to_change = line
                    place[line.split()[0]] = [line.split()[1], line.split()[2]]

    with open(file_name + ".pl") as f:
        data = f.readlines()

        substring = to_change.split()[1]
        substring = substring.replace(to_change.split()[1], str(new_x), 1)
        to_change = to_change.replace(to_change.split()[1], substring, 1)

        substring = to_change.split()[2]
        substring = substring.replace(to_change.split()[2], str(new_y), 1)
        to_change = to_change.replace(to_change.split()[2], substring, 1)

    for i in range(len(data)):

        if re.search(r'\b' + to_change.split()[0] + r'\b', data[i]):
            data[i] = to_change + "\n"

    with open(file_name + ".pl", 'w') as p:
        p.writelines(data)


def total_hpwl(file_name):
    """
	@gt
	this function takes in as a parameter a benchmark
	returns hpwl
	:param file_name: str
	:return hpwl: int
	"""

    nodes = {}
    netsx = {}
    netsy = {}
    counter = 0
    hpwl = 0

    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if line.split()[0] not in nodes:
                        nodes[line.split()[0]] = []
                        nodes[line.split()[0]].append(line.split()[1])
                        nodes[line.split()[0]].append(line.split()[2])

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    nodes[line.split()[0]].append(line.split()[1])
                    nodes[line.split()[0]].append(line.split()[2])

    with open(file_name + ".nets") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if "NetDegree" in line:
                    num_of_nodes = int(line.split()[2])
                    net_name = "n" + str(counter)
                    counter += 1
                    netsx[net_name] = []
                    netsy[net_name] = []
                elif re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if net_name in netsx:
                        if len(netsx[net_name]) == 0:
                            netsx[net_name].append(int(nodes[line.split()[0]][2]))
                            netsx[net_name].append(int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]))

                            netsy[net_name].append(int(nodes[line.split()[0]][3]))
                            netsy[net_name].append(int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]))
                        else:
                            if int(nodes[line.split()[0]][2]) < netsx[net_name][0]:
                                netsx[net_name][0] = int(nodes[line.split()[0]][2])

                            if int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]) > netsx[net_name][1]:
                                netsx[net_name][1] = int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0])

                            if int(nodes[line.split()[0]][3]) < netsy[net_name][0]:
                                netsy[net_name][0] = int(nodes[line.split()[0]][3])

                            if int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]) > netsy[net_name][1]:
                                netsy[net_name][1] = int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1])

    for net in netsx:
        hpwl += float(netsx[net][1] - netsx[net][0] + netsy[net][1] - netsy[net][0])

    return (hpwl)


def check_move_hpwl(file_name, node, x, y):
    """
	@gt
	this function takes in as a parameter a benchmark, a node
	and 2 coordinates x and y
	returns supposed hpwl if that node was moved to these coordinates
	:param file_name: str
	:param node: str
	:param x: int
	:param y: int
	:return hpwl: int
	"""

    nodes = {}
    netsx = {}
    netsy = {}
    counter = 0
    hpwl = 0

    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if line.split()[0] not in nodes:
                        nodes[line.split()[0]] = []
                    nodes[line.split()[0]].append(line.split()[1])
                    nodes[line.split()[0]].append(line.split()[2])

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    nodes[line.split()[0]].append(line.split()[1])
                    nodes[line.split()[0]].append(line.split()[2])

    nodes[node][2] = x
    nodes[node][3] = y

    with open(file_name + ".nets") as f:
        for i, line in enumerate(f):

            line = line.strip()

            if line:
                if "NetDegree" in line:
                    num_of_nodes = int(line.split()[2])
                    net_name = "n" + str(counter)
                    counter += 1
                    netsx[net_name] = []
                    netsy[net_name] = []
                elif re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if net_name in netsx:
                        if len(netsx[net_name]) == 0:
                            netsx[net_name].append(int(nodes[line.split()[0]][2]))
                            netsx[net_name].append(int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]))

                            netsy[net_name].append(int(nodes[line.split()[0]][3]))
                            netsy[net_name].append(int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]))
                        else:
                            if int(nodes[line.split()[0]][2]) < netsx[net_name][0]:
                                netsx[net_name][0] = int(nodes[line.split()[0]][2])

                            if int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]) > netsx[net_name][1]:
                                netsx[net_name][1] = int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0])

                            if int(nodes[line.split()[0]][3]) < netsy[net_name][0]:
                                netsy[net_name][0] = int(nodes[line.split()[0]][3])

                            if int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]) > netsy[net_name][1]:
                                netsy[net_name][1] = int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1])

    for net in netsx:
        hpwl += float(netsx[net][1] - netsx[net][0] + netsy[net][1] - netsy[net][0])

    return (hpwl)


def locate_nodes_in_area(nodes_file_name, x1, y1, x2, y2):
    """
	@gk
	This function takes as input the name of the benchmark.nodes
	and the coordinates to form an area and returns a list of the
	names of the nodes inside the defined area.
	:param nodes_file_name:
	:param x1:
	:param y1:
	:param x2:
	:param y2:
	:return:
	"""
    data = []
    nodes = {}
    res_nodes = []
    lx = rx = ly = uy = height = width = 0

    pl_file_name = nodes_file_name.replace('.nodes', '.pl')
    with open(pl_file_name) as pf:
        for num, line in enumerate(pf, 0):
            if num == 0 or '#' in line or line == '\n':
                continue
            else:
                data = line.split()
                lx = int(data[1])
                ly = int(data[2])
                nodes[data[0]] = [lx]
                nodes[data[0]].append(ly)

    with open(nodes_file_name) as nf:
        for num, line in enumerate(nf):
            if num == 0 or '#' in line or line == '\n' or "NumNodes" in line or "NumTerminals" in line:
                continue
            else:
                data = line.split()
                nodes[data[0]].append(int(data[1]))
                nodes[data[0]].append(int(data[2]))

    for n in nodes.items():
        if (x1 <= n[1][0] <= x2 or x1 <= n[1][0] + n[1][2] <= x2) \
                and (y1 <= n[1][1] <= y2 or y1 <= n[1][1] + n[1][3] <= y2):
            res_nodes.append(n[0])
        else:
            continue

    return res_nodes


def find_similar_cells(nodes_file_name, node_name):
    """
	@gk
	This function takes as input a benchmarks node file
	and a node's name and returns a list of the nodes similar to the
	given one in width and height
	:param nodes_file_name:
	:param node_name:
	:return:
	"""
    data = []
    nodes = {}
    result = []

    with open(nodes_file_name) as n:
        for num, line in enumerate(n):
            if num == 0 or '#' in line or line == '\n' or "NumNodes" in line or "NumTerminals" in line:
                continue
            else:
                data = line.split()
                nodes[data[0]] = [float(data[1])]
                nodes[data[0]].append(float(data[2]))

    wh = nodes.get(node_name)

    for n in nodes.items():
        if n[1][0] == wh[0] and n[1][1] == wh[1]:
            result.append(n[0])

    return result


def check_swap_cells_hpwl(file_name, node1, node2):
    """
	@gt
	this function takes in as a parameter a benchmark and two (2) nodes
	returns supposed hpwl if these nodes were swapped
	:param file_name: str
	:param node1: str
	:param node2: str
	:return hpwl: int
	"""

    nodes = {}
    netsx = {}
    netsy = {}
    counter = 0
    hpwl = 0

    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if line.split()[0] not in nodes:
                        nodes[line.split()[0]] = []
                    nodes[line.split()[0]].append(line.split()[1])
                    nodes[line.split()[0]].append(line.split()[2])

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    nodes[line.split()[0]].append(int(line.split()[1]))
                    nodes[line.split()[0]].append(int(line.split()[2]))

    nodes[node1][2] += nodes[node2][2]
    nodes[node2][2] = nodes[node1][2] - nodes[node2][2]
    nodes[node1][2] = nodes[node1][2] - nodes[node2][2]

    nodes[node1][3] += nodes[node2][3]
    nodes[node2][3] = nodes[node1][3] - nodes[node2][3]
    nodes[node1][3] = nodes[node1][3] - nodes[node2][3]

    with open(file_name + ".nets") as f:
        for i, line in enumerate(f):

            line = line.strip()

            if line:
                if "NetDegree" in line:
                    num_of_nodes = int(line.split()[2])
                    net_name = "n" + str(counter)
                    counter += 1
                    netsx[net_name] = []
                    netsy[net_name] = []
                elif re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if net_name in netsx:
                        if len(netsx[net_name]) == 0:
                            netsx[net_name].append(int(nodes[line.split()[0]][2]))
                            netsx[net_name].append(int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]))

                            netsy[net_name].append(int(nodes[line.split()[0]][3]))
                            netsy[net_name].append(int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]))
                        else:
                            if int(nodes[line.split()[0]][2]) < netsx[net_name][0]:
                                netsx[net_name][0] = int(nodes[line.split()[0]][2])

                            if int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0]) > netsx[net_name][1]:
                                netsx[net_name][1] = int(nodes[line.split()[0]][2]) + int(nodes[line.split()[0]][0])

                            if int(nodes[line.split()[0]][3]) < netsy[net_name][0]:
                                netsy[net_name][0] = int(nodes[line.split()[0]][3])

                            if int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1]) > netsy[net_name][1]:
                                netsy[net_name][1] = int(nodes[line.split()[0]][3]) + int(nodes[line.split()[0]][1])

    for net in netsx:
        hpwl += float(netsx[net][1] - netsx[net][0] + netsy[net][1] - netsy[net][0])

    return (hpwl)


def classify_by_weight(wts_file):
    """
	@gk
	This function takes as input .wts file's name and
	returns the weight of all nodes in a dictionary
	dictionary --> {node's name: [weight]}
	:param wts_file: str
	:return nodes{}: {str: [int]}
	"""

    nodes = {}
    data = []
    flag = 0
    with open(wts_file) as wf:
        for num, line in enumerate(wf, 0):
            if num == 0 or '#' in line or line == '\n':
                continue
            else:
                data = line.split()
                if data[1] != '0':
                    if data[1] not in nodes.keys():
                        nodes[data[1]] = []
                    nodes[data[1]].append(data[0])
                else:
                    continue
    return nodes


def get_non_terminal_nodes_list(file_name):
    """
    @gt
    this function takes in as a parameter a .nodes file,
    after checking if the line contains node information
    it checks if the node of that line is characterized as a terminal one
    and if it is not, it appends it in a list
    :param file_name: str
    :return non_terminal_list: list[str, str,..., str]
    """
    non_terminal_list = []
    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    node_info = line.split()
                    if len(node_info) == 3:
                        non_terminal_list.append(node_info[0])

    return non_terminal_list


def select_nodes_for_swap(file_name, weights_dict):
    nodes = []
    non_terminals = get_non_terminal_nodes_list(file_name)
    node_num = len(non_terminals) // 10
    flag = True
    while flag:
        for key, values in weights_dict.items():
            if len(nodes) < node_num:
                node_to_append = weights_dict[key][random.randint(0, len(values) - 1)]
                nodes.append(node_to_append)
            else:
                flag = False
    return nodes

def create_uniform_bins(file_name, divider):
    '''
    @gt
    this function takes in as a parameter a benchmark and a number x
    divides the chip in x*x parts and returns a dictionary with the
    starting and finishing coordinates of each part
    :param file_name: str
    :param divider: int
    :return
    '''

    rows = []
    max_width = 0
    bins = {}

    with open(file_name + ".scl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if line.split()[0] == "Coordinate":
                    starting_height = line.split()[2]
                if line.split()[0] == "Height":
                    ending_height = int(starting_height) + int(line.split()[2])
                    line_height = line.split()[2]
                if line.split()[0] == "Sitespacing":
                    sitespacing = line.split()[2]
                if line.split()[0] == "SubrowOrigin":
                    starting_x = line.split()[2]
                    ending_x = int(starting_x) + int(sitespacing) * int(line.split()[5])
                    if ending_x > max_width:
                        max_width = ending_x
                    rows.append([starting_x, starting_height, ending_x, ending_height])

    max_height = rows[-1][3]

    counter = 0

    for i in range(divider):
        for j in range(divider):
            start_x = (j) * (max_width / divider)
            start_y = (i) * (max_height / divider)
            end_x = (j + 1) * (max_width / divider)
            end_y = (i + 1) * (max_height / divider)

            bins[counter] = [start_x, start_y, end_x, end_y]
            counter += 1

    return bins



def rotate_cells(file_name, node_list):
    """
    @gt
    this function takes in as a parameter a benchmark and a list of nodes
    rotates their coordinates right to left.
    First node's coordinates go to last node's coordinates
    :param file_name: str
    :param node_list: list[str, str, str....,str]
    :return
    """

    to_change = {}

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if line.split()[0] in node_list:
                        to_change[node_list.index(line.split()[0])] = line

    with open(file_name + ".pl") as f:
        data = f.readlines()

    for i in range(len(to_change.values()) - 1, -1, -1):
        to_change[i] = to_change[i].replace(node_list[i], node_list[i - 1])

    for i in range(len(data)):

        for node in to_change.values():
            if re.search(r'\b' + node.split()[0] + r'\b', data[i]):
                data[i] = node + "\n"

    with open(file_name + ".pl", 'w') as p:
        p.writelines(data)


def get_nodes_for_swap(file_name):
    weights = classify_by_weight(file_name)
    print(weights.keys())
    nodes_for_swap = select_nodes_for_swap('../mPL6/ibm01-mPL', weights)
    print(len(nodes_for_swap))
    return nodes_for_swap

def get_node_info(node_name, nodes_file_name):
    """
    @gk
    This function takes as input the name of the node
    and a benchmarks nodes file name and returns info about the node
    info returned --> [width, height, low_x, low_y, movetype]
    :param node_name:
    :param nodes_file_name:
    :return:
    """

    data = []
    node = []
    mvtype = ''

    with open(nodes_file_name) as n:
        for num, line in enumerate(n):
            if node_name in line:
                data = line.split()
                if node_name == data[0]:
                    node.append(float(data[1]))
                    node.append(float(data[2]))
                    if 'terminal' in line:
                        mvtype = 'terminal'
                    elif 'terminal_NI' in line:
                        mvtype = 'terminal_NI'
                    else:
                        mvtype = 'non-terminal'
                    break

    pl_file_name = nodes_file_name.replace('.nodes', '.pl')
    with open(pl_file_name) as p:
        for num, line in enumerate(p):
            if node_name in line:
                data = line.split()
                if node_name == data[0]:
                    node.append(float(data[1]))
                    node.append(float(data[2]))
                    break

    node.append(mvtype)
    return node

def get_overlaps(file_name):
    """
    @gt
    this function takes in a benchmark as a parameter
    returns lists the overlapping nodes
    :param file_name: str
    :return overlapping: list[(str, str), (str, str),..., (str, str)]
    """

    place = {}
    size = {}
    sap = {}
    overlapping = []
    active_list = []
    max_width = 0

    with open(file_name + ".scl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if line.split()[0] == "Sitespacing":
                    sitespacing = line.split()[2]
                if line.split()[0] == "SubrowOrigin":
                    starting_x = line.split()[2]
                    ending_x = int(starting_x) + int(sitespacing) * int(line.split()[5])
                    if ending_x > max_width:
                        max_width = ending_x

    divider = max_width // 10

    with open(file_name + ".nodes") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if len(line.split()) == 3:
                        size[line.split()[0]] = [line.split()[1], line.split()[2]]

    with open(file_name + ".pl") as f:
        for i, line in enumerate(f):

            line = line.strip()
            if line:
                if re.match(r'[a-z]{1}[0-9]+', line.split()[0]):
                    if line.split()[0] in size:
                        place[line.split()[0]] = [line.split()[1], line.split()[2]]
                        sap_num = int(line.split()[1]) // divider
                        if sap_num not in sap.keys():
                            sap[sap_num] = []
                        sap[sap_num].append([line.split()[0], int(line.split()[1]),
                                             int(line.split()[1]) + int(size[line.split()[0]][0]), int(line.split()[2]),
                                             "start"])

                        sap[sap_num].append([line.split()[0], int(line.split()[1]),
                                             int(line.split()[1]) + int(size[line.split()[0]][0]),
                                             int(line.split()[2]) + int(size[line.split()[0]][1]), "end"])

    for lista in sap.values():
        lista.sort(key=lambda x: x[3])
        lista.sort(key=lambda x: x[4], reverse=True)
        for element in lista:
            if element[4] == "start":
                if len(active_list) == 0:
                    active_list.append(element[0])
                else:
                    for node in active_list:
                        if int(place[node][0]) < int(place[element[0]][0]) + int(size[element[0]][0]) \
                                and int(place[node][0]) + int(size[node][0]) > int(place[element[0]][0]) \
                                and int(place[node][1]) < int(place[element[0]][1]) + int(size[element[0]][1]) \
                                and int(place[node][1]) + int(size[node][1]) > int(place[element[0]][1]):
                            overlap = (node, element[0])
                            overlapping.append(overlap)
                    active_list.append(element[0])
            else:
                active_list.remove(element[0])
    return overlapping



def vertical_slide_up(node, bins):
    node_bin = get_node_bin(node, bins)
    print(node)
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    try:
        if bins[node_bin + BIN_SPLIT][1] > bins[node_bin][1]:

            place_node(directory + "/ibm01", node, coordinates[0],
                       coordinates[1] + bins[node_bin + 4][1] - bins[node_bin][1])
        else:
            print("yolo")
            place_node(directory + "/ibm01", node, coordinates[0],
                       coordinates[1] + bins[node_bin % BIN_SPLIT][1] - bins[node_bin][1])
    except KeyError:
        place_node(directory + "/ibm01", node, coordinates[0],
                   coordinates[1] + bins[node_bin % BIN_SPLIT][1] - bins[node_bin][1])
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)


def vertical_slide_down(node, bins):
    node_bin = get_node_bin(node, bins)
    print(node)
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    try:
        if bins[node_bin][1] > bins[node_bin - BIN_SPLIT][1]:

            place_node(directory + "/ibm01", node, coordinates[0],
                       coordinates[1] + bins[node_bin - 4][1] - bins[node_bin][1])
        else:
            print("yolo")
            place_node(directory + "/ibm01", node, coordinates[0],
                       coordinates[1] + bins[(BIN_SPLIT ** 2) - BIN_SPLIT + node_bin][1] - bins[node_bin][1])
    except KeyError:
        place_node(directory + "/ibm01", node, coordinates[0],
                   coordinates[1] + bins[(BIN_SPLIT ** 2) - BIN_SPLIT + node_bin][1] - bins[node_bin][1])
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    print(bins)


def multiple_vertical_slide_up(node, bins, slide_number):
    for i in range(slide_number):
        vertical_slide_up(node, bins)


def multiple_vertical_slide_down(node, bins, slide_number):
    for i in range(slide_number):
        vertical_slide_down(node, bins)


def horizontal_slide_right(node, bins):
    node_bin = get_node_bin(node, bins)

    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    try:
        if bins[node_bin + 1][0] > bins[node_bin][0]:

            place_node(directory + "/ibm01", node, coordinates[0] + bins[node_bin + 1][0] - bins[node_bin][0],
                       coordinates[1])
        else:
            print("yolo")
            place_node(directory + "/ibm01", node,
                       coordinates[0] + bins[node_bin - BIN_SPLIT + 1][0] - bins[node_bin][0], coordinates[1])
    except KeyError:
        place_node(directory + "/ibm01", node, coordinates[0] + bins[node_bin - BIN_SPLIT + 1][0] - bins[node_bin][0],
                   coordinates[1])
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)


def horizontal_slide_left(node, bins):
    node_bin = get_node_bin(node, bins)
    # print(node)
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    try:
        if bins[node_bin][0] > bins[node_bin - 1][0]:
            #	print(coordinates)
            #	print(coordinates[0]+bins[node_bin+1][0]-bins[node_bin][0])
            place_node(directory + "/ibm01", node, coordinates[0] - bins[node_bin][0] - bins[node_bin - 1][0],
                       coordinates[1])
        else:
            place_node(directory + "/ibm01", node,
                       coordinates[0] - bins[node_bin][0] + bins[node_bin + BIN_SPLIT - 1][0], coordinates[1])
    except KeyError:
        place_node(directory + "/ibm01", node, coordinates[0] - bins[node_bin][0] + bins[node_bin + BIN_SPLIT - 1][0],
                   coordinates[1])
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    print(coordinates)
    print(bins)


def multiple_horizontal_slide_left(node, bins, slide_number):
    for i in range(slide_number):
        horizontal_slide_left(node, bins)


def multiple_horizontal_slide_right(node, bins, slide_number):
    for i in range(slide_number):
        horizontal_slide_right(node, bins)


def swap_cells(pl_file_name, cell1, cell2):
    """
    @gk
    This function takes as input a benchmarks pl file,
    and the name of two nodes that are to be swapped.
    Then as a result it pseudo-overwrites the file, by creating
    a new one, replacing the old one.
    NOTE that it would be better to use a copy of the original benchmark
    in order to avoid messing the original file !
    :param pl_file_name:
    :param cell1:
    :param cell2:
    :return:
    """
    line_cell_1 = ''
    line_cell_2 = ''
    data = []
    with open(pl_file_name) as p:
        for num, line in enumerate(p):
            if cell1 in line:
                data = line.split()
                if data[0] == cell1:
                    line_cell_1 = line
            if cell2 in line:
                data = line.split()
                if data[0] == cell2:
                    line_cell_2 = line

    with open(pl_file_name) as p:
        data = p.readlines()

    for i in range(len(data)):
        if data[i] == line_cell_1:
            data[i] = line_cell_2.replace(cell2, cell1)
        if data[i] == line_cell_2:
            data[i] = line_cell_1.replace(cell1, cell2)

    with open(pl_file_name, 'w') as p:
        p.writelines(data)


def set_up_repo():
    directory = os.getcwd() + "/pl_for_detailed"
    repo = git.Repo.clone_from("https://github.com/testibm01pl/testpl", directory)
    return directory, repo


def get_node_bin(node, bins):
    coordinates = get_coordinates(directory + "/ibm01.pl", node)
    for i in range(BIN_SPLIT ** 2):
        if bins[i][0] < coordinates[0] < bins[i][2] and bins[i][1] < coordinates[1] < bins[i][3]:
            return i


def find_cells_to_swap_global(cells):
    to_swap = {}
    j = 0

    for cell in cells:
        if j // CELLS_PER_GROUP not in to_swap.keys():
            to_swap[j // CELLS_PER_GROUP] = []
        to_swap[j // CELLS_PER_GROUP].append(cell)
        j += 1

    return to_swap


def find_cells_to_swap_bin(cells, bins, node_bin):
    to_swap = {}
    j = 0

    for cell in cells:

        coordinates = get_coordinates(directory + "/ibm01.pl", cell)
        if bins[node_bin][0] < coordinates[0] < bins[node_bin][2] and bins[node_bin][1] < coordinates[1] < \
                bins[node_bin][3]:

            if len(return_nets_for_node(directory + "/ibm01", cell)) > 9:
                if j // CELLS_PER_GROUP not in to_swap.keys():
                    to_swap[j // CELLS_PER_GROUP] = []
                to_swap[j // CELLS_PER_GROUP].append(cell)
                j += 1

    return to_swap


if __name__ == '__main__':

    i = 0
    swap_nodes = get_nodes_for_swap('../mPL6/ibm01-mPL.wts')

    # print([(x, get_coordinates('pl_for_detailed/ibm01.pl', x)) for x in get_non_terminal_nodes_list('pl_for_detailed/ibm01')])
    print(total_hpwl('../mPL6/ibm01-mPL'))

    for node in swap_nodes:
        nets = return_nets_for_node('../mPL6/ibm01-mPL', node)
        net_nodes = []
        print(nets)
        for net in nets:
            net_nodes.append(get_coordinates_net('../mPL6/ibm01-mPL.nets', net))

        for net in net_nodes:
            del net[node]
        x_values = []
        y_values = []

        print(net_nodes)

        for net in net_nodes:
            x_values.append((9999999, -9999999))
            y_values.append((9999999, -9999999))
            for value in net.values():
                if int(value[0]) < int(x_values[-1][0]): x_values[-1] = (value[0], x_values[-1][1])
                if int(value[0]) > int(x_values[-1][1]): x_values[-1] = (x_values[-1][0], value[0])
                if int(value[1]) < int(y_values[-1][0]): y_values[-1] = (value[1], y_values[-1][1])
                if int(value[1]) > int(y_values[-1][1]): y_values[-1] = (y_values[-1][0], value[1])

        print(x_values)
        print(y_values)
        x_list = []
        y_list = []

        for value in x_values:
            for x in value:
                x_list.append(x)

        for value in y_values:
            for y in value:
                y_list.append(y)

        x_list.sort()
        y_list.sort()
        x_list = [int(x) for x in x_list]
        y_list = [int(y) for y in y_list]
        medianX = (x_list[(len(x_list) // 2) - 1], x_list[len(x_list) // 2])
        medianY = (y_list[(len(y_list) // 2) - 1], y_list[len(y_list) // 2])
        print(medianX)
        print(medianY)
        medx = np.median(x_list)
        medy = np.median(y_list)
        print(x_list)
        print(y_list)
        hpwl = total_hpwl('../mPL6/ibm01-mPL')
        print(hpwl)
        lista = find_similar_cells('../mPL6/ibm01-mPL.nodes', node)
        nodes = locate_nodes_in_area('../mPL6/ibm01-mPL.nodes', medianX[0], medianY[0], medianX[1],
                                     medianY[1])

        if len(nodes) == 0:

            print("WE MAY HAVE A PLACE TO PUT A DICK IN")
            if check_move_hpwl('../mPL6/ibm01-mPL', node, int(medx), int(medy)) < hpwl:

                if len(locate_nodes_in_area('../mPL6/ibm01-mPL.nodes',
                                        int(medianX[0]),
                                        int(medianY[0]),
                                        int(medianX[0]) + int(get_node_info(node, '../mPL6/ibm01-mPL.nodes')[0]) + 1,
                                        int(medianY[0]) + int(get_node_info(node, '../mPL6/ibm01-mPL.nodes')[1]) + 1)) == 0\
                        and check_move_hpwl('../mPL6/ibm01-mPL', node, medianX[0], medianY[0]) < hpwl:
                    print("PLACING IN SPACE")
                    place_node('../mPL6/ibm01-mPL', node, int(medianX[0]), int(medianY[0]))
            # print(check_move_hpwl('pl_for_detailed/ibm01', 'a17', int(medx), int(medy)))
        hpwl_per_possible_swap = {}
        min_hpwl_ascending = []
        for possible_swap in nodes:
            possible_hpwl = check_swap_cells_hpwl('../mPL6/ibm01-mPL', node, possible_swap)
            if possible_hpwl < hpwl and possible_hpwl not in hpwl_per_possible_swap.keys():
                hpwl_per_possible_swap[int(possible_hpwl)] = possible_swap
        min_hpwl_ascending = list(hpwl_per_possible_swap.keys())
        min_hpwl_ascending.sort()

        for wirelength in min_hpwl_ascending:
            if int(get_node_info(node, '../mPL6/ibm01-mPL.nodes')[0]) == int(get_node_info(hpwl_per_possible_swap[wirelength], '../mPL6/ibm01-mPL.nodes')[0]) \
                    and int(get_node_info(node, '../mPL6/ibm01-mPL.nodes')[1]) == int(get_node_info(hpwl_per_possible_swap[wirelength], '../mPL6/ibm01-mPL.nodes')[1]):
                print("SWAPING THAT MOFO")
                print("x1 " + str(get_node_info(node, '../mPL6/ibm01-mPL.nodes')[0]))
                print("x2 " + str(get_node_info(hpwl_per_possible_swap[wirelength], '../mPL6/ibm01-mPL.nodes')[0]))
                swap_cells('../mPL6/ibm01-mPL.pl', node, hpwl_per_possible_swap[wirelength])
                break
        print(nodes)
        i += 1
        print(i)
    print(total_hpwl('../mPL6/ibm01-mPL'))
