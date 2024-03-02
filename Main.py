import sys
import readline
from class_definition.showTechClass import *

def proc(command):
    switch_command = ''
    bash_command = ''
    command = re.sub(r' +', ' ', command) # removing white spaces between words if any
    try:
        switch_command, bash_command = command.split('|', maxsplit=1)
        switch_command = switch_command.rstrip()
    except ValueError as e:
        switch_command = command
    if bash_command:
        command_prior_pipe = showtech.command_processor(showtech.sed(switch_command))
        input_data = command_prior_pipe.encode()
        result = subprocess.run(bash_command, shell=True, input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bash_output = result.stdout.decode()
        bash_err = result.stderr.decode()
        if bash_err:
            print(bash_err)
        else:
            print(bash_output)
    else:
        print(showtech.command_processor(showtech.sed(switch_command)))

showtech = ShowTech(sys.argv[1]) 
showtech.show_tech_commands_modifier() 
showtech.get_hostname() 
showtech.gather_commands() 
showtech.routing_logic() 

# giving the completer function as input to the readline for autocompleting commands
readline.parse_and_bind ("bind ^I rl_complete") 
readline.set_completer(showtech.complete)

if (len(sys.argv)-1 == 1):
    # Loop for the device console
    while True:
        try:
            command = input(f'{showtech.hostname}: ').strip() # strips off starting and ending whitespacese
            if command == '':
               continue
            proc(command)
        except KeyboardInterrupt as e:
            print()
        except ValueError as e:
            print('wrong input or / notation not supported')
            pass

elif (len(sys.argv)-1 == 2):
    command = sys.argv[-1].strip()
    try:
        if command == '':
           sys.exit()
        proc(command)
    except KeyboardInterrupt as e:
        print()
    except ValueError as e:
        print('wrong input or / notation not supported')
        pass