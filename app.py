import os
import streamlit as st
import base64
from openai import OpenAI


def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(
    page_title="Análisis de Imágenes con IA",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.title("🖼️ Análisis de Imágenes con Inteligencia Artificial")
st.caption("Utiliza el modelo GPT-4o de OpenAI para interpretar y analizar imágenes.")


ke = st.text_input("Ingresa tu clave de OpenAI:", type="password")
if not ke:
    st.warning("Por favor ingresa tu clave API para continuar.")
else:
    os.environ["OPENAI_API_KEY"] = ke


api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


uploaded_file = st.file_uploader("Sube una imagen (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("📸 Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)


show_details = st.toggle("¿Quieres preguntar algo específico sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area(
        "Agrega tu pregunta o contexto aquí:",
        placeholder="Ejemplo: ¿Qué tipo de animal aparece? o ¿Qué emociones transmite la escena?",
    )
else:
    additional_details = None


analyze_button = st.button("🔎 Analizar imagen", type="secondary")


if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analizando la imagen... por favor espera "):
        try:
            base64_image = encode_image(uploaded_file)
            prompt_text = "Describe lo que observas en esta imagen en español, de manera clara y concisa."

            if show_details and additional_details:
                prompt_text += f"\n\nInstrucción adicional del usuario:\n{additional_details}"

           
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ]

           
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Ocurrió un error durante el análisis: {e}")


elif analyze_button:
    if not uploaded_file:
        st.warning("Por favor sube una imagen antes de analizar.")
    elif not api_key:
        st.warning("Por favor ingresa tu clave de OpenAI para continuar.")
