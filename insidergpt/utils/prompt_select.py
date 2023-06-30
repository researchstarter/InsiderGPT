from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import RadioList, Label
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import prompt


def prompt_continuation(width, line_number, wrap_count):
 
    if wrap_count > 0:
        return " " * (width - 3) + "-> "
    text = ("- %i - " % (line_number + 1)).rjust(width)
    return HTML("<strong>%s</strong>") % text


def prompt_select(title="", values=None, style=None, async_=False):
 
    bindings = KeyBindings()

    @bindings.add("c-d")
    def exit_(event):
        
        event.app.exit()

    @bindings.add("s-right")
    def exit_with_value(event):
       
        event.app.exit(result=radio_list.current_value)

    radio_list = RadioList(values)
    application = Application(
        layout=Layout(HSplit([Label(title), radio_list])),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=False,
    )

    return application.run_async() if async_ else application.run()


def prompt_ask(text, multiline=True) -> str:
   
    kb = KeyBindings()
    if multiline:

        @kb.add("enter")
        def _(event):
            event.current_buffer.insert_text("\n")

    @kb.add("s-right")
    def _(event):
        event.current_buffer.validate_and_handle()

    return prompt(
        text,
        multiline=multiline,
        prompt_continuation=prompt_continuation,
        key_bindings=kb,
    )

