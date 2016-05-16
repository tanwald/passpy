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

    def unlock(self):
        self.items = self.app.getItems()

        self.categoriesListModel.append(
            [self.ALL_CATEGORIES, self.ALL_CATEGORIES]
        )
        for category in sorted(self.app.getCategories()):
            self.categoriesListModel.append(
                [self.app.bundle[category], category]
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
        self.itemListModel.clear()
        for itemName in sorted(items.keys()):
            self.itemListModel.append([itemName])

    def setItemData(self):
        self.itemInfoModel = Gtk.ListStore(str, str, str)
        self.itemInfoView = Gtk.TreeView(model=self.itemInfoModel)
        for i in range(2):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(' ', cell, text=i)
            self.itemInfoView.append_column(col)

        scrollItemInfoView = Gtk.ScrolledWindow()
        scrollItemInfoView.add(self.itemInfoView)

        itemInfoSelection = self.itemInfoView.get_selection()
        itemInfoSelection.connect('changed', self.onItemEntrySelection)

        self.grid.attach(scrollItemInfoView, 2, 1, 2, 1)

    def updateItemData(self, itemName):
        self.itemInfoModel.clear()
        item = None
        try:
            item = self.items[itemName]
        except KeyError, e:
            logger.error('Could not find item {}'.format(e))

        if item:
            item.decrypt()
            self.itemLabel.set_text(itemName)
            for entry in item.getEntries():
                if entry.isVisible:
                    if entry.isUsername:
                        self.itemInfoModel.insert(
                            0,
                            [entry.getKey(), entry.getValue(),
                             unicode(entry.value)]
                        )
                    else:
                        self.itemInfoModel.append(
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
        if iter:
            itemName = model[iter][0]
            self.updateItemData(itemName)

        return True

    def onItemEntrySelection(self, selection):
        (model, iter) = selection.get_selected()
        if iter:
            value = model[iter][2]
            self.clipboard.set_text(value, -1)

        return True
