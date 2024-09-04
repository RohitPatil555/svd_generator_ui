import tkinter as tk
from tkinter import ttk

class GenericPopUp(tk.Toplevel):
    def __init__(self, _type, title, parent, on_save, parameters):
        super().__init__(parent)
        self._type = _type
        self.title(title)
        #self.geometry("300x150")
        self.on_save = on_save  # Function to call when saving
        self.var_list = {}
        self.var_type = {}

        for param in parameters:
            name = param["name"]

            if param["type"] == "string":
                var = tk.StringVar()
            elif self._check_int_type(param["type"]):
                var = tk.IntVar()
            else:
                print("Unsupported type : %s"%(param["type"]))
                return
            self.var_list[name] = var
            self.var_type[name] = param["type"]

        for key, var in self.var_list.items():
            ttk.Label(self, text=key).pack(pady=5)
            _entry = ttk.Entry(self, textvariable=var)
            _entry.pack(pady=5)

        save_button = ttk.Button(self, text="Save", command=self.save_data)
        save_button.pack(pady=10)

    def _check_int_type(self, type):
        allowed_type = ["int", "addr32", "intHex"]
        if type in allowed_type:
            return True
        return False

    def _conv_addr32(self, value):
        _val = "0x%08x"%(value)
        return _val

    def _conv_intHex(self, value):
        _val = "0x%x"%(value)
        return _val

    def save_data(self):
        data = {"Type" : self._type }

        for key, var in self.var_list.items():
            value = var.get()
            attr_name = "_conv_%s"%(self.var_type[key])
            _final_val = None

            if hasattr(self, attr_name):
                converter = getattr(self, attr_name)
                _final_val = converter(value)
            else:
                _final_val = value
            data[key] = _final_val

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
