# Flask-Sass

instead of `from flask.exts.scss import Scss`

use `from flask_scss import Scss`

if you encounter `from collections import Iterable` error

change the line to `from collections.abc import Iterable`

put all the `*.sass` file in assets folder and you are good to go