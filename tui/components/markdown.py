from itertools import accumulate

from textual.widget import Widget

from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment
from rich.style import Style

from textual.message import Message, MessageTarget
from rich.markdown import Markdown, MarkdownContext, UnknownElement, Paragraph

from tui.api.models import Highlight

class MyMarkdown(Markdown, Widget):

    class FinishedRender(Message):
        """Finished Render"""

        def __init__(self, sender: MessageTarget):
            super().__init__(sender)

    def __init__(self, markup, article, *args, **kwargs):
        self.article = article
        self.my_elements = []
        super().__init__(markup, *args, **kwargs)

    def get_element_at_line(self, line: int):
        for i in range(len(self.my_elements)):
            el = self.my_elements[i]
            if isinstance(el, Paragraph) and el.text.plain == '':
                self.num_mapping[i] = 0

        self.num_mapping_cumsum = list(accumulate(self.num_mapping))
        index = self.num_mapping_cumsum.index(next(x for x in self.num_mapping_cumsum if line <= x))
        element = self.my_elements[index]
        return index, element

    def get_highlight_mapping(self):
        for i in range(len(self.my_elements)):
            el = self.my_elements[i]
            if isinstance(el, Paragraph) and el.text.plain == '':
                self.num_mapping[i] = 0
        blob = []
        blob.extend(" ")
        if self.article:
            highlighted_elements = {x.segment for x in self.article.highlights}
        else:
            return ""
        for i in range(len(self.my_elements)):
            if isinstance(self.my_elements[i], Segment):
                length = 1
            else:
                length = self.num_mapping[i]
            if i in highlighted_elements:
                blob.extend(["🟨"] * length)
            else:
                blob.extend(["⬛"] * length)
        return "\n".join(blob)

    async def finished_render(self):
        await self.emit(self.FinishedRender(self))

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render markdown to the console."""
        self.num_mapping = []
        self.my_elements = []
        if self.article:
            highlighted_elements = {x.segment for x in self.article.highlights}
        else:
            highlighted_elements = {}
        element_count = 0
        style = console.get_style(self.style, default="none")
        options = options.update(height=None)
        context = MarkdownContext(
            console,
            options,
            style,
            inline_code_lexer=self.inline_code_lexer,
            inline_code_theme=self.inline_code_theme,
        )
        nodes = self.parsed.walker()
        inlines = self.inlines
        new_line = False
        for current, entering in nodes:
            node_type = current.t
            if node_type in ("html_inline", "html_block", "text"):
                context.on_text(current.literal.replace("\n", " "), node_type)
            elif node_type == "linebreak":
                if entering:
                    context.on_text("\n", node_type)
            elif node_type == "softbreak":
                if entering:
                    context.on_text(" ", node_type)
            elif node_type == "link":
                if entering:
                    link_style = console.get_style("markdown.link", default="none")
                    if self.hyperlinks:
                        link_style += Style(link=current.destination)
                    context.enter_style(link_style)
                else:
                    context.leave_style()
                    if not self.hyperlinks:
                        context.on_text(" (", node_type)
                        style = Style(underline=True) + console.get_style(
                            "markdown.link_url", default="none"
                        )
                        context.enter_style(style)
                        context.on_text(current.destination, node_type)
                        context.leave_style()
                        context.on_text(")", node_type)
            elif node_type in inlines:
                if current.is_container():
                    if entering:
                        context.enter_style(f"markdown.{node_type}")
                    else:
                        context.leave_style()
                else:
                    context.enter_style(f"markdown.{node_type}")
                    if current.literal:
                        context.on_text(current.literal, node_type)
                    context.leave_style()
            else:
                element_class = self.elements.get(node_type) or UnknownElement
                if current.is_container():
                    if entering:
                        element = element_class.create(self, current)
                        context.stack.push(element)
                        element.on_enter(context)
                    else:
                        element = context.stack.pop()
                        if context.stack:
                            if context.stack.top.on_child_close(context, element):
                                if new_line:
                                    self.my_elements.append(Segment("\n"))
                                    self.num_mapping.append(1)
                                    yield Segment("\n")
                                    element_count += 1
                                self.my_elements.append(element)
                                self.num_mapping.append(len(console.render_lines(element, context.options)))
                                if element_count in highlighted_elements:
                                    context.enter_style(Style(bgcolor='blue'))
                                yield from console.render(element, context.options)
                                if element_count in highlighted_elements:
                                    context.leave_style()
                                element_count += 1
                                element.on_leave(context)
                            else:
                                element.on_leave(context)
                        else:
                            element.on_leave(context)
                            self.my_elements.append(element)
                            self.num_mapping.append(len(console.render_lines(element, context.options)))

                            yield from console.render(element, context.options)
                            element_count += 1
                        new_line = element.new_line
                else:
                    element = element_class.create(self, current)
                    context.stack.push(element)
                    element.on_enter(context)
                    if current.literal:
                        element.on_text(context, current.literal.rstrip())
                    context.stack.pop()
                    if context.stack.top.on_child_close(context, element):
                        if new_line:
                            self.my_elements.append(Segment("\n"))
                            self.num_mapping.append(1)
                            yield Segment("\n")
                            element_count += 1
                        self.my_elements.append(element)
                        self.num_mapping.append(len(console.render_lines(element, context.options)))
                        yield from console.render(element, context.options)
                        element_count += 1
                        element.on_leave(context)
                    else:
                        element.on_leave(context)
                    new_line = element.new_line