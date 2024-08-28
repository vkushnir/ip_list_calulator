#!/usr/bin/env python3.10

# Calculates ip network lists

import argparse
import csv
import json
import logging
import re
import sys
from ipaddress import ip_address, ip_interface, summarize_address_range, collapse_addresses, \
    AddressValueError, NetmaskValueError

import yaml

# Network formats
# 127.0.0.1
# 172.16.0.0/12
# 192.168.10.0/255.255.255.0
# 192.168.1.0-192.168.1.255
# 192.168.1.0*255
re_ip_range = re.compile(r'\s*'
                         r'(?P<first>[0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,7})'
                         r'\s*-\s*'
                         r'(?P<last>[0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,7})'
                         r'\s*')
re_ip_count = re.compile(r'\s*'
                         r'(?P<first>[0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,7})'
                         r'\*'
                         r'(?P<count>\d+)'
                         r'\s*')
re_ip_network = re.compile(r'\s*'
                           r'(?P<address>[0-9]{1,3}(?:\.[0-9]{1,3}){3}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,7})'
                           r'(?:\/(?P<mask>[0-9]{1,3}))?'
                           r'\s*')
re_json = re.compile(r'(?i)\.json$')
re_csv = re.compile(r'(?i)\.csv$')
re_yaml = re.compile(r'(?i)\.ya?ml$')
re_txt = re.compile(r'(?i)\.txt$')


# ArgumetParser Classes & Functions

def is_ip_range(value: str) -> bool:
    """
    Check if the value is an IP range
    :param value: The value to check. Example: "192.168.1.0-192.168.1.255"
    :return: True if the value is an IP range, False otherwise
    """
    return re_ip_range.match(value) is not None


def get_from_ip_range(range: str) -> list:
    """
    Get a list of IP networks from a range
    :param range: The range to get the networks from. Example: "192.168.1.0-192.168.1.255"
    :return: A list of IP networks. Example: [IP4Network('192.168.1.0/24')]
    """
    match = re_ip_range.match(range)
    first = ip_address(match.group('first'))
    last = ip_address(match.group('last'))
    return list(summarize_address_range(first, last))


def is_ip_count(value: str) -> bool:
    """
    Check if the value is an IP count.
    :param value: The value to check. Example: "192.168.2.0*128"
    :return: True if the value is an IP count, False otherwise
    """
    return re_ip_count.match(value) is not None


def get_from_ip_count(count: str) -> list:
    """
    Get a list of IP networks from a count.
    :param count: The count to get the networks from. Example: "192.168.2.0*128"
    :return: A list of IP networks. Example: [IP4Network('192.168.2.0/25')]
    """
    match = re_ip_count.match(count)
    first = ip_address(match.group('first'))
    count = int(match.group('count'))
    return list(summarize_address_range(first, first + count - 1))


def is_ip_network(value: str) -> bool:
    """
    Check if the value is an IP network.
    :param value: The value to check. Example: "172.16.0.0/12", "192.168.0.0/255.255.0.0, "127.0.0.1"
    :return: True if the value is an IP network, False otherwise
    """
    return re_ip_network.match(value) is not None


def get_from_ip_network(network: str) -> list:
    """
    Get a list of IP networks from a network.
    :param network: The network to get the networks from. Example: "172.16.0.0/12", "192.168.0.0/255.255.0.0, "127.0.0.1"
    :return: A list of IP networks. Example: [IP4Network('172.16.0.0/12')], [IP4Network('192.168.0.0/16')], [IP4Network('127.0.0.1/32')]
    """
    try:
        interface = ip_interface(network)
    except (AddressValueError, NetmaskValueError):
        logger.error(f'Invalid network: {network}')
        return []
    return [ip_interface(network).network]


def get_from_string(value: str) -> list:
    """
    Get a list of IP networks from a string.
    :param value: The string to get the networks from.
    :return: A list of IP networks.
    """
    if is_ip_range(value):
        return get_from_ip_range(value)
    elif is_ip_count(value):
        return get_from_ip_count(value)
    elif is_ip_network(value):
        return get_from_ip_network(value)
    else:
        logger.error(f'Invalid network: {value}')
        return []


def is_json(value: str) -> bool:
    """
    Check if the value is a JSON file.
    :param value: The file name to check
    :return: True if the value is a JSON file extension, False otherwise
    """
    return re_json.search(value) is not None


