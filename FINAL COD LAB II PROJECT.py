from tkinter import *
from PIL import Image, ImageTk
import cv2
import requests
from io import BytesIO
import random
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter import ttk
import webbrowser

#*************************************  Funtctions  ******************************************************************************#


#Updates The Video in the Video Frame
def update_video():
    ret, frame = cap.read()
    if ret:
        # Convert OpenCV BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to PhotoImage object and update the label
        img = ImageTk.PhotoImage(Image.fromarray(rgb_frame))
        video_label.img = img
        video_label.config(image=img)

        # Call update_video again after a delay (in milliseconds)
        root.after(33, update_video)
    else:
        # Restart the video when it reaches the end
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


# Generating the Pokemon in Game Frame
class Pokemon:
    # Calling attributes of the pokemon for it's placement in the window or frame
    def __init__(self, frame, x, y):
        self.frame = frame
        # Image Frame
        self.image_label = Label(frame, bg="#111111", fg="#F8EC99")
        self.image_label.place(x=x, y=y)

        #Information Label
        self.information_label = Label(frame, text='', bg="#111111", fg="#F8EC99")
        self.information_label.place(y=y + 220, x=x + 20)

        # Calling another function from inside the class
        self.generate_random_pokemon()


    # Pokemon Generator
    def generate_random_pokemon(self):

        #Random Function to generate random number for the pokemon id
        random_pok_id = random.randint(1, 898)

        #Importing the API URL
        api_url_link = f'https://pokeapi.co/api/v2/pokemon/{random_pok_id}/'

        # Make a request to the API
        response = requests.get(api_url_link)

        # Checking status code from the request library, it returns a number that indicates the status ie. 200 when working 404 when not working
        if response.status_code == 200:
            # Parsing data from the JSON file
            pokemon_data = response.json()

            # Using capitalize function to display the name in capital alphabets
            # Extracting from pokemon_data
            self.name = pokemon_data['name'].capitalize()
            self.types = ','.join([t['type']['name'].capitalize() for t in pokemon_data['types']])
            self.base_experience = pokemon_data['base_experience']
            self.stats = '\n '.join([f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}" for stat in
                                     pokemon_data['stats']])

            # Extract generation information from species endpoint
            species_url = pokemon_data['species']['url']
            species_response = requests.get(species_url)
            species_data = species_response.json()
            self.generation = species_data['generation']['name'].capitalize()

            # Fetch the image from the URL
            image_url = pokemon_data['sprites']['front_default']
            image_response = requests.get(image_url)
            image_data = Image.open(BytesIO(image_response.content))
            image_data = image_data.resize((200, 200))
            # Convert the image to Tkinter PhotoImage
            self.image_tk = ImageTk.PhotoImage(image_data)

            self.image_label.config(image=self.image_tk)
            self.image_label.image = self.image_tk
            self.information_label.config(
                text=f'Name: {self.name} \n Type: {self.types} \n Base Experience : {self.base_experience} \n Stats: {self.stats} \n Generation: {self.generation}')

        else:
            #Show Error
            messagebox.showerror('Error', 'Pokemon refused to show up. Try again.')

# When the Pokemon attacks another Pokemon
def ATTACK():
    # Get base experience of each player's Pokemon
    player1_base_experience = player1_pokemon.base_experience
    player2_base_experience = player2_pokemon.base_experience

    # Extract and convert stats to integers
    player1_stats = int(''.join(filter(str.isdigit, player1_pokemon.stats)))
    player2_stats = int(''.join(filter(str.isdigit, player2_pokemon.stats)))

    total_player1_strength = player1_base_experience + player1_stats
    total_player2_strength = player2_base_experience + player2_stats

    # Determine the winner based on total strength
    if total_player1_strength > total_player2_strength:
        winner_message = f"{player1_pokemon.name} WINS!!"
    elif total_player1_strength < total_player2_strength:
        winner_message = f"{player2_pokemon.name} WINS!!"
    else:
        # If the Total Strength is same
        winner_message = "It's a tie! Both Pokémon have the same total strength."

    # Show the winner message in a messagebox
    messagebox.showinfo("Battle Result", winner_message)


