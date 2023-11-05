import pygame
from pygame.locals import*
import card_test
import random

# NOTE: there are some differences between this implementation and the original ruleset of monopoly, such as:
# you may only escape jail by rolling doubles, can't pay bail to get out
# you have to option to purchase the tile you're standing on before & after rolling, not just after
# players get eliminated as soon as their money turns negative, they do not get an opportunity to sell property to get out of debt
# players are allowed to roll infinitely as long as they keep getting doubles
# there are likely some other minor differences because this is not a 1:1 implementation of monopoly's ruleset

# modified the size to be less, 1000x1000 went off screen for me
size = width, height = (900, 900)

# initializes various things related to the pygame library
pygame.init()
running = True
clock = pygame.time.Clock()
message_end_time = pygame.time.get_ticks() + 3000
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Monopoly")
font = pygame.font.SysFont(None, 20)
gamestate = "title"

# creates board background
boardImg = pygame.image.load('assets/board.png').convert()
boardImg = pygame.transform.scale(boardImg, (int(width*0.7), int(height*0.7)))
board_rect = boardImg.get_rect(center=screen.get_rect().center)


# card test buttons
chancetest = pygame.image.load('assets/chance_test.png').convert()
commtest = pygame.image.load('assets/comm_test.png').convert()
commtest_rect = commtest.get_rect() # Gets dimension of card image for button
chancetest_rect = chancetest.get_rect()

# Create rotated surfaces for the button images
commtest_rotated = pygame.transform.rotate(commtest, 400)
chancetest_rotated = pygame.transform.rotate(chancetest, 45)

# Get the dimensions of the rotated button images
commtest_rotated_rect = commtest_rotated.get_rect()
chancetest_rotated_rect = chancetest_rotated.get_rect()

# Update the position and size of the button rectangles based on the rotated image dimensions
commbutton = pygame.Rect(width*(10/11-0.02)-commtest_rotated_rect.width, height*(1/11+0.02), commtest_rotated_rect.width, commtest_rotated_rect.height)
chancebutton = pygame.Rect(width*(1/11+0.02), height*(10/11-0.02)-chancetest_rotated_rect.height, chancetest_rotated_rect.width, chancetest_rotated_rect.height)

# title screen button
startbutton = pygame.Rect(width/2.9, height/2, int(width*0.3), int(height*0.12))

def to_pointer(value): # dereference with retval[0]
	# places a value inside a size 1 array in order to allow it to be passed by reference, essentially acting as a pointer
	return [value]

class Player:	# attributes: name
	position = 0
	money = 1500
	in_jail = False
	name = ""
	eliminated = False

class PropertyTile:	# attributes: name, color, cost, house price, penalties
	tile_id = 0
	tile_type = "PropertyTile"
	house_count = 0
	owner = None

	name = ""
	color = ""
	cost = 0
	house_price = 0
	penalties = []

	def __init__(self, given_name, given_color, given_cost, given_price, given_penalties):
		self.name = given_name
		self.color = given_color
		self.cost = given_cost
		self.house_price = given_price
		self.penalties = given_penalties

	def draw(self): # draws property tile, consisting of color banner, name, houses, and cost
		if self.owner != None: # shades background of tile depending on which player owns the tile
			if self.owner[0].name == "Player 1":
				pygame.draw.rect(screen, (38, 148, 88), self.outline, 0)
			elif self.owner[0].name == "Player 2":
				pygame.draw.rect(screen, (48, 144, 145), self.outline, 0)
		else: # otherwise just uses the default background color
			pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		pygame.draw.rect(screen, self.banner_c, self.banner, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))
		screen.blit(self.cost_text, (self.outline.centerx-self.cost_text.get_rect().width/2, self.outline.y+height*(1/11)-self.cost_text.get_rect().height))
		if self.house_count == 5: # displays all houses as red to indicate a hotel
			for x in self.house_squares:
				pygame.draw.rect(screen, (186, 31, 0), x, 0)
		else: # otherwise displays each house as green if there's a house, or gray if there's no house
			i = 1
			for x in self.house_squares:
				if i > self.house_count:
					pygame.draw.rect(screen, (58, 63, 71), x, 0)
				else:
					pygame.draw.rect(screen, (23, 163, 60), x, 0)				
				i = i + 1

class RailroadTile:	# attributes: name, cost
	tile_id = 0
	tile_type = "RailroadTile"
	owner = None

	name = ""
	cost = 0

	def __init__(self, given_name, given_cost):
		self.name = given_name
		self.cost = given_cost

	def draw(self): # draws railroad tile, consisting of name & cost
		if self.owner != None: #  shades background of tile depending on which player owns the tile
			if self.owner[0].name == "Player 1":
				pygame.draw.rect(screen, (38, 148, 88), self.outline, 0)
			elif self.owner[0].name == "Player 2":
				pygame.draw.rect(screen, (48, 144, 145), self.outline, 0)
		else:
			pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))
		screen.blit(self.cost_text, (self.outline.centerx-self.cost_text.get_rect().width/2, self.outline.y+height*(1/11)-self.cost_text.get_rect().height))

