import re

def handle_per_vlan(self, command, match=None):
    content = self.command_searcher('show vlan')
    vlan = re.findall(r'show vlan (\w+)', command)[0]
    output = '''VLAN  Name                             Status    Ports
----- -------------------------------- --------- -------------------------------\n'''
    ptr = 0
    for lines in content.splitlines():
        if ptr != 0:
            if not re.search(r'^[\d]+.+', lines):
                output += lines + '\n'
            else:
                ptr = 0
                return output
        if re.search(fr'^{vlan} .+', lines):
            output += lines + '\n'
            ptr = 1
    return ('Vlan does not exists')