# Function to retrieve Pokemon data from the PokeAPI based on its ID or name
def get_pokemon_data(identifier, by_name=False):
    # Importing API URL
    base_url = 'https://pokeapi.co/api/v2/pokemon/'
    
    # Constructing the URL based on whether the search is by name or ID
    if by_name:
        url = f'{base_url}{identifier.lower()}/'
    else:
        url = f'{base_url}{identifier}/'
    
    # Sending a GET request to the PokeAPI
    response = requests.get(url)
    
    # Checking if the request was successful (status code 200)
    if response.status_code == 200:
        # Parsing the JSON response
        pokemon_data = response.json()
        return pokemon_data
    else:
        # Returning None if the request was not successful
        return None

    

#SEARCH POKEMON
def display_pokemon_info(identifier, by_name=False):
    # Retrieve Pokemon data based on the identifier (either name or ID)
    pokemon_data = get_pokemon_data(identifier, by_name)

    if pokemon_data:
        # Extract relevant information from the Pokemon data
        name = pokemon_data.get('name', '').capitalize()
        types = [t['type']['name'].capitalize() for t in pokemon_data.get('types', [])]

        abilities = [ability['ability']['name'].capitalize() for ability in pokemon_data.get('abilities', [])]
        hidden_ability = next((ability['ability']['name'].capitalize() for ability in pokemon_data.get('abilities', []) if ability.get('is_hidden')), None)

        # Convert weight from hectograms to kilograms
        weight = pokemon_data.get('weight', 0) / 10.0
        base_experience = pokemon_data.get('base_experience', 0)
        
        # Get the generation of the Pokemon based on its species URL
        generation = get_generation_from_species(pokemon_data.get('species', {}).get('url', ''))

        # Retrieve the URL for the Pokemon's front image and display it in a label
        image_url = pokemon_data.get('sprites', {}).get('front_default', '')
        if image_url:
            image = Image.open(requests.get(image_url, stream=True).raw)
            image = image.resize((300, 300))
            image = ImageTk.PhotoImage(image)
            image_label.config(image=image)
            image_label.image = image
        else:
            # If no image URL is found, set the image label to None
            image_label.config(image=None)

        # Construct the text with Pokemon information
        info_text = f"Name: {name}\n"
        info_text += f"Type: {', '.join(types)}\n"
        info_text += f"Ability (Hidden): {hidden_ability}\n" if hidden_ability else ""
        info_text += f"Abilities: {', '.join(abilities)}\n"
        info_text += f"Weight: {weight} kg\n"
        info_text += f"Base Experience: {base_experience}\n"
        info_text += f"Generation: {generation}\n"

        # Update the result label with the constructed Pokemon information
        result_label.config(text=info_text)
    else:
        # If Pokemon data is not found, update the result label with an error message
        result_label.config(text="Pokemon data not found.")


def show_pokemon_info():
    # Get the search value from the entry widget
    search_value = search_entry.get()
    
    # Get the selected search type from the dropdown menu
    search_type = search_type_var.get()
    
    # Check if the search type is "ID" or "Name"
    if search_type == "ID":
        # Call the display_pokemon_info function with the ID as input
        info_text = display_pokemon_info(search_value)
    else:
        # Call the display_pokemon_info function with the Name and by_name set to True
        info_text = display_pokemon_info(search_value, by_name=True)
    
    # Configure the result label to display the retrieved information with a specific background color
    result_label.config(text=info_text, bg='#036094')




