import gradio as gr

def do_graph(user_input, chat_bot):
    '''
    输入框提交后，执行的函数
    '''
    if user_input:
        chat_bot.append({'role':'user', 'content':user_input})
    return '', chat_bot # 输入框置为空，聊天框显示输入内容

css = '''
#bgc {background-color: #7FFFD4}
.feedback textarea {font-size: 24px !important}
'''
with gr.Blocks(title='AI智能助手', css=css) as instatnt:
    gr.Label('AI智能助手', container=False)
    chatbot = gr.Chatbot(type='messages', height=350, label='chatbox')
    input_textbox = gr.Textbox(label='请输入你的问题', value='')
    input_textbox.submit(do_graph, [input_textbox, chatbot], [input_textbox, chatbot]) # 回车触发

if __name__=='__main__':
    instatnt.launch(debug=True)