# Consulting Studio — Elementor Clone

A clone of the layout, structure, style, and functionality of
`https://consulting-studio.elementra.themerex.net/`, packaged as an
Elementor-importable template plus companion CSS.

## Files

- `consulting-studio-template.json` — Elementor page template (import in Elementor)
- `custom-styles.css` — Companion CSS for fonts, buttons, cards, hover effects
- `SETUP.md` — This file

## How to Import

1. In WordPress, go to **Templates → Saved Templates → Import Templates**.
2. Upload `consulting-studio-template.json`.
3. Edit any page with Elementor → click the folder icon → **My Templates** → Insert.
4. Go to **Elementor → Custom CSS** (or your child theme `style.css`) and paste the
   contents of `custom-styles.css`.

## What's Included

| Section | Layout | Notes |
|---|---|---|
| Hero | Full width, centered | Eyebrow, H1, sub, CTA button |
| Mission | 50/50 two column | Text + 2x2 image gallery |
| Services | 4 column | Icon-box cards w/ hover lift |
| CTA Banner | Full width | Purple background, white button |
| Stats | 3 column | Animated counters |
| Blog | 3 column | Card layout with meta + title |
| Newsletter | Centered | Heading + form shortcode |
| Footer | 4 column | Address, contact, nav, social |
| Copyright | Strip | Centered text |

## Color Palette

| Token | Hex | Use |
|---|---|---|
| Primary | `#3519E2` | Headlines, accents |
| Secondary | `#0059F0` | Links, eyebrows |
| Accent | `#384EDF` | Buttons |
| Text | `#1F242E` | Body |
| Muted | `#ACAFB2` | Meta text |
| BG Alt | `#F6F7F1` | Section backgrounds |
| Success | `#72BF40` | Checkmarks |

## Typography

- Body & headings: **Inter** (load via Google Fonts or Elementor's font manager)
- Headings: weight 500–600, slight negative letter-spacing
- Body: weight 400, line-height 1.7

## Customization Tips

- **Replace placeholder images:** the JSON uses `via.placeholder.com` URLs — swap them
  with your own uploads in the Elementor editor.
- **Stats counters:** edit ending number, prefix, and suffix per counter widget.
- **Newsletter form:** the template uses a `[contact-form-7]` shortcode placeholder —
  install Contact Form 7 (or swap for Elementor Pro Form widget).
- **Navigation menu:** the original site's nav is theme-driven. Build a WP menu under
  **Appearance → Menus** and assign it to your header.

## Notes

- All copy in the template is paraphrased so you can drop in your own brand voice.
- Icons use Font Awesome (bundled with Elementor).
- The template is laid out as a single page; split into sub-pages by copying sections
  into new templates.
