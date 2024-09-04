import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .tk_popup import GenericPopUp, SelectAction
from .svd_template import SvdTemplates
from .store_yaml import SocYamlGenerator
from .export_svd import ExportSvd

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Soc Description")
        self.root.geometry("600x400")
        self._soc_tmpl = SvdTemplates()
        self._selected_item = ""
        self.soc_gen = None

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(self.button_frame, textvariable=self.type_var)
        self.type_combobox['values'] = ('None','ARM-M7')  # Example types
        self.type_combobox.current(0)  # Set default selection
        self.type_combobox.pack(side=tk.LEFT, padx=5)

        self.add_button = ttk.Button(self.button_frame, text="Add Node", command=self.add_node)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = ttk.Button(self.button_frame, text="Remove", command=self.remove_node)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.expand_button = ttk.Button(self.button_frame, text="Expand All", command=self.expand_all)
        self.expand_button.pack(side=tk.LEFT, padx=5)

        self.collapse_button = ttk.Button(self.button_frame, text="Collapse All", command=self.collapse_all)
        self.collapse_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.save_tree)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(self.button_frame, text="Export", command=self.export_svd)
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")

        self.tree_scroll_v = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.tree_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_h = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_h.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Metadata"),
            show="tree headings", yscrollcommand=self.tree_scroll_v.set, xscrollcommand=self.tree_scroll_h.set)
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree_scroll_v.config(command=self.tree.yview)
        self.tree_scroll_h.config(command=self.tree.xview)
        self.tree_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.heading("#0", text="Hierarchy")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Metadata", text="Metadata")

        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)

    def _error_message(self, title, message):
        print("%s \n \t %s"%(title, message))
        messagebox.showerror(title, message)

    def _generic_popup(self, type, callback):
        GenericPopUp(type, "%s Parameter"%(type), self.root, callback, self._soc_tmpl.get_template(type))

    def _modify_tree(self, data):
        values = self._soc_tmpl.get_values(data)
        self.tree.insert(self._selected_item, tk.END, text=data["Name"], values=values)
        self._selected_item = ""

    def add_device(self, callback):
        self._selected_item = ""
        self._generic_popup("Device", callback)

    def add_register(self, callback):
        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Device":
                self._generic_popup("Register", callback)
            else:
                self._error_message("Invalid Operation", "Add register operation can perform on device only")

    def add_device_derived(self, callback):
        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Device":
                self._generic_popup("Derived", callback)
            else:
                self._error_message("Invalid Operation", "Add derived operation can perform on device only")

    def add_field(self, callback):
        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Register":
                self._generic_popup("Field", callback)
            else:
                self._error_message("Invalid Operation", "Add register operation can perform on device only")

    def add_interrupt(self, callback):
        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Device" or _type == "Derived":
                self._generic_popup("Interrupt", callback)
            else:
                self._error_message("Invalid Operation", "Add register operation can perform on device only")

    def add_node(self):
        action_dict = {
            "Device" : {
                "action" : self.add_device,
                "callback" : self._modify_tree
            },
            "Register" : {
                "action" : self.add_register,
                "callback" : self._modify_tree
            },
            "Field" : {
                "action" : self.add_field,
                "callback" : self._modify_tree
            },
            "Interrupt" : {
                "action" : self.add_interrupt,
                "callback" : self._modify_tree
            },
            "Derived" : {
                "action" : self.add_device_derived,
                "callback" : self._modify_tree
            }
        }

        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Device":
                del action_dict["Field"]
            elif _type == "Derived":
                del action_dict["Device"]
                del action_dict["Register"]
                del action_dict["Field"]
                del action_dict["Derived"]
            elif _type == "Register":
                del action_dict["Device"]
                del action_dict["Interrupt"]
                del action_dict["Register"]
            elif _type == "Field" or _type == "Interrupt":
                self._error_message("Invalid Operation", "Add operation not allowed on %s  " %(_type))
                return
        else:
            print("Not found selected ID")
            del action_dict["Interrupt"]
            del action_dict["Register"]
            del action_dict["Field"]
            del action_dict["Derived"]

        SelectAction("Add action", self.root, action_dict)

    def remove_node(self):
        # Example function to remove a node (this is just a placeholder)
        selected_item = self.tree.focus()  # Get currently selected item
        if selected_item:
            self.tree.delete(selected_item)

    def expand_all(self):
        # Example function to expand all nodes
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
            self.expand_all_recursively(item)

    def expand_all_recursively(self, parent):
        # Recursively expand children
        for item in self.tree.get_children(parent):
            self.tree.item(item, open=True)
            self.expand_all_recursively(item)

    def collapse_all(self):
        # Example function to collapse all nodes
        for item in self.tree.get_children():
            self.tree.item(item, open=False)
            self.collapse_all_recursively(item)

    def collapse_all_recursively(self, parent):
        # Recursively collapse children
        for item in self.tree.get_children(parent):
            self.tree.item(item, open=False)
            self.collapse_all_recursively(item)

    def save_tree(self):
        if self.soc_gen:
            del self.soc_gen
        self.soc_gen = SocYamlGenerator("ARM-M7")
        self.soc_gen.generate(self.tree)
        print(self.soc_gen.get_rawdata())
        self.soc_gen.save_file("test_soc.yaml")

    def export_svd(self):
        if self.soc_gen:
            e = ExportSvd(self.soc_gen.get_rawdata(), "temp_script.yaml")
            e.generate()

    def on_closing(self):
        """Handle the window close event."""
        self.root.destroy()
