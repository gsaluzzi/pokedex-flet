import flet as ft
import requests
import time

def obtener_color_tipo(tipo):
    colores = {
        "fire": "#F08030", "water": "#6890F0", "grass": "#78C850", "electric": "#F8D030",
        "ice": "#98D8D8", "fighting": "#C03028", "poison": "#A040A0", "ground": "#E0C068",
        "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820", "rock": "#B8A038",
        "ghost": "#705898", "dragon": "#7038F8", "dark": "#705848", "steel": "#B8B8D0",
        "fairy": "#EE99AC", "normal": "#A8A878"
    }
    return colores.get(tipo, "#f8f8f8")

def obtener_evoluciones(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    data = response.json()
    evoluciones = []
    actual = data["chain"]
    
    while actual:
        nombre = actual["species"]["name"]
        url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{nombre}"
        res_pokemon = requests.get(url_pokemon)
        if res_pokemon.status_code == 200:
            datos_pokemon = res_pokemon.json()
            imagen = datos_pokemon["sprites"]["front_default"]
        else:
            imagen = None
        
        evoluciones.append({"nombre": nombre.capitalize(), "imagen": imagen})
        actual = actual["evolves_to"][0] if actual["evolves_to"] else None
    
    return evoluciones

def buscar_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        habilidades = [h["ability"]["name"].capitalize() for h in data["abilities"]]
        movimientos = [m["move"]["name"].capitalize() for m in data["moves"][:7]]
        tipo = data["types"][0]["type"]["name"]
        
        species_url = data["species"]["url"]
        species_response = requests.get(species_url)
        evolution_chain_url = species_response.json()["evolution_chain"]["url"]
        evoluciones = obtener_evoluciones(evolution_chain_url)
        
        return {
            "nombre": data["name"].capitalize(),
            "id": data["id"],
            "altura": data["height"],
            "peso": data["weight"],
            "imagen": data["sprites"]["front_default"],
            "habilidades": habilidades,
            "movimientos": movimientos,
            "tipo": tipo,
            "evoluciones": evoluciones
        }
    else:
        return None

def main(page: ft.Page):
    
    page.title = "Pokédex"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f8f8f8"    
    
    nombre_input = ft.TextField(label="Nombre del Pokémon", width=300)
    resultado_izq = ft.Column(spacing=10, alignment=ft.MainAxisAlignment.START, opacity=0)
    resultado_cen = ft.Column(spacing=10, alignment=ft.MainAxisAlignment.START, opacity=0)
    resultado_der = ft.Column(spacing=10, alignment=ft.MainAxisAlignment.START, opacity=0)
    resultado_evo = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER, opacity=0)
    carga = ft.ProgressRing(visible=False)
    
    def on_buscar(e):
        nombre = nombre_input.value.strip()
        if not nombre:
            return
        
        carga.visible = True
        resultado_izq.opacity = 0
        resultado_cen.opacity = 0
        resultado_der.opacity = 0
        resultado_evo.opacity = 0
        page.update()
        
        time.sleep(1)
        
        datos = buscar_pokemon(nombre)
        carga.visible = False
        resultado_izq.controls.clear()
        resultado_cen.controls.clear()
        resultado_der.controls.clear()
        resultado_evo.controls.clear()

        if datos:
            page.bgcolor = obtener_color_tipo(datos["tipo"])
            resultado_izq.controls.append(ft.Text(f"Nombre: {datos['nombre']}", size=20, weight="bold"))
            resultado_izq.controls.append(ft.Text(f"ID: {datos['id']}"))
            resultado_izq.controls.append(ft.Text(f"Altura: {datos['altura']} dm"))
            resultado_izq.controls.append(ft.Text(f"Peso: {datos['peso']} hg"))
            resultado_izq.controls.append(ft.Image(src=datos["imagen"], width=150, height=150))
            
            resultado_cen.controls.append(ft.Text("Habilidades:", size=18, weight="bold"))
            resultado_cen.controls.append(ft.Column([ft.Text(f" - {hab}") for hab in datos["habilidades"]]))
            
            resultado_der.controls.append(ft.Text("Movimientos:", size=18, weight="bold"))
            resultado_der.controls.append(ft.Column([ft.Text(f" - {mov}") for mov in datos["movimientos"]]))
            
            resultado_evo.controls.append(ft.Text("Evoluciones:", size=18, weight="bold"))
            for evo in datos["evoluciones"]:
                resultado_evo.controls.append(ft.Column([
                    ft.Text(evo["nombre"]),
                    ft.Image(src=evo["imagen"], width=100, height=100)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            
            resultado_izq.opacity = 1
            resultado_cen.opacity = 1
            resultado_der.opacity = 1
            resultado_evo.opacity = 1
        else:
            resultado_izq.controls.append(ft.Text("Pokémon no encontrado.", color="red", size=18))
            resultado_izq.opacity = 1
        
        page.update()
    
    boton_buscar = ft.ElevatedButton(
        "Buscar", 
        on_click=on_buscar,
        bgcolor="#ffcb05", 
        color="black",
        scale=1.0,
        animate_scale=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT)
    )
    
  
    page.add(
        ft.Column([ft.Text("Pokédex", size=30, weight="bold", color="red"),
            nombre_input,
            boton_buscar,
            carga
            ,ft.Row([
                resultado_izq,
                resultado_cen,
                resultado_der,               
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START, spacing = 60),
            resultado_evo 
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main, assets_dir="assets", view=ft.WEB_BROWSER)
