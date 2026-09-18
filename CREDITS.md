# Credits

## Font

The `card.png` identity card is generated with **LanaPixel** by
[eishiya](http://fontstruct.fontshop.com/fontstructions/show/353229).

License: [Creative Commons Attribution-ShareAlike 3.0](http://creativecommons.org/licenses/by-sa/3.0/)

FontStruct is a trademark of FSI FontShop International GmbH.

## Regenerating the card

```bash
python3 -m venv .venv && ./.venv/bin/pip install pillow
./.venv/bin/python make_card.py
```

`avatar.jpg` is the source photo for the ASCII portrait panel.
