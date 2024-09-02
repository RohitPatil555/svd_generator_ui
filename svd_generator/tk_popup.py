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
