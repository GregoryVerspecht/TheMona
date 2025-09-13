class Button:
    def __init__(self,id, name, mac_address):
        self.id = id
        self.name = name
        self.mac = mac_address
    
    def show(self):
        print(f"Button {self.name}!")
    
