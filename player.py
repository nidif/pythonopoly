class Player:
    def __init__(self, name, game_piece_type, cash = 1500):
        self.name = name
        self.game_piece = GamePiece(self.name, game_piece_type)
        self.properties = []
        self.cash = cash
        self.in_jail = False

    def add_property(self, property):
        self.properties.append(property)

    def remove_property(self, property):
        self.properties.remove(property)

    def pay(self, amount):
        self.cash -= amount

    def receive(self, amount):
        self.cash += amount

class Property:
    def __init__(self, name, cost, rent):
        self.name = name
        self.cost = cost
        self.rent = rent
        self.owner = None
    
    def buy(self, player):
        if self.owner == player:
            player.cash -= self.cost
            self.owner = None
    
    def sell(self, seller, buyer, price):
        if self.owner == seller and seller != buyer:
            seller.cash += price
            buyer.cash -= price
            self.owner = buyer



class GamePiece:
    def __init__(self, player_name, piece_type):
        self.player_name = player_name
        self.piece_type = piece_type