class CardTile:	# attributes: name (just the card type)
	tile_id = 0
	tile_type = "CardTile"

	name = ""

	def __init__(self, given_name):
		self.name = given_name

	def draw(self): # draws card tile, consisting of just the name
		pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))

class TaxTile:	# attributes: name, penalty
	tile_id = 0
	tile_type = "TaxTile"

	name = ""
	penalty = 0

	def __init__(self, given_name, given_penalty):
		self.name = given_name
		self.penalty = given_penalty

	def draw(self): # draws tax tile, consisting of the name and tax amount
		pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))

class CornerTile:	# attributes: name, sends to prison?
	tile_id = 0
	tile_type = "CornerTile"

	name = ""
	sends_to_prison = False

	def __init__(self, given_name, given_bool):
		self.name = given_name
		self.sends_to_prison = given_bool

	def draw(self): # draws corner tile, consisting of just the name
		pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))

class UtilityTile:	# name, cost
	tile_id = 0
	tile_type = "UtilityTile"
	owner = None

	name = ""
	cost = 0

	def __init__(self, given_name, given_cost):
		self.name = given_name
		self.cost = given_cost

	def draw(self): # draws utility tile, consisting of the name and cost
		if self.owner != None: #  shades background of tile depending on which player owns the tile
			if self.owner[0].name == "Player 1":
				pygame.draw.rect(screen, (38, 148, 88), self.outline, 0)
			elif self.owner[0].name == "Player 2":
				pygame.draw.rect(screen, (48, 144, 145), self.outline, 0)
		else:
			pygame.draw.rect(screen, (57, 196, 150), self.outline, 0)
		screen.blit(self.name_text, (self.outline.centerx-self.name_text.get_rect().width/2, self.outline.y+self.name_text.get_rect().height/3.5))

