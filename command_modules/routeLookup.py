import re

def parsing_routing_table(contents, routes):
    # creating a routes dictionary: routes = {'default': ['0.0.0.0/0', '0.0.0.0/8', '32.55.116.0/26', '32.55.178.20/31', 'mgmt': ['0.0.0.0/8']}
    vrfs_list_original = re.findall(r'VRF: (.+)', contents)
    for vrf in vrfs_list_original:
        # if vrf to work on is last in the list
        if vrfs_list_original.index(vrf) == len(vrfs_list_original) - 1:
            first_match = re.search(vrf, contents).span()[1]
            second_match = first_match + re.search(r'------------- (show|bash).*', contents[first_match+1:]).span()[0]
        else: 
            first_match = re.search(vrf, contents).span()[1]
            second_match = re.search('VRF: .*', contents[first_match+1:]).span()[0]
            second_match += first_match - 1
        routes[vrf] = re.findall(r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/\d{1,2}', contents[first_match:second_match])


def creating_vrf_routing_table(routes):
        # will return a format as follows: {'127.0.0.1/32': {'binary_equivalent': '01111111000000000000000000000001', 'prefix': '32'}}
        vrf_table = {}
        for route in routes:
            binary_equivalent = ''
            splitted_route = route.split('/')
            splitted_route_dot = splitted_route[0].split('.')
            for nums in splitted_route_dot:
                binary_equivalent = binary_equivalent + str(format(int(nums), '08b'))
            vrf_table[route] = { 'binary_equivalent': binary_equivalent, 'prefix': splitted_route[1] }
        # print(vrf_table)
        # print('------')
        return vrf_table


def lookup(table, ip_address, vrf, matched_routes):
    # Checking if the ip provided is a valid ip
    ip_regex = r'(?:2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    if re.match(ip_regex, ip_address) == None:
        return("Invalid ip address")
    else:
        ip_binary_equivalent = ''
        max_pl = 0
        splitted_address = ip_address.split('.')
        for nums in splitted_address:
            ip_binary_equivalent = ip_binary_equivalent + str(format(int(nums), '08b'))
        try:
           vrf_route = table[vrf]
        except KeyError as e:
            return('wrong vrf entered')
        for route in vrf_route:
                if ip_binary_equivalent.startswith(vrf_route[route]['binary_equivalent'][0:int(vrf_route[route]['prefix'])]):
                    if int(vrf_route[route]['prefix']) > max_pl:
                        max_pl = int(vrf_route[route]['prefix'])
                        matched_routes.append(route)
        if len(matched_routes) == 0:
             if re.match(ip_regex, '0.0.0.0') != None:
                  matched_routes.append('0.0.0.0')
        return matched_routes[-1]


def vrf_route_lookup(contents, address_match, vrf):
    lookup = '' 
    pfirst_match = re.search(f'VRF: {vrf}', contents).span()[1] # matches the first line of the vrf routing entry
    pattern = re.compile("VRF:.*|------------- show.*") # pattern to know if the next show command start or if the next vrf in the routing entry starts
    psecond_match = pattern.search(contents[pfirst_match+1:]).span()[0] # match for the last line in the routing for that vrf
    psecond_match += pfirst_match - 1
    lookup = f'VRF: {vrf}' + '\n'
    route_match = re.search(rf'[^vV][^iI][^aA][\s]+{address_match}.*(via|is directly connected).+', contents[pfirst_match:psecond_match]) # matches the first line in the match Eg: B E      172.27.160.32/28 [20/0] via VTEP 10.167.252.3 VNI 8014 router-mac 98:5d:82:a1:d0:87
    try:
        lookup += route_match.group()
    except AttributeError as e:
        return 'no routes exists'
    lnum = route_match.span()[1] # match number within vrf routing entry
    route_match_number = pfirst_match+lnum+1 # match number within the whole routing entry
    for line in contents[route_match_number:(route_match_number+1800)].splitlines(): # Following is to match next via lines in case we have ecmp
        via_match_line = re.search('   via ([0-9]|VTEP).+', line)
        if via_match_line:
            lookup += '\n' + ("%-28s%-37s" % (25*" ",via_match_line.group()))
        else:
            break
    return lookup
                
                
def routing_table_ouput(contents, vrf):
    try:
        first_match = re.search(f'VRF: {vrf}[\s].+', contents)
        first_line_no = first_match.span()[1]
        vrf_name = first_match.group()
        second_line_no = re.search("VRF:.*|------------- show.*", contents[first_line_no+1:]).span()[0]
        second_line_no += first_line_no
        return f'{vrf_name} + \n + {contents[first_line_no:second_line_no]}'
    except AttributeError as e:
         return 'vrf does not exist'
    

def handle_ip_route(self, command, match):
    if command in ['show ip route kernel unprogrammed', 'show ip route vrf all-detail', 'show ip route vrf all-host', 'show ip route vrf all-summary']:
        return(self.command_searcher(command))
    else:
        clist = command.split(' ')
        clist_len = len(clist)
        match clist_len:
            case 3:
                return(routing_table_ouput(self.routing_contents, 'default'))
            case 4:
                vrfc = 'default'
                ip_add = clist[-1]
            case 5:
                if clist[3] == 'vrf':
                    vrfc = clist[-1]
                    return(routing_table_ouput(self.routing_contents, vrfc))
                else:
                    return('invalid input')
            case 6:
                try:
                    vrfc = clist[-2]
                    ip_add = clist[-1]
                    if vrfc not in self.routes:
                        return('vrf does not exist')
                except KeyError as e:
                        return('invalid input')
            case _:
                return('invalid input')
        if (len(clist) == 6 or len(clist) == 4):
            route_ip = lookup(self.vrf_routing_table, ip_add, vrfc, self.matched_routes)
            if route_ip == 'Invalid ip address':
                return 'Invalid ip address'
            else:
                self.matched_routes = []
                return vrf_route_lookup(self.routing_contents, route_ip, vrfc)
                    