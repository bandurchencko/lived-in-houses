# -*- coding: utf-8 -*-
"""Assemble the trailer: two Unreal walk-throughs + the browser viewer frames + "from a picture" (the concept art slowly
zooming, dissolving into an orbit of the house the generator built from it) + an end card, English captions.

    python sobrat_rolik.py <frames> <tavern-walkthrough.mp4> <house-walkthrough.mp4> <out.mp4> [<picture.jpg> <picture-frames>]
"""
import subprocess
import sys

SHRIFT = "C\\:/Windows/Fonts/segoeui.ttf"
SHRIFT_B = "C\\:/Windows/Fonts/seguisb.ttf"


def podpis(tekst, t0, t1, razmer=46, y='h-150'):
    return ("drawtext=fontfile='%s':text='%s':fontsize=%d:fontcolor=white:x=(w-text_w)/2:y=%s:"
            "box=1:boxcolor=black@0.45:boxborderw=18:enable='between(t,%.2f,%.2f)'" % (SHRIFT_B, tekst, razmer, y, t0, t1))


def main(kadry, prohod_a, prohod_b, vyhod, kartinka=None, kadry_obraz=None):
    obshchee = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30,setsar=1,format=yuv420p'
    vhody = ['-i', prohod_a, '-i', prohod_b, '-framerate', '30', '-i', kadry + '/kadr-%04d.png']
    fg = [
        '[0:v]trim=0:13,setpts=PTS-STARTPTS,%s,%s,%s,fade=t=in:st=0:d=0.4,fade=t=out:st=12.6:d=0.4[a]' % (
            obshchee, podpis('Tavern with forge  ·  seed 4  ·  walk in  ·  Unreal Engine 5', 0.3, 5.0),
            podpis('Porch  ·  hall with the common table  ·  stairs  ·  hearth', 5.2, 12.6)),
        '[1:v]trim=0:9.3,setpts=PTS-STARTPTS,%s,%s,fade=t=in:st=0:d=0.4,fade=t=out:st=8.9:d=0.4[b]' % (
            obshchee, podpis('Thatched house with a porch  ·  seed 1717', 0.3, 8.9)),
        '[2:v]%s,%s,%s,%s,%s,%s,fade=t=in:st=0:d=0.4,fade=t=out:st=16.6:d=0.4[c]' % (
            obshchee, podpis('The same generator in the browser  ·  seed 13', 0.2, 3.0),
            podpis('Take the roof off  ·  cut through the floors', 3.0, 8.5),
            podpis('Seed 7', 8.5, 10.0), podpis('Seed 4', 10.0, 11.5),
            podpis('Houses with a yard  ·  seeds 1818  ·  2020  ·  1717', 11.5, 16.8)),
    ]
    otrezki = '[a][b][c]'
    if kartinka and kadry_obraz:                       # «рисунок → дом»: 3 с рисунка с наплывом, растворение в облёт
        vhody += ['-loop', '1', '-t', '3.2', '-i', kartinka, '-framerate', '30', '-i', kadry_obraz + '/kadr-%04d.png']
        fg += [
            "[3:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x1d2126,"
            "zoompan=z='min(zoom+0.0009,1.09)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30,"
            "trim=0:3.2,setpts=PTS-STARTPTS,setsar=1,format=yuv420p,%s,fade=t=in:st=0:d=0.4[kart]" % (
                podpis('From a picture  ·  concept art by Astra', 0.2, 3.2)),
            '[4:v]%s[orb0]' % obshchee,
            "[kart][orb0]xfade=transition=fade:duration=0.7:offset=2.5,%s,fade=t=out:st=7.1:d=0.4[d]" % (
                podpis('The AI reads the picture  ·  the generator builds a house you can enter', 2.9, 7.5)),
        ]
        otrezki += '[d]'
    fg += [
        ("color=c=0x1d2126:s=1920x1080:d=3.5:r=30,format=yuv420p,"
         "drawtext=fontfile='%s':text='Lived-in Houses':fontsize=110:fontcolor=white:x=(w-text_w)/2:y=330,"
         "drawtext=fontfile='%s':text='A rule-based generator of enterable village houses':fontsize=48:"
         "fontcolor=0xdddddd:x=(w-text_w)/2:y=480,"
         "drawtext=fontfile='%s':text='github.com/bandurchencko/lived-in-houses':fontsize=44:fontcolor=0xe07a52:"
         "x=(w-text_w)/2:y=580,"
         "drawtext=fontfile='%s':text='Garden of Worlds  ·  Сад миров':fontsize=36:fontcolor=0xaaaaaa:x=(w-text_w)/2:y=680,"
         "fade=t=in:st=0:d=0.5[e]") % (SHRIFT_B, SHRIFT, SHRIFT_B, SHRIFT),
        '%s[e]concat=n=%d:v=1:a=0[v]' % (otrezki, otrezki.count('[') + 1),
    ]
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'] + vhody + [
        '-filter_complex', ';'.join(fg), '-map', '[v]', '-c:v', 'libx264', '-crf', '24', '-preset', 'slow',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', vyhod]
    subprocess.run(cmd, check=True)
    print('ролик:', vyhod)


if __name__ == '__main__':
    main(*sys.argv[1:7])