def get_generation_from_species(species_url):
    # Make a GET request to the species URL
    species_response = requests.get(species_url)
    
    # Check if the request was successful (status code 200)
    if species_response.status_code == 200:
        # Parse the JSON data from the response
        species_data = species_response.json()
        
        # Extract the generation name from the species data, capitalize it, and return
        generation = species_data.get('generation', {}).get('name', '').capitalize()
        return generation
    else:
        # Return "Unknown" if the request was not successful
        return "Unknown"

def update_pokkball_image():
    # Open the pokeball image file
    pokeball_image = Image.open('pball.png')
    
    # Resize the pokeball image to 350x350 pixels
    pokeball_image = pokeball_image.resize((350, 350))
    
    # Convert the resized image to a PhotoImage object
    pokeball_image = ImageTk.PhotoImage(pokeball_image)
    
    # Update the image of the 'pokkball' (assuming 'pokkball' is a tkinter Label widget)
    pokkball.config(image=pokeball_image)
    
    # Keep a reference to the PhotoImage to prevent it from being garbage collected
    pokkball.image = pokeball_image

# Items Loading
def load_items(item_listbox):
    # Fetch item data from the PokeAPI
    data = requests.get('https://pokeapi.co/api/v2/item?limit=20').json()

    # Display item names in the listbox
    for item in data['results']:
        item_listbox.insert(END, item['name'])


# Fetching Information when the item is clicked upon
def show_item_details(item_listbox, description_label, image_lab):
    selected_item_index = item_listbox.curselection()
    if selected_item_index:
        selected_item_name = item_listbox.get(selected_item_index)

        # Fetch detailed item data
        item_data = requests.get(f'https://pokeapi.co/api/v2/item/{selected_item_name}/').json()

        # Update the description label
        description_text = f"Name: {item_data['name']}\n\n"
        description_text += f"Category: {item_data['category']['name']}\n\n"

        description_text += f"Effect: {item_data.get('effect_entries', [{}])[0].get('effect', '')}\n\n"
        description_text += f"Fling Power: {item_data.get('fling_power', '')}\n\n"

        attributes = ', '.join(attr['name'] for attr in item_data.get('attributes', []))
        description_text += f"Attributes: {attributes}\n\n"

        description_label.config(text=description_text)

        # Load and display item image
        image_url = item_data['sprites'].get('default', '')
        if image_url:
            image = Image.open(requests.get(image_url, stream=True).raw)
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)
            image_lab.config(image=photo)
            image_lab.image = photo

#Instructions For every Frame
def Game_Instruction():
    game_frame.tkraise()
    messagebox.showinfo('How to Play','2 Pokemons are already generated. \nYou can change your pokemon from buttons. \n Stronger one will win ')

def Pokemon_Search_Instruction():
    pokemon_frame.tkraise()
    messagebox.showinfo('Instructions','You can Search Pokemon from their ID \nor Change it to Name and search it from their name')

def Item_Search():
    item_frame.tkraise()
    messagebox.showinfo('Instructions','list of Items is provided \n Click on them to see their Information')

def Watch_Link():
    watch_frame.tkraise()
    messagebox.showinfo("Instructions","Click on the Movie Poster to \nWatch the Pokémon and see it's description")


#Links to the web browser link where the user can watch the series of pokemon
def Watch_Pokemon1997():
    webbrowser.open('https://anitaku.to/category/pokemon')

def Watch_Pokemon1999():
    webbrowser.open('https://anitaku.to/category/pokemon-the-movie-2000-dub')

def Watch_Mewtwo():
    webbrowser.open('https://anitaku.to/category/pokemon-mewtwo-returns-dub')

def Watch_PAdvanced():
    webbrowser.open('https://anitaku.to/category/pokemon-advanced-generation-dub')

def Watch_BestWishes():
    webbrowser.open('https://anitaku.to/category/pokemon-best-wishes')




#*************************************  Root         ******************************************************************************#
#*************************************       Window  ******************************************************************************#

# Create the main window
root = Tk()
root.title("Pokemon Attack!")
root.geometry("1400x700")

