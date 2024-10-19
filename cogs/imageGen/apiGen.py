import json
from urllib import request, parse
import random

#This is the ComfyUI api prompt format.

#If you want it for a specific workflow you can "enable dev mode options"
#in the settings of the UI (gear beside the "Queue Size: ") this will enable
#a button on the UI to save workflows in api format.

#keep in mind ComfyUI is pre alpha software so this format will change a bit.

#this is the one for the default workflow
prompt_text = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 8,
            "denoise": 1,
            "latent_image": [
                "5",
                0
            ],
            "model": [
                "4",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "sampler_name": "euler",
            "scheduler": "normal",
            "seed": 8566257,
            "steps": 20
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "CheckpointYesmix_v35.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "height": 512,
            "width": 512
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": "masterpiece best quality girl"
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": "bad hands"
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
                "8",
                0
            ]
        }
    }
}
"""



prompt = json.loads(prompt_text)
#set the text prompt for our positive CLIPTextEncode
prompt["6"]["inputs"]["text"] = "masterpiece best quality Tiger"

#set the seed for our KSampler node
#prompt["3"]["inputs"]["seed"] = 5

def queue_prompt(u_prompt):
    p = {"prompt": u_prompt}
    data = json.dumps(p).encode('utf-8')

    # Erstelle eine Anfrage mit JSON-Daten
    req = request.Request("http://127.0.0.1:8188/prompt", data=data, headers={'Content-Type': 'application/json'})

    try:
        # Sende die Anfrage und empfange die Antwort
        response = request.urlopen(req)

        # Lese die Antwort aus und dekodiere sie
        result = response.read().decode('utf-8')

        # Resultat (JSON oder Bild-URL) ausgeben
        print("Response from API:", result)

        # Wenn das Ergebnis eine Bild-URL oder Bilddaten enthält, speichere das Bild
        # Beispiel: Wenn du eine URL zurückbekommst, lade das Bild herunter
        result_data = json.loads(result)
        if 'image_url' in result_data:
            image_url = result_data['image_url']
            download_image(image_url)

    except request.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
    except request.URLError as e:
        print(f"URLError: {e.reason}")

queue_prompt(prompt)