class Board:
	message_count = 0 	# helps determine the offset of displaying new messages
	mortgage_rate = 0.5	# property cost * mortgage_rate = money received for mortgaging
	monopoly_rate = 2	# rent with 0 houses * monopoly_rate = money received (only applies if you have a monopoly with no houses on the tile)
	railroad_rate = [25, 50, 100, 200]	# cost of rent, depends on how many railroads are owned
	player_turn = 0		# which player's turn it is
	next_turn = 0		# which player is next up
	mode = ""			# if the player is buying/selling houses, or selling property
	tiles = []
	players = []

	def message(self, txt): # displays a message in the middle of the screen with given text
		messagetext = font.render(txt, True, (0, 0, 0))
		screen.blit(messagetext, (boardImg.get_rect().centerx*1.5-messagetext.get_rect().width/2, boardImg.get_rect().centery*1.5-messagetext.get_rect().height/2+(boardImg.get_rect().height*0.035*self.message_count)))
		self.message_count = self.message_count + 1
		pygame.display.flip()
		

	def add_player(self, name): # puts a new player in the game with the given name
		new_player = Player()
		new_player.name = name
		self.players.append(to_pointer(new_player))
    
	def eliminate_player(self, player): # removes a player from the game
		for prop in self.tiles: # frees up all the property they owned
			if prop[0].owner == player:
				prop[0].owner = None
				prop[0].house_count = 0
		player.eliminated = True

	def initialize(self): # adds every tile with corresponding attributes
		self.tiles.append(to_pointer(CornerTile("Go", False)))
		self.tiles.append(to_pointer(PropertyTile("Medit. Ave", "Brown", 60, 50, [2, 10, 30, 90, 160, 250])))
		self.tiles.append(to_pointer(CardTile("Comm Chest")))
		self.tiles.append(to_pointer(PropertyTile("Baltic Ave", "Brown", 60, 50, [4, 20, 60, 180, 320, 450])))
		self.tiles.append(to_pointer(TaxTile("Income Tax", 200)))
		self.tiles.append(to_pointer(RailroadTile("Reading Rail", 200)))
		self.tiles.append(to_pointer(PropertyTile("Oriental Ave", "Cyan", 100, 50, [6, 30, 90, 270, 400, 550])))
		self.tiles.append(to_pointer(CardTile("Chance")))
		self.tiles.append(to_pointer(PropertyTile("Vermont Ave", "Cyan", 100, 50, [6, 30, 90, 270, 400, 550])))
		self.tiles.append(to_pointer(PropertyTile("Conn. Ave", "Cyan", 120, 50, [8, 40, 100, 300, 450, 600])))
		self.tiles.append(to_pointer(CornerTile("Visiting Jail", False)))
		self.tiles.append(to_pointer(PropertyTile("St. Charles", "Pink", 140, 100, [10, 50, 150, 450, 625, 750])))
		self.tiles.append(to_pointer(UtilityTile("Electric Co.", 150)))
		self.tiles.append(to_pointer(PropertyTile("States Ave", "Pink", 140, 100, [10, 50, 150, 450, 625, 750])))
		self.tiles.append(to_pointer(PropertyTile("Virginia Ave", "Pink", 160, 100, [12, 60, 180, 500, 700, 900])))
		self.tiles.append(to_pointer(RailroadTile("Penn. Rail", 200)))
		self.tiles.append(to_pointer(PropertyTile("St. James", "Orange", 180, 100, [14, 70, 200, 550, 750, 950])))
		self.tiles.append(to_pointer(CardTile("Comm Chest")))
		self.tiles.append(to_pointer(PropertyTile("Tenn. Ave", "Orange", 180, 100, [14, 70, 200, 550, 750, 950])))
		self.tiles.append(to_pointer(PropertyTile("New York St.", "Orange", 200, 100, [16, 80, 220, 600, 800, 1000])))
		self.tiles.append(to_pointer(CornerTile("Free Parking", False)))
		self.tiles.append(to_pointer(PropertyTile("Kent. Ave", "Red", 220, 150, [18, 90, 250, 700, 875, 1050])))
		self.tiles.append(to_pointer(CardTile("Chance")))
		self.tiles.append(to_pointer(PropertyTile("Indiana Ave", "Red", 220, 150, [18, 90, 250, 700, 875, 1050])))
		self.tiles.append(to_pointer(PropertyTile("Illinois Ave", "Red", 240, 150, [20, 100, 300, 750, 925, 1100])))
		self.tiles.append(to_pointer(RailroadTile("B&O Rail", 200)))
		self.tiles.append(to_pointer(PropertyTile("Atlantic Ave", "Yellow", 260, 150, [22, 110, 330, 800, 975, 1150])))
		self.tiles.append(to_pointer(PropertyTile("Ventnor Ave", "Yellow", 260, 150, [22, 110, 330, 800, 975, 1150])))
		self.tiles.append(to_pointer(UtilityTile("Water Works", 150)))
		self.tiles.append(to_pointer(PropertyTile("Marvin Ave", "Yellow", 280, 150, [24, 120, 360, 850, 1025, 1200])))
		self.tiles.append(to_pointer(CornerTile("Go to Jail", True)))
		self.tiles.append(to_pointer(PropertyTile("Pacific Ave", "Green", 300, 200, [26, 130, 390, 900, 1100, 1275])))
		self.tiles.append(to_pointer(PropertyTile("NC Ave", "Green", 300, 200, [26, 130, 390, 900, 1100, 1275])))
		self.tiles.append(to_pointer(CardTile("Comm Chest")))
		self.tiles.append(to_pointer(PropertyTile("Pacific Ave", "Green", 320, 200, [28, 150, 450, 1000, 1200, 1400])))
		self.tiles.append(to_pointer(RailroadTile("Short Line", 200)))
		self.tiles.append(to_pointer(CardTile("Chance")))
		self.tiles.append(to_pointer(PropertyTile("Park Place", "Blue", 350, 200, [35, 175, 500, 1100, 1300, 1500])))
		self.tiles.append(to_pointer(TaxTile("Luxury Tax", 75)))
		self.tiles.append(to_pointer(PropertyTile("Boardwalk", "Blue", 400, 200, [50, 200, 600, 1400, 1700, 2000])))

	def draw_chest(self, player): # draws a card from the chest pile, has various effects/messages
		num = random.randint(0, len(card_test.chestcards)-1)
		self.message("Hit a Chest tile: " + card_test.chestcards[num])
		clock.tick(1/2)
		if num == 0: # advances to go, gets $200 bonus for it
			player[0].position = 0
			player[0].money = player[0].money + 200
		elif num == 1: # gets free $200
			player[0].money = player[0].money + 200
		elif num == 2: # loses $50
			player[0].money = player[0].money - 50
		elif num == 3: # gains $50
			player[0].money = player[0].money + 50
		elif num == 4: # goes to jail
			player[0].in_jail = True
			player[0].position = 10
		elif num == 5: # gains $100
			player[0].money = player[0].money + 100
		elif num == 6: # gains $20
			player[0].money = player[0].money + 20
		elif num == 7: # takes $10 from all other non-eliminated players
			for plr in self.players:
				if plr != player and plr[0].eliminated == False:
					plr[0].money = plr[0].money - 10
					player[0].money = player[0].money + 10
		elif num == 8: # gains $100
			player[0].money = player[0].money + 100
		elif num == 9: # loses $100
			player[0].money = player[0].money - 100
		elif num == 10: # loses $50
			player[0].money = player[0].money - 50
		elif num == 11: # loses $25
			player[0].money = player[0].money - 25
		elif num == 12: # charged $40 for every owned house, and $115 for every owned hotel
			fee = 0
			for tile in self.tiles:
				if tile[0].tile_type == "PropertyTile" and tile[0].owner == player:
					if tile[0].house_count == 5:
						fee = fee + 115
					else:
						fee = fee + tile[0].house_count*40
			player[0].money = player[0].money - fee
		elif num == 13: # gains $10
			player[0].money = player[0].money + 10
		elif num == 14: # gains $100
			player[0].money = player[0].money + 100

	def draw_chance(self, player): # draws card from chance pile, with various effects/messages
		num = random.randint(0, len(card_test.chancecards)-1)
		self.message("Hit a Chance tile: " + card_test.chancecards[num])
		clock.tick(1/2)
		if num == 0: # goes to boardwalk
			player[0].position = 39
		elif num == 1: # advances to go, gets $200 bonus
			player[0].position = 0
			player[0].money = player[0].money + 200
		elif num == 2: # advances to tile 24, receiving $200 if they pass go to do so
			if player[0].position > 24:
				player[0].money = player[0].money + 200
			player[0].position = 24
		elif num == 3: # advances to tile 11, receiving $200 if they pass go to do so
			if player[0].position > 11:
				player[0].money = player[0].money + 200
			player[0].position = 11
		elif num == 4: # goes to nearest railroad tile
			shortest_distance = 50
			assoc_tile = None
			for tile in self.tiles:
				if tile[0].tile_type == "RailroadTile":
					new_distance = abs(player[0].position - tile[0].tile_id)
					if new_distance < shortest_distance:
						shortest_distance = new_distance
						assoc_tile = tile
			player[0].position = assoc_tile[0].tile_id
		elif num == 5: # goes to nearest utility tile
			shortest_distance = 50
			assoc_tile = None
			for tile in self.tiles:
				if tile[0].tile_type == "UtilityTile":
					new_distance = abs(player[0].position - tile[0].tile_id)
					if new_distance < shortest_distance:
						shortest_distance = new_distance
						assoc_tile = tile
			player[0].position = assoc_tile[0].tile_id
		elif num == 6: # gets free $50
			player[0].money = player[0].money + 50
		elif num == 7: # goes back 3 tiles
			new_position = player[0].position - 3
			if new_position < 0:
				player[0].position = new_position + 40
			else:
				player[0].position = new_position
		elif num == 8: # goes to jail
			player[0].in_jail = True
			player[0].position = 10
		elif num == 9: # must pay $100 for every hotel, and $35 for every house
			fee = 0
			for tile in self.tiles:
				if tile[0].tile_type == "PropertyTile" and tile[0].owner == player:
					if tile[0].house_count == 5:
						fee = fee + 100
					else:
						fee = fee + tile[0].house_count*35
			player[0].money = player[0].money - fee
		elif num == 10: # loses $15
			player[0].money = player[0].money - 15
		elif num == 11: # advances to tile 5, receiving $200 if they pass go to do so
			if player[0].position > 5:
				player[0].money = player[0].money + 200
			player[0].position = 5
		elif num == 12: # pay $50 to every other non-eliminated player
			for plr in self.players:
				if plr != player and plr[0].eliminated == False:
					plr[0].money = plr[0].money + 50
					player[0].money = player[0].money - 50
		elif num == 13: # gains $150
			player[0].money = player[0].money + 150

	def to_jail(self, player): # sends player to jail
		player[0].in_jail = True
		player[0].position = 10

	def has_monopoly(self, player, color): # determines if a player has a monopoly over a certain color
		validity = True
		for prop in self.tiles:
			if (prop[0].tile_type == "PropertyTile") and prop[0].color == color:
				if prop[0].owner != player:
					validity = False
		return validity

	def railroads_owned(self, player): # gets number of railroads owned by a player
		railroads = 0
		for prop in self.tiles:
			if (prop[0].tile_type == "RailroadTile") and prop[0].owner == player:
				railroads = railroads + 1
		return railroads

	def utilities_owned(self, player): # gets number of utilities owned by a player
		utilities = 0
		for prop in self.tiles:
			if (prop[0].tile_type == "UtilityTile") and prop[0].owner == player:
				utilities = utilities + 1
		return utilities

	def get_player(self, player_name): # retrieves a player pointer based on a player name
		for plr in self.players:
			if plr[0].name == player_name:
				return plr

	def buy_property(self, player, property): # attempts to purchase a given tile for the given player
		if property[0].tile_type == "PropertyTile" or property[0].tile_type == "RailroadTile" or property[0].tile_type == "UtilityTile":
			if player[0].money >= property[0].cost and property[0].owner == None:
				self.message("Bought")
				player[0].money = player[0].money - property[0].cost
				property[0].owner = player
			else:
				self.message("Can't buy")
				clock.tick(1/0.5)

	def sell_property(self, player, property): # attempts to sell a given tile from the given player
		if (property[0].tile_type == "PropertyTile" or property[0].tile_type == "RailroadTile" or property[0].tile_type == "UtilityTile") and property[0].owner == player:
			if property[0].tile_type == "PropertyTile": # if it's a colored tile, check to see if the player has a monopoly
				if self.has_monopoly(player, property[0].color): # if so, it forces the player to sell all other houses
					for prop in self.tiles:
						if prop[0].tile_type == "PropertyTile" and prop[0].color == property[0].color:
							player[0].money = player[0].money + (self.mortgage_rate * prop[0].house_price * prop[0].house_count)
							prop[0].house_count = 0
			player[0].money = player[0].money + (self.mortgage_rate * property[0].cost)
			property[0].owner = None

	def buy_house(self, player, property): # attempts to buy a house on the given property for a player
		if player[0].money >= property[0].house_price and self.has_monopoly(player, property[0].color) and property[0].house_count < 5:
			property[0].house_count = property[0].house_count + 1
			player[0].money = player[0].money - property[0].house_price

	def sell_house(self, player, property): # attempts to sell a house on the given property for a player
		if property[0].house_count > 0:
			player[0].money = player[0].money + (property[0].house_price * self.mortgage_rate)
			property[0].house_count = property[0].house_count - 1

	def roll_dice(self, player): # rolls dice and causes events to happen depending on where the player ends up
		roll1 = random.randint(1, 6)
		roll2 = random.randint(1, 6)

		self.message(player[0].name + " rolled " + str(roll1) + " & " + str(roll2))
		clock.tick(1/1.5)

		total_roll = roll1 + roll2
		if player[0].in_jail == True: # breaks player out of jail if they roll doubles
			if roll1 == roll2:
				player[0].in_jail = False
			else:
				return False

		initial_pos = player[0].position
		new_pos = initial_pos + total_roll

		if new_pos >= 40:	# passing go, collect 200
			new_pos = new_pos - 40
			player[0].money = player[0].money + 200

		player[0].position = new_pos
		landed_on = self.tiles[new_pos]

		if landed_on[0].tile_type == "PropertyTile" or landed_on[0].tile_type == "RailroadTile" or landed_on[0].tile_type == "UtilityTile":
			if landed_on[0].owner == None:
				pass
			elif landed_on[0].owner != player:
				# pay rent to owner of the tile
				rent_cost = 0
				if landed_on[0].tile_type == "PropertyTile": # rent based on how many houses there are (or aren't) on the tile
					num_houses = landed_on[0].house_count
					if num_houses == 0 and self.has_monopoly(landed_on[0].owner, landed_on[0].color):
						rent_cost = landed_on[0].penalties[0] * self.monopoly_rate
					else:
						rent_cost = landed_on[0].penalties[num_houses]
				elif landed_on[0].tile_type == "RailroadTile": # rent based on how many railroads are owned by the player
					railroads = self.railroads_owned(landed_on[0].owner)
					rent_cost = self.railroad_rate[railroads-1]
				elif landed_on[0].tile_type == "UtilityTile": # rent based on how many utilities are owned by the player, and the roll of the dice
					utilities = self.utilities_owned(landed_on[0].owner)
					if utilities == 1:
						rent_cost = total_roll * 4
					elif utilities == 2:
						rent_cost = total_roll * 10

				if player[0].money - rent_cost < 0: # makes sure the money that puts the player negative can't go to the other player
					landed_on[0].owner[0].money = landed_on[0].owner[0].money + player[0].money
				else:
					landed_on[0].owner[0].money = landed_on[0].owner[0].money + rent_cost

				player[0].money = player[0].money - rent_cost # pays the actual rent now
				self.message("Paid $" + str(rent_cost) + " of rent to " + landed_on[0].owner[0].name)
		elif landed_on[0].tile_type == "TaxTile": # just costs the player based on the tax amount of the tile
			rent_cost = landed_on[0].penalty
			player[0].money = player[0].money - rent_cost
			self.message("Paid $" + str(rent_cost) + " of rent")
		elif landed_on[0].tile_type == "CornerTile" and landed_on[0].sends_to_prison == True: # send to prison if the tile dictates it
			self.to_jail(player)
		elif landed_on[0].tile_type == "CardTile": # draw a chest or chance card depending on the tile
			if landed_on[0].name == "Comm Chest":
				self.draw_chest(player)
			elif landed_on[0].name == "Chance":
				self.draw_chance(player)
		
		if roll1 == roll2: # code that calls this function will use ret value to determine whether or not they get to immediately roll again
			return True
		else:
			return False