icon_image = PhotoImage(file='Logo2.png')  # Replace 'path/to/your/icon.gif' with the actual path to your icon file
# Set the window icon using wm_iconphoto
root.wm_iconphoto(True, icon_image)

#*************************************  Initializing Frames  ******************************************************************************#


# Frame for Video 
video_frame = Frame(root, height=700, width=1400, bg="#000")
video_frame.place(x=0, y=0)

#Frame for Menu
menu_frame = Frame(root,width=1400,height=700,bg='#1d2233')
menu_frame.place(x=0,y=0)

# Frame fro Game
game_frame = Frame(root,width=1400, height=600, bg='#111111')
game_frame.place(x=0, y=100)

# Frame for Player 2
game_frame2 = Frame(root, width=1400, height=600, bg='#111111')
game_frame2.place(x=0,y=100)

#Frame for Navigation Bar
NavigationFrame = Frame(menu_frame, height=100, width=1400, bg="#DC0A2D")
NavigationFrame.place(x=0, y=0)

# Frame for Pokemon Search 
pokemon_frame = Frame(root,width=1400,height=600,bg='#111111')
pokemon_frame.place(x=0,y=100)

# Frame for Item Search
item_frame = Frame(root,width=1400,height=600,bg='#111111')
item_frame.place(x=0,y=100)

#Frame fro Item List
items_frame = Frame(item_frame, padx=40, pady=10, height=400, width=200, bg="#111111")
items_frame.place(x=300,y=70)

#Frame for Description
description_frame = Frame(item_frame, padx=50, pady=50,bg='#111111',width=500,height=500)
description_frame.place(x=500,y=45)

#Desription for Watch List of Pokemon
watch_frame = Frame(root,width=1400,height=600,bg='#111111')
watch_frame.place(x=0,y=100)



#*************************************  Video Frame  ******************************************************************************#

# Create a label to display the video without border
video_label = Label(video_frame, bd=0)
video_label.place(x=40, y=0)
# Open the video file using OpenCV
cap = cv2.VideoCapture("pokemon.mp4")  # Replace with the path to your video file
# Start updating the video display
update_video()

# Create a button on top of the video frame
start = Image.open('start.png')
start = ImageTk.PhotoImage(start)
start_button = Button(video_frame, image=start,bg="#000000", bd=0, command=menu_frame.tkraise)
start_button.place(x=500, y=550)

#*************************************  Menu Frame  ******************************************************************************#

# Logo in the Navigation Bar
logo = Image.open('logo.png')
logo = logo.resize((80, 80))
logo = ImageTk.PhotoImage(logo)
logo_image = Button(NavigationFrame, image=logo, bg='#DC0A2D',bd=0,command=video_frame.tkraise)
logo_image.place(x=10, y=10)

# Menu button for coming to back to menu Frame
menu = Image.open('menu.png')
menu = ImageTk.PhotoImage(menu)
menu_button = Button(NavigationFrame, image=menu, bg="#DC0A2D",bd=0 , command= menu_frame.tkraise)
menu_button.place(x=1200,y=40)

# Pokemon Logo
p = Image.open('p.png')
p = p.resize((280,80))
p = ImageTk.PhotoImage(p)
pp = Label(NavigationFrame,image=p, bg="#DC0A2D")
pp.place(x=100,y=10)

# Button to go to Pokemon Search Frame
pokSearch = Image.open('pok.png')
pokSearch = ImageTk.PhotoImage(pokSearch)
pokButton = Button(menu_frame,image=pokSearch, bg='#1d2233',bd=0,command=Pokemon_Search_Instruction)
pokButton.place(x= 100,y=200)

# Button to navigate to Item Information Frame
item = Image.open('itemss.png')
item = ImageTk.PhotoImage(item)
item_button = Button(menu_frame, image=item,bg='#1d2233',bd=0,command=Item_Search)
item_button.place(x=100,y=300)

# Button to go to Game Frame for 2 Players 
ivi = Image.open('game.png')
ivi = ImageTk.PhotoImage(ivi)
ivi_button = Button(menu_frame, image=ivi,bg='#1d2233',bd=0,command=Game_Instruction)
ivi_button.place(x=100,y=400 )

# Button to go to Watch List Frame
wtch = Image.open('watch.png')
wtch = ImageTk.PhotoImage(wtch)
watch = Button(menu_frame, image=wtch, bg='#1d2233',bd=0,command=Watch_Link)
watch.place(x= 100, y= 500)

# Pikachu Ball Image
im=Image.open('image 1.png')
im=ImageTk.PhotoImage(im)
pika_image = Label(menu_frame,image=im,bg="#1d2233")
pika_image.place(x=500,y=100)

#*************************************  Pokemon Search Frame  ******************************************************************************#

# Create and place UI elements
search_label = Label(pokemon_frame, text="Search Pokemon:",bg="#111111",fg='white')
search_label.place(x=200,y=50)

# BAckground of the Entry Field
entry_field = Image.open('filed.png')
entry_field = ImageTk.PhotoImage(entry_field)
Label(pokemon_frame, image= entry_field, bg="#111111").place(x=175,y=70)

# Entry Field for Pokemon Search
search_entry = Entry(pokemon_frame,fg='white',bg='#00A3FF')
search_entry.place(x=200,y=80)

# Dropdown menu for name and id
search_type_var = StringVar(value="ID")
search_type_menu = ttk.Combobox(pokemon_frame, textvariable=search_type_var, values=["ID", "Name"])
search_type_menu.place(x=200,y=120)

# Button to retrieve information
show_button = Button(pokemon_frame, text="Show Pokemon Info" ,bg='#00A3FF',fg='white',padx=10,pady=5, command=lambda: [show_pokemon_info(), update_pokkball_image()]) # it calls 2 functions at a time using lambda
show_button.place(x=200,y=160)

# Initializing variable for font size
infofont = tkFont.Font(size=13)

#Label with the inforamtion of Pokemon
result_label = Label(pokemon_frame, text="",fg='white',font = infofont,bg="#111111",justify='left')
result_label.place(x=200,y=220)

# Display Pokemon Ball
pokeball = Image.open('pballo.png')
pokeball = pokeball.resize((250,250))
pokeball = ImageTk.PhotoImage(pokeball)
pokkball = Label(pokemon_frame, image=pokeball, bg='#111111')
pokkball.place(x=700,y=230)


# Image label to display the Pokémon image
image_label = Label(pokemon_frame ,bg="#111111")
image_label.place(x=600,y=100)

#*************************************  Game Frame  ******************************************************************************#

# Create two Pokemon instances for each player
player1_pokemon = Pokemon(game_frame, 100, 20)
player2_pokemon = Pokemon(game_frame2, 1100, 20)

# Create buttons for each player to generate a new Pokemon
Button(game_frame, text="Change Pokémon", bg="#111111", fg="#F7D346",
       command=player1_pokemon.generate_random_pokemon).place(x=130, y=400)
Button(game_frame2, text="Change Pokémon", bg="#111111", fg="#F4D346",
       command=player2_pokemon.generate_random_pokemon).place(x=1150, y=400)

# Pikachu image
imgg=Image.open('image 1.png')
imgg=imgg.resize((350,350))
imgg=ImageTk.PhotoImage(imgg)
pikachu_image = Label(game_frame,image=imgg,bg="#111111")
pikachu_image.place(x=500,y=20)

pikachu_image = Label(game_frame2,image=imgg,bg="#111111")
pikachu_image.place(x=500,y=20)

# Display image for Player 1
player1 = Image.open('player1.png')
player1 = player1.resize((100,100))
player1=ImageTk.PhotoImage(player1)
Player1 = Label(game_frame, image=player1,bg="#111111")
Player1.place(x=130,y=425)