def is_csv(value: str) -> bool:
    """
    Check if the value is a CSV file.
    :param value: The file name to check
    :return: True if the value is a CSV file extension, False otherwise
    """
    return re_csv.search(value) is not None


def is_yaml(value: str) -> bool:
    """
    Check if the value is a YAML file.
    :param value: The file name to check
    :return: True if the value is a YAML file extension, False otherwise
    """
    return re_yaml.search(value) is not None


def is_txt(value: str) -> bool:
    """
    Check if the value is a TXT file.
    :param value: The file name to check
    :return: True if the value is a TXT file extension, False otherwise
    """
    return re_txt.search(value) is not None


def _copy_items(items: list) -> list:
    if items is None:
        return []
    # The copy module is used only in the 'append' and 'append_const'
    # actions, and it is needed only when the default value isn't a list.
    # Delay its import for speeding up the common case.
    if type(items) is list:
        return items[:]
    import copy
    return copy.copy(items)


class FileReader:
    """
    Base class for file readers
    """
    
    def __init__(self, file):
        self.file = file
    
    def __iter__(self):
        pass
    
    def network(self):
        pass


class TxtReader(FileReader):
    """
    Reads networks from a text file
    Example:
        192.168.12.0-192.168.12.255
        172.17.0.0-172.17.0.3
        10.0.0.0/8
        172.16.0.0*128
        192.168.1.1
        192.168.10.0/24
        192.168.11.0/255.255.255.0
    """
    
    def __iter__(self):
        with open(self.file, 'r') as file:
            for line in file:
                networks = get_from_string(line.strip())
                for network in networks:
                    yield network


