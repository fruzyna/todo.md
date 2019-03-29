import datetime
from datetime import datetime as dt

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
        name = name.lower()
        best = None
        for item in self.items:
            iName = item.name.lower()
            if iName == name:
                return item
            elif iName.startswith(name) and (not best or len(iName) < len(best.name)):
                best = item
        if best:
            return best
        return None

    def getItems(self, hideDone=False, dueOnly=False):
        if not hideDone and not dueOnly:
            return self.items
        items = []
        for item in self.items:
            if (not hideDone or item.getData('done') == 'False') and (not dueOnly or item.getData('date')):
                items.append(item)
        return items

    def empty(self):
        for item in self.items:
            if item.getData('done') == 'False':
                return False
        return True

config = []
categories = []
dateFormat = '%Y-%m-%d'

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
def printCategoryItems(name, items, showDate=False, showEmpty=False):
    if len(items) > 0 or showEmpty:
        print(name, 'items')
        print(('-'*(len(name)+6)))
        for item in sortByDone(sortByDate(items, 'date')):
            name = item.name
            if item.getData('done') == 'True':
                striked = ''
                # strikes through complete items
                for c in name:
                    striked += '\u0336' + c
                name = striked
            print('-', name)
            date = item.getData('date')
            if showDate and date:
                print('  -', date)
        return True
    return False

# Sort done items to the bottom
def sortByDone(items):
    done = [i for i in items if i.getData('done') == 'True']
    undone = [i for i in items if not i.getData('done') == 'True']
    return undone + done

# Sort items by creation date
def sortByDate(items, dateKey):
    items = items.copy()
    if len(items) == 1:
        return [items[0]]
    elif len(items) == 0:
        return []
    earliest = 0
    for i in range(1, len(items)):
        if not items[earliest].getData(dateKey) and items[i].getData(dateKey):
            earliest = i
        elif items[i].getData(dateKey) and dt.strptime(items[i].getData(dateKey), dateFormat) < dt.strptime(items[earliest].getData(dateKey), dateFormat):
                earliest = i
    return [items.pop(earliest)] + sortByDate(items, dateKey)

# Sort items by priority
def sortByPriority(items):
    items = items.copy()
    if len(items) == 1:
        return [items[0]]
    elif len(items) == 0:
        return []
    highest = 0
    highVal = 0
    for i in range(0, len(items)):
        val = items[i].getData('priority')
        if val and int(val) > highVal:
            highest = i
            highVal = int(val)
    return [items.pop(highest)] + sortByPriority(items)

# delete old items
def deleteOld(days):
    delCount = 0
    for category in categories:
        remove = []
        for item in category.items:
            due = item.getData('date')
            created = item.getData('created')
            # only delete completed items
            if item.getData('done') == 'True':
                if due:
                    # use the due date if it exists
                    deleteOn = dt.strptime(due, dateFormat)
                else:
                    # otherwise use the creation date
                    deleteOn = dt.strptime(created, dateFormat)
                # add X days to the date
                deleteOn += datetime.timedelta(days=days)
                if deleteOn <= dt.today():
                    # queue for deletion
                    remove.append(item)
        delCount += len(remove)
        for item in remove:
            category.items.remove(item)
    return delCount