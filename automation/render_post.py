"""
soul.orbits — render Instagram post images from YAML data + HTML template.

Usage:
    python render_post.py <post.yaml>           # single post
    python render_post.py --batch <dir>         # all .yaml files in dir
"""
import sys
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright

from starfield import starfield_data_uri

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"

TEMPLATE_MAP = {
    "daily_transit": TEMPLATES / "template_a_daily_transit.html",
    "daily_transit_meme": TEMPLATES / "template_a_meme.html",
    "carousel_hook": TEMPLATES / "template_d_carousel_hook.html",
    "carousel_sign": TEMPLATES / "template_d_carousel_sign.html",
    "carousel_cta": TEMPLATES / "template_d_carousel_cta.html",
    "carousel_cover": TEMPLATES / "template_b_carousel_cover.html",
    "carousel_slide": TEMPLATES / "template_b_carousel_slide.html",
    "quote": TEMPLATES / "template_c_quote.html",
    # Stories — 1080x1920 (vertical 9:16)
    "story_daily_transit": TEMPLATES / "story_a_daily_transit.html",
    "story_which_sign": TEMPLATES / "story_b_which_sign.html",
    "story_poll": TEMPLATES / "story_c_poll.html",
    "story_question": TEMPLATES / "story_d_question.html",
}

STORY_TEMPLATES = {"story_daily_transit", "story_which_sign", "story_poll", "story_question"}


def render_html(html: str, out_path: Path, browser, viewport: dict | None = None):
    vp = viewport or {"width": 1080, "height": 1350}
    context = browser.new_context(viewport=vp, device_scale_factor=2)
    page = context.new_page()
    page.set_content(html, wait_until="networkidle")
    page.wait_for_timeout(800)
    page.screenshot(path=str(out_path), full_page=False, omit_background=False)
    context.close()


def fill_template(template_html: str, fields: dict, slide_idx: int = 0) -> str:
    out = template_html
    # Inject a deterministic-but-varied starfield per slide
    if "{{STARFIELD}}" in out:
        out = out.replace("{{STARFIELD}}", starfield_data_uri(seed=7 + slide_idx))
    for key, value in fields.items():
        out = out.replace(f"{{{{{key.upper()}}}}}", str(value))
    return out


def render_post(post_yaml: Path, browser) -> list[Path]:
    data = yaml.safe_load(post_yaml.read_text(encoding="utf-8"))
    out_dir = post_yaml.parent / "images"
    out_dir.mkdir(exist_ok=True)
    rendered = []

    if data["template"] == "carousel":
        # multi-slide: data["slides"] is a list of {template, fields}
        for i, slide in enumerate(data["slides"], start=1):
            tmpl = TEMPLATE_MAP[slide["template"]]
            html = fill_template(tmpl.read_text(encoding="utf-8"), slide["fields"], slide_idx=i)
            out = out_dir / f"{post_yaml.stem}-slide{i:02d}.png"
            render_html(html, out, browser)
            rendered.append(out)
    else:
        tmpl = TEMPLATE_MAP[data["template"]]
        html = fill_template(tmpl.read_text(encoding="utf-8"), data["fields"])
        out = out_dir / f"{post_yaml.stem}.png"
        # Stories use 1080x1920 viewport instead of 1080x1350.
        vp = {"width": 1080, "height": 1920} if data["template"] in STORY_TEMPLATES else None
        render_html(html, out, browser, viewport=vp)
        rendered.append(out)

    return rendered


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: render_post.py <post.yaml> | --batch <dir>", file=sys.stderr)
        sys.exit(1)

    if args[0] == "--batch":
        target_dir = Path(args[1])
        yamls = sorted(target_dir.glob("*.yaml"))
    else:
        yamls = [Path(args[0])]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for y in yamls:
            print(f"rendering {y.name}...", flush=True)
            outs = render_post(y, browser)
            for o in outs:
                print(f"  -> {o.name}")
        browser.close()


if __name__ == "__main__":
    main()