game = Board()
game.initialize()
game.add_player("Player 1")
game.add_player("Player 2")

# buttons used for interacting with the board
dicebutton = pygame.Rect(width*(1/11+0.02), height*(1/11+0.02), width*0.2, height*0.06)
dicebutton_text = font.render("Roll dice", True, (0, 0, 0))

turnbutton = pygame.Rect(width*(0.2+1/11+0.04), height*(1/11+0.02), width*0.2, height*0.06)
turnbutton_text = font.render("Go to next player's turn", True, (0, 0, 0))

bpropbutton = pygame.Rect(width*(1/11+0.02), height*(0.06+1/11+0.04), width*0.2, height*0.06)
bpropbutton_text = font.render("Buy property", True, (0, 0, 0))

spropbutton = pygame.Rect(width*(0.2+1/11+0.04), height*(0.06+1/11+0.04), width*0.2, height*0.06)
spropbutton_text = font.render("Sell property", True, (0, 0, 0))

bhousebutton = pygame.Rect(width*(1/11+0.02), height*(0.12+1/11+0.06), width*0.2, height*0.06)
bhousebutton_text = font.render("Buy house", True, (0, 0, 0))

shousebutton = pygame.Rect(width*(0.2+1/11+0.04), height*(0.12+1/11+0.06), width*0.2, height*0.06)
shousebutton_text = font.render("Sell house", True, (0, 0, 0))

