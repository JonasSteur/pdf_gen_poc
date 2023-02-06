from weasyprint import HTML


def html_to_pdf(html: str) -> bytes:
    html = HTML(string=html)
    return html.write_pdf()
