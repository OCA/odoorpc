# -*- coding: utf-8 -*-

import base64

from odoorpc.tests import LoginTestCase
from odoorpc.tools import v


class TestFieldBinary(LoginTestCase):
    def test_field_binary_read(self):
        if v(self.odoo.version)[0] < 13:
            img = self.user.image
        else:
            img = self.user.image_1920
        base64.b64decode(img.encode('ascii'))

    def test_field_binary_write(self):
        if v(self.odoo.version)[0] < 13:
            backup = self.user.image
            jpeg_file = (
                b"\xff\xd8\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02"
                b"\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05"
                b"\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e"
                b"\x0b\x09\x09\x0d\x11\x0d\x0e\x0f\x10\x10\x11\x10\x0a\x0c\x12\x13"
                b"\x12\x10\x13\x0f\x10\x10\x10\xff\xc9\x00\x0b\x08\x00\x01\x00\x01"
                b"\x01\x01\x11\x00\xff\xcc\x00\x06\x00\x10\x10\x05\xff\xda\x00\x08"
                b"\x01\x01\x00\x00\x3f\x00\xd2\xcf\x20\xff\xd9"
            )  # https://github.com/mathiasbynens/small/blob/master/jpeg.jpg

            self.user.image = base64.b64encode(jpeg_file).decode('ascii')
            data = self.user.read(['image'])[0]
            decoded = base64.b64decode(data['image'].encode('ascii'))
            self.assertEqual(decoded, jpeg_file)

            # Restore original value
            self.user.image = backup
            data = self.user.read(['image'])[0]
            self.assertEqual(data['image'], backup)
            self.assertEqual(self.user.image, backup)
        else:
            backup = self.user.image_1920
            jpeg_file = (
                b"\xff\xd8\xff\xdb\x00\x43\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02"
                b"\x02\x03\x03\x03\x03\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05"
                b"\x06\x09\x08\x0a\x0a\x09\x08\x09\x09\x0a\x0c\x0f\x0c\x0a\x0b\x0e"
                b"\x0b\x09\x09\x0d\x11\x0d\x0e\x0f\x10\x10\x11\x10\x0a\x0c\x12\x13"
                b"\x12\x10\x13\x0f\x10\x10\x10\xff\xc9\x00\x0b\x08\x00\x01\x00\x01"
                b"\x01\x01\x11\x00\xff\xcc\x00\x06\x00\x10\x10\x05\xff\xda\x00\x08"
                b"\x01\x01\x00\x00\x3f\x00\xd2\xcf\x20\xff\xd9"
            )  # https://github.com/mathiasbynens/small/blob/master/jpeg.jpg

            self.user.image_1920 = base64.b64encode(jpeg_file).decode('ascii')
            data = self.user.read(['image_1920'])[0]
            decoded = base64.b64decode(data['image_1920'].encode('ascii'))
            self.assertEqual(decoded, jpeg_file)

            # Restore original value
            self.user.image_1920 = backup
            data = self.user.read(['image_1920'])[0]
            self.assertEqual(data['image_1920'], backup)
            self.assertEqual(self.user.image_1920, backup)
