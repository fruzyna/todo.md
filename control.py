#
# Objects
#

# Item configuration data object
class Configuration:
    def __init__(self, key, value):
        self.key = key
        self.value = value

# Item object
class Item:
    def __init__(self, name):
        self.name = name
        self.data = []

    def addData(self, key, value):
        config = Configuration(key, value)
        for i,d in enumerate(self.data):
            if d.key == key:
                self.data[i] = config
                return
        self.data.append(config)

    def getData(self, key):
        for d in self.data:
            if d.key == key:
                return d.value
        return None

# Category object
class Category:
    def __init__(self, name):
        self.name = name
        self.items = []

    def addItem(self, name):
        item = Item(name)
        self.items.append(item)
        return item

    def getItemByName(self, name):
        best = None
        for item in self.items:
            iName = item.name
            if iName == name:
                return item
            elif iName.startswith(name) and (not best or len(iName) < len(best.name)):
                best = item
        if best:
            return best
        return None

config = []
categories = []

#
# Helper functions
#

# Finds the appropriate category object for a partial or full name
def getCategoryByName(name):
    name = name.lower()
    best = None
    for cat in categories:
        category = cat.name.lower()
        if category == name:
            return cat
        elif category.startswith(name) and (not best or len(category) < len(best.name)):
            # if the string doesn't match see if it is close
            best = cat
    if best:
        return best
    return None

# Returns a list of all category names
def getCategoryNames():
    return [cat.name for cat in categories]

# Determines the shortest necessary string to describe a string in a list
def findShortcuts(items):
    lengths = []
    bolds = []
    for item in items:
        bold = '\033[1m\033[4m'
        # iteratively try longer and longer strings
        for i in range(len(item)):
            length = i+1
            found = False
            for other in items:
                # if a string matches add a letter
                if other.startswith(item[0:length]) and other != item:
                    found = True
                    continue
            least = length
            bold += item[i]
            if not found:
                bold += '\033[0m' + item[length:]
                break
        lengths.append(least)
        bolds.append(bold)
    # returns the original list, the lengths of the shortcuts, and a bolded version
    return items, lengths, bolds

# Creates a new category with a name
def addCategory(name):
    categories.append(Category(name))

# Prints all the items in a category
def printCategoryItems(category):
    print(category.name, 'items')
    print(('-'*(len(category.name)+6)))
    for item in category.items:
        name = item.name
        if item.getData('done') == 'True':
            striked = ''
            # strikes through complete items
            for c in name:
                striked += '\u0336' + c
            name = striked
        print('-', name)