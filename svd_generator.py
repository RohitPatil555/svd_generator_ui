import tkinter as tk
from tkinter import ttk
import yaml
from tkinter import messagebox

class SocTemplateDb:
    def __init__(self):
        self.tmpl_device = [
            {
                "type" : "string",
                "name" : "Name"
            },
            {
                "type" : "int",
                "name" : "baseAddress"
            },
            {
                "type" : "string",
                "name" : "description"
            }
        ]
        self.tmpl_register = [
            {
                "type" : "string",
                "name" : "Name"
            },
            {
                "type" : "int",
                "name" : "addressOffset"
            },
            {
                "type" : "string",
                "name" : "description"
            }
        ]
        self.tmpl_field = [
            {
                "type" : "string",
                "name" : "Name"
            },
            {
                "type" : "int",
                "name" : "bitOffset"
            },
            {
                "type" : "int",
                "name" : "bitWidth"
            },
            {
                "type" : "string",
                "name" : "description"
            }
        ]
        self.tmpl_interrupt = [
            {
                "type" : "string",
                "name" : "Name"
            },
            {
                "type" : "int",
                "name" : "value"
            },
            {
                "type" : "string",
                "name" : "description"
            }
        ]

    def get_template(self, type):
        if type == "Device":
            return self.tmpl_device
        elif type == "Register":
            return self.tmpl_register
        elif type == "Field":
            return self.tmpl_field
        elif type == "Interrupt":
            return self.tmpl_interrupt
        else:
            print("Error: Unhandled type %s"%(type))

    def get_values(self, data):
        Type = data["Type"]
        Metadata = data
        return (Type, Metadata)

class SocYamlGenerator:
    def __init__(self, cpu_type):
        _cpu_path = self._get_cpu_svdpath(cpu_type)
        self.rawdata = {
            "_svd" : _cpu_path,
            "_add" : [
            ]
        }

    def _get_cpu_svdpath(self, cpu_type):
        return "arm_cm7.svd"

    def _get_fields(self, tree, _reg_id):
        fields = {}

        for _item_id in tree.get_children(_reg_id):
            if _item_id:
                _item = tree.item(_item_id)
                field_dict = yaml.safe_load(_item["values"][1])
                _field = field_dict
                del _field["Type"]
                del _field["Name"]

                name = _item["text"]
                fields[name] = _field

        print(fields)
        return fields

    def _get_registers(self, tree, _device_id):
        regs = {}

        for _item_id in tree.get_children(_device_id):
            if _item_id:
                _item = tree.item(_item_id)
                if _item["values"][0] != "Register":
                    continue
                reg_dict = yaml.safe_load(_item["values"][1])
                fields = self._get_fields(tree, _item_id)
                _reg = reg_dict
                del _reg["Type"]
                del _reg["Name"]
                if len(fields):
                    _reg["fields"] = fields

                name = _item["text"]
                regs[name] = _reg

        return regs

    def _get_interrupts(self, tree, _device_id):
        interrupts = {}

        for _item_id in tree.get_children(_device_id):
            if _item_id:
                _item = tree.item(_item_id)
                if _item["values"][0] != "Interrupt":
                    continue
                intp_dict = yaml.safe_load(_item["values"][1])
                _interrupt = intp_dict
                del _interrupt["Type"]
                del _interrupt["Name"]

                name = _item["text"]
                interrupts[name] = _interrupt

        return interrupts

    def generate(self, tree):
        devices = {}

        for _item_id in tree.get_children(""):
            if _item_id:
                _item = tree.item(_item_id)
                device_dict = yaml.safe_load(_item["values"][1])
                regs = self._get_registers(tree, _item_id)
                interrupts = self._get_interrupts(tree, _item_id)
                _device = device_dict
                del _device["Type"]
                del _device["Name"]
                if len(regs):
                    _device["registers"] = regs
                if len(interrupts):
                    _device["interrupts"] = interrupts

                name = _item["text"]
                devices[name] = _device

        self.rawdata["_add"] = devices

    def save_file(self, filepath):
        with open(filepath, 'w') as outfile:
            yaml.dump(self.rawdata, outfile,default_flow_style=False,default_style=None)

    def get_rawdata(self):
        return self.rawdata