def draw_buttons():
	# Load button images and rotate them
	commtest = pygame.image.load('assets/comm_test.png').convert_alpha()
	commtest = pygame.transform.rotate(commtest, 45)
	commtest.set_colorkey((0, 0, 0)) # sets black as the transparent color
	chancetest = pygame.image.load('assets/chance_test.png').convert_alpha()
	chancetest = pygame.transform.rotate(chancetest, 45)
	chancetest.set_colorkey((0, 0, 0)) # sets black as the transparent color

	# Blit button images to the screen
	screen.blit(commtest, (commbutton.x, commbutton.y))
	screen.blit(chancetest, (chancebutton.x, chancebutton.y))

	# Draw button rectangles to see where buttons are
	pygame.draw.rect(screen, (255, 0, 0), commbutton, -1)
	pygame.draw.rect(screen, (255, 0, 0), chancebutton, -1)

	player = game.players[game.player_turn]
	tile = game.tiles[player[0].position]
	if (tile[0].tile_type == "PropertyTile" or tile[0].tile_type == "UtilityTile" or tile[0].tile_type == "RailroadTile") and tile[0].owner == None:
		# only prompts player to buy a tile if it's purchasable and has no owner
		pygame.draw.rect(screen, (0, 255, 0), bpropbutton, 0)
		screen.blit(bpropbutton_text, (bpropbutton.centerx-bpropbutton_text.get_rect().width/2, bpropbutton.centery-bpropbutton_text.get_rect().height/2))

	# only displays prompt for buying houses if the player has at least 1 monopoly
	clrs = ["Brown", "Cyan", "Pink", "Orange", "Yellow", "Green", "Blue", "Red"]
	for c in clrs:
		if game.has_monopoly(player, c):
			pygame.draw.rect(screen, (0, 255, 0), bhousebutton, 0)
			screen.blit(bhousebutton_text, (bhousebutton.centerx-bhousebutton_text.get_rect().width/2, bhousebutton.centery-bhousebutton_text.get_rect().height/2))
			break

	# just displays the other 2 buttons
	pygame.draw.rect(screen, (255, 0, 0), spropbutton, 0)
	screen.blit(spropbutton_text, (spropbutton.centerx-spropbutton_text.get_rect().width/2, spropbutton.centery-spropbutton_text.get_rect().height/2))

	pygame.draw.rect(screen, (255, 0, 0), shousebutton, 0)
	screen.blit(shousebutton_text, (shousebutton.centerx-shousebutton_text.get_rect().width/2, shousebutton.centery-shousebutton_text.get_rect().height/2))

	# either lets player roll dice or pass on their turn, based on whether or not they get to go next
	if(game.player_turn == game.next_turn):
		pygame.draw.rect(screen, (255, 255, 255), dicebutton, 0)
		screen.blit(dicebutton_text, (dicebutton.centerx-dicebutton_text.get_rect().width/2, dicebutton.centery-dicebutton_text.get_rect().height/2))
	else:
		pygame.draw.rect(screen, (255, 255, 255), turnbutton, 0)
		screen.blit(turnbutton_text, (turnbutton.centerx-turnbutton_text.get_rect().width/2, turnbutton.centery-turnbutton_text.get_rect().height/2))

