from datetime import datetime as dt

from control import *

# Lists the items in a given list or all
def listItems(params):
    dueOnly = 'due' in params
    hideDone = not 'hideDone' in params
    showDate = 'date' in params or dueOnly
    if 1 in params:
        catName = params[1]
        category = getCategoryByName(catName)
        if category:
            printCategoryItems(category.name, category.getItems(hideDone=hideDone, dueOnly=dueOnly), showDate=showDate)
        else:
            print('Category', catName, 'not found!')
    else:
        # if there isn't a list provided print them all
        empty = 'empty' in params
        for i, category in enumerate(categories):
            success = printCategoryItems(category.name, category.getItems(hideDone=hideDone, dueOnly=dueOnly), showDate=showDate, showEmpty=empty)
            if i != (len(categories) - 1) and success:
                print()

# Lists all the items
def listAllItems(params):
    dueOnly = 'due' in params
    priority = 'priority' in params
    items = []
    for category in categories:
        for item in category.items:
            if not dueOnly or item.getData('date'):
                items.append(item)
    if priority:
        sorted = sortByPriority(items)
    else:
        sorted = sortByDate(items, 'created')
    for item in sortByDone(items):
        name = item.name
        if item.getData('done') == 'True':
            striked = ''
            # strikes through complete items
            for c in name:
                striked += '\u0336' + c
            name = striked
        print('-', name)

# print the details of a given item
def itemDetails(params):
    if 2 in params:
        itemName = params[1]
        catName = params[2]
        category = getCategoryByName(catName)
        if category:
            item = category.getItemByName(itemName)
            if item:
                print(item.name)
                print(('-'*(len(item.name))))
                print('category:', category.name)
                for data in item.data:
                    print(data.key + ':', data.value)
            else:
                print('Item', itemName, 'not found')
        else:
            print('Category', catName, 'not found!')
    else:
        print('Item name and category are required arguments!')
    
# print a list of all categories
def listCategories(params):
    print('Categories')
    print(('-'*10))
    # bold the shortcuts
    _, _, bold = findShortcuts(getCategoryNames())
    for category in bold:
        print('-', category)

# create a new category
def newCategory(params):
    if 1 in params:
        addCategory(params[1])
    else:
        addCategory(input('Category Name: '))

# mark a item as done
def markDone(params):
    done = 'True'
    if 3 in params:
        d = params[3].lower()
        if d == 'true' or d == 'false':
            done = d[0].upper() + d[1:]

    if 2 in params:
        name = params[1]
        catName = params[2]

        category = getCategoryByName(catName)
        if category:
            item = category.getItemByName(name)
            if item:
                item.addData('done', done)
                doneStr = ['not done', 'done']
                print('Set', item.name, 'to', doneStr[done == 'True'])
            else:
                print('Item not found!')
        else:
            print('Category not found!')
    else:
        print('Item name and category are required arguments!')

# add item to a category
def addItem(params):
    if 2 in params:
        name = params[1]
        category = params[2]

        cat = getCategoryByName(category)
        if cat and not cat.getItemByName(name):
            item = cat.addItem(name)
            # add done and created
            item.addData('done', 'False')
            item.addData('created', dt.today().strftime(dateFormat))

            if 'date' in params:
                item.addData('date', params['date'])
            if 'priority' in params:
                item.addData('priority', params['priority'])
            else:
                item.addData('priority', '0')
        elif not cat:
            print('Category', category, 'not found!')
        else:
            print('Item already exists in', category)
    else:
        print('Item name and category parameters required!')

# delete complete items
def deleteDone(params):
    count = deleteOld(0)
    print('Deleted', count, 'items')

# remove a category
def removeCategory(params):
    if 1 in params:
        catName = params[1]
        cat = getCategoryByName(catName)
        if cat:
            yes = input('Are you sure you want to remove ' + cat.name + '? [yes/NO] ').lower() == 'yes'
            if yes:
                categories.remove(cat)
                print(cat.name, 'removed!')
        else:
            print('Category', catName, 'not found!')
    else:
        print('Category name required!')