class GenericPopUp(tk.Toplevel):
    def __init__(self, _type, title, parent, on_save, parameters):
        super().__init__(parent)
        self._type = _type
        self.title(title)
        #self.geometry("300x150")
        self.on_save = on_save  # Function to call when saving
        self.var_list = {}

        for param in parameters:
            name = param["name"]

            if param["type"] == "string":
                var = tk.StringVar()
            elif param["type"] == "int":
                var = tk.IntVar()
            else:
                print("Unsupported type : %s"%(param["type"]))
                return
            self.var_list[name] = var


        for key, var in self.var_list.items():
            ttk.Label(self, text=key).pack(pady=5)
            _entry = ttk.Entry(self, textvariable=var)
            _entry.pack(pady=5)

        save_button = ttk.Button(self, text="Save", command=self.save_data)
        save_button.pack(pady=10)

    def save_data(self):
        data = {"Type" : self._type }

        for key, var in self.var_list.items():
            value = var.get()
            data[key] = value

        self.on_save(data)
        self.destroy()

class SelectAction(tk.Toplevel):
    def __init__(self, title, parent, dict):
        super().__init__(parent)
        self.title(title)
        self._dict = dict
        self.root = parent

        self.action_var = tk.StringVar()
        action_list = ()
        for key, val in self._dict.items():
            action_list += (key,)

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        _combox = ttk.Combobox(self.button_frame, textvariable=self.action_var)
        _combox['values'] = action_list
        _combox.current(0)
        _combox.pack(side=tk.LEFT, padx=5)

        self.add_button1 = ttk.Button(self.button_frame, text="Next", command=self.next_action)
        self.add_button1.pack(side=tk.LEFT, padx=5)

    def next_action(self):
        act = self.action_var.get()
        callback = self._dict[act]["callback"]
        method = self._dict[act]["action"]

        method(callback)
        self.destroy()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Soc Description")
        self.root.geometry("600x400")
        self._soc_tmpl = SocTemplateDb()
        self._selected_item = ""

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
        # self.add_button1 = ttk.Button(self.button_frame, text="Add Device", command=self.add_device)
        # self.add_button1.pack(side=tk.LEFT, padx=5)
        # self.add_button2 = ttk.Button(self.button_frame, text="Add Register", command=self.add_register)
        # self.add_button2.pack(side=tk.LEFT, padx=5)
        # self.add_button3 = ttk.Button(self.button_frame, text="Add Field", command=self.add_field)
        # self.add_button3.pack(side=tk.LEFT, padx=5)
        # self.add_button4 = ttk.Button(self.button_frame, text="Add Interrupt", command=self.add_interrupt)
        # self.add_button4.pack(side=tk.LEFT, padx=5)

        self.remove_button = ttk.Button(self.button_frame, text="Remove", command=self.remove_node)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.expand_button = ttk.Button(self.button_frame, text="Expand All", command=self.expand_all)
        self.expand_button.pack(side=tk.LEFT, padx=5)

        self.collapse_button = ttk.Button(self.button_frame, text="Collapse All", command=self.collapse_all)
        self.collapse_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(self.button_frame, text="Save", command=self.save_tree)
        self.save_button.pack(side=tk.LEFT, padx=5)

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
            if _type == "Device":
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
            }
        }

        self._selected_item = self.tree.focus()
        if self._selected_item:
            _item = self.tree.item(self._selected_item)
            _type = _item["values"][0]
            if _type == "Device":
                del action_dict["Field"]
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
        soc_gen = SocYamlGenerator("ARM-M7")
        soc_gen.generate(self.tree)
        print(soc_gen.get_rawdata())
        soc_gen.save_file("test_soc.yaml")

    def on_closing(self):
        """Handle the window close event."""
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