for i in range(40):
	tile = game.tiles[i]
	tile[0].tile_id = i

	# gets positions for each tile along the edge of the board
	if i >= 0 and i < 10:
		xpos = width*(i/11)
		ypos = height*0
	elif i >= 10 and i < 20:
		xpos = width*(10/11)
		ypos = height*(i-10)/11
	elif i >= 20 and i < 30:
		xpos = width*(10-(i-20))/11
		ypos = height*(10/11)
	elif i >= 30 and i < 40:
		xpos = width*0
		ypos = height*(10-(i-30))/11
	
	# assigns name text & background objects to the tile
	tile[0].outline = pygame.Rect(xpos, ypos, width/11, width/11)
	tile[0].name_text = font.render(tile[0].name, True, (0, 0, 0))

	# gets color for the banner of a property tile
	if tile[0].tile_type == "PropertyTile":
		if tile[0].color == "Brown":
			banner_color = (112, 74, 20)
		elif tile[0].color == "Cyan":
			banner_color = (56, 255, 248)
		elif tile[0].color == "Pink":
			banner_color = (255, 0, 208)
		elif tile[0].color == "Orange":
			banner_color = (255, 111, 0)
		elif tile[0].color == "Red":
			banner_color = (255, 0, 0)
		elif tile[0].color == "Yellow":
			banner_color = (251, 255, 0)
		elif tile[0].color == "Green":
			banner_color = (0, 135, 7)
		elif tile[0].color == "Blue":
			banner_color = (4, 0, 255)
		
		# assigns drawing-related objects & values to the tile it's associated with
		tile[0].banner = pygame.Rect(xpos, ypos, width/11, width/11/4)
		tile[0].banner_c = banner_color
		tile[0].cost_text = font.render("$" + str(tile[0].cost), True, (0, 0, 0))

		# also adds house icons to the tile it's associated with
		squares = []
		for j in range(4):
			squares.append(pygame.Rect(xpos, ypos+width/11/4+(width/11*(3/4)/4)*j, width/11*(3/4)/4, width/11*(3/4)/4))
		tile[0].house_squares = squares
	elif tile[0].tile_type == "RailroadTile":
		# assigns cost text object to the tile
		tile[0].cost_text = font.render("$" + str(tile[0].cost), True, (0, 0, 0))
	elif tile[0].tile_type == "TaxTile":
		# assigns tax text object to the tile
		tile[0].tax_text = font.render("$" + str(tile[0].penalty), True, (0, 0, 0))

