import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🎨 ESTILO OCEAN DANY
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #020617, #0c4a6e);
    color: #e0f2fe;
}

/* Banner */
.banner {
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0px 5px 25px rgba(0,0,0,0.4);
}

/* Botones */
.stButton > button {
    background: linear-gradient(90deg, #0ea5e9, #0369a1);
    color: white;
    border-radius: 14px;
    padding: 12px;
    font-weight: bold;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.07);
    background: linear-gradient(90deg, #0284c7, #075985);
}
</style>
""", unsafe_allow_html=True)

# 🐋 Banner
st.markdown("""
<div class="banner">
    <h1>🐋 Control por Voz - Dany 🌊</h1>
    <p>Habla y controla tu mundo IoT 💙</p>
</div>
""", unsafe_allow_html=True)

# MQTT
def on_publish(client,userdata,result):
    print("dato publicado")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write("📩 Respuesta:", message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("RAYIT4")
client1.on_message = on_message

# UI
st.subheader("🎤 Control por Voz")

# Imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=220)

st.write("💬 Presiona el botón y habla (ON / OFF)")

# BOTÓN VOZ
stt_button = Button(label="🎙️ Hablar", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# RESULTADO
if result:
    if "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip().upper()

        st.success(f"🧠 Entendí: {texto}")

        # MQTT ENVÍO (COMPATIBLE CON TU ESP32)
        client1.on_publish = on_publish
        client1.connect(broker,port)

        message = json.dumps({"Act1": texto})
        client1.publish("cmqtt_amotorcito", message)  # ✅ MISMO TOPIC QUE TODO

# Carpeta temporal
try:
    os.mkdir("temp")
except:
    pass
