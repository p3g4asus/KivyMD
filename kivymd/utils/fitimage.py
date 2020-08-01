"""
Fit Image
=========

Feature to automatically crop a `Kivy` image to fit your layout
Write by Benedikt Zwölfer

Referene - https://gist.github.com/benni12er/95a45eb168fc33a4fcd2d545af692dad


Example:
========

    BoxLayout:
        size_hint_y: None
        height: dp(200)
        orientation: 'vertical'

        FitImage:
            size_hint_y: 3
            source: 'images/img1.jpg'

        FitImage:
            size_hint_y: 1
            source: 'images/img2.jpg'
"""

from kivy.clock import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget


class FitImage(BoxLayout):
    source = ObjectProperty()
    container = ObjectProperty()
    allow_stretch = BooleanProperty(None, allownone=True)
    keep_ratio = BooleanProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(allow_stretch=self.on_allow_stretch)
        self.bind(keep_ratio=self.on_keep_ratio)
        self._late_init()

    def on_allow_stretch(self, inst, val):
        self.on_mod_par()

    def on_keep_ratio(self, inst, val):
        self.on_mod_par()

    def on_mod_par(self):
        if self.allow_stretch is None and self.keep_ratio is None:
            if not self.container or isinstance(self.container, AsyncImage):
                if self.container:
                    self.remove_widget(self.container)
                self._late_init()
        elif (self.allow_stretch is not None or self.keep_ratio is not None):
            if not self.container or isinstance(self.container, Container):
                if self.container:
                    self.remove_widget(self.container)
                    self.unbind(source=self.container.setter("source"))
                    self.container.uninit()
                self._late_init()
            else:
                if self.allow_stretch is not None:
                    self.container.allow_stretch = self.allow_stretch
                if self.keep_ratio is not None:
                    self.container.keep_ratio = self.keep_ratio

    def _late_init(self, *args):
        if self.allow_stretch is None and self.keep_ratio is None:
            self.container = Container(self.source)
            self.bind(source=self.container.setter("source"))
        else:
            kwargs2 = dict()
            if self.allow_stretch is not None:
                kwargs2['allow_stretch'] = self.allow_stretch
            if self.keep_ratio is not None:
                kwargs2['keep_ratio'] = self.keep_ratio
            self.container = AsyncImage(**kwargs2)
            self.bind(size=self.container.setter('size'))
            self.bind(source=self.container.setter("source"))
            self.container.source = self.source
            self.size_hint = (None, None)
            self.container.size = self.size
        self.add_widget(self.container)


class Container(Widget):
    source = ObjectProperty()
    image = ObjectProperty()

    def uninit(self):
        self.image.unbind(on_load=self.adjust_size)
        self.unbind(size=self.adjust_size, pos=self.adjust_size)

    def __init__(self, source, **kwargs):
        super().__init__(**kwargs)
        self.image = AsyncImage()
        self.image.bind(on_load=self.adjust_size)
        self.source = source
        self.bind(size=self.adjust_size, pos=self.adjust_size)

    def on_source(self, instance, value):
        if isinstance(value, str):
            self.image.source = value
        else:
            self.image.texture = value
        self.adjust_size()

    def adjust_size(self, *args):
        if not self.parent or not self.image.texture:
            return

        (par_x, par_y) = self.parent.size

        if par_x == 0 or par_y == 0:
            with self.canvas:
                self.canvas.clear()
            return

        par_scale = par_x / par_y
        (img_x, img_y) = self.image.texture.size
        img_scale = img_x / img_y

        if par_scale > img_scale:
            (img_x_new, img_y_new) = (img_x, img_x / par_scale)
        else:
            (img_x_new, img_y_new) = (img_y * par_scale, img_y)

        crop_pos_x = (img_x - img_x_new) / 2
        crop_pos_y = (img_y - img_y_new) / 2

        subtexture = self.image.texture.get_region(
            crop_pos_x, crop_pos_y, img_x_new, img_y_new
        )

        with self.canvas:
            self.canvas.clear()
            Color(1, 1, 1)
            Rectangle(texture=subtexture, pos=self.pos, size=(par_x, par_y))