def draw_board():
	# Load the board image and scale it to the size of the screen
	boardImg = pygame.image.load('assets/board.png')
	boardImg = pygame.transform.scale(boardImg, (width, height))
	screen.blit(boardImg, (0, 0)) # Blit the board image onto the screen

	# calls tile type-specific draw function on each tile
	for i in range(40):
		tile = game.tiles[i]
		tile[0].draw()

	loops = 0
	for player in game.players:
		tile = game.tiles[player[0].position]

		# displays player's position on the board with a black label
		if player == game.players[0]:
			player_piece = pygame.Rect(tile[0].outline.x+(width/11)*0.228125, tile[0].outline.y+(width/11)/4+5, (width/11)*0.73125, 15)
		else:
			player_piece = pygame.Rect(tile[0].outline.x+(width/11)*0.228125, tile[0].outline.y+(width/11)/4+25, (width/11)*0.73125, 15)
		pygame.draw.rect(screen, (0, 0, 0), player_piece, 0)

		# writes player's name on their label on the board
		player_text = font.render(player[0].name, True, (255, 255, 255))
		screen.blit(player_text, (player_piece.x, player_piece.y))

		# writes out each player's name and money
		money_indicator = font.render(player[0].name + ": " + str(player[0].money), True, (0, 0, 0))
		screen.blit(money_indicator, (boardImg.get_rect().width*0.45, boardImg.get_rect().height*(0.75 + 0.02*loops)))
		loops = loops + 1
	
	# display's which player's turn it is
	nmtxt = font.render(game.players[game.player_turn][0].name + "'s turn", True, (0, 255, 0))
	screen.blit(nmtxt, (boardImg.get_rect().width*0.45, boardImg.get_rect().height*(0.75 + 0.02*len(game.players))))

	# displays which mode (selling houses, selling property, or buying houses) the player is in
	modetxt = font.render(game.mode, True, (255, 0, 0))
	screen.blit(modetxt, (boardImg.get_rect().width*0.45, boardImg.get_rect().height*(0.75 + 0.02*(1+len(game.players)))))

def draw_title():
	# Load the title bg image and scale it to the size of the screen
	titlebg = pygame.image.load('assets/titlebg.png')
	titlebg = pygame.transform.scale(titlebg, (width, height))
	screen.blit(titlebg, (0, 0)) # Blit the board image onto the screen
		
	# Load title image and start button
	titlelogo = pygame.image.load('assets/title.png')
	titlebutton = pygame.image.load('assets/titlestart.png')
	titlelogo = pygame.transform.scale(titlelogo, (int(width*0.72), int(height*0.2)))
	titlebutton = pygame.transform.scale(titlebutton, (int(width*0.3), int(height*0.12)))

	# Blit button images to the screen
	screen.blit(titlelogo, (width/7, height/4))
	screen.blit(titlebutton, (width/2.9, height/2))

