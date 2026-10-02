"""Actual close-up hair render coverage for the licensed Ashley May development asset.

This is rendering QA, not measured hair optics or identity validation.
"""
import base64
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat

COLORS = ['#836c57', '#ffffff', '#493025', '#201a16', '#ac7946', '#854629']
STYLES = ['wavy', 'straight', 'curly']
LENGTHS = [0.75, 1.0, 1.35]
VIEWS = ['front', 'side']


def run_hair_closeups(page, root: Path, checks: dict) -> None:
    folder = root / 'hair-closeups'
    folder.mkdir(exist_ok=True)
    page.evaluate("KR.reset();KR.view('front')")
    page.locator('#detail').click()
    records = []
    digests = {}
    for color in COLORS:
        for style in STYLES:
            for length in LENGTHS:
                for view in VIEWS:
                    result = page.evaluate("""(args)=>{
                      KR.change('hair',args.color);
                      KR.change('hairStyle',args.style);
                      KR.change('length',args.length);
                      KR.view(args.view);
                      KR.renderer.render(KR.scene,KR.camera);
                      return {
                        png:KR.renderer.domElement.toDataURL('image/png'),
                        webglError:KR.renderer.getContext().getError(),
                        state:{hair:KR.state.hair,hairStyle:KR.state.hairStyle,length:KR.state.length,view:KR.state.view}
                      };
                    }""", {'color': color, 'style': style, 'length': length, 'view': view})
                    raw = base64.b64decode(result.pop('png').split(',', 1)[1])
                    tag = color[1:]
                    length_tag = str(length).replace('.', 'p')
                    name = f'{tag}-{style}-{length_tag}-{view}.png'
                    (folder / name).write_bytes(raw)
                    image = Image.open(folder / name).convert('RGB')
                    if max(ImageStat.Stat(image).stddev) < 2:
                        checks['errors'].append('Uniform actual hair close-up: ' + name)
                    expected = {'hair': color, 'hairStyle': style, 'length': length, 'view': view}
                    if result['webglError'] or result['state'] != expected:
                        checks['errors'].append('Hair close-up state/WebGL failure: ' + name)
                    digest = hashlib.sha256(raw).hexdigest()
                    digests[(color, style, length, view)] = digest
                    records.append({'path': 'hair-closeups/' + name, 'sha256': digest,
                                    'hair': color, 'style': style, 'length': length, 'view': view,
                                    'pixel_size': list(image.size), **result})
    # Each individual control value must have a visible effect in at least one
    # direct close-up comparison against the default state.
    default = ('#836c57', 'wavy', 1.0)
    effect_failures = []
    for color in COLORS:
        if color != default[0] and all(digests[(color, default[1], default[2], view)] == digests[(default[0], default[1], default[2], view)] for view in VIEWS):
            effect_failures.append('hair color ' + color)
    for style in STYLES:
        if style != default[1] and all(digests[(default[0], style, default[2], view)] == digests[(default[0], default[1], default[2], view)] for view in VIEWS):
            effect_failures.append('hair style ' + style)
    for length in LENGTHS:
        if length != default[2] and all(digests[(default[0], default[1], length, view)] == digests[(default[0], default[1], default[2], view)] for view in VIEWS):
            effect_failures.append('hair length ' + str(length))
    if effect_failures:
        checks['errors'].append('Hair controls lacked rendered visual effect: ' + ', '.join(effect_failures))

    # Lossless contact sheet for rapid human inspection; native frames remain
    # available so the atlas is not treated as the only evidence.
    sample = Image.open(root / records[0]['path']).convert('RGB')
    thumb_w = 360
    thumb_h = round(sample.height * thumb_w / sample.width)
    cell_h = thumb_h + 28
    columns = 6
    rows = (len(records) + columns - 1) // columns
    atlas = Image.new('RGB', (thumb_w * columns, cell_h * rows), 'white')
    draw = ImageDraw.Draw(atlas)
    for i, record in enumerate(records):
        x, y = (i % columns) * thumb_w, (i // columns) * cell_h
        frame = Image.open(root / record['path']).convert('RGB')
        frame.thumbnail((thumb_w, thumb_h))
        atlas.paste(frame, (x, y + 28))
        draw.text((x + 5, y + 5),
                  f"{record['hair']} {record['style']} {record['length']} {record['view']}",
                  fill='black')
    atlas.save(root / 'hair-closeups-rendered.png')
    (root / 'hair-closeups-manifest.json').write_text(json.dumps(records, indent=2))
    checks['hair_closeups'] = {
        'executed_renders': len(records),
        'coverage': 'exhaustive 6 hair colors x 3 styles x 3 length boundary/default values x 2 representative camera views',
        'colors': COLORS, 'styles': STYLES, 'lengths': LENGTHS, 'views': VIEWS,
        'effect_failures': effect_failures, 'evidence': records,
        'visual_approval': False, 'measured_hair_optics_validated': False,
        'physical_hardware': False,
        'limits': 'Chromium close-up rendering and state/effect checks; human image inspection remains required and this is not real-device validation.'
    }
    page.evaluate("KR.reset()")
