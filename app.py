import gradio as gr
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import requests
from io import BytesIO

model = load_model("eurosat_classifier.keras", compile=False)

class_names = ['Annual Crop', 'Forest', 'Herbaceous Vegetation', 'Highway', 'Industrial',
               'Pasture', 'Permanent Crop', 'Residential', 'River', 'Sea/Lake']

def predict(image):
    image = image.resize((224, 224))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    preds = model.predict(image)[0]
    top_indices = preds.argsort()[-3:][::-1]
    result = {class_names[i]: float(preds[i]) for i in top_indices}
    return result

def load_image_from_url(url, display_size=(1000, 400)):
    response = requests.get(url)
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image = image.resize(display_size)
    return image

with gr.Blocks() as demo:
    gr.Markdown("## 🌍 Land Use and Land Cover Classification")
    gr.Markdown("""Upload a satellite or aerial image, or select one of the example images below to classify it into 1 of the 10 land use categories.  
Categories include: Annual Crop, Forest, Herbaceous Vegetation, Highway, Industrial, Pasture, Permanent Crop, Residential, River, Sea/Lake
""")

    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil", label="Input Image")
            with gr.Row():
                submit_btn = gr.Button("Submit", variant="primary")
                clear_btn = gr.ClearButton(components=[image_input])
        output = gr.Label(num_top_classes=3)

    submit_btn.click(fn=predict, inputs=image_input, outputs=output)

    gr.Markdown("### 🖼️ Example Images (click to load)")

    with gr.Row():
        btn1 = gr.Button(value="Athens, Greece 🏙️")
        btn2 = gr.Button(value="Autobahn, Germany 🚗")
        btn3 = gr.Button(value="Amazon River 🌊")

    btn1.click(fn=lambda: load_image_from_url(
        "https://storage.googleapis.com/p-oaf-ibe-back-00e-strapi-uploads/Pl_A_iades_Neo_Athens_Greece_4bd3eabcee/Pl_A_iades_Neo_Athens_Greece_4bd3eabcee.jpg"),
        outputs=image_input)

    btn2.click(fn=lambda: load_image_from_url(
        "https://www.shutterstock.com/image-photo/aerial-drone-view-road-junction-600nw-2380656867.jpg"),
        outputs=image_input)

    btn3.click(fn=lambda: load_image_from_url(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Amazon17_%285641020319%29.jpg/330px-Amazon17_%285641020319%29.jpg"),
        outputs=image_input)

demo.launch()