pygame.display.update()

game.buy_property(game.players[0], game.tiles[37])
game.buy_property(game.players[0], game.tiles[39])

i = 1
dice_clicked = False # these are used to prevent double clicking a button before code is finished running
turn_clicked = False
bprop_clicked = False
sprop_clicked = False
bhouse_clicked = False
shouse_clicked = False
while running:
	pygame.display.flip()  # refresh screen
	game.message_count = 0
	clock.tick(60)         # wait until next frame (60 fps)
	current_time = pygame.time.get_ticks()

	if gamestate == "title":
		# draw title
		draw_title()
	else:
		# draw board each frame
		draw_board()

		# draw buttons each frame
		draw_buttons()

	#event checker
	for event in pygame.event.get():
		if event.type == QUIT:
			running = False

		# click start button
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:           
			if startbutton.collidepoint(pygame.mouse.get_pos()):
				gamestate = "main"

		# putting in card draw test stuff
		# draw from chance
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:      
			player = game.players[game.player_turn]     
			if dicebutton.collidepoint(pygame.mouse.get_pos()) and game.next_turn == game.player_turn and dice_clicked == False:
				# rolls dice, lets player repeat their move
				dice_clicked = True
				result = game.roll_dice(player)
				if result == False:
					game.next_turn = game.player_turn + 1
				if game.next_turn == len(game.players):
					game.next_turn = 0
			elif turnbutton.collidepoint(pygame.mouse.get_pos()):
				# switch turns
				if turn_clicked == False:
					turn_clicked = True
					game.player_turn = game.next_turn
			elif bpropbutton.collidepoint(pygame.mouse.get_pos()):
				# buy property that the player is stationed on
				if bprop_clicked == False:
					bprop_clicked = True
					game.buy_property(player, game.tiles[player[0].position])
			elif spropbutton.collidepoint(pygame.mouse.get_pos()):
				# switch mode for selling property
				if sprop_clicked == False:
					sprop_clicked = True
					if game.mode != "MODE: Selling Property (click a property to sell it)":
						game.mode = "MODE: Selling Property (click a property to sell it)"
					elif game.mode == "MODE: Selling Property (click a property to sell it)":
						game.mode = ""
			elif bhousebutton.collidepoint(pygame.mouse.get_pos()):
				# switch to mode for buying houses
				if bhouse_clicked == False:
					bhouse_clicked = True
					if game.mode != "MODE: Buying House (click a property to buy a house for it)":
						game.mode = "MODE: Buying House (click a property to buy a house for it)"
					elif game.mode == "MODE: Buying House (click a property to buy a house for it)":
						game.mode = ""
			elif shousebutton.collidepoint(pygame.mouse.get_pos()):
				# switch to mode for selling houses
				if shouse_clicked == False:
					shouse_clicked = True
					if game.mode != "MODE: Selling House (click a property to sell one of its houses)":
						game.mode = "MODE: Selling House (click a property to sell one of its houses)"
					elif game.mode == "MODE: Selling House (click a property to sell one of its houses)":
						game.mode = ""

			for t in game.tiles:
				if game.mode == "MODE: Selling Property (click a property to sell it)":
					# clicking a tile will sell it if you own the tile
					if (t[0].tile_type == "PropertyTile" or t[0].tile_type == "UtilityTile" or t[0].tile_type == "RailroadTile") and t[0].owner != None:
						if t[0].outline.collidepoint(pygame.mouse.get_pos()):
							game.sell_property(player, t)
				elif game.mode == "MODE: Buying House (click a property to buy a house for it)":
					# clicking a tile will place a house on it if it's part of your monopoly
					if t[0].tile_type == "PropertyTile" and t[0].owner != None:
						if t[0].outline.collidepoint(pygame.mouse.get_pos()):
							game.buy_house(player, t)
				elif game.mode == "MODE: Selling House (click a property to sell one of its houses)":
					if t[0].tile_type == "PropertyTile" and t[0].owner != None:
						if t[0].outline.collidepoint(pygame.mouse.get_pos()):
							game.sell_house(player, t)

	for plr in game.players:
		if plr[0].money < 0:
			plr[0].eliminated = True
			game.message(plr[0].name + " has lost!")
			clock.tick(1/4)
			pygame.quit()

	pygame.display.flip() # clear screen
	dice_clicked = False
	turn_clicked = False
	bprop_clicked = False
	sprop_clicked = False
	bhouse_clicked = False
	shouse_clicked = False

pygame.quit()