class CsvReader(FileReader):
    """
    Reads networks from a CSV file
    Example:
        192.168.12.0,192.168.12.255
        172.17.0.0,172.17.0.2
        10.0.0.0/8
        172.16.0.0,128
        192.168.1.1
        192.168.10.0/24
        192.168.11.0/255.255.255.0
    """
    
    def __iter__(self):
        with open(self.file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 0:
                    continue
                elif len(row) == 1:
                    networks = get_from_ip_network(row[0])
                else:
                    if row[1].isnumeric():
                        networks = list(
                            summarize_address_range(ip_address(row[0]), ip_address(row[0]) + int(row[1]) - 1))
                    elif is_ip_network(row[1]):
                        networks = list(summarize_address_range(ip_address(row[0]), ip_address(row[1])))
                    else:
                        networks = get_from_ip_network(row[0])
                for network in networks:
                    yield network


class JsonReader(FileReader):
    """
    Reads networks from a JSON file
    Example:
        {
          "ipv4": [
            "192.168.12.0-192.168.12.255",
            "172.17.0.0-172.17.0.2",
            "10.0.0.0/8",
            "172.16.0.0*128",
            "192.168.1.1",
            "192.168.10.0/24"
          ]
        }
    """
    
    def __init__(self, file, paths=None):
        if paths is None:
            paths = ['ipv4', 'ipv6']
        self.paths = paths
        super().__init__(file)
    
    def __iter__(self):
        with open(self.file, 'r') as file:
            data_js = json.load(file)
            for path in self.paths:
                if has_attr_path(data_js, path.split('.')):
                    data = get_attr_path(data_js, path.split('.'))
                    for item in data:
                        networks = get_from_string(item.strip())
                        for network in networks:
                            yield network


class YamlReader(FileReader):
    """
    Reads networks from a YAML file
    Example:
        ipv4:
          - "192.168.12.0-192.168.12.255"
          - "172.17.0.0-172.17.0.3"
          - "10.0.0.0/8"
          - "172.16.0.0*128"
          - "192.168.1.1"
          - "192.168.10.0/24"
          - "192.168.11.0/255.255.255.0"
    """
    
    def __init__(self, file, paths=None):
        if paths is None:
            paths = ['ipv4', 'ipv6']
        self.paths = paths
        super().__init__(file)
    
    def __iter__(self):
        with open(self.file, 'r') as file:
            data_yml = yaml.safe_load(file)
            for path in self.paths:
                if path in data_yml:
                    data = data_yml[path]
                    for item in data:
                        networks = get_from_string(item.strip())
                        for network in networks:
                            yield network


class AddIPNetwork(argparse.Action):
    """
    Add a network to the list of networks
    """
    
    def __call__(self, parser, namespace, values, option_string=None):
        # Get the current value of the attribute
        networks = getattr(namespace, self.dest, None)
        networks = argparse._copy_items(networks)
        logger.log(logging.DEBUG, f'{self.dest.upper()}: {values}')
        # Get the list of networks from the value
        try:
            networks_list = get_from_string(values)
        except (AddressValueError, NetmaskValueError):
            parser.error(f'Invalid network: {values}')
        # Add the networks to the list
        networks.extend(networks_list)
        # Set the new value of the attribute
        logger.debug(f'Setting namespace({self.dest}) to {networks}')
        setattr(namespace, self.dest, networks)


class AddIPNetworksFromFile(argparse.Action):
    """
    Add networks from a file to the list of networks
    """
    
    def __call__(self, parser, namespace, values, option_string=None):
        # Get the current value of the attribute
        networks = getattr(namespace, self.dest, None)
        networks = argparse._copy_items(networks)
        logger.debug(f'{self.dest.upper()}: from {values}')
        if is_yaml(values):
            reader = YamlReader(values)
        elif is_json(values):
            reader = JsonReader(values)
        elif is_csv(values):
            reader = CsvReader(values)
        else:
            reader = TxtReader(values)
        networks.extend(list(reader))
        # Set the new value of the attribute
        logger.debug(f'Setting namespace({self.dest}) to {networks}')
        setattr(namespace, self.dest, networks)


# Main Functions
def ip_network_exclude(network, exclude):
    """
    Exclude a network from another network
    :param network: The network to exclude from
    :param exclude: The network to exclude
    :return: A list of networks
    """
    if network.subnet_of(exclude):
        return []
    elif network.overlaps(exclude):
        return list(network.address_exclude(exclude))
    else:
        return [network]


def print_networks(networks, types):
    """
    Print the networks
    :param networks: The networks to print
    :param types: The types of networks to print
    """
    for attr in types.keys():
        nets = [net for net in networks if getattr(net, attr)]
        if len(nets) > 0:
            print(f'  * {types[attr]}: {",".join([str(net) for net in nets])}')


def has_attr_path(obj, attrs):
    """
    Check if the object has the attributes from the list
    Example: to check if the object has the attributes path 'top.data.value' do:
        has_attr_path(obj, ['top', 'data', 'value'])
    :param obj: The object to check
    :param attrs: The list of attributes to check
    :return: True if the object has the attributes, False otherwise
    """
    attr = attrs.pop(0)
    return attr in obj if len(attrs) == 0 or attr not in obj else has_attr_path(obj[attr], attrs)


def get_attr_path(obj, attrs):
    """
    Get the attribute from the object
    Example: to get the attribute path 'top.data.value' from the object do:
        get_attr_path(obj, ['top', 'data', 'value'])
    :param obj: The object to get the attribute from
    :param attrs: The list of attributes to get
    :return: The attribute value
    """
    attr = attrs.pop(0)
    return obj.get(attr, None) if len(attrs) == 0 or attr not in obj else get_attr_path(obj[attr], attrs)


def get_args():
    """
    Get the command line arguments
    :return: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='IP Network List Calculator')
    parser.set_defaults(add=[], sub=[])
    grp_input = parser.add_argument_group('Input options')
    grp_input.add_argument('-a', '--add', dest='add', action=AddIPNetwork, help='Network to add')
    grp_input.add_argument('-d', '--del', dest='sub', action=AddIPNetwork, help='Network to subtract')
    grp_input.add_argument('--add-list', dest='add_lists', action='append',
                           help='File with networks to add', default=[])
    grp_input.add_argument('--add-path', dest='add_paths', action='append',
                           help='Path inside objects to add, if file is JSON or YAML')
    grp_input.add_argument('--del-list', dest='sub_lists', action='append',
                           help='File with networks to subtract', default=[])
    grp_input.add_argument('--del-path', dest='sub_paths', action='append',
                           help='Path inside objects to subtract, if file is JSON or YAML')
    grp_output = parser.add_argument_group('Output options')
    grp_output.add_argument('-o', '--output', help='Output file')
    grp_output_format = grp_output.add_mutually_exclusive_group()
    grp_output_format.add_argument('--json', action='store_true', help='Output in JSON format')
    grp_output_format.add_argument('--csv', action='store_true', help='Output in CSV format')
    grp_output_format.add_argument('--txt', action='store_true', help='Output in TXT format')
    grp_output_format.add_argument('--yaml', action='store_true', help='Output in YAML format')
    grp_output_format.add_argument('--stdout', action='store_true', help='Output to stdout')
    grp_output.add_argument('-s', '--sort', action='store_true', help='Sort output')
    grp_options = parser.add_argument_group('Options')
    grp_options.add_argument('--version', action='version', version='%(prog)s 1.0')
    grp_options.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    grp_options.add_argument('-q', '--quiet', action='store_true', help='Quiet output')
    grp_options.add_argument('-m', '--merge', action='store_true', help='Merge networks if possible')
    # grp_output.add_argument('-i', '--intersect', action='store_true', help='Show intersect between networks')
    return parser.parse_args()


def main(args):
    """
    Main function
    :param args: Command line arguments
    """
    # Load the networks from the files
    for add_list in args.add_lists:
        if is_yaml(add_list):
            reader = YamlReader(add_list, args.add_paths)
        elif is_json(add_list):
            reader = JsonReader(add_list, args.add_paths)
        elif is_csv(add_list):
            reader = CsvReader(add_list)
        else:
            reader = TxtReader(add_list)
        args.add.extend(list(reader))
    for sub_list in args.sub_lists:
        if is_yaml(sub_list):
            reader = YamlReader(sub_list, args.sub_paths)
        elif is_json(sub_list):
            reader = JsonReader(sub_list, args.sub_paths)
        elif is_csv(sub_list):
            reader = CsvReader(sub_list)
        else:
            reader = TxtReader(sub_list)
        args.sub.extend(list(reader))
    if not args.quiet:
        print(f'Networks to add: {",".join([str(net) for net in args.add])}')
        print(f'Networks to subtract: {",".join([str(net) for net in args.sub])}')
    result = []
    # Get the networks to subtract from the networks to add
    sub_networks = [sub_network for sub_network in args.sub for add_network in args.add if
                    add_network.overlaps(sub_network)]
    if len(sub_networks) == 0:
        result = args.add
    else:
        while len(args.add) > 0:
            add_networks = [args.add.pop()]
            for sub_network in sub_networks:
                if len(add_networks) == 0:
                    break
                new_add_networks = []
                for add_network in add_networks:
                    new_add_networks.extend(ip_network_exclude(add_network, sub_network))
                add_networks = new_add_networks
            if len(add_networks) > 0:
                result.extend(add_networks)
    if args.merge:
        result = list(collapse_addresses(result))
    if not args.quiet:
        print('---')
        if args.sort:
            ipv4 = [net for net in result if net.version == 4]
            if len(ipv4) > 0:
                print("IPv4 Networks:")
                ipv4_attrs = dict(is_link_local="Link Local", is_private="Private",
                                  is_global="Global", is_loopback="Loopback", is_multicast="Multicast",
                                  is_reserved="Reserved",
                                  is_unspecified="Unspecified")
                print_networks(ipv4, ipv4_attrs)
            ipv6 = [net for net in result if net.version == 6]
            if len(ipv6) > 0:
                print("IPv6 Networks:")
                ipv6_attrs = dict(is_link_local="Link Local", is_site_local="Site Local", is_private="Private",
                                  is_global="Global", is_loopback="Loopback", is_multicast="Multicast",
                                  is_reserved="Reserved",
                                  is_unspecified="Unspecified")
                print_networks(ipv6, ipv6_attrs)
        else:
            print(f'IPv4 Networks: {",".join([str(net) for net in result if net.version == 4])}')
            print(f'IPv6 Networks: {",".join([str(net) for net in result if net.version == 6])}')
    
    # for add_network in args.add:
    #    print(f'Subtracting from {add_network}')
    #    networks = [add_network]
    #    for sub_network in args.sub:
    #        print(f'Excluding {sub_network} from {networks}')
    #        nets = [ip_network_exclude(net, sub_network) for net in networks]
    #        print(f'Nets: {nets}')


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    args = get_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.debug(args)
    main(args)
