# -*- coding: utf-8 -*-
# pylutim
# Copyright (C) Impulse-PW [Impulse-PW@openmailbox.org]
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import requests
import typing
import os
import imghdr
import base64
from validators.url import url as is_url


class image_too_large(Exception):
    pass


class invalid_server(Exception):
    pass


class invalid_delete_url(Exception):
    pass


class invalid_modify_url(Exception):
    pass


class upload_not_allowed(Exception):
    pass


class controller(object):
    def __init__(self, url: str) -> None:
        self.session = requests.session()
        self.server_info = None
        self.url = url

        if self.url.endswith("/"):
            self.url = self.url[:-1]

        if not self.is_valid_server():
            raise invalid_server("Invalid Lutim server given!")

        self.login_required = self.session.get(
            self.url + "/login").status_code != 404
        self.logged_in = False

    # Not meantioned in Documentation because it is not intended to be used
    # other than in initialization
    def get_server_info(self) -> typing.Union[dict, bool]:
        server_info_expectations = set(["always_encrypt",
                                        "broadcast_message",
                                        "contact",
                                        "default_delay",
                                        "image_magick",
                                        "max_delay",
                                        "max_file_size"])

        try:
            response = self.session.get(self.url + "/infos").json()
        except ValueError:
            return False
        else:
            if server_info_expectations.issubset(list(response.keys())):
                self.server_info = response

                if "upload_enabled" in self.server_info.keys():
                    if not self.server_info['upload_enabled']:
                        raise upload_not_allowed(
                            "Server does not allow uploading!")

                return response
        return False

    # Not meantioned in Documentation because it is not intended to be used
    # other than in initialization
    def is_valid_server(self) -> bool:
        if is_url(self.url):
            if self.get_server_info():
                return True
        return False

    def login(self, username: str, password: str) -> dict:
        if self.login_required:
            if self.logged_in:
                return {"msg": "You're already logged in!", "success": False}

            else:
                response = self.session.post(
                    self.url + "/login",
                    data={
                        "login": username,
                        "password": password,
                        "format": "json"}).json()

                if response["success"]:
                    self.logged_in = True

                return response
        else:
            return {
                "msg": "Server has authentication disabled!",
                "success": False}

    def logout(self) -> dict:
        if self.login_required:
            if self.logged_in:
                response = self.session.post(
                    self.url + "/logout",
                    data={"format": "json"}).json()
                if response["success"]:
                    self.logged_in = False
                return response

            else:
                return {
                    "msg": "Can't log out, you're not logged in!",
                    "success": False}
        else:
            return {
                "msg": "Server has authentication disabled!",
                "success": False}

    def upload(self, file_dir: str, delete_day: int, delete_after_view: int,
               keep_exif: int, crypt: int) -> typing.Union[typing.Type, dict]:
        if not os.path.isfile(file_dir):
            raise OSError("Image file doesn't exist!")
        elif not imghdr.what(file_dir) in ["png", "jpg", "jpeg", "gif"]:
            raise OSError("Image file not any of allowed image formats!")
        elif os.path.getsize(file_dir) > self.server_info["max_file_size"]:
            raise image_too_large(
                "Image exceeds filesize allowed by the server!")
        else:
            if not self.logged_in and self.login_required:
                return {
                    "msg": "You need to be logged in to do that!",
                    "success": False}
            else:
                with open(file_dir, 'rb') as f:
                    response = self.session.post(
                        self.url,
                        files={
                            'file': f},
                        data={
                            'format': 'json',
                            'delete-day': delete_day,
                            'first-view': delete_after_view,
                            'keep-exif': keep_exif,
                            'crypt': crypt}).json()
                    if response["success"]:
                        if self.server_info["image_magick"]:
                            return image(
                                self.url,
                                response["msg"]["real_short"],
                                response["msg"]["short"],
                                response["msg"]["ext"],
                                response["msg"]["token"],
                                response["msg"]["thumb"],
                                self.session)
                        else:
                            return image(
                                self.url,
                                response["msg"]["real_short"],
                                response["msg"]["short"],
                                response["msg"]["ext"],
                                response["msg"]["token"],
                                self.session)
                    else:
                        return response


class image(object):
    def __init__(
            self,
            server_url: str,
            real_short: str,
            short: str,
            ext: str,
            token: str,
            thumbnail: str = None,
            session: requests.session = requests.session()) -> None:
        self.session = session
        self.thumbnail = thumbnail
        self.has_thumbnail = True if thumbnail else False
        self.server_url = server_url
        if not is_url(server_url):
            raise invalid_server("Invalid Lutim server given!")
        controller(self.server_url)
        self.real_short = real_short
        self.short = short
        self.ext = ext
        self.token = token
        self.about_url = "{}/about/{}".format(self.server_url, self.short)
        self.base_url = "{}/{}".format(self.server_url, self.short)
        self.view_url = "{}.{}".format(self.base_url, self.ext)
        self.markdown_url = "![]({})".format(self.base_url)
        self.dl_url = self.base_url + "?dl"
        self.twitter_url = self.base_url + "?t"
        self.delete_url = "{}/d/{}/{}".format(
            self.server_url, self.real_short, self.token)
        self.modify_url = "{}/m/{}/{}".format(
            self.server_url, self.real_short, self.token)

    def delete(self) -> dict:
        response = requests.get(self.delete_url, data={
                                "format": "json"}).json()
        return response

    def download(self, path) -> None:
        with open(path, "wb") as f:
            f.write(self.session.get(self.base_url).content)

    def get_base64(self) -> str:
        return base64.b64encode(self.session.get(self.base_url).content)

    def get_info(self) -> dict:
        return self.session.get(self.about_url).json()

    def get_counter(self) -> dict:
        return self.session.post(
            self.server_url + "/c",
            data={
                "short": self.real_short,
                "token": self.token}).json()

    def modify(self, delete_day: int, first_view: int) -> dict:
        response = requests.post(
            self.modify_url,
            data={
                "delete-day": delete_day,
                "first-view": first_view,
                "format": "json"}).json()

        return response
