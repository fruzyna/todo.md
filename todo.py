import sys, os

from commands import *

#
# Todo file functions
#
# creates the todo file
def createTodo(file):
    config.append(Configuration('author', input('Author: ')))
    writeTodo(file)

# save to the todo file
def writeTodo(file):
    with open(file, 'w+') as f:
        f.write('---\n')
        for cfg in config:
            f.write(cfg.key + ': ' + cfg.value + '\n')
        f.write('---\n')

        for cat in categories:
            f.write('###' + cat.name + '\n')
            for item in cat.items:
                f.write('- ' + item.name + '\n')
                for d in item.data:
                    f.write('  - ' + d.key + ': ' + d.value + '\n')

# reads the todo file
def readTodo(file):
    with open(file, 'r') as f:
        inConfig = False
        currCat = ''
        currItem = ''

        text = f.read()
        lines = text.split('\n')
        for line in lines:
            #print('Line', line)
            if line == '---':
                inConfig = not inConfig
                #print('In config', inConfig)
                continue
            
            if inConfig:
                if ':' in line:
                    parts = line.split(':')
                    key = parts[0].strip()
                    value = parts[1].strip()
                    config.append(Configuration(key, value))
                    #print('Config', key, value)
                continue

            for spaces, c in enumerate(line):
                if c == '-':
                    if spaces == 0:
                        currItem = line[2:]
                        #print('New item', currItem, 'to', currCat)
                        getCategoryByName(currCat).addItem(currItem)
                    elif spaces == 2:
                        parts = line[4:].split(':')
                        #print('New data', key, value, 'to', currItem, 'in', currCat)
                        getCategoryByName(currCat).getItemByName(currItem).addData(parts[0].strip(), parts[1].strip())
                    break
                elif c != ' ':
                    currCat = line[3:]
                    #print('New category', currCat)
                    addCategory(currCat)
                    break

#
# Load in data
#
args = sys.argv[1:]
confDir = '~/.config/todo/'
file = confDir + 'todo.md'

confDir = os.path.expanduser(confDir)

if confDir[-1] != '/':
    confDir += '/'

# create config file if they don't exist
if not os.path.exists(confDir):
    choice = input('No configuration exists. Would you like to link to an existing configuration directory? [y/N] ')
    if choice.lower() == 'y':
        to = input('Where is the existing directory: ')
        to = os.path.expanduser(to)
        os.symlink(to, confDir[:-1])
    else:
        print('Creating new configuration...')
        os.makedirs(confDir)

if len(args) > 0 and '.md' in args[-1]:
    file = args[-1]
    args = args[:-2]

file = os.path.expanduser(file)
if not os.path.exists(file):
    print('File doesn\'t exist, creating', file)
    createTodo(file)

readTodo(file)

def helpCmd(params):
    print('Commands')
    print('--------')
    for key in cmds:
        tabs = '\t'
        if len(key) < 8:
            tabs += '\t'
        print(key + tabs + cmds[key][1])

#
# Check command
#
cmds = dict({
    'add': [addItem, 'Add a new item to a category.'],
    'categories': [listCategories, 'List available categories.'],
    'cats': [listCategories, 'Abbreviated version of the categories command.'],
    'chDate': [changeDate, 'Provide a new date for an item.'],
    'create': [newCategory, 'Create a new category.'],
    'delDone': [deleteDone, 'Delete all completed items.'],
    'details': [itemDetails, 'Provide details on a given item.'],
    'dets': [itemDetails, 'Abbreviated version of the details command.'],
    'done': [markDone, 'Mark/unmark an item as done.'],
    'help': [helpCmd, 'List all available commands.'],
    'list': [listItems, 'List all items by category or items in a particular category.'],
    'list-all': [listAllItems, 'List all items without categories.'],
    'ls': [listItems, 'Abbreviated version of the list command.'],
    'remove': [removeCategory, 'Remove a category.'],
    'setPriority': [setPriority, 'Set a priority of an item.']
})

args = sys.argv[1:]
argDict = {}

# process all arguments first
required = True
if len(args) > 0 and args[-1][0:2] == '--':
    print('Invalid argument', args[-1], 'requires a value.')
    exit()
for i, arg in enumerate(args):
    if arg[0] == '-' and not arg[1].isdigit():
        required = False
        if arg[1] == '-':
            nextArg = args[i+1]
            if nextArg[0] != '-':
                argDict[arg[2:]] = nextArg
            else:
                print('Invalid argument', arg, 'requires a value.')
                exit()
        else:
            argDict[arg[1:]] = 'True'
    elif required:
        if i == 0:
            argDict['cmd'] = arg
        else:
            argDict[i] = arg

# print argument dictionary for debugging
#print(argDict)

# get command name
mode = 'list'
if 'cmd' in argDict:
    mode = argDict['cmd']

# call command function
if mode in cmds:
    # delete any complete items greater than 3 past due
    deleteOld(3)
    fn = cmds[mode][0]
    fn(argDict)
    writeTodo(file)
else:
    print('Invalid command!')