# Display image for Player 2
player2 = Image.open('player2.png')
player2 = player2.resize((100,100))
player2=ImageTk.PhotoImage(player2)
Player2 = Label(game_frame2, image=player2,bg="#111111")
Player2.place(x=1150,y=425)

# Attack Button
attack_button = Button(game_frame,text='Attack!!',bg='#F4D346', padx=20,pady=15,command=game_frame2.tkraise)
attack_button.place(x=600,y=500)

attack_button = Button(game_frame2,text='Attack!!',bg='#F4D346', padx=20,pady=15,command=ATTACK)
attack_button.place(x=600,y=500)

#*************************************  Items Frame  ******************************************************************************#

#List box for displaying the items
item_listbox = Listbox(items_frame, selectmode=SINGLE,bg='#fad55a',height=300,width=50)
item_listbox.place(x=0,y=50)

# Description LAbel to display the information of the item
description_label = Label(description_frame, text="",bg='#111111',fg='white', justify=LEFT,padx=20,wraplength=300)
description_label.place(x=0,y=100)

# LAbel to display the image of the item
image_lab = Label(description_frame,bg='#111111')
image_lab.place(x=0,y=0)

#Function to load the item
load_items(item_listbox)

# Bind the '<<ListboxSelect>>' event to the show_item_details function
# This event occurs when an item in the item_listbox is selected
# The lambda function passes the event, item_listbox, description_label, and image_label to show_item_details
item_listbox.bind('<<ListboxSelect>>', lambda event: show_item_details(item_listbox, description_label, image_lab))

#Display Pikachu image
pika = Image.open('pikachu.png')
pika = pika.resize((150,150))
pika = ImageTk.PhotoImage(pika)
piika = Label(item_frame, image= pika, bg='#111111')
piika.place(x=1200,y=400)

#Display Dragon Image
dra = Image.open('dragon.png')
dra = dra.resize((150,150))
dra = ImageTk.PhotoImage(dra)
dragon = Label(item_frame,image=dra, bg="#111111")
dragon.place(x=50,y=400)

#*************************************  Watch Frame  ******************************************************************************#


# Displaying the posters of the Pokemon Posters
# calling the function to open the link to watch it

p97 = Image.open('pok1997.jpg')
p97 = p97.resize((250,400))
p97 = ImageTk.PhotoImage(p97)
poke1997 = Button(watch_frame,image=p97,command=Watch_Pokemon1997)
poke1997.place(x=10,y=50)

p99 = Image.open('pikachumovie1999.jpg')
p99 = p99.resize((250,400))
p99 = ImageTk.PhotoImage(p99)
poke199 = Button(watch_frame,image=p99 , command=Watch_Pokemon1999)
poke199.place(x=280,y=50)

p00 = Image.open('mewtworeturn2000.jpg')
p00 = p00.resize((250,400))
p00 = ImageTk.PhotoImage(p00)
poke200 = Button(watch_frame,image=p00, command=Watch_Mewtwo)
poke200.place(x=555,y=50)

p02 = Image.open('pokemonadvngen2002.jpg')
p02 = p02.resize((250,400))
p02 = ImageTk.PhotoImage(p02)
poke2002 = Button(watch_frame,image=p02 , command=Watch_PAdvanced)
poke2002.place(x=830,y=50)

p210 = Image.open('pokemon-best-wishes 2010.jpg')
p210 = p210.resize((250,400))
p210 = ImageTk.PhotoImage(p210)
pok210 = Button(watch_frame, image= p210, command=Watch_BestWishes)
pok210.place(x=1105,y=50)

# Jigglepuff Image
j = Image.open('jiggle.png')
j = j.resize((100,100))
j = ImageTk.PhotoImage(j)
ji = Label(watch_frame, image= j, bg='#111111')
ji.place(x=700,y=500)


#To raise the video frame to the top
video_frame.tkraise()
# Start the Tkinter main loop
root.mainloop()