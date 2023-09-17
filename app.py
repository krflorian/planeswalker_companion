import gradio


def ask(text):
    return [
        [
            "can you show me a link?",
            "is this the [link](https://orf.at/)?",
        ],
    ]


# creates a new Blocks app and assigns it to the variable demo.
with gradio.Blocks() as demo:
    chatbot = gradio.Chatbot()

    with gradio.Row():
        txt = gradio.Textbox(show_label=False, placeholder="Enter text and press enter")

    txt.submit(ask, txt, chatbot)
    txt.submit(None, None, txt, _js="() => {''}")

demo.launch()
