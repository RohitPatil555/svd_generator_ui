
class SvdTemplates:
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
