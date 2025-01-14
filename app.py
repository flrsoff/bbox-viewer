import os
from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import base64
from tkinter import Tk, filedialog
import cv2

def load_image(image_path: str, shape=(640, 480)):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    labels: dict[str, list[tuple[int, int, int, int]]] = dict()
    
    last_dot_index = image_path.rfind(".")
    if last_dot_index == -1: return None
    
    label_path = image_path[:last_dot_index] + '.txt'
    with open(label_path) as file:
        for line in file:
            id, tx, ty, tw, th = line.strip().split()
            tx = float(tx) * width; ty = float(ty) * height
            tw = float(tw) * width; th = float(th) * height
            
            left   = int(tx - tw / 2)
            right  = int(tx + tw / 2)
            top    = int(ty - th / 2)
            bottom = int(ty + th / 2)
            
            if id in labels: labels[id].append((left, right, top, bottom))
            else           : labels[id]     = [(left, right, top, bottom)]
            
    for id in labels:
        for left, right, top, bottom in labels[id]:
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
                
    scale = min(shape[0] / width, shape[1] / height)
    image = cv2.resize(image, (int(scale * width), int(scale * height)))
    
    _, buffer = cv2.imencode(image_path[last_dot_index:], image)
    return base64.b64encode(buffer.tobytes()).decode('utf-8')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

images = []
current_index = 0
selected_folder = None

app.layout = html.Div(id='main-container', className='container', children=[
    html.Div(className='folder-name', children=[
        html.Span('Foler path'),
        html.Span('Choose', id='choose-folder-btn', className='choose')
    ]), 
    html.Div(className='file-info', children=
        html.Span(f'', id='file-name', className='file-name')
    ),  
    html.Div(className='image-container', children=html.Img(id='image-display', src='.jpg', alt='Select a folder with images', className='image')),
    html.Div(className='buttons-container', children=[
        html.Button(id='prev-btn', className='nav-button prev-button', children=html.Img(src='assets/prev-icon.png', alt='prev')),
        html.Button(id='next-btn', className='nav-button next-button', children=html.Img(src='assets/next-icon.png', alt='next'))
    ])
])



@app.callback(
    Output('choose-folder-btn', 'children'),
    Output('file-name', 'children'),
    Output('image-display', 'src'),
    Input("choose-folder-btn", "n_clicks"),
    Input("prev-btn", "n_clicks"),
    Input("next-btn", "n_clicks"),
    prevent_initial_call=True
)
def update(_, __, ___):
    global images, current_index, selected_folder

    if ctx.triggered_id == 'choose-folder-btn':
        root = Tk(); root.withdraw()
        if selected_folder: folder_path = filedialog.askdirectory(initialdir=selected_folder)
        else              : folder_path = filedialog.askdirectory(                          )
        root.destroy()

        if folder_path:
            images = [
                os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
            ]
            
            current_index = 0
            selected_folder = folder_path
    elif ctx.triggered_id == 'prev-btn' and len(images):
        if current_index     > 0          : current_index -= 1
        else                              : current_index  = len(images)-1
    elif ctx.triggered_id == 'next-btn' and len(images):
        if current_index + 1 < len(images): current_index += 1
        else                              : current_index  = 0
    
    if len(images):
        return (
            selected_folder, 
            images[current_index].split('/')[-1], 
            f'data:image/png;base64,{load_image(images[current_index], (1280, 720))}'
        )
    return 'Choose', '', 'Empty'

app.clientside_callback(
    """
        function(id) {
            document.addEventListener("keydown", function(event) {
                    if (event.key == 'ArrowLeft') {
                        document.getElementById('prev-btn').click();
                    }
                    if (event.key == 'ArrowRight') {
                        document.getElementById('next-btn').click();
                    }
            });
            return window.dash_clientside.no_update;
        }
    """,
    Output('prev-btn', "id"),
    Input('prev-btn', "id")
)

if __name__ == "__main__":
    app.run_server(debug=True)
