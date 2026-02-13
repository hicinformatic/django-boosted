"""Formatting utilities for django-boosted."""

from django.utils.html import format_html


def format_label(
    text: str,
    label_type: str = "info",
    size: str | None = None,
    link: str | None = None,
    style: str | None = None,
) -> str:
    classes = ["boost-label"]
    valid_types = [
        "success",
        "info",
        "warning",
        "danger",
        "primary",
        "secondary",
        "default",
    ]
    if label_type.lower() in valid_types:
        classes.append(label_type.lower())
    else:
        classes.append("info")
    if size and size.lower() in ["small", "big"]:
        classes.append(size.lower())
    if link:
        classes.append("link")
    css_class = " ".join(classes)
    tag = "a" if link else "span"
    if link and style:
        return format_html(
            '<{} href="{}" class="{}" style="{}">{}</{}>',
            tag,
            link,
            css_class,
            style,
            text,
            tag,
        )
    if link:
        return format_html(
            '<{} href="{}" class="{}">{}</{}>', tag, link, css_class, text, tag
        )
    if style:
        return format_html(
            '<{} class="{}" style="{}">{}</{}>', tag, css_class, style, text, tag
        )
    return format_html('<{} class="{}">{}</{}>', tag, css_class, text, tag)


def format_status(
    name: str, status: bool, style: str | None = None, link: str | None = None
) -> str:
    icon = "✓" if status else "✗"
    status_class = "success" if status else "error"
    tag = "a" if link else "span"
    return format_html(
        '<{} href="{}"><span class="boost-status {}" style="{}">{}</span> '
        '<code>{}</code></{}>',
        tag,
        link,
        status_class,
        style,
        icon,
        name,
        tag,
    )


def format_with_help_text(html_content: str, help_text: str | None = None) -> str:
    if help_text:
        return format_html(
            '{}<br><small class="help">{}</small>', html_content, help_text
        )
    return html_content
