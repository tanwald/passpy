import gi
import logging

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from os import path

logger = logging.getLogger('PassPy.MainView')


class MainView(object):
    def __init__(self, app, window):
        self.ALL_CATEGORIES = app.bundle['categories.all']

        self.app = app
        self.window = window

        self.items = None
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.grid = Gtk.Grid(
            column_homogeneous=True,
            column_spacing=1,
            row_spacing=1
        )

        self.setHeader()
        self.setCategories()
        self.setItemList()
        self.setItemData()
        self.itemLock = False
        self.itemEntryLock = False

    def unlock(self):
        self.items = self.app.getItems()

        self.categoriesListModel.append(
            [self.ALL_CATEGORIES, self.ALL_CATEGORIES]
        )
        for category in self.app.getCategories():
            try:
                self.categoriesListModel.append(
                    [self.app.bundle[category], category]
                )
            except KeyError, e:
                logger.warn(
                    'Tried to add an unknown category: {}'.format(e)
                )
        self.categorySelection.select_iter(
            self.categoriesListModel.get_iter_first()
        )

        self.updateItemList(self.items)
        self.window.add(self.grid)
        self.window.show_all()
        self.search.grab_focus()

    def setHeader(self):
        self.logo = Gtk.Image(margin=10)
        self.logo.set_from_file(
            path.join(path.dirname(path.abspath(__file__)),
                      '../resources/logo64.png')
        )
        self.search = Gtk.Entry()
        self.search.connect('changed', self.onSearch)
        self.search.connect('activate', self.onSearchEnter)
        self.search.connect('focus-in-event', lambda x, y: x.set_text(''))
        self.itemLabel = Gtk.Label()

        self.grid.attach(self.logo, 0, 0, 1, 1)
        self.grid.attach(self.search, 1, 0, 1, 1)
        self.grid.attach(self.itemLabel, 2, 0, 2, 1)

    def setCategories(self):
        self.categoriesListModel = Gtk.ListStore(str, str)

        categoriesListView = Gtk.TreeView(model=self.categoriesListModel)
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('Categories', cell, text=0)
        categoriesListView.append_column(col)

        self.categorySelection = categoriesListView.get_selection()
        self.categorySelection.connect('changed', self.onCategorySelection)

        self.grid.attach(categoriesListView, 0, 1, 1, 1)

    def setItemList(self):
        self.itemListModel = Gtk.ListStore(str)

        self.itemListView = Gtk.TreeView(model=self.itemListModel)
        self.itemListView.set_hexpand(True)
        self.itemListView.set_vexpand(True)
        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('Items', cell, text=0)
        self.itemListView.append_column(col)

        scrollItemListView = Gtk.ScrolledWindow()
        scrollItemListView.add(self.itemListView)

        itemSelection = self.itemListView.get_selection()
        itemSelection.connect('changed', self.onItemSelection)

        self.grid.attach(scrollItemListView, 1, 1, 1, 1)

    def updateItemList(self, items):
        # don't update item selection during update
        self.itemLock = True
        self.itemListModel.clear()
        for itemName in sorted(items.keys()):
            self.itemListModel.append([itemName])
        self.itemLock = False

    def setItemData(self):
        # key value data
        self.itemDataModel = Gtk.ListStore(str, str, str)
        self.itemDataView = Gtk.TreeView(model=self.itemDataModel)
        for i in range(2):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(' ', cell, text=i)
            self.itemDataView.append_column(col)

        self.scrollItemDataView = Gtk.ScrolledWindow()
        self.scrollItemDataView.add(self.itemDataView)

        itemEntrySelection = self.itemDataView.get_selection()
        itemEntrySelection.connect('changed', self.onItemEntrySelection)

        # plain text data
        self.textBuffer = Gtk.TextBuffer()
        textView = Gtk.TextView(
            buffer=self.textBuffer,
            wrap_mode=Gtk.WrapMode.WORD,
            editable=False,
            right_margin=25,
            left_margin=25
        )
        textView.set_cursor_visible(False)
        try:
            textView.set_top_margin(25)
            textView.set_bottom_margin(25)
        except:
            logger.warn('You are using an older version of pygobject.')

        self.scrollTextView = Gtk.ScrolledWindow()
        self.scrollTextView.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC
        )
        self.scrollTextView.add(textView)

        # stack
        self.itemDataStack = Gtk.Stack()
        self.itemDataStack.add_named(self.scrollItemDataView, 'key-value')
        self.itemDataStack.add_named(self.scrollTextView, 'plain-text')

        self.grid.attach(self.itemDataStack, 2, 1, 2, 1)

    def updateItemData(self, itemName):
        # don't update item entry selection during update
        self.itemEntryLock = True
        self.itemDataModel.clear()
        item = None
        try:
            item = self.items[itemName]
        except KeyError, e:
            logger.error('Could not find item {}'.format(e))

        if item:
            item.decrypt()
            self.itemLabel.set_text(itemName)
            if item.type == 'securenotes.SecureNote':
                self.textBuffer.set_text(
                    item.getEntries()[0].getValue(trimmed=False)
                )
                self.itemDataStack.set_visible_child(self.scrollTextView)
            else:
                self.insertEntries(item)
                self.itemDataStack.set_visible_child(self.scrollItemDataView)

        self.itemEntryLock = False

    def insertEntries(self, item):
        for entry in item.getEntries():
            if entry.isVisible:
                if entry.isUsername:
                    self.itemDataModel.insert(
                        0,
                        [entry.getKey(), entry.getValue(),
                         unicode(entry.value)]
                    )
                else:
                    self.itemDataModel.append(
                        [entry.getKey(), entry.getValue(),
                         unicode(entry.value)]
                    )

    def onSearch(self, entry):
        query = entry.get_text()
        # always search within all categories
        self.categorySelection.select_iter(
            self.categoriesListModel.get_iter_first()
        )
        self.updateItemList(self.app.getItems(name=query))

        return True

    def onSearchEnter(self, entry):
        self.itemListView.grab_focus()
        self.updateItemData(self.itemListModel[0][0])

        return True

    def onCategorySelection(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            category = model[iter][1]

            if category == self.ALL_CATEGORIES:
                items = self.app.getItems(name=self.search.get_text())
            else:
                items = self.app.getItems(
                    type=category,
                    name=self.search.get_text()
                )
            self.updateItemList(items)

        return True

    def onItemSelection(self, selection):
        (model, iter) = selection.get_selected()
        if iter and not self.itemLock:
            itemName = model[iter][0]
            self.updateItemData(itemName)

        return True

    def onItemEntrySelection(self, selection):
        (model, iter) = selection.get_selected()
        if iter and not self.itemEntryLock:
            value = model[iter][2]
            self.clipboard.set_text(value, -1)

        return True
