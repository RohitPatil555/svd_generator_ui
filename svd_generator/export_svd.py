import yaml

class ExportSvd:
    def __init__(self, data, filepath):
        self.data = data
        self._file = open(filepath, "w")

    def _field(self, f):
        del f["Type"]
        return f

    def _register(self, r):
        fields = {}

        if "fields" in r:
            for f in r["fields"]:
                field = self._field(f)
                name = field["Name"]
                del field["Name"]
                fields[name] = field

            r["fields"] = fields

        del r["Type"]
        return r

    def _interupts(self , i):
        del i["Type"]
        return i

    def _device(self, d):
        regs = {}
        interrupts = {}

        if "registers" in d:
            for r in d["registers"]:
                reg = self._register(r)
                name = reg["Name"]
                del reg["Name"]
                regs[name] = reg

            d["registers"] = regs

        if "interrupts" in d:
            for _i in d["interrupts"]:
                intr = self._interupts(_i)
                name = intr["Name"]
                del intr["Name"]
                interrupts[name] = intr

            d["interrupts"] = interrupts

        del d["Type"]

        return d

    def _derived(self, parent_name, _ddev):
        _ddev["derivedFrom"] = parent_name

        interrupts = {}
        if "interrupts" in _ddev:
            for _i in _ddev["interrupts"]:
                intr = self._interupts(_i)
                name = intr["Name"]
                del intr["Name"]
                interrupts[name] = intr

            _ddev["interrupts"] = interrupts

        del _ddev["Type"]
        return _ddev

    def _build_yamlInst_add(self, inst):
        final_struct = {}
        final_struct["_add"] = inst

        yaml_out = yaml.dump(final_struct)
        del final_struct
        return yaml_out

    def _build_yamlInst_svd(self, path):
        final_struct = {}
        final_struct["_svd"] = path

        yaml_out = yaml.dump(final_struct)
        del final_struct
        return yaml_out

    def _append_to_file(self, _out):
        self._file.write("")
        self._file.write(_out)

    def generate(self):
        conv_output = self._build_yamlInst_svd(self.data["cpu"])
        self._append_to_file(conv_output)

        _final_devices = {}
        for _d in self.data["devices"]:
            _mod_device = self._device(_d)
            device_name = _mod_device["Name"]
            del _mod_device["Name"]
            derived_list = None
            if "deriveds" in _mod_device:
                derived_list = _mod_device["deriveds"]

            # convert _final_device in yam string and writ down to file.
            del _mod_device["deriveds"]
            _final_devices[device_name] = _mod_device

            if derived_list:
                for _ddev in derived_list:
                    derived = self._derived(device_name, _ddev)
                    name = derived["Name"]
                    del derived["Name"]
                    _final_devices[name] = derived

        conv_output = self._build_yamlInst_add(_final_devices)
        self._append_to_file(conv_output)
