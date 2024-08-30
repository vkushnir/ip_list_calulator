# IP List Calculator

## Description

The script is designed to generate a list of IP addresses resulting from the addition or subtraction of a list of networks.

Networks can be specified in the following formats:

* `xxx.xxx.xxx.xxx` - a single IP address
* `xxx.xxx.xxx.xxx/yy` - a network with a CIDR mask
* `xxx.xxx.xxx.xxx/zzz.zzz.zzz.zzz` - a network with a subnet mask
* `xxx.xxx.xxx.xxx-xxx.xxx.xxx.xxx` - a range of IP addresses
* `xxx.xxx.xxx.xxx*nnn` - the starting IP address and the number of IP addresses

Similar formats can be used for IPv6 networks.

* `xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx` - a single IP address
* `xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx/yy` - a network with a CIDR mask
* `xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx-xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx` - a range of IP addresses
* `xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx*nnn` - the starting IP address and the number of IP addresses

_Examples:_

* `127.0.0.1`
* `192.168.0.0/16`
* `172.16.0.0/172.31.255.255`
* `192.168.0.0-192.168.0.255`
* `172.16.0.0*4`

## Command Line Parameters

Networks can be added one at a time or as a list.

### Networks

* `-a`, `--add` - add networks
* `-d`, `--del` - subtract networks

_Example:_

```bash
./ip_list_calculator.py --add 172.16.0.0/12 --del 172.17.0.0/24 --del 172.24.0.0/13
Networks to add: 172.16.0.0/12
Networks to subtract: 172.17.0.0/24,172.24.0.0/13
---
IPv4 Networks: 172.20.0.0/14,172.18.0.0/15,172.16.0.0/16,172.17.128.0/17,172.17.64.0/18,172.17.32.0/19,172.17.16.0/20,172.17.8.0/21,172.17.4.0/22,172.17.2.0/23,172.17.1.0/24
IPv6 Networks:
```

### Networks lists

Network lists can be specified in a text file, as well as in JSON or YAML format.

The filename containing the networks is specified with the `--add-list` or `--del-list` parameter. If this is a structured file, the path to the array of networks is specified with the `--add-path` or `--del-path` parameters.

#### Text File

In a text file, each network is specified on a separate line.

_Example: **tests/test.txt**_

```text
192.168.12.0-192.168.12.255
172.17.0.0-172.17.0.3
10.0.0.0/8
172.16.0.0*128
192.168.1.1
192.168.10.0/24
192.168.11.0/255.255.255.0
```

```shell
./ip_list_calculator.py --add-list tests/test.txt
Networks to add: 192.168.12.0/24,172.17.0.0/30,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24,192.168.11.0/24
Networks to subtract:
---
IPv4 Networks: 192.168.12.0/24,172.17.0.0/30,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24,192.168.11.0/24
IPv6 Networks:
```

#### JSON

In a JSON file, networks are specified in the form of an array.

_Example: **tests/test.json**_

```json
{
  "networks": {
    "ipv4": [
      "192.168.12.0-192.168.12.255",
      "172.17.0.0-172.17.0.2",
      "10.0.0.0/8",
      "172.16.0.0*128",
      "192.168.1.1",
      "192.168.10.0/24"
    ],
    "ipv6": [
      "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
      "2001:0db8:85a3:0000:0000:8a2e:0370:7334/64",
      "2001:0db8:85a3:0000:0000:8a2e:0370:7334*128",
      "2001:0db8:85a3:0000:0000:8a2e:0370:7334-2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    ]
  }
}
```

```shell
./ip_list_calculator.py --add-list tests/test.json --add-path networks.ipv4
Networks to add: 192.168.12.0/24,172.17.0.0/31,172.17.0.2/32,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24
Networks to subtract:
---
IPv4 Networks: 192.168.12.0/24,172.17.0.0/31,172.17.0.2/32,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24
IPv6 Networks:
```

#### YAML

In a YAML file, networks are specified in the form of an array, similarly to JSON.

_Example: **tests/test.yaml**_

```yaml
networks:
  ipv4:
    - "192.168.12.0-192.168.12.255"
    - "172.17.0.0-172.17.0.3"
    - "10.0.0.0/8"
    - "172.16.0.0*128"
    - "192.168.1.1"
    - "192.168.10.0/24"
    - "192.168.11.0/255.255.255.0"
  ipv6:
    - "2001:db8::/32"
    - "2001:db8::/128"
```
    
```shell
./ip_list_calculator.py --add-list tests/test.yaml --add-path networks.ipv4
Networks to add: 192.168.12.0/24,172.17.0.0/30,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24,192.168.11.0/24
Networks to subtract:
---
IPv4 Networks: 192.168.12.0/24,172.17.0.0/30,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24,192.168.11.0/24
IPv6 Networks:
```

### Output

* `--output` - the name of the file to save the result

If only the `--output` parameter is specified, the file type is determined by the file extension. If the `--txt`, `--json`, or `--yaml` parameter is specified, the file type is determined by that parameter.

The format for saving data in **JSON** and **YAML** files:

```json
{
  "IPv4": [],
  "IPv6": []
}
```

```yaml
IPv4:
  -
IPv6:
  -
```

## Options

 `-q`, `--quiet` - do not display the result on the screen
 `-s`, `--sort` - networks are grouped by type when displayed on the screen (Loopback, Private, Public, Multicast, Reserved, Unassigned).
 `-m`, `--merge` - merge networks if they overlap.

_Examples:_

```shell
./ip_list_calculator.py --add-list tests/test.json --add-path networks.ipv4 --add 127.0.0.1 --add 1.1.1.1 --add 8.8.8.8 --sort
Networks to add: 127.0.0.1/32,1.1.1.1/32,8.8.8.8/32,192.168.12.0/24,172.17.0.0/31,172.17.0.2/32,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24
Networks to subtract:
---
IPv4 Networks:
  * Private: 127.0.0.1/32,192.168.12.0/24,172.17.0.0/31,172.17.0.2/32,10.0.0.0/8,172.16.0.0/25,192.168.1.1/32,192.168.10.0/24
  * Global: 1.1.1.1/32,8.8.8.8/32
  * Loopback: 127.0.0.1/32
```

```shell
./ip_list_calculator.py --add 192.168.10.0/24 --add 192.168.0.0/16 --add 172.16.0.0/25 --add 172.16.0.128/25 --merge
Networks to add: 192.168.10.0/24,192.168.0.0/16,172.16.0.0/25,172.16.0.128/25
Networks to subtract:
---
IPv4 Networks: 172.16.0.0/24,192.168.0.0/16
IPv6 Networks:
```