from graph_chat.log_utils import log


def draw_graph(graph, filename:str):
    try:
        mermaid_code = graph.get_graph().draw_mermaid_png()
        with open(filename, 'wb') as f:
            f.write(mermaid_code)
    except Exception as e:
        log.exception(e)

