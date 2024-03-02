import re        

def shrunsec(self, command, match=None):
    section_input = re.split('sec(?:t(?:i(?:on?)?)?)?', command)[-1].strip()
    section_output = ''
    relevant_section = False
    contents = self.command_searcher('show running-config sanitized')
    output = ''
    for line in contents.splitlines():
        if not line.startswith(' '):
            if relevant_section:
                output += section_output.rstrip() 
                if line.startswith('!'):
                    output += '\n' + line.rstrip() + '\n'
            relevant_section = False
            section_output = ''
        if re.match('.*' + section_input + '.*', line, re.I):
            relevant_section = True
        section_output += line +'\n'
    return output

def shrunint(self, command, match=None):
    matched = False
    contents = self.command_searcher('show running-config sanitized')
    try:
        interface = re.findall(r'show running-config sanitized interfaces (\w.+)', command)
        interface = re.sub(' ', '', interface[0])
        if not re.search(r'[0-9]', interface):
            return('Please enter a valid interface')
        content = ''
        for lines in contents.splitlines():
            if matched:
                if re.search(r'^!', lines):
                    return content
                content += lines + '\n'
            if not matched:
                matches = re.search(rf'^interface\b {interface}\b', lines, re.IGNORECASE)
                if matches:
                    content += lines + '\n'
                    matched = True
        if content == '':
            return('interface does not exist')
    except IndexError as e:
        return('Please enter the interface')



