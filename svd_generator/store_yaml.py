import yaml

class SocYamlGenerator:
    def __init__(self, cpu_type):
        _cpu_path = self._get_cpu_svdpath(cpu_type)
        self.rawdata = {
            "cpu" : _cpu_path,
            "devices" : [
            ]
        }

    def _get_cpu_svdpath(self, cpu_type):
        return "arm_cm7.svd"

    def _get_fields(self, tree, _reg_id):
        fields = []

        for _item_id in tree.get_children(_reg_id):
            if _item_id:
                _item = tree.item(_item_id)
                field_dict = yaml.safe_load(_item["values"][1])
                _field = field_dict

                fields.append(_field)

        return fields

    def _get_registers(self, tree, _device_id):
        regs = []

        for _item_id in tree.get_children(_device_id):
            if _item_id:
                _item = tree.item(_item_id)
                if _item["values"][0] != "Register":
                    continue
                reg_dict = yaml.safe_load(_item["values"][1])
                fields = self._get_fields(tree, _item_id)
                _reg = reg_dict

                if len(fields):
                    _reg["fields"] = fields

                regs.append(_reg)

        return regs

    def _get_interrupts(self, tree, _device_id):
        interrupts = []

        for _item_id in tree.get_children(_device_id):
            if _item_id:
                _item = tree.item(_item_id)
                if _item["values"][0] != "Interrupt":
                    continue
                intp_dict = yaml.safe_load(_item["values"][1])
                _interrupt = intp_dict

                interrupts.append(_interrupt)

        return interrupts

    def _get_derived(self, tree, _device_id):
        deriveds = []

        for _item_id in tree.get_children(_device_id):
            if _item_id:
                _item = tree.item(_item_id)
                if _item["values"][0] != "Derived":
                    continue
                intp_dict = yaml.safe_load(_item["values"][1])
                interrupts = self._get_interrupts(tree, _item_id)
                _derived = intp_dict
                if len(interrupts):
                    _derived["interrupts"] = interrupts

                deriveds.append(_derived)

        return deriveds

    def generate(self, tree):
        devices = []

        for _item_id in tree.get_children(""):
            if _item_id:
                _item = tree.item(_item_id)
                device_dict = yaml.safe_load(_item["values"][1])
                regs = self._get_registers(tree, _item_id)
                interrupts = self._get_interrupts(tree, _item_id)
                deriveds = self._get_derived(tree, _item_id)
                _device = device_dict

                if len(regs):
                    _device["registers"] = regs
                if len(interrupts):
                    _device["interrupts"] = interrupts
                if len(deriveds):
                    _device["deriveds"] = deriveds

                devices.append(_device)

        self.rawdata["devices"] = devices

    def save_file(self, filepath):
        with open(filepath, 'w') as outfile:
            yaml.dump(self.rawdata, outfile,default_flow_style=False,default_style=None)

    def get_rawdata(self):
        return self.rawdata
