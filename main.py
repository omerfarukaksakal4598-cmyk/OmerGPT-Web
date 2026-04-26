from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
import random

app = Ursina()

# --- AYARLAR VE RENKLER (Resim Gerektirmez) ---
# Resim yerine doğrudan Ursina'nın renklerini tanımlıyoruz
BLOCK_COLORS = {
    'grass':  color.lime,      # Çim -> Açık Yeşil
    'stone':  color.gray,      # Taş -> Gri
    'dirt':   color.brown,     # Toprak -> Kahverengi
    'wood':   color.rgb(101, 67, 33), # Odun -> Kahverengi Kütük
    'leaves': color.green      # Yaprak -> Yeşil
}

selected_block = 'grass'
inventory_open = False
noise = PerlinNoise(octaves=2, seed=random.randint(1, 1000))

# --- BLOK SINIFI ---
class Voxel(Button):
    def __init__(self, position=(0,0,0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube', # Ursina'nın standart dokusunu kullan
            color=BLOCK_COLORS[block_type], # Rengi ayarla
            highlight_color=color.white, # Fareyle gelince beyazla
            scale=1
        )
        self.block_type = block_type

    def input(self, key):
        if self.hovered and not inventory_open:
            if key == 'right mouse down':
                if selected_block in BLOCK_COLORS:
                    Voxel(position=self.position + mouse.normal, block_type=selected_block)
            if key == 'left mouse down':
                destroy(self)

# --- ARAYÜZ (HOTBAR VE BÜYÜK MENU) ---
hotbar = Entity(parent=camera.ui, model='quad', scale=(0.5, 0.08), origin=(0, -0.5), y=-0.45, color=color.black66)
selector = Entity(parent=hotbar, model='quad', scale=(0.2, 0.9), x=-0.4, y=0.5, color=color.white, z=-0.01)

inventory_menu = Entity(parent=camera.ui, model='quad', scale=(0.8, 0.6), color=color.black90, enabled=False)
Text(text="BÜYÜK ENVANTER", parent=inventory_menu, y=0.4, scale=2, origin=(0,0))

def pick_item(name):
    global selected_block
    selected_block = name
    hand.color = BLOCK_COLORS[name] # Elin rengini güncelle
    toggle_inventory()

# Menü butonlarını oluştur
i = 0
for name, col in BLOCK_COLORS.items():
    b = Button(parent=inventory_menu, text=name, color=col, scale=(0.15, 0.1), x=-0.35 + (i%4)*0.24, y=0.2 - (i//4)*0.15)
    b.on_click = Func(pick_item, name)
    i += 1

def toggle_inventory():
    global inventory_open
    inventory_open = not inventory_open
    inventory_menu.enabled = inventory_open
    mouse.locked = not inventory_open
    player.enabled = not inventory_open

# --- TUŞ VE EL KONTROLLERİ ---
hand = Entity(parent=camera.ui, model='cube', color=BLOCK_COLORS['grass'], scale=(0.2, 0.4, 0.2), position=(0.6, -0.45), rotation=(30, -10, 0))

def input(key):
    global selected_block
    if key == 'e':
        toggle_inventory()
    
    if not inventory_open:
        # 1-5 tuşları ile hotbar seçimi
        for i, name in enumerate(BLOCK_COLORS.keys()):
            if i < 5 and key == str(i+1):
                selected_block = name
                selector.x = -0.4 + (i * 0.2)
                hand.color = BLOCK_COLORS[name]

# --- DÜNYA OLUŞTURMA (HAFİF) ---
def generate_world():
    for z in range(12):
        for x in range(12):
            y = floor(noise([x/15, z/15]) * 4)
            # Çim yüzey
            Voxel(position=(x, y, z), block_type='grass')
            # Toprak katmanı
            Voxel(position=(x, y-1, z), block_type='dirt')

def update():
    if held_keys['left mouse'] or held_keys['right mouse']:
        hand.position = (0.5, -0.3)
    else:
        hand.position = (0.6, -0.45)

player = FirstPersonController()
Sky()
generate_world()
app